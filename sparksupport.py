"""
Spark Support Functions
Utility functions for Spark processing
"""

import re
import json

# Try to import Spark, but make it optional
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import udf, col
    from pyspark.sql.types import StringType, IntegerType, DoubleType
    SPARK_AVAILABLE = True
except ImportError:
    SPARK_AVAILABLE = False
    # Create dummy classes for type hints
    class SparkSession:
        pass
    class udf:
        pass
    class col:
        pass

def create_spark_session(app_name="RailSewa"):
    """Create and return Spark session"""
    if not SPARK_AVAILABLE:
        raise ImportError("PySpark is not installed. Install it with: pip install pyspark")
    
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    return spark

def extract_pnr(text):
    """Extract PNR number from tweet text"""
    if not text:
        return None
    
    # PNR is typically 10 digits
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
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^\w\s]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.lower().strip()

def classify_urgency(text):
    """Simple rule-based urgency classification (can be replaced with ML model)"""
    if not text:
        return 0
    
    text_lower = text.lower()
    
    # Emergency keywords
    emergency_keywords = [
        'emergency', 'urgent', 'help', 'accident', 'fire', 'medical',
        'stuck', 'stranded', 'delay', 'late', 'cancelled', 'breakdown'
    ]
    
    # Check for emergency keywords
    for keyword in emergency_keywords:
        if keyword in text_lower:
            return 1
    
    return 0

def extract_train_number(text):
    """Extract train number from complaint text"""
    if not text:
        return None
    
    # Common patterns: "Train No 12345", "Train 12345", "Train#12345", "12345"
    # Indian train numbers are typically 4-5 digits
    patterns = [
        r'train\s*(?:no|number|#)?\s*:?\s*(\d{4,5})\b',  # Train No 12345
        r'\b(\d{4,5})\s*(?:train|express|mail)\b',  # 12345 train
        r'\b(\d{4,5})\b',  # Any 4-5 digit number (fallback)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            train_num = match.group(1)
            # Validate: train numbers are usually 4-5 digits, not PNR (10 digits)
            if len(train_num) <= 5:
                return train_num
    
    return None

def extract_delay_minutes(text):
    """Extract delay information in minutes from complaint text"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Patterns: "delayed by 2 hours", "2 hour delay", "120 minutes", "late by 30 mins"
    patterns = [
        r'delay(?:ed)?\s*(?:by|of)?\s*(\d+)\s*(?:hour|hr|h)\s*(?:(\d+)\s*(?:min|minute|mins)?)?',
        r'(\d+)\s*(?:hour|hr|h)\s*(?:(\d+)\s*(?:min|minute|mins)?)?\s*delay',
        r'late\s*(?:by)?\s*(\d+)\s*(?:hour|hr|h)\s*(?:(\d+)\s*(?:min|minute|mins)?)?',
        r'(\d+)\s*(?:min|minute|mins)\s*(?:delay|late)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            hours = int(match.group(1)) if match.group(1) else 0
            minutes = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
            total_minutes = hours * 60 + minutes
            if total_minutes > 0:
                return total_minutes
    
    return None

def classify_severity(message: str) -> tuple:
    """
    Returns (severity_label, severity_score).
    severity_label ∈ {'low', 'medium', 'high'}
    severity_score is a float in [0,1] where higher = more severe.
    """
    if not message:
        return ('low', 0.0)
    
    text_lower = message.lower()
    score = 0.0
    
    # High severity keywords (weight: +0.4 each, max 1.0)
    high_severity_keywords = [
        'emergency', 'accident', 'fire', 'medical', 'critical', 'life',
        'death', 'injured', 'hospital', 'ambulance', 'stuck', 'stranded',
        'breakdown', 'derailment', 'collision'
    ]
    
    # Medium severity keywords (weight: +0.2 each, max 0.6)
    medium_severity_keywords = [
        'delay', 'late', 'cancelled', 'urgent', 'help', 'problem',
        'issue', 'complaint', 'fault', 'broken', 'not working'
    ]
    
    # Low severity keywords (weight: +0.1 each, max 0.3)
    low_severity_keywords = [
        'feedback', 'suggestion', 'improve', 'better', 'good', 'satisfied',
        'thank', 'appreciate', 'nice', 'comfortable'
    ]
    
    # Count high severity keywords
    high_count = sum(1 for keyword in high_severity_keywords if keyword in text_lower)
    score += min(high_count * 0.4, 1.0)
    
    # Count medium severity keywords (only if not already high)
    if score < 0.8:
        medium_count = sum(1 for keyword in medium_severity_keywords if keyword in text_lower)
        score += min(medium_count * 0.2, 0.6)
    
    # Count low severity keywords (reduces score)
    low_count = sum(1 for keyword in low_severity_keywords if keyword in text_lower)
    score = max(0.0, score - (low_count * 0.1))
    
    # Check for delay information (adds to severity)
    delay = extract_delay_minutes(message)
    if delay:
        if delay >= 120:  # 2+ hours
            score = min(1.0, score + 0.3)
        elif delay >= 60:  # 1-2 hours
            score = min(1.0, score + 0.2)
        elif delay >= 30:  # 30-60 minutes
            score = min(1.0, score + 0.1)
    
    # Normalize score to [0, 1]
    score = min(1.0, max(0.0, score))
    
    # Determine label
    if score >= 0.7:
        label = 'high'
    elif score >= 0.4:
        label = 'medium'
    else:
        label = 'low'
    
    return (label, round(score, 2))

# Register UDFs (only if Spark is available)
if SPARK_AVAILABLE:
    extract_pnr_udf = udf(extract_pnr, IntegerType())
    clean_tweet_udf = udf(clean_tweet, StringType())
    classify_urgency_udf = udf(classify_urgency, IntegerType())
else:
    # Dummy UDFs for when Spark is not available
    extract_pnr_udf = None
    clean_tweet_udf = None
    classify_urgency_udf = None

def parse_tweet_json(tweet_json):
    """Parse JSON tweet string"""
    try:
        return json.loads(tweet_json)
    except:
        return None

def get_tweet_text(tweet_data):
    """Extract text from tweet data"""
    if isinstance(tweet_data, dict):
        return tweet_data.get('text', '')
    return str(tweet_data)

def save_to_database(df, connection_string):
    """Save DataFrame to MySQL database"""
    try:
        df.write \
            .format("jdbc") \
            .option("url", connection_string) \
            .option("dbtable", "tweets") \
            .option("user", "username") \
            .option("password", "password") \
            .mode("append") \
            .save()
    except Exception as e:
        print(f"Error saving to database: {e}")

