# 📨 Apache Kafka Setup - Step by Step Guide

## 📋 Overview

Apache Kafka is a distributed streaming platform used to handle real-time data feeds. For RailSewa, it receives complaints from Telegram Bot and streams them to Spark for processing.

---

## 🏠 Option A: Local Kafka Setup (Development)

### **Prerequisites**

- **Java JDK 8 or higher** (required for Kafka)
- **At least 2GB free disk space**

---

### **Step 1: Install Java JDK**

#### **Check if Java is installed:**
```bash
java -version
```

#### **If not installed:**

**Windows:**
1. Download from: https://www.oracle.com/java/technologies/downloads/
2. Install JDK 8 or higher
3. Set JAVA_HOME environment variable

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install openjdk-11-jdk

# Verify
java -version
```

**macOS:**
```bash
brew install openjdk@11
```

---

### **Step 2: Download Apache Kafka**

```bash
# Create directory for Kafka
mkdir -p ~/kafka
cd ~/kafka

# Download Kafka (replace version with latest)
wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz

# Extract
tar -xzf kafka_2.13-3.6.0.tgz

# Rename for convenience
mv kafka_2.13-3.6.0 kafka

# Go to Kafka directory
cd kafka
```

**Windows:**
1. Download from: https://kafka.apache.org/downloads
2. Extract ZIP file to `C:\kafka`
3. Open Command Prompt in that directory

---

### **Step 3: Start Zookeeper**

Kafka requires Zookeeper to run. Start it first:

**Linux/macOS:**
```bash
# Start Zookeeper (runs in foreground)
bin/zookeeper-server-start.sh config/zookeeper.properties

# Or run in background
bin/zookeeper-server-start.sh config/zookeeper.properties &
```

**Windows:**
```cmd
bin\windows\zookeeper-server-start.bat config\zookeeper.properties
```

**Keep this terminal open!** Zookeeper must be running.

---

### **Step 4: Start Kafka Broker**

Open a **new terminal** (keep Zookeeper running):

**Linux/macOS:**
```bash
cd ~/kafka/kafka

# Start Kafka server
bin/kafka-server-start.sh config/server.properties

# Or run in background
bin/kafka-server-start.sh config/server.properties &
```

**Windows:**
```cmd
cd C:\kafka
bin\windows\kafka-server-start.bat config\server.properties
```

**Keep this terminal open too!** Kafka must be running.

---

### **Step 5: Create Kafka Topic**

Open a **third terminal**:

**Linux/macOS:**
```bash
cd ~/kafka/kafka

# Create topic for RailSewa
bin/kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --topic raw_tweets
```

**Windows:**
```cmd
cd C:\kafka
bin\windows\kafka-topics.bat --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic raw_tweets
```

---

### **Step 6: Verify Topic Created**

**Linux/macOS:**
```bash
# List all topics
bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Should see: raw_tweets
```

**Windows:**
```cmd
bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092
```

---

### **Step 7: Test Kafka (Optional)**

**Producer (send messages):**
```bash
# Linux/macOS
bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic raw_tweets

# Windows
bin\windows\kafka-console-producer.bat --bootstrap-server localhost:9092 --topic raw_tweets
```

Type some messages and press Enter.

**Consumer (receive messages):**
Open another terminal:
```bash
# Linux/macOS
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic raw_tweets --from-beginning

# Windows
bin\windows\kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic raw_tweets --from-beginning
```

You should see messages from producer!

---

### **Step 8: Update .env File**

Your `.env` file should already have:
```bash
KAFKA_BROKER=localhost:9092
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=raw_tweets
```

Verify these values are correct.

---

## 🐳 Option B: Docker Setup (Easier Alternative)

### **Step 1: Install Docker**

Download from: https://www.docker.com/products/docker-desktop

### **Step 2: Run Kafka with Docker Compose**

Create `docker-compose-kafka.yml`:

```yaml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

### **Step 3: Start Kafka**

```bash
docker-compose -f docker-compose-kafka.yml up -d
```

### **Step 4: Create Topic**

```bash
docker exec -it kafka_kafka_1 kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --topic raw_tweets
```

### **Step 5: Stop Kafka**

```bash
docker-compose -f docker-compose-kafka.yml down
```

---

## ☁️ Option C: Cloud Kafka (Production)

### **Confluent Cloud (Recommended)**

1. Sign up at: https://www.confluent.io/confluent-cloud/
2. Create cluster
3. Get bootstrap servers URL
4. Create API keys
5. Update `.env`:
   ```bash
   KAFKA_BROKER=your-cluster.confluent.cloud:9092
   KAFKA_BROKERS=your-cluster.confluent.cloud:9092
   KAFKA_TOPIC=raw_tweets
   ```

### **AWS MSK (Managed Streaming for Kafka)**

1. Go to AWS Console → MSK
2. Create cluster
3. Get bootstrap servers
4. Update `.env` with bootstrap server addresses

---

## ✅ Verification Checklist

After setup:

- [ ] Java JDK installed
- [ ] Zookeeper running (port 2181)
- [ ] Kafka running (port 9092)
- [ ] Topic `raw_tweets` created
- [ ] Can produce messages
- [ ] Can consume messages
- [ ] `.env` file configured correctly

---

## 🧪 Test Kafka Connection

Create `test_kafka.py`:

```python
from kafka import KafkaProducer, KafkaConsumer
import json
import time

# Test Producer
try:
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    test_message = {'test': 'Hello Kafka!'}
    producer.send('raw_tweets', test_message)
    producer.flush()
    print("✅ Producer: Message sent successfully!")
    
except Exception as e:
    print(f"❌ Producer Error: {e}")

# Test Consumer
try:
    consumer = KafkaConsumer(
        'raw_tweets',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    print("✅ Consumer: Connected successfully!")
    print("Waiting for messages (press Ctrl+C to stop)...")
    
    for message in consumer:
        print(f"Received: {message.value}")
        break  # Just test one message
        
except Exception as e:
    print(f"❌ Consumer Error: {e}")
```

Run it:
```bash
python test_kafka.py
```

---

## 🚀 Running Kafka Services

### **Start Services (Every time you want to use Kafka):**

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

**Terminal 3 - Your Application:**
```bash
cd "Z:\cloud el"
python kafka_file/telegram_stream.py
```

---

## 🛑 Stop Kafka Services

Press `Ctrl+C` in each terminal, or:

```bash
# Stop Kafka
bin/kafka-server-stop.sh

# Stop Zookeeper
bin/zookeeper-server-stop.sh
```

---

## 🆘 Troubleshooting

### **Port already in use?**

```bash
# Check what's using port 9092
# Linux/macOS
lsof -i :9092

# Windows
netstat -ano | findstr :9092

# Kill the process or change Kafka port in config/server.properties
```

### **Zookeeper connection refused?**

- Make sure Zookeeper is running first
- Check port 2181 is accessible
- Verify `zookeeper.connect` in `server.properties`

### **Can't create topic?**

- Verify Kafka is running
- Check bootstrap server address
- Ensure you have permissions

### **Messages not appearing?**

- Check topic name matches
- Verify consumer is subscribed to correct topic
- Check auto_offset_reset setting

---

## 📚 Additional Resources

- **Kafka Documentation**: https://kafka.apache.org/documentation/
- **Kafka Quick Start**: https://kafka.apache.org/quickstart
- **Confluent Platform**: https://docs.confluent.io/

---

## 🎉 Success!

Once Kafka is running:
- ✅ Telegram Bot can send complaints to Kafka
- ✅ Spark can consume from Kafka
- ✅ Real-time processing pipeline is ready

**Your Kafka setup is complete!** 🚂

