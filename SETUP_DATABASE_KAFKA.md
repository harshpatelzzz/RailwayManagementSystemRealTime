# 🚀 Complete Setup Guide: Database + Kafka

## 📋 Quick Overview

This guide combines MySQL and Kafka setup for RailSewa project.

---

## 🎯 What You'll Set Up

1. **MySQL Database** - Store complaints and responses
2. **Apache Kafka** - Stream complaints from Telegram Bot to Spark

---

## ⚡ Quick Start (Choose Your Path)

### **Path 1: Local Development (Recommended for Testing)**
- Local MySQL
- Local Kafka
- Fastest setup
- Good for development

### **Path 2: Docker (Easiest)**
- MySQL in Docker
- Kafka in Docker
- One command to start everything
- Isolated environment

### **Path 3: Cloud Production**
- AWS RDS for MySQL
- Cloud Kafka (Confluent/AWS MSK)
- Scalable and reliable
- For production deployment

---

## 📚 Detailed Guides

### **For MySQL Setup:**
👉 See **`SETUP_MYSQL.md`** for complete step-by-step instructions

### **For Kafka Setup:**
👉 See **`SETUP_KAFKA.md`** for complete step-by-step instructions

---

## ✅ Setup Checklist

### **MySQL:**
- [ ] MySQL installed
- [ ] Database `twitter` created
- [ ] User `railsewa` created with password
- [ ] Schema run: `mysql -u railsewa -p twitter < database/schema.sql`
- [ ] `.env` updated with DB credentials
- [ ] Connection tested

### **Kafka:**
- [ ] Java JDK installed
- [ ] Kafka downloaded and extracted
- [ ] Zookeeper running (port 2181)
- [ ] Kafka running (port 9092)
- [ ] Topic `raw_tweets` created
- [ ] `.env` updated with Kafka settings
- [ ] Connection tested

---

## 🧪 Test Everything Together

After setting up both, test the complete pipeline:

### **1. Start Services**

**Terminal 1 - Zookeeper:**
```bash
cd ~/kafka/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties
```

**Terminal 2 - Kafka:**
```bash
cd ~/kafka/kafka
bin/kafka-server-start.sh config/server.properties
```

**Terminal 3 - Telegram Bot:**
```bash
cd "Z:\cloud el"
python kafka_file/telegram_stream.py
```

**Terminal 4 - Spark Processing (if using Spark):**
```bash
spark-submit new_live_processing.py
```

**Terminal 5 - Web Dashboard:**
```bash
cd "Z:\cloud el\railways"
php -S localhost:8000
```

### **2. Test Flow**

1. Send message to Telegram Bot
2. Check Kafka consumer sees message
3. Check Spark processes it
4. Check MySQL has the record
5. Check web dashboard shows it

---

## 🔧 Common Issues

### **Database Connection Failed**
- Check MySQL is running
- Verify credentials in `.env`
- Test: `mysql -u railsewa -p twitter`

### **Kafka Connection Failed**
- Check Zookeeper is running
- Check Kafka is running
- Verify ports 2181 and 9092 are open
- Test: `telnet localhost 9092`

### **Services Won't Start**
- Check Java is installed: `java -version`
- Check ports aren't in use
- Check disk space
- Check logs for errors

---

## 📝 Final .env Configuration

Your complete `.env` should look like:

```bash
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=railsewa
DB_PASSWORD=your_password
DB_NAME=twitter

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token

# Kafka
KAFKA_BROKER=localhost:9092
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=raw_tweets

# Spark (optional)
SPARK_MASTER=spark://localhost:7077
```

---

## 🎉 You're Ready!

Once both are set up:
- ✅ Database ready to store complaints
- ✅ Kafka ready to stream data
- ✅ Full pipeline operational

**See individual guides for detailed instructions!** 🚂

