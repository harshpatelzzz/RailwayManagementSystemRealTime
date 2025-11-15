"""
Parse Raw Tweets
Utility script for parsing and cleaning raw tweet data
"""

import json
import re
from datetime import datetime

def extract_pnr(text):
    """Extract PNR number from tweet"""
    if not text:
        return None
    
    pnr_pattern = r'\b\d{10}\b'
    match = re.search(pnr_pattern, text)
    
    if match:
        return int(match.group())
    return None

def clean_tweet(text):
    """Clean tweet text"""
    if not text:
        return ""
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove user mentions
    text = re.sub(r'@\w+', '', text)
    
    # Remove hashtags
    text = re.sub(r'#\w+', '', text)
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^\w\s]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def extract_location(text):
    """Extract location information from tweet"""
    # This is a placeholder - implement based on your needs
    return None, None

def parse_tweet_json(tweet_json):
    """Parse JSON tweet string"""
    try:
        if isinstance(tweet_json, str):
            return json.loads(tweet_json)
        return tweet_json
    except:
        return None

def classify_tweet(text):
    """Classify tweet as emergency or feedback"""
    if not text:
        return 0
    
    text_lower = text.lower()
    
    emergency_keywords = [
        'emergency', 'urgent', 'help', 'accident', 'fire', 'medical',
        'stuck', 'stranded', 'delay', 'late', 'cancelled', 'breakdown',
        'problem', 'issue', 'complaint'
    ]
    
    for keyword in emergency_keywords:
        if keyword in text_lower:
            return 1
    
    return 0

def format_tweet_data(raw_tweet):
    """Format raw tweet data into structured format"""
    parsed = parse_tweet_json(raw_tweet)
    
    if not parsed:
        return None
    
    text = parsed.get('text', '')
    cleaned_text = clean_tweet(text)
    pnr = extract_pnr(text)
    prediction = classify_tweet(cleaned_text)
    
    return {
        'tweet_id': parsed.get('tweet_id') or parsed.get('id'),
        'text': text,
        'cleaned_text': cleaned_text,
        'username': parsed.get('author_id') or parsed.get('username', 'unknown'),
        'pnr': pnr,
        'prediction': prediction,
        'created_at': parsed.get('created_at'),
        'latitude': None,
        'longitude': None
    }

if __name__ == "__main__":
    # Example usage
    sample_tweet = {
        "tweet_id": 1234567890,
        "text": "Train 12345 is delayed. PNR: 1234567890. Need urgent help!",
        "author_id": "user123",
        "created_at": "2024-01-01T10:00:00Z"
    }
    
    formatted = format_tweet_data(json.dumps(sample_tweet))
    print(json.dumps(formatted, indent=2))

