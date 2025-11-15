# 🔑 Quick Start: Getting Credentials

## TL;DR - Fastest Way to Get Everything

### 1. Database (MySQL) - 5 minutes

**Local MySQL:**
```bash
# Install
sudo apt-get install mysql-server

# Create database
mysql -u root -p
CREATE DATABASE twitter;
CREATE USER 'railsewa'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON twitter.* TO 'railsewa'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Run schema
mysql -u railsewa -p twitter < database/schema.sql
```

**Result:**
```
DB_HOST=localhost
DB_USER=railsewa
DB_PASSWORD=password123
DB_NAME=twitter
```

---

### 2. Twitter API - 10 minutes

**Step-by-Step:**

1. **Go to:** https://developer.twitter.com/
2. **Sign in** with Twitter account
3. **Click:** "Developer Portal" → "Projects & Apps"
4. **Click:** "Create Project" → Fill details → "Next"
5. **Click:** "Create App" → Name it → "Complete"
6. **Go to:** "Keys and tokens" tab
7. **Copy these 5 values:**
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Bearer Token
   - Access Token
   - Access Token Secret

**Result:**
```
TWITTER_BEARER_TOKEN=xxxxx
TWITTER_CONSUMER_KEY=xxxxx
TWITTER_CONSUMER_SECRET=xxxxx
TWITTER_ACCESS_TOKEN=xxxxx
TWITTER_ACCESS_TOKEN_SECRET=xxxxx
```

**⚠️ Important:** Copy keys immediately - they won't show again!

---

### 3. Kafka - Already Configured (Default)

For local development, use defaults:

```
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=twitterstream
```

No setup needed if using local Kafka!

---

### 4. Spark - Already Configured (Default)

For local development:

```
SPARK_MASTER=spark://localhost:7077
```

No setup needed if using local Spark!

---

## 📝 Complete .env File

Create `.env` file in project root:

```bash
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=railsewa
DB_PASSWORD=your_mysql_password
DB_NAME=twitter

# Kafka (defaults)
KAFKA_BROKER=localhost:9092
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=twitterstream

# Twitter API (get from developer.twitter.com)
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_CONSUMER_KEY=your_api_key
TWITTER_CONSUMER_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Spark (defaults)
SPARK_MASTER=spark://localhost:7077
TRAINING_DATA_PATH=data/training_data.csv
MODEL_PATH=saved_model/tweet_classifier_model
```

---

## ✅ Checklist

- [ ] MySQL installed and database created
- [ ] Twitter Developer account created
- [ ] All 5 Twitter API keys copied
- [ ] `.env` file created with all values
- [ ] Tested MySQL connection
- [ ] Ready to deploy!

---

## 🎯 What You Actually Need

**Required:**
1. ✅ MySQL database (local or AWS RDS)
2. ✅ Twitter API credentials (5 keys)

**Optional (have defaults):**
- Kafka (defaults to localhost:9092)
- Spark (defaults to localhost:7077)

---

## 📚 Detailed Guides

For step-by-step with screenshots and troubleshooting:
- See `HOW_TO_GET_CREDENTIALS.md` for complete guide
- See `deploy/DEPLOYMENT_GUIDE.md` for deployment

---

**Quick Setup Time: ~15 minutes total!** 🚂

