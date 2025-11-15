"""
Original Live Processing Script
Alternative implementation for tweet processing
"""

from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
from sparksupport import create_spark_session

def process_tweets(rdd):
    """Process tweets from RDD"""
    if not rdd.isEmpty():
        tweets = rdd.collect()
        for tweet in tweets:
            try:
                data = json.loads(tweet[1])
                print(f"Processing tweet: {data.get('text', '')[:50]}...")
            except Exception as e:
                print(f"Error parsing tweet: {e}")

def main():
    spark = create_spark_session("TweetStreaming")
    ssc = StreamingContext(spark.sparkContext, 10)
    
    kafka_stream = KafkaUtils.createStream(
        ssc,
        'localhost:2181',
        'tweet_group',
        {'twitterstream': 1}
    )
    
    kafka_stream.foreachRDD(process_tweets)
    
    ssc.start()
    ssc.awaitTermination()

if __name__ == "__main__":
    main()

