"""
Live Processing of Tweets using Spark Streaming
Reads from Kafka, processes tweets, and saves to MySQL
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

def save_tweet_to_db(tweet_data):
    """Save processed tweet to MySQL database"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        sql = """
        INSERT INTO tweets 
        (tweet, username, pnr, prediction, tweet_id, time, response_status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            tweet_data.get('tweet', ''),
            tweet_data.get('username', ''),
            tweet_data.get('pnr'),
            tweet_data.get('prediction', 0),
            tweet_data.get('tweet_id'),
            datetime.now(),
            0  # response_status: 0 = not responded
        )
        
        cursor.execute(sql, values)
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error saving tweet to database: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def process_rdd(rdd):
    """Process each RDD batch"""
    if rdd.isEmpty():
        return
    
    # Create Spark session for this batch
    spark = create_spark_session("LiveTweetProcessing")
    
    try:
        # Convert RDD to DataFrame
        tweet_schema = StructType([
            StructField("tweet_id", LongType(), True),
            StructField("text", StringType(), True),
            StructField("author_id", StringType(), True),
            StructField("created_at", StringType(), True)
        ])
        
        # Parse JSON strings
        parsed_rdd = rdd.map(lambda x: json.loads(x[1]) if isinstance(x, tuple) else json.loads(x))
        df = spark.createDataFrame(parsed_rdd, tweet_schema)
        
        # Process tweets
        df = df.withColumn("cleaned_text", clean_tweet_udf(col("text")))
        df = df.withColumn("pnr", extract_pnr_udf(col("text")))
        df = df.withColumn("prediction", classify_urgency_udf(col("cleaned_text")))
        
        # Collect and save to database
        rows = df.collect()
        
        for row in rows:
            tweet_data = {
                'tweet': row.text,
                'username': row.author_id or 'unknown',
                'pnr': row.pnr,
                'prediction': row.prediction,
                'tweet_id': row.tweet_id
            }
            
            save_tweet_to_db(tweet_data)
            print(f"Processed tweet {row.tweet_id}: Prediction = {row.prediction}")
    
    except Exception as e:
        print(f"Error processing RDD: {e}")
    finally:
        spark.stop()

def main():
    """Main streaming function"""
    
    # Spark configuration
    spark = create_spark_session("LiveTweetStreaming")
    ssc = StreamingContext(spark.sparkContext, batchDuration=10)  # 10 second batches
    
    # Kafka configuration
    kafka_brokers = os.getenv('KAFKA_BROKERS', 'localhost:9092')
    kafka_topic = os.getenv('KAFKA_TOPIC', 'twitterstream')
    
    print(f"Connecting to Kafka: {kafka_brokers}")
    print(f"Topic: {kafka_topic}")
    
    # Create Kafka stream
    kafka_stream = KafkaUtils.createStream(
        ssc,
        zookeeper_quorum='localhost:2181',
        group_id='tweet_processor',
        topics={kafka_topic: 1}
    )
    
    # Process each batch
    kafka_stream.foreachRDD(process_rdd)
    
    print("Starting Spark Streaming...")
    ssc.start()
    ssc.awaitTermination()

if __name__ == "__main__":
    main()

