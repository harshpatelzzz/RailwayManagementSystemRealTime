"""Test Kafka connection"""
from kafka import KafkaProducer
import time

print("Testing Kafka connection to localhost:9092...")
try:
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        request_timeout_ms=10000,
        api_version=(0, 10, 1)
    )
    print("[SUCCESS] Successfully connected to Kafka!")
    producer.close()
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check if Kafka is running: netstat -ano | findstr :9092")
    print("2. Wait 10-15 seconds after starting Kafka")
    print("3. Check Kafka window for errors")

