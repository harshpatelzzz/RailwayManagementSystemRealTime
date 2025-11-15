"""
Full System Runner - Simulates Complete RailSewa Infrastructure
Follows QUICKSTART.md workflow but runs locally without external dependencies
"""

import os
import json
import time
import threading
from datetime import datetime
from sparksupport import clean_tweet, extract_pnr, classify_urgency
from dotenv import load_dotenv
import sqlite3

# Load environment variables
load_dotenv()

class LocalDatabase:
    """Local SQLite database to simulate MySQL"""
    
    def __init__(self, db_path='local_twitter.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables matching schema.sql"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tweets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tweet TEXT NOT NULL,
                username TEXT,
                pnr INTEGER,
                prediction INTEGER DEFAULT 0,
                tweet_id INTEGER UNIQUE,
                latitude REAL,
                longitude REAL,
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_status INTEGER DEFAULT 0,
                response TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print("[DATABASE] Tables created successfully")
    
    def insert_tweet(self, tweet_data):
        """Insert tweet into database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tweets (tweet, username, pnr, prediction, tweet_id, time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            tweet_data['tweet'],
            tweet_data['username'],
            tweet_data.get('pnr'),
            tweet_data['prediction'],
            tweet_data.get('tweet_id'),
            datetime.now()
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_stats(self):
        """Get statistics"""
        cursor = self.conn.cursor()
        
        total = cursor.execute('SELECT COUNT(*) FROM tweets').fetchone()[0]
        emergency = cursor.execute('SELECT COUNT(*) FROM tweets WHERE prediction = 1').fetchone()[0]
        feedback = cursor.execute('SELECT COUNT(*) FROM tweets WHERE prediction = 0').fetchone()[0]
        responded = cursor.execute('SELECT COUNT(*) FROM tweets WHERE response_status = 1').fetchone()[0]
        
        return {
            'total': total,
            'emergency': emergency,
            'feedback': feedback,
            'responded': responded,
            'pending': total - responded
        }
    
    def get_tweets(self, filter_type='all', limit=100):
        """Get tweets with filtering"""
        cursor = self.conn.cursor()
        
        if filter_type == 'emergency':
            query = 'SELECT * FROM tweets WHERE prediction = 1 ORDER BY time DESC LIMIT ?'
        elif filter_type == 'feedback':
            query = 'SELECT * FROM tweets WHERE prediction = 0 ORDER BY time DESC LIMIT ?'
        else:
            query = 'SELECT * FROM tweets ORDER BY time DESC LIMIT ?'
        
        cursor.execute(query, (limit,))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

class KafkaSimulator:
    """Simulates Kafka message queue"""
    
    def __init__(self):
        self.messages = []
        self.subscribers = []
        self.running = False
    
    def produce(self, topic, message):
        """Produce message to topic"""
        self.messages.append({
            'topic': topic,
            'message': message,
            'timestamp': time.time()
        })
        # Notify subscribers
        for callback in self.subscribers:
            callback(message)
    
    def subscribe(self, callback):
        """Subscribe to messages"""
        self.subscribers.append(callback)
    
    def start(self):
        """Start Kafka simulator"""
        self.running = True
        print("[KAFKA] Kafka simulator started")

class TwitterStreamSimulator:
    """Simulates Twitter streaming"""
    
    def __init__(self, kafka):
        self.kafka = kafka
        self.running = False
        self.sample_tweets = [
            "Train 12345 is delayed by 2 hours! PNR: 1234567890 Urgent help needed @RailMinIndia",
            "Great service on Indian Railways! Comfortable journey, clean coaches.",
            "Medical emergency in coach S3. Need immediate assistance. PNR: 9876543210",
            "Excellent food quality and staff behavior. Keep up the good work!",
            "Train breakdown on track. Passengers stranded. PNR: 5555555555",
            "Thank you for the punctual service. Very satisfied with the journey.",
            "AC not working in coach A1. Very uncomfortable. PNR: 1111111111",
            "Clean washrooms and well-maintained stations. Great job!",
            "Train cancelled without notice. Need refund. PNR: 2222222222",
            "Smooth journey, on-time arrival. Highly recommend!",
        ]
    
    def start_streaming(self):
        """Start streaming tweets"""
        self.running = True
        print("[TWITTER STREAM] Starting Twitter stream simulation...")
        
        tweet_id = int(time.time() * 1000)
        for i, tweet_text in enumerate(self.sample_tweets):
            if not self.running:
                break
            
            tweet_data = {
                'tweet_id': tweet_id + i,
                'text': tweet_text,
                'author_id': f'user{i+1}',
                'created_at': datetime.now().isoformat()
            }
            
            # Send to Kafka
            self.kafka.produce('twitterstream', json.dumps(tweet_data))
            print(f"[TWITTER STREAM] Tweet {i+1}/{len(self.sample_tweets)} sent to Kafka")
            time.sleep(2)  # Simulate streaming delay
        
        print("[TWITTER STREAM] Streaming completed")

class SparkProcessor:
    """Simulates Spark processing"""
    
    def __init__(self, kafka, database):
        self.kafka = kafka
        self.database = database
        self.running = False
        self.processed_count = 0
    
    def process_tweet(self, tweet_json):
        """Process a single tweet"""
        try:
            data = json.loads(tweet_json)
            
            text = data.get('text', '')
            cleaned = clean_tweet(text)
            pnr = extract_pnr(text)
            prediction = classify_urgency(cleaned)
            
            tweet_data = {
                'tweet': text,
                'username': data.get('author_id', 'unknown'),
                'pnr': pnr,
                'prediction': prediction,
                'tweet_id': data.get('tweet_id')
            }
            
            # Save to database
            self.database.insert_tweet(tweet_data)
            self.processed_count += 1
            
            print(f"[SPARK] Processed tweet #{self.processed_count}: {prediction} ({'Emergency' if prediction == 1 else 'Feedback'})")
            return tweet_data
        except Exception as e:
            print(f"[SPARK] Error processing tweet: {e}")
            return None
    
    def start_processing(self):
        """Start processing tweets from Kafka"""
        self.running = True
        print("[SPARK] Spark processor started")
        
        def on_message(message):
            if self.running:
                self.process_tweet(message)
        
        self.kafka.subscribe(on_message)

class FullSystemRunner:
    """Main system runner"""
    
    def __init__(self):
        print("=" * 70)
        print("RailSewa - Full System Runner")
        print("=" * 70)
        print("\nInitializing components...")
        
        # Step 1: Setup Database (Step 3 in QUICKSTART)
        print("\n[STEP 3] Setting up database...")
        self.db = LocalDatabase()
        
        # Step 2: Setup Kafka (Step 4-5 in QUICKSTART)
        print("[STEP 4-5] Setting up Kafka simulator...")
        self.kafka = KafkaSimulator()
        self.kafka.start()
        
        # Step 3: Setup Spark Processor (Step 9 in QUICKSTART)
        print("[STEP 9] Setting up Spark processor...")
        self.spark = SparkProcessor(self.kafka, self.db)
        self.spark.start_processing()
        
        # Step 4: Setup Twitter Stream (Step 7 in QUICKSTART)
        print("[STEP 7] Setting up Twitter stream...")
        self.twitter_stream = TwitterStreamSimulator(self.kafka)
    
    def run(self):
        """Run the full system"""
        print("\n" + "=" * 70)
        print("Starting Full System")
        print("=" * 70)
        
        # Start Twitter streaming in background
        stream_thread = threading.Thread(target=self.twitter_stream.start_streaming)
        stream_thread.daemon = True
        stream_thread.start()
        
        # Wait for streaming to complete
        stream_thread.join()
        
        # Give time for processing
        time.sleep(3)
        
        # Display results
        self.display_results()
    
    def display_results(self):
        """Display system results"""
        print("\n" + "=" * 70)
        print("System Results")
        print("=" * 70)
        
        stats = self.db.get_stats()
        
        print(f"\n[DATABASE STATISTICS]")
        print(f"  Total Tweets:    {stats['total']}")
        print(f"  Emergency:       {stats['emergency']}")
        print(f"  Feedback:        {stats['feedback']}")
        print(f"  Responded:       {stats['responded']}")
        print(f"  Pending:         {stats['pending']}")
        
        print(f"\n[PROCESSING STATISTICS]")
        print(f"  Processed:       {self.spark.processed_count} tweets")
        
        print(f"\n[RECENT TWEETS]")
        recent_tweets = self.db.get_tweets(limit=5)
        for tweet in recent_tweets:
            type_label = "Emergency" if tweet['prediction'] == 1 else "Feedback"
            pnr_info = f"PNR: {tweet['pnr']}" if tweet['pnr'] else "No PNR"
            print(f"  [{tweet['id']}] {type_label} - @{tweet['username']}")
            print(f"      {tweet['tweet'][:60]}...")
            print(f"      {pnr_info}")
            print()
        
        print("=" * 70)
        print("System Status: RUNNING")
        print("=" * 70)
        print("\nComponents:")
        print("  [OK] Database (SQLite)")
        print("  [OK] Kafka Simulator")
        print("  [OK] Spark Processor")
        print("  [OK] Twitter Stream")
        print("\nTo view web dashboard, open: dashboard.html")
        print("Database file: local_twitter.db")

def main():
    """Main function"""
    print("\nFollowing QUICKSTART.md workflow...")
    print("\nNote: This is a local simulation. For production setup:")
    print("  - Use real MySQL database (AWS RDS)")
    print("  - Install Apache Kafka & Zookeeper")
    print("  - Setup Spark cluster")
    print("  - Configure Twitter API credentials")
    print("\nStarting local simulation...\n")
    
    runner = FullSystemRunner()
    runner.run()
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("1. View dashboard: Open dashboard.html in browser")
    print("2. Check database: local_twitter.db")
    print("3. For production: Follow QUICKSTART.md with real infrastructure")

if __name__ == "__main__":
    main()

