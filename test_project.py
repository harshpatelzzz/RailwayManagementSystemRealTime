"""
Test script to verify project setup and components
This can run without full infrastructure (Kafka, Spark, MySQL)
"""

import os
import sys

def test_imports():
    """Test if basic imports work"""
    print("Testing imports...")
    try:
        import pandas as pd
        print("[OK] pandas imported")
    except ImportError as e:
        print(f"[FAIL] pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("[OK] numpy imported")
    except ImportError as e:
        print(f"[FAIL] numpy import failed: {e}")
        return False
    
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        print("[OK] scikit-learn imported")
    except ImportError as e:
        print(f"[FAIL] scikit-learn import failed: {e}")
        return False
    
    try:
        import tweepy
        print("[OK] tweepy imported")
    except ImportError as e:
        print(f"[FAIL] tweepy import failed: {e}")
        return False
    
    try:
        from kafka import KafkaProducer
        print("[OK] kafka-python imported")
    except ImportError as e:
        print(f"[FAIL] kafka-python import failed: {e}")
        return False
    
    try:
        import pymysql
        print("[OK] pymysql imported")
    except ImportError as e:
        print(f"[FAIL] pymysql import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("[OK] python-dotenv imported")
    except ImportError as e:
        print(f"[FAIL] python-dotenv import failed: {e}")
        return False
    
    return True

def test_spark():
    """Test Spark import (may fail if Java not installed)"""
    print("\nTesting Spark...")
    try:
        from pyspark.sql import SparkSession
        print("[OK] PySpark imported")
        
        # Try to create a Spark session (will fail if Java not installed)
        try:
            spark = SparkSession.builder.appName("Test").getOrCreate()
            print("[OK] Spark session created")
            spark.stop()
            return True
        except Exception as e:
            print(f"[WARN] Spark session creation failed (Java may not be installed): {e}")
            print("  This is expected if Java/JDK is not installed")
            return False
    except ImportError as e:
        print(f"[FAIL] PySpark import failed: {e}")
        return False

def test_project_files():
    """Test if project files exist"""
    print("\nTesting project files...")
    files = [
        'kafka_file/stream_data.py',
        'train_model.py',
        'new_live_processing.py',
        'sparksupport.py',
        'railways/index.php',
        'railways/config.php',
        'database/schema.sql'
    ]
    
    all_exist = True
    for file in files:
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            print(f"[FAIL] {file} - NOT FOUND")
            all_exist = False
    
    return all_exist

def test_tweet_processing():
    """Test tweet processing functions"""
    print("\nTesting tweet processing...")
    try:
        sys.path.insert(0, '.')
        from sparksupport import clean_tweet, extract_pnr, classify_urgency
        
        # Test cleaning
        test_tweet = "Train is delayed! @RailMinIndia PNR: 1234567890 https://example.com"
        cleaned = clean_tweet(test_tweet)
        print(f"[OK] Tweet cleaning: '{test_tweet}' -> '{cleaned}'")
        
        # Test PNR extraction
        pnr = extract_pnr("My PNR is 1234567890")
        if pnr == 1234567890:
            print(f"[OK] PNR extraction: Found PNR {pnr}")
        else:
            print(f"[FAIL] PNR extraction failed")
            return False
        
        # Test classification
        emergency_tweet = "Train breakdown urgent help needed"
        feedback_tweet = "Great service thank you"
        
        emergency_pred = classify_urgency(emergency_tweet)
        feedback_pred = classify_urgency(feedback_tweet)
        
        if emergency_pred == 1 and feedback_pred == 0:
            print(f"[OK] Classification: Emergency={emergency_pred}, Feedback={feedback_pred}")
        else:
            print(f"[WARN] Classification may need tuning")
        
        return True
    except Exception as e:
        print(f"[FAIL] Tweet processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_env_file():
    """Check if .env file exists"""
    print("\nChecking configuration...")
    if os.path.exists('.env'):
        print("[OK] .env file exists")
        print("  [WARN] Remember to update it with your credentials!")
        return True
    else:
        print("[FAIL] .env file not found")
        print("  Run: python setup.py")
        return False

def main():
    print("=" * 60)
    print("RailSewa Project - Component Test")
    print("=" * 60)
    
    results = {
        'imports': test_imports(),
        'spark': test_spark(),
        'files': test_project_files(),
        'processing': test_tweet_processing(),
        'config': check_env_file()
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test, result in results.items():
        status = "[PASS]" if result else "[FAIL/WARN]"
        print(f"{test.upper():15} {status}")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Install missing dependencies: pip install -r requirements.txt")
    print("2. Configure .env file with your credentials")
    print("3. Setup MySQL database (see database/schema.sql)")
    print("4. Install and configure Kafka & Zookeeper")
    print("5. Install Java/JDK for Spark")
    print("6. Train model: python train_model.py (or spark-submit)")
    print("\nFor full setup instructions, see README.md or QUICKSTART.md")

if __name__ == "__main__":
    main()

