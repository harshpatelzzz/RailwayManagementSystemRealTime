"""
Kafka Consumer for RailSewa
Reads messages from Kafka, processes them, and saves to MySQL database
"""

import os
import json
import re
from datetime import datetime
from kafka import KafkaConsumer
import pymysql
from dotenv import load_dotenv
from sparksupport import clean_tweet, extract_pnr, extract_train_number, extract_delay_minutes, classify_severity
from ml_predictor import classify_urgency_ml

# Load environment variables
load_dotenv()

# Kafka Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'raw_tweets')

# Database Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'twitter')


def get_db_connection():
    """Get MySQL database connection"""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None


def save_complaint_to_db(complaint_data):
    """Save processed complaint to MySQL database"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Try to insert with analytics columns (if they exist)
        # If columns don't exist, fall back to basic insert
        try:
            # Check if analytics columns exist by attempting a query
            cursor.execute("""
                SELECT train_number, delay_minutes, severity_label, severity_score 
                FROM tweets 
                LIMIT 1
            """)
            has_analytics_columns = True
        except:
            has_analytics_columns = False
        
        if has_analytics_columns:
            # Insert with analytics columns
            sql = """
            INSERT INTO tweets 
            (tweet, username, pnr, prediction, tweet_id, user_id, chat_id, source, time, response_status,
             train_number, delay_minutes, severity_label, severity_score) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                complaint_data.get('text', ''),
                complaint_data.get('username', ''),
                complaint_data.get('pnr'),
                complaint_data.get('prediction', 0),
                complaint_data.get('complaint_id'),
                complaint_data.get('user_id'),
                complaint_data.get('chat_id'),
                'Telegram',
                datetime.now(),
                0,  # response_status: 0 = not responded
                complaint_data.get('train_number'),
                complaint_data.get('delay_minutes'),
                complaint_data.get('severity_label'),
                complaint_data.get('severity_score')
            )
        else:
            # Fall back to basic insert (without analytics columns)
            sql = """
            INSERT INTO tweets 
            (tweet, username, pnr, prediction, tweet_id, user_id, chat_id, source, time, response_status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                complaint_data.get('text', ''),
                complaint_data.get('username', ''),
                complaint_data.get('pnr'),
                complaint_data.get('prediction', 0),
                complaint_data.get('complaint_id'),
                complaint_data.get('user_id'),
                complaint_data.get('chat_id'),
                'Telegram',
                datetime.now(),
                0  # response_status: 0 = not responded
            )
        
        cursor.execute(sql, values)
        connection.commit()
        
        # Get the inserted ID
        inserted_id = cursor.lastrowid
        cursor.close()
        
        print(f"✅ Saved complaint ID {inserted_id} to database")
        return True
        
    except pymysql.IntegrityError as e:
        if 'Duplicate entry' in str(e):
            print(f"⚠️  Complaint {complaint_data.get('complaint_id')} already exists in database (skipping)")
            connection.rollback()
            return False
        else:
            print(f"❌ Database integrity error: {e}")
            connection.rollback()
            return False
    except Exception as e:
        print(f"❌ Error saving complaint to database: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


def process_message(message_data):
    """Process a single Kafka message"""
    try:
        # Parse JSON message
        if isinstance(message_data, bytes):
            message_data = message_data.decode('utf-8')
        
        if isinstance(message_data, str):
            data = json.loads(message_data)
        else:
            data = message_data
        
        # Extract message fields
        text = data.get('text', '')
        complaint_id = data.get('complaint_id') or data.get('tweet_id') or data.get('message_id')
        user_id = data.get('user_id')
        username = data.get('username') or data.get('first_name', '') or f"user_{user_id}"
        chat_id = data.get('chat_id')
        
        if not text:
            print("⚠️  Empty message text, skipping...")
            return None
        
        # Process the complaint
        cleaned_text = clean_tweet(text)
        pnr = extract_pnr(text)
        
        # Use ML model for classification (with rule-based fallback)
        from ml_predictor import get_predictor
        predictor = get_predictor()
        prediction = classify_urgency_ml(text)
        prediction_method = "ML Model" if predictor.is_available() else "Rule-Based"
        
        train_number = extract_train_number(text)
        delay_minutes = extract_delay_minutes(text)
        severity_label, severity_score = classify_severity(text)
        
        complaint_type = "Emergency" if prediction == 1 else "Feedback"
        
        # Create complaint data structure
        complaint_data = {
            'text': text,
            'username': username,
            'pnr': pnr,
            'prediction': prediction,
            'complaint_id': complaint_id,
            'user_id': user_id,
            'chat_id': chat_id,
            'train_number': train_number,
            'delay_minutes': delay_minutes,
            'severity_label': severity_label,
            'severity_score': severity_score
        }
        
        # Print processing info
        print(f"\n{'='*60}")
        print(f"📨 Processing Complaint")
        print(f"{'='*60}")
        print(f"ID: {complaint_id}")
        print(f"User: {username} (ID: {user_id})")
        print(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
        print(f"PNR: {pnr if pnr else 'Not found'}")
        print(f"Train: {train_number if train_number else 'Not found'}")
        print(f"Delay: {delay_minutes} minutes" if delay_minutes else "Delay: Not found")
        print(f"Classification: {complaint_type} ({prediction}) [{prediction_method}]")
        print(f"Severity: {severity_label} (score: {severity_score})")
        print(f"{'='*60}")
        
        # Save to database
        if save_complaint_to_db(complaint_data):
            print(f"✅ Successfully processed and saved complaint!")
            return complaint_data
        else:
            print(f"❌ Failed to save complaint to database")
            return None
            
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON message: {e}")
        print(f"   Raw message: {message_data[:200]}")
        return None
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function to start Kafka consumer"""
    print("="*60)
    print("🚂 RailSewa - Kafka Consumer")
    print("="*60)
    print(f"Kafka Broker: {KAFKA_BROKER}")
    print(f"Kafka Topic: {KAFKA_TOPIC}")
    print(f"Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    # Check ML model availability
    from ml_predictor import get_predictor
    predictor = get_predictor()
    if predictor.is_available():
        print("[OK] ML Model: Loaded and ready")
    else:
        print("[WARNING] ML Model: Not found, using rule-based classification")
        print("   To train ML model, run: python train_ml_model.py")
    
    print("="*60)
    print("\nStarting consumer...")
    print("Waiting for messages from Kafka...")
    print("Press Ctrl+C to stop.\n")
    
    try:
        # Create Kafka consumer
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='latest',  # Start from latest messages
            enable_auto_commit=True,
            group_id='railsewa-consumer-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        print("✅ Connected to Kafka!")
        print("✅ Consumer ready. Listening for messages...\n")
        
        # Process messages
        processed_count = 0
        for message in consumer:
            try:
                # Get message value (already deserialized)
                message_data = message.value
                
                # Process the message
                result = process_message(message_data)
                
                if result:
                    processed_count += 1
                    print(f"\n📊 Total processed: {processed_count}\n")
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error in message loop: {e}")
                continue
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Consumer stopped by user")
    except Exception as e:
        print(f"❌ Error starting consumer: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'consumer' in locals():
            consumer.close()
        print("\n✅ Consumer closed. Goodbye!")


if __name__ == "__main__":
    main()

