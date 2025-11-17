"""
Live Processing of Telegram Complaints using Spark Structured Streaming
Reads from Kafka, processes complaints, and saves to MySQL
Uses Structured Streaming (works with Kafka KRaft mode, no Zookeeper needed)
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType
from sparksupport import (
    create_spark_session, extract_pnr_udf, clean_tweet_udf,
    classify_urgency_udf
)
import json
import pymysql
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
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
            charset='utf8mb4'
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def save_complaint_to_db(complaint_data):
    """Save processed complaint to MySQL database"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
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
        cursor.close()
        return True
    except pymysql.IntegrityError as e:
        if 'Duplicate entry' in str(e):
            print(f"⚠️  Complaint {complaint_data.get('complaint_id')} already exists (skipping)")
            connection.rollback()
            return False
        else:
            print(f"Error saving complaint to database: {e}")
            connection.rollback()
            return False
    except Exception as e:
        print(f"Error saving complaint to database: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def process_batch(df, epoch_id):
    """Process each batch of streaming data"""
    if df.isEmpty():
        return
    
    try:
        # Process complaints
        df_processed = df.withColumn("cleaned_text", clean_tweet_udf(col("text")))
        df_processed = df_processed.withColumn("pnr", extract_pnr_udf(col("text")))
        df_processed = df_processed.withColumn("prediction", classify_urgency_udf(col("cleaned_text")))
        
        # Collect and save to database
        rows = df_processed.collect()
        
        for row in rows:
            complaint_data = {
                'text': row.text,
                'username': row.username or f"user_{row.user_id}",
                'pnr': row.pnr if row.pnr else None,
                'prediction': row.prediction,
                'complaint_id': row.complaint_id,
                'user_id': row.user_id,
                'chat_id': row.chat_id
            }
            
            if save_complaint_to_db(complaint_data):
                print(f"✅ Processed complaint {row.complaint_id}: Prediction = {row.prediction} ({'Emergency' if row.prediction == 1 else 'Feedback'})")
    
    except Exception as e:
        print(f"❌ Error processing batch: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main streaming function using Structured Streaming"""
    
    # Kafka configuration
    kafka_brokers = os.getenv('KAFKA_BROKER', 'localhost:9092')
    kafka_topic = os.getenv('KAFKA_TOPIC', 'raw_tweets')
    
    print("="*60)
    print("🚂 RailSewa - Spark Structured Streaming")
    print("="*60)
    print(f"Kafka Broker: {kafka_brokers}")
    print(f"Kafka Topic: {kafka_topic}")
    print(f"Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print("="*60)
    print("\nStarting Spark Structured Streaming...")
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("RailSewaComplaintProcessing") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    # Define schema for Kafka messages (JSON format)
    complaint_schema = StructType([
        StructField("complaint_id", LongType(), True),
        StructField("text", StringType(), True),
        StructField("user_id", LongType(), True),
        StructField("username", StringType(), True),
        StructField("first_name", StringType(), True),
        StructField("last_name", StringType(), True),
        StructField("chat_id", LongType(), True),
        StructField("timestamp", StringType(), True)
    ])
    
    # Read from Kafka
    kafka_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_brokers) \
        .option("subscribe", kafka_topic) \
        .option("startingOffsets", "latest") \
        .load()
    
    # Parse JSON from Kafka value
    parsed_df = kafka_df.select(
        from_json(col("value").cast("string"), complaint_schema).alias("data")
    ).select("data.*")
    
    # Process and write
    query = parsed_df.writeStream \
        .foreachBatch(process_batch) \
        .outputMode("append") \
        .trigger(processingTime='10 seconds') \
        .start()
    
    print("✅ Spark Streaming started!")
    print("Waiting for messages from Kafka...")
    print("Press Ctrl+C to stop.\n")
    
    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopping Spark Streaming...")
        query.stop()
        spark.stop()
        print("✅ Spark Streaming stopped.")

if __name__ == "__main__":
    main()

