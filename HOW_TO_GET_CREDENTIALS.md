# How to Get All Credentials for .env File
## Step-by-Step Guide

This guide will walk you through getting every credential needed for your RailSewa project.

---

## 📋 Table of Contents

1. [Database Credentials (MySQL)](#1-database-credentials-mysql)
2. [Twitter API Credentials](#2-twitter-api-credentials)
3. [Kafka Configuration](#3-kafka-configuration)
4. [Spark Configuration](#4-spark-configuration)
5. [Complete .env File Template](#complete-env-file-template)

---

## 1. Database Credentials (MySQL)

### Option A: Local MySQL Installation

#### Step 1: Install MySQL
```bash
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install mysql-server

# On Windows
# Download from: https://dev.mysql.com/downloads/mysql/
# Install MySQL Installer

# On macOS
brew install mysql
```

#### Step 2: Start MySQL Service
```bash
# Linux
sudo systemctl start mysql
sudo systemctl enable mysql

# Windows
# MySQL starts automatically after installation

# macOS
brew services start mysql
```

#### Step 3: Secure MySQL Installation
```bash
sudo mysql_secure_installation
```
Follow prompts to:
- Set root password
- Remove anonymous users
- Disable remote root login
- Remove test database

#### Step 4: Create Database and User
```bash
# Login to MySQL
mysql -u root -p
```

Then run these SQL commands:
```sql
-- Create database
CREATE DATABASE twitter;

-- Create user
CREATE USER 'railsewa'@'localhost' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON twitter.* TO 'railsewa'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Exit
EXIT;
```

#### Step 5: Run Schema
```bash
mysql -u railsewa -p twitter < database/schema.sql
```

**Your Database Credentials:**
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=railsewa
DB_PASSWORD=your_secure_password (the one you set)
DB_NAME=twitter
```

### Option B: AWS RDS (Cloud Database)

#### Step 1: Create AWS Account
1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Complete registration (requires credit card)

#### Step 2: Access RDS Console
1. Login to AWS Console
2. Search for "RDS" in services
3. Click "RDS" service

#### Step 3: Create Database
1. Click "Create database"
2. Choose "Standard create"
3. Select "MySQL" as engine
4. Choose version (8.0 recommended)
5. Select "Free tier" template (if eligible)

#### Step 4: Configure Database
- **DB instance identifier**: `railsewa-db`
- **Master username**: `admin` (or your choice)
- **Master password**: Create a strong password (save it!)
- **DB instance class**: `db.t3.micro` (free tier)

#### Step 5: Configure Network
- **VPC**: Default VPC
- **Public access**: Yes (for testing)
- **Security group**: Create new or use default
- **Database port**: 3306

#### Step 6: Create Database
1. Click "Create database"
2. Wait 5-10 minutes for creation
3. Note the **Endpoint** (e.g., `railsewa-db.xxxxx.us-east-1.rds.amazonaws.com`)

#### Step 7: Configure Security Group
1. Go to RDS → Your database → Connectivity & security
2. Click on Security group
3. Click "Edit inbound rules"
4. Add rule:
   - Type: MySQL/Aurora
   - Port: 3306
   - Source: Your IP address (or 0.0.0.0/0 for testing)

#### Step 8: Connect and Setup
```bash
# Connect to RDS
mysql -h your-endpoint.rds.amazonaws.com -u admin -p

# Create database
CREATE DATABASE twitter;

# Run schema
mysql -h your-endpoint.rds.amazonaws.com -u admin -p twitter < database/schema.sql
```

**Your RDS Credentials:**
```
DB_HOST=your-endpoint.rds.amazonaws.com
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=your_master_password
DB_NAME=twitter
```

---

## 2. Twitter API Credentials

### Step 1: Create Twitter Developer Account

1. Go to https://developer.twitter.com/
2. Click "Sign up" or "Apply"
3. Sign in with your Twitter account
4. If new, click "Apply for a developer account"

### Step 2: Apply for Developer Account

1. **Select your use case:**
   - Choose "Making a bot" or "Exploring the API"
   - For RailSewa, select "Making a bot"

2. **Describe your use case:**
   - Example: "Building a real-time complaint management system for Indian Railways that processes tweets, classifies them, and allows administrators to respond"

3. **Review and accept terms**
   - Read Twitter Developer Policy
   - Accept terms and conditions

4. **Submit application**
   - Wait for approval (usually instant for basic access)

### Step 3: Create a Project and App

1. After approval, go to https://developer.twitter.com/en/portal/dashboard
2. Click "Create Project"
3. Fill in project details:
   - **Project name**: RailSewa
   - **Use case**: Select "Making a bot"
   - **Project description**: "Real-time tweet processing system for railway complaints"

4. Click "Next"

### Step 4: Create App

1. **App name**: `railsewa-app` (must be unique)
2. Click "Complete"

### Step 5: Get API Keys

1. In your project dashboard, click on your app
2. Go to "Keys and tokens" tab
3. You'll see:

#### API Key and Secret (Consumer Keys)
1. Click "Regenerate" or "Generate" for API Key
2. Click "Regenerate" or "Generate" for API Secret
3. **IMPORTANT**: Copy these immediately (they won't be shown again!)

#### Bearer Token
1. Scroll to "Bearer Token"
2. Click "Regenerate" or "Generate"
3. Copy the token

#### Access Token and Secret
1. Scroll to "Access Token and Secret"
2. Click "Generate"
3. Copy both Access Token and Access Token Secret

### Step 6: Set App Permissions

1. Go to "Settings" tab
2. Under "App permissions", select:
   - **Read and Write** (for posting responses)
3. Click "Save"

### Step 7: Enable OAuth 1.0a

1. In "Settings" tab
2. Under "User authentication settings"
3. Click "Set up" or "Edit"
4. Enable OAuth 1.0a
5. Save changes

**Your Twitter API Credentials:**
```
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_CONSUMER_KEY=your_api_key_here
TWITTER_CONSUMER_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

### ⚠️ Important Notes:
- **Never share these keys publicly**
- **Don't commit .env file to Git**
- **Regenerate keys if compromised**
- **Free tier has rate limits** (1,500 tweets/month for streaming)

---

## 3. Kafka Configuration

### For Local Development (Default)

If running Kafka locally, use these defaults:

```
KAFKA_BROKER=localhost:9092
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=twitterstream
```

### For Production/Remote Kafka

#### Step 1: Install Kafka (if not using Docker)

```bash
# Download Kafka
wget https://downloads.apache.org/kafka/3.5.0/kafka_2.13-3.5.0.tgz
tar -xzf kafka_2.13-3.5.0.tgz
cd kafka_2.13-3.5.0
```

#### Step 2: Configure Kafka

Edit `config/server.properties`:
```properties
# Broker ID (unique for each broker)
broker.id=0

# Listeners
listeners=PLAINTEXT://localhost:9092
advertised.listeners=PLAINTEXT://localhost:9092

# Zookeeper connection
zookeeper.connect=localhost:2181
```

#### Step 3: Get Kafka Address

- **Local**: `localhost:9092`
- **Remote**: `your-server-ip:9092` or `kafka.yourdomain.com:9092`

**Your Kafka Configuration:**
```
KAFKA_BROKER=localhost:9092
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=twitterstream
```

---

## 4. Spark Configuration

### For Local Development

```
SPARK_MASTER=spark://localhost:7077
```

### For Production Cluster

#### Step 1: Install Spark

```bash
# Download Spark
wget https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
tar -xzf spark-3.5.0-bin-hadoop3.tgz
```

#### Step 2: Configure Spark Master

Edit `conf/spark-env.sh`:
```bash
export SPARK_MASTER_HOST=your-master-ip
export SPARK_MASTER_PORT=7077
```

#### Step 3: Get Spark Master URL

- **Local**: `spark://localhost:7077`
- **Remote**: `spark://your-master-ip:7077`
- **Cloud**: `spark://your-cluster-master:7077`

**Your Spark Configuration:**
```
SPARK_MASTER=spark://localhost:7077
TRAINING_DATA_PATH=data/training_data.csv
MODEL_PATH=saved_model/tweet_classifier_model
```

---

## Complete .env File Template

Create your `.env` file with all credentials:

```bash
# ============================================
# Database Configuration
# ============================================
# For Local MySQL:
DB_HOST=localhost
DB_PORT=3306
DB_USER=railsewa
DB_PASSWORD=your_mysql_password_here
DB_NAME=twitter

# For AWS RDS:
# DB_HOST=your-endpoint.rds.amazonaws.com
# DB_PORT=3306
# DB_USER=admin
# DB_PASSWORD=your_rds_password_here
# DB_NAME=twitter

# ============================================
# Kafka Configuration
# ============================================
KAFKA_BROKER=localhost:9092
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=twitterstream

# ============================================
# Twitter API Configuration
# ============================================
# Get these from: https://developer.twitter.com/en/portal/dashboard
TWITTER_BEARER_TOKEN=your_bearer_token_from_twitter
TWITTER_CONSUMER_KEY=your_api_key_from_twitter
TWITTER_CONSUMER_SECRET=your_api_secret_from_twitter
TWITTER_ACCESS_TOKEN=your_access_token_from_twitter
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_from_twitter

# ============================================
# Spark Configuration
# ============================================
SPARK_MASTER=spark://localhost:7077
TRAINING_DATA_PATH=data/training_data.csv
MODEL_PATH=saved_model/tweet_classifier_model
```

---

## 🔒 Security Best Practices

1. **Never commit .env to Git**
   - Already in `.gitignore`
   - Keep credentials private

2. **Use strong passwords**
   - Minimum 16 characters
   - Mix of letters, numbers, symbols

3. **Rotate credentials regularly**
   - Change passwords every 90 days
   - Regenerate API keys if compromised

4. **Limit access**
   - Only give credentials to trusted team members
   - Use environment-specific credentials

5. **Monitor usage**
   - Check Twitter API usage
   - Monitor database connections
   - Review access logs

---

## ✅ Verification Checklist

After setting up credentials, verify:

- [ ] MySQL connection works: `mysql -u railsewa -p twitter`
- [ ] Twitter API keys are valid (test with a simple API call)
- [ ] Kafka is accessible: `telnet localhost 9092`
- [ ] Spark master is running: `curl http://localhost:8080`
- [ ] All credentials are in `.env` file
- [ ] `.env` file is NOT in Git (check `.gitignore`)

---

## 🆘 Troubleshooting

### Can't connect to MySQL?
- Check if MySQL is running: `sudo systemctl status mysql`
- Verify credentials: `mysql -u railsewa -p`
- Check firewall: `sudo ufw allow 3306`

### Twitter API not working?
- Verify keys are correct (no extra spaces)
- Check API permissions (Read and Write)
- Verify rate limits not exceeded
- Check Twitter Developer Portal for status

### Kafka connection issues?
- Check Zookeeper is running: `zkServer.sh status`
- Verify Kafka is running: `ps aux | grep kafka`
- Check port: `netstat -tulpn | grep 9092`

---

## 📞 Need Help?

- **Twitter API**: https://developer.twitter.com/en/support
- **MySQL**: https://dev.mysql.com/doc/
- **Kafka**: https://kafka.apache.org/documentation/
- **Spark**: https://spark.apache.org/docs/

---

**All credentials obtained? Update your `.env` file and you're ready to deploy!** 🚂

