"""
Live Processing of Telegram Complaints using Spark Streaming
Reads from Kafka, processes complaints, and saves to MySQL
"""

from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from sparksupport import (
    create_spark_session, extract_pnr_udf, clean_tweet_udf,
    classify_urgency_udf, parse_tweet_json, get_tweet_text
)
from pyspark.sql.functions import col, udf, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, TimestampType
import json
import pymysql
import os
from datetime import datetime

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
        
        # Check if user_id and chat_id columns exist (for backward compatibility)
        # If they don't exist, use simpler insert
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
    except Exception as e:
        print(f"Error saving complaint to database: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def process_rdd(rdd):
    """Process each RDD batch"""
    if rdd.isEmpty():
        return
    
    # Create Spark session for this batch
    spark = create_spark_session("LiveComplaintProcessing")
    
    try:
        # Convert RDD to DataFrame
        # Schema matches Telegram message structure
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
        
        # Parse JSON strings
        parsed_rdd = rdd.map(lambda x: json.loads(x[1]) if isinstance(x, tuple) else json.loads(x))
        df = spark.createDataFrame(parsed_rdd, complaint_schema)
        
        # Process complaints
        df = df.withColumn("cleaned_text", clean_tweet_udf(col("text")))
        df = df.withColumn("pnr", extract_pnr_udf(col("text")))
        df = df.withColumn("prediction", classify_urgency_udf(col("cleaned_text")))
        
        # Collect and save to database
        rows = df.collect()
        
        for row in rows:
            complaint_data = {
                'text': row.text,
                'username': row.username or f"user_{row.user_id}",
                'pnr': row.pnr,
                'prediction': row.prediction,
                'complaint_id': row.complaint_id,
                'user_id': row.user_id,
                'chat_id': row.chat_id
            }
            
            save_complaint_to_db(complaint_data)
            print(f"Processed complaint {row.complaint_id}: Prediction = {row.prediction} ({'Emergency' if row.prediction == 1 else 'Feedback'})")
    
    except Exception as e:
        print(f"Error processing RDD: {e}")
        import traceback
        traceback.print_exc()
    finally:
        spark.stop()

def main():
    """Main streaming function"""
    
    # Spark configuration
    spark = create_spark_session("LiveComplaintStreaming")
    ssc = StreamingContext(spark.sparkContext, batchDuration=10)  # 10 second batches
    
    # Kafka configuration
    kafka_brokers = os.getenv('KAFKA_BROKERS', 'localhost:9092')
    kafka_topic = os.getenv('KAFKA_TOPIC', 'raw_tweets')
    
    print(f"Connecting to Kafka: {kafka_brokers}")
    print(f"Topic: {kafka_topic}")
    print("Processing Telegram complaints...")
    
    # Create Kafka stream
    kafka_stream = KafkaUtils.createStream(
        ssc,
        zookeeper_quorum='localhost:2181',
        group_id='complaint_processor',
        topics={kafka_topic: 1}
    )
    
    # Process each batch
    kafka_stream.foreachRDD(process_rdd)
    
    print("Starting Spark Streaming...")
    ssc.start()
    ssc.awaitTermination()

if __name__ == "__main__":
    main()

