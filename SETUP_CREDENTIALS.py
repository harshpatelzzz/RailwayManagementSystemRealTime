"""
Interactive Credential Setup Script
Helps you set up your .env file step by step
"""

import os
import getpass
import re

def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def get_input(prompt, default=None, password=False):
    """Get user input with optional default"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    if password:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)
    
    return value if value else default

def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def setup_database():
    """Setup database credentials"""
    print_header("Database Configuration")
    
    print("\nChoose database type:")
    print("1. Local MySQL")
    print("2. AWS RDS")
    print("3. Skip (use defaults)")
    
    choice = input("\nChoice [1]: ").strip() or "1"
    
    if choice == "3":
        return {
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_USER': 'railsewa',
            'DB_PASSWORD': '',
            'DB_NAME': 'twitter'
        }
    
    if choice == "2":
        print("\nAWS RDS Configuration:")
        host = get_input("RDS Endpoint", "your-endpoint.rds.amazonaws.com")
        user = get_input("Database Username", "admin")
        password = getpass.getpass("Database Password: ")
        db_name = get_input("Database Name", "twitter")
        port = get_input("Port", "3306")
    else:
        print("\nLocal MySQL Configuration:")
        host = get_input("Host", "localhost")
        port = get_input("Port", "3306")
        user = get_input("Database Username", "railsewa")
        password = getpass.getpass("Database Password: ")
        db_name = get_input("Database Name", "twitter")
    
    return {
        'DB_HOST': host,
        'DB_PORT': port,
        'DB_USER': user,
        'DB_PASSWORD': password,
        'DB_NAME': db_name
    }

def setup_kafka():
    """Setup Kafka configuration"""
    print_header("Kafka Configuration")
    
    print("\nUsing defaults for local development?")
    use_defaults = input("Use defaults (localhost:9092) [Y/n]: ").strip().lower() or "y"
    
    if use_defaults == "y":
        return {
            'KAFKA_BROKER': 'localhost:9092',
            'KAFKA_BROKERS': 'localhost:9092',
            'KAFKA_TOPIC': 'twitterstream'
        }
    
    broker = get_input("Kafka Broker", "localhost:9092")
    topic = get_input("Kafka Topic", "twitterstream")
    
    return {
        'KAFKA_BROKER': broker,
        'KAFKA_BROKERS': broker,
        'KAFKA_TOPIC': topic
    }

def setup_twitter():
    """Setup Twitter API credentials"""
    print_header("Twitter API Configuration")
    
    print("\nTo get Twitter API credentials:")
    print("1. Go to: https://developer.twitter.com/")
    print("2. Sign in and create a project/app")
    print("3. Go to 'Keys and tokens' tab")
    print("4. Copy all 5 credentials\n")
    
    input("Press Enter when you have the credentials ready...")
    
    bearer_token = getpass.getpass("Twitter Bearer Token: ")
    consumer_key = getpass.getpass("Twitter Consumer Key (API Key): ")
    consumer_secret = getpass.getpass("Twitter Consumer Secret (API Secret): ")
    access_token = getpass.getpass("Twitter Access Token: ")
    access_token_secret = getpass.getpass("Twitter Access Token Secret: ")
    
    return {
        'TWITTER_BEARER_TOKEN': bearer_token,
        'TWITTER_CONSUMER_KEY': consumer_key,
        'TWITTER_CONSUMER_SECRET': consumer_secret,
        'TWITTER_ACCESS_TOKEN': access_token,
        'TWITTER_ACCESS_TOKEN_SECRET': access_token_secret
    }

def setup_spark():
    """Setup Spark configuration"""
    print_header("Spark Configuration")
    
    print("\nUsing defaults for local development?")
    use_defaults = input("Use defaults (spark://localhost:7077) [Y/n]: ").strip().lower() or "y"
    
    if use_defaults == "y":
        return {
            'SPARK_MASTER': 'spark://localhost:7077',
            'TRAINING_DATA_PATH': 'data/training_data.csv',
            'MODEL_PATH': 'saved_model/tweet_classifier_model'
        }
    
    master = get_input("Spark Master URL", "spark://localhost:7077")
    training_path = get_input("Training Data Path", "data/training_data.csv")
    model_path = get_input("Model Path", "saved_model/tweet_classifier_model")
    
    return {
        'SPARK_MASTER': master,
        'TRAINING_DATA_PATH': training_path,
        'MODEL_PATH': model_path
    }

def create_env_file(config):
    """Create .env file from configuration"""
    env_content = """# Database Configuration
