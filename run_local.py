"""
Local Runner for RailSewa Project
Runs the system locally without requiring Kafka, Spark, or MySQL
Simulates the full workflow for testing
"""

import os
import json
import time
from datetime import datetime
from sparksupport import clean_tweet, extract_pnr, classify_urgency
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LocalTweetProcessor:
    """Local tweet processor that simulates the full system"""
    
    def __init__(self):
        self.tweets = []
        self.stats = {
            'total': 0,
            'emergency': 0,
            'feedback': 0,
            'processed': 0
        }
    
    def process_tweet(self, tweet_text, username="test_user", tweet_id=None):
        """Process a single tweet"""
        if tweet_id is None:
            tweet_id = int(time.time() * 1000)  # Generate ID
        
        # Clean and process
        cleaned = clean_tweet(tweet_text)
        pnr = extract_pnr(tweet_text)
        prediction = classify_urgency(cleaned)
        tweet_type = "Emergency" if prediction == 1 else "Feedback"
        
        # Create tweet record
        tweet_data = {
            'id': len(self.tweets) + 1,
            'tweet_id': tweet_id,
            'tweet': tweet_text,
            'cleaned_tweet': cleaned,
            'username': username,
            'pnr': pnr,
            'prediction': prediction,
            'type': tweet_type,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'response_status': 0
        }
        
        # Update stats
        self.stats['total'] += 1
        if prediction == 1:
            self.stats['emergency'] += 1
        else:
            self.stats['feedback'] += 1
        self.stats['processed'] += 1
        
        # Store tweet
        self.tweets.append(tweet_data)
        
        return tweet_data
    
    def get_stats(self):
        """Get processing statistics"""
        return self.stats.copy()
    
    def get_tweets(self, filter_type='all', limit=10):
        """Get tweets with optional filtering"""
        tweets = self.tweets.copy()
        
        if filter_type == 'emergency':
            tweets = [t for t in tweets if t['prediction'] == 1]
        elif filter_type == 'feedback':
            tweets = [t for t in tweets if t['prediction'] == 0]
        
        # Sort by time (newest first) and limit
        tweets.sort(key=lambda x: x['time'], reverse=True)
        return tweets[:limit]
    
    def respond_to_tweet(self, tweet_id, response):
        """Simulate responding to a tweet"""
        for tweet in self.tweets:
            if tweet['id'] == tweet_id:
                tweet['response'] = response
                tweet['response_status'] = 1
                return True
        return False

def simulate_twitter_stream(processor, num_tweets=10):
    """Simulate incoming tweets"""
    sample_tweets = [
        ("Train 12345 is delayed by 2 hours! PNR: 1234567890 Urgent help needed @RailMinIndia", "user1"),
        ("Great service on Indian Railways! Comfortable journey, clean coaches.", "user2"),
        ("Medical emergency in coach S3. Need immediate assistance. PNR: 9876543210", "user3"),
        ("Excellent food quality and staff behavior. Keep up the good work!", "user4"),
        ("Train breakdown on track. Passengers stranded. PNR: 5555555555", "user5"),
        ("Thank you for the punctual service. Very satisfied with the journey.", "user6"),
        ("AC not working in coach A1. Very uncomfortable. PNR: 1111111111", "user7"),
        ("Clean washrooms and well-maintained stations. Great job!", "user8"),
        ("Train cancelled without notice. Need refund. PNR: 2222222222", "user9"),
        ("Smooth journey, on-time arrival. Highly recommend!", "user10"),
    ]
    
    print("=" * 70)
    print("RailSewa - Local System Runner")
    print("=" * 70)
    print(f"\nSimulating Twitter stream with {num_tweets} tweets...\n")
    
    for i, (tweet_text, username) in enumerate(sample_tweets[:num_tweets], 1):
        print(f"Processing Tweet {i}/{num_tweets}...")
        result = processor.process_tweet(tweet_text, username)
        
        print(f"  User: {result['username']}")
        print(f"  Text: {result['tweet'][:60]}...")
        print(f"  Type: {result['type']}")
        print(f"  PNR: {result['pnr'] if result['pnr'] else 'Not found'}")
        print()
        
        time.sleep(0.5)  # Simulate processing delay
    
    return processor

