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

