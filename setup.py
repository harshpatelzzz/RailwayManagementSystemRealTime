"""
Setup script for RailSewa project
Helps with initial configuration and setup
"""

import os
import sys

def create_env_file():
    """Create .env file from template"""
    env_example = """# Database Configuration
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=twitter

# Kafka Configuration
KAFKA_BROKER=localhost:9092
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=twitterstream

# Twitter API Configuration
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_CONSUMER_KEY=your_consumer_key
TWITTER_CONSUMER_SECRET=your_consumer_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Model Configuration
TRAINING_DATA_PATH=data/training_data.csv
MODEL_PATH=saved_model/tweet_classifier_model
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_example)
        print("Created .env file. Please update it with your credentials.")
    else:
        print(".env file already exists.")

def create_directories():
    """Create necessary directories"""
    directories = [
        'data',
        'saved_model',
        'assets/css',
        'assets/js',
        'kafka_file',
        'railways',
        'parsing_raw_tweets'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def main():
    print("Setting up RailSewa project...")
    print("-" * 50)
    
    create_directories()
    create_env_file()
    
    print("-" * 50)
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Update .env file with your credentials")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Setup database (see README.md)")
    print("4. Configure Kafka and Spark")
    print("5. Train model: spark-submit train_model.py")

if __name__ == "__main__":
    main()

