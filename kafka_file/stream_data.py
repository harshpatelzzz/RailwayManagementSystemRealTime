"""
Twitter Stream Data Producer for Kafka
Streams tweets related to Indian Railways and sends them to Kafka topic
"""

import tweepy
import json
import time
from kafka import KafkaProducer
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TwitterStreamListener(tweepy.StreamingClient):
    """Custom Twitter Stream Listener"""
    
    def __init__(self, bearer_token, producer, topic):
        super().__init__(bearer_token)
        self.producer = producer
        self.topic = topic
        
    def on_tweet(self, tweet):
        """Called when a new tweet is received"""
        try:
            # Extract tweet data
            tweet_data = {
                'tweet_id': tweet.id,
                'text': tweet.text,
                'author_id': tweet.author_id,
                'created_at': str(tweet.created_at),
                'public_metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else {}
            }
            
            # Send to Kafka
            self.producer.send(self.topic, value=json.dumps(tweet_data).encode('utf-8'))
            print(f"Tweet sent to Kafka: {tweet.id}")
            
        except Exception as e:
            print(f"Error processing tweet: {e}")
    
    def on_error(self, status):
        """Handle errors"""
        print(f"Error: {status}")
        return True

def main():
    """Main function to start streaming"""
    
    # Kafka configuration
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'twitterstream')
    
    # Twitter API credentials
    BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
    CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
    ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    if not BEARER_TOKEN:
        print("Error: Twitter Bearer Token not found in environment variables")
        return
    
    # Initialize Kafka Producer
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"Connected to Kafka broker: {KAFKA_BROKER}")
    except Exception as e:
        print(f"Error connecting to Kafka: {e}")
        return
    
    # Initialize Twitter Stream
    stream = TwitterStreamListener(BEARER_TOKEN, producer, KAFKA_TOPIC)
    
    # Add rules for Indian Railways related tweets
    # Remove existing rules
    rules = stream.get_rules()
    if rules.data:
        rule_ids = [rule.id for rule in rules.data]
        stream.delete_rules(rule_ids)
    
    # Add new rules
    rules = [
        "Indian Railways OR @RailMinIndia OR @IRCTCofficial OR railway complaint",
        "train delay OR train late OR railway service",
        "PNR status OR railway ticket OR train booking"
    ]
    
    for rule in rules:
        stream.add_rules(tweepy.StreamRule(rule))
    
    print("Starting Twitter stream...")
    print("Streaming tweets related to Indian Railways...")
    
    # Start streaming
    try:
        stream.filter(
            tweet_fields=['created_at', 'author_id', 'public_metrics'],
            expansions=['author_id']
        )
    except KeyboardInterrupt:
        print("\nStopping stream...")
        producer.close()
    except Exception as e:
        print(f"Stream error: {e}")
        producer.close()

if __name__ == "__main__":
    main()

