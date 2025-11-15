"""
Original Live Processing Script
Alternative implementation for complaint processing
"""

from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
from sparksupport import create_spark_session

def process_complaints(rdd):
    """Process complaints from RDD"""
    if not rdd.isEmpty():
        complaints = rdd.collect()
        for complaint in complaints:
            try:
                data = json.loads(complaint[1])
                print(f"Processing complaint: {data.get('text', '')[:50]}...")
            except Exception as e:
                print(f"Error parsing complaint: {e}")

def main():
    spark = create_spark_session("ComplaintStreaming")
    ssc = StreamingContext(spark.sparkContext, 10)
    
    kafka_stream = KafkaUtils.createStream(
        ssc,
        'localhost:2181',
        'complaint_group',
        {'raw_tweets': 1}
    )
    
    kafka_stream.foreachRDD(process_complaints)
    
    ssc.start()
    ssc.awaitTermination()

if __name__ == "__main__":
    main()