def display_dashboard(processor):
    """Display a simple dashboard"""
    stats = processor.get_stats()
    tweets = processor.get_tweets(limit=5)
    
    print("=" * 70)
    print("DASHBOARD - Real-time Statistics")
    print("=" * 70)
    print(f"\nTotal Tweets Processed: {stats['total']}")
    print(f"Emergency Tweets:       {stats['emergency']}")
    print(f"Feedback Tweets:        {stats['feedback']}")
    print(f"Processing Rate:        {stats['processed']} tweets")
    
    print("\n" + "-" * 70)
    print("Recent Tweets (Last 5)")
    print("-" * 70)
    
    for tweet in tweets:
        type_badge = "[EMERGENCY]" if tweet['prediction'] == 1 else "[FEEDBACK]"
        pnr_info = f"PNR: {tweet['pnr']}" if tweet['pnr'] else "No PNR"
        
        print(f"\n[{tweet['id']}] {type_badge} - {tweet['time']}")
        print(f"  User: {tweet['username']}")
        print(f"  Text: {tweet['tweet'][:70]}...")
        print(f"  {pnr_info}")

def interactive_mode(processor):
    """Interactive mode for testing"""
    print("\n" + "=" * 70)
    print("Interactive Mode")
    print("=" * 70)
    print("\nCommands:")
    print("  'stats' - Show statistics")
    print("  'tweets [all|emergency|feedback]' - Show tweets")
    print("  'process <tweet_text>' - Process a new tweet")
    print("  'respond <id> <response>' - Respond to a tweet")
    print("  'quit' - Exit")
    print()
    
    while True:
        try:
            command = input("RailSewa> ").strip()
            
            if not command:
                continue
            
            if command == 'quit' or command == 'exit':
                break
            elif command == 'stats':
                stats = processor.get_stats()
                print(f"\nStatistics:")
                print(f"  Total: {stats['total']}")
                print(f"  Emergency: {stats['emergency']}")
                print(f"  Feedback: {stats['feedback']}")
            elif command.startswith('tweets'):
                parts = command.split()
                filter_type = parts[1] if len(parts) > 1 else 'all'
                tweets = processor.get_tweets(filter_type=filter_type, limit=10)
                print(f"\nShowing {len(tweets)} tweets (filter: {filter_type}):")
                for tweet in tweets:
                    type_badge = "[EMERGENCY]" if tweet['prediction'] == 1 else "[FEEDBACK]"
                    print(f"  [{tweet['id']}] {type_badge} - {tweet['username']}: {tweet['tweet'][:50]}...")
            elif command.startswith('process '):
                tweet_text = command[8:]
                result = processor.process_tweet(tweet_text)
                print(f"\nProcessed tweet #{result['id']}:")
                print(f"  Type: {result['type']}")
                print(f"  PNR: {result['pnr'] if result['pnr'] else 'Not found'}")
            elif command.startswith('respond '):
                parts = command.split(' ', 2)
                if len(parts) >= 3:
                    tweet_id = int(parts[1])
                    response = parts[2]
                    if processor.respond_to_tweet(tweet_id, response):
                        print(f"\nResponse added to tweet #{tweet_id}")
                    else:
                        print(f"\nTweet #{tweet_id} not found")
                else:
                    print("Usage: respond <id> <response_text>")
            else:
                print("Unknown command. Type 'quit' to exit.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main function"""
    processor = LocalTweetProcessor()
    
    print("\n" + "=" * 70)
    print("RailSewa - Local System Runner")
    print("=" * 70)
    print("\nThis runs the system locally without requiring:")
    print("  - Kafka/Zookeeper")
    print("  - Spark cluster")
    print("  - MySQL database")
    print("  - Twitter API")
    print("\nIt simulates the full workflow for testing purposes.")
    print()
    
    # Run simulation
    processor = simulate_twitter_stream(processor, num_tweets=10)
    
    # Display dashboard
    display_dashboard(processor)
    
    # Ask for interactive mode (skip if not in interactive terminal)
    print("\n" + "=" * 70)
    try:
        response = input("Enter interactive mode? (y/n): ").strip().lower()
        
        if response == 'y' or response == 'yes':
            interactive_mode(processor)
        else:
            print_summary(processor)
    except (EOFError, KeyboardInterrupt):
        # Not in interactive terminal, just show summary
        print_summary(processor)

def print_summary(processor):
    """Print summary and next steps"""
    print("\n" + "=" * 70)
    print("System Running Successfully!")
    print("=" * 70)
    print("\nThe local system has processed tweets successfully.")
    print("\nTo run the full system with real infrastructure:")
    print("  1. Setup MySQL database (see database/schema.sql)")
    print("  2. Install and start Kafka/Zookeeper")
    print("  3. Configure Twitter API credentials in .env")
    print("  4. Run: python kafka_file/stream_data.py")
    print("  5. Run: spark-submit new_live_processing.py")
    print("\nFor interactive mode, run: python run_local.py")
    print("See README.md or QUICKSTART.md for detailed instructions.")

if __name__ == "__main__":
    main()

