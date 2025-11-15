"""
Demo script to test tweet processing without full infrastructure
This demonstrates the core functionality without requiring Kafka, Spark, or MySQL
"""

import os
import sys
from sparksupport import clean_tweet, extract_pnr, classify_urgency

def demo_tweet_processing():
    """Demonstrate tweet processing functionality"""
    print("=" * 60)
    print("RailSewa - Tweet Processing Demo")
    print("=" * 60)
    
    # Sample tweets
    sample_tweets = [
        {
            "text": "Train 12345 is delayed by 2 hours! PNR: 1234567890 Urgent help needed @RailMinIndia",
            "expected_type": "Emergency"
        },
        {
            "text": "Great service on Indian Railways! Comfortable journey, clean coaches. Thank you!",
            "expected_type": "Feedback"
        },
        {
            "text": "Medical emergency in coach S3. Need immediate assistance. PNR: 9876543210",
            "expected_type": "Emergency"
        },
        {
            "text": "Excellent food quality and staff behavior. Keep up the good work!",
            "expected_type": "Feedback"
        },
        {
            "text": "Train breakdown on track. Passengers stranded. PNR: 5555555555",
            "expected_type": "Emergency"
        }
    ]
    
    print("\nProcessing sample tweets...\n")
    
    for i, tweet_data in enumerate(sample_tweets, 1):
        text = tweet_data["text"]
        expected = tweet_data["expected_type"]
        
        # Process tweet
        cleaned = clean_tweet(text)
        pnr = extract_pnr(text)
        prediction = classify_urgency(cleaned)
        tweet_type = "Emergency" if prediction == 1 else "Feedback"
        
        # Display results
        print(f"Tweet {i}:")
        print(f"  Original: {text}")
        print(f"  Cleaned:  {cleaned}")
        print(f"  PNR:      {pnr if pnr else 'Not found'}")
        print(f"  Type:     {tweet_type} (Expected: {expected})")
        match_status = "[OK]" if tweet_type == expected else "[MISMATCH]"
        print(f"  Match:    {match_status}")
        print()
    
    print("=" * 60)
    print("Demo completed!")
    print("=" * 60)
    print("\nNote: This is a rule-based classifier.")
    print("For production, train an ML model using train_model.py")

if __name__ == "__main__":
    demo_tweet_processing()