DB_HOST={DB_HOST}
DB_PORT={DB_PORT}
DB_USER={DB_USER}
DB_PASSWORD={DB_PASSWORD}
DB_NAME={DB_NAME}

# Kafka Configuration
KAFKA_BROKER={KAFKA_BROKER}
KAFKA_BROKERS={KAFKA_BROKERS}
KAFKA_TOPIC={KAFKA_TOPIC}

# Twitter API Configuration
TWITTER_BEARER_TOKEN={TWITTER_BEARER_TOKEN}
TWITTER_CONSUMER_KEY={TWITTER_CONSUMER_KEY}
TWITTER_CONSUMER_SECRET={TWITTER_CONSUMER_SECRET}
TWITTER_ACCESS_TOKEN={TWITTER_ACCESS_TOKEN}
TWITTER_ACCESS_TOKEN_SECRET={TWITTER_ACCESS_TOKEN_SECRET}

# Model Configuration
TRAINING_DATA_PATH={TRAINING_DATA_PATH}
MODEL_PATH={MODEL_PATH}
""".format(**config)
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("\n⚠️  .env file already exists!")
        overwrite = input("Overwrite? [y/N]: ").strip().lower()
        if overwrite != 'y':
            print("Keeping existing .env file")
            return False
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully!")
    return True

def main():
    """Main setup function"""
    print_header("RailSewa Credential Setup")
    print("\nThis script will help you configure your .env file")
    print("You can skip any section and use defaults\n")
    
    config = {}
    
    # Database setup
    print("\n" + "-" * 60)
    setup_db = input("Setup database credentials? [Y/n]: ").strip().lower() or "y"
    if setup_db == "y":
        config.update(setup_database())
    else:
        config.update({
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
            'DB_USER': 'railsewa',
            'DB_PASSWORD': '',
            'DB_NAME': 'twitter'
        })
    
    # Kafka setup
    print("\n" + "-" * 60)
    setup_kafka_choice = input("Setup Kafka configuration? [Y/n]: ").strip().lower() or "y"
    if setup_kafka_choice == "y":
        config.update(setup_kafka())
    else:
        config.update({
            'KAFKA_BROKER': 'localhost:9092',
            'KAFKA_BROKERS': 'localhost:9092',
            'KAFKA_TOPIC': 'twitterstream'
        })
    
    # Twitter setup
    print("\n" + "-" * 60)
    setup_twitter_choice = input("Setup Twitter API credentials? [Y/n]: ").strip().lower() or "y"
    if setup_twitter_choice == "y":
        config.update(setup_twitter())
    else:
        print("⚠️  Twitter API credentials are required for streaming!")
        config.update({
            'TWITTER_BEARER_TOKEN': '',
            'TWITTER_CONSUMER_KEY': '',
            'TWITTER_CONSUMER_SECRET': '',
            'TWITTER_ACCESS_TOKEN': '',
            'TWITTER_ACCESS_TOKEN_SECRET': ''
        })
    
    # Spark setup
    print("\n" + "-" * 60)
    setup_spark_choice = input("Setup Spark configuration? [Y/n]: ").strip().lower() or "y"
    if setup_spark_choice == "y":
        config.update(setup_spark())
    else:
        config.update({
            'SPARK_MASTER': 'spark://localhost:7077',
            'TRAINING_DATA_PATH': 'data/training_data.csv',
            'MODEL_PATH': 'saved_model/tweet_classifier_model'
        })
    
    # Create .env file
    print_header("Creating .env File")
    if create_env_file(config):
        print("\n✅ Configuration complete!")
        print("\nNext steps:")
        print("1. Review .env file")
        print("2. Test database connection")
        print("3. Verify Twitter API keys")
        print("4. Run: python run_full_system.py")
    else:
        print("\nConfiguration saved but .env file not overwritten")

if __name__ == "__main__":
    main()

