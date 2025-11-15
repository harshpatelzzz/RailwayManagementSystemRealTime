# 🚂 RailSewa Production Deployment - Complete Setup

## ✅ What Has Been Created

### 📦 Deployment Scripts (in `deploy/` folder)

1. **production_setup.sh** - Automated installation of all infrastructure
   - Installs Java, MySQL, Zookeeper, Kafka, Spark, PHP, Apache
   - One-command setup for production environment

2. **setup_mysql.sh** - MySQL database configuration
   - Creates database and user
   - Runs schema.sql automatically
   - Configures permissions

3. **setup_kafka.sh** - Kafka & Zookeeper setup
   - Starts Zookeeper
   - Starts Kafka broker
   - Creates twitterstream topic

4. **setup_spark.sh** - Spark cluster configuration
   - Configures Spark Master
   - Starts Spark Worker
   - Sets up cluster mode

5. **start_services.sh** - Start all services
   - Zookeeper → Kafka → Spark → Twitter Stream → Processing
   - All services in correct order

6. **stop_services.sh** - Stop all services gracefully
   - Clean shutdown of all components

7. **check_services.sh** - Service status checker
   - Real-time status of all services
   - Color-coded output

### 🐳 Docker Deployment

**docker-compose.yml** - Complete containerized setup
- MySQL container
- Zookeeper container
- Kafka container
- Spark Master container
- Spark Worker container
- PHP/Apache web server container

### 📚 Documentation

1. **DEPLOYMENT_GUIDE.md** - Comprehensive deployment guide
2. **PRODUCTION_README.md** - Quick reference
3. **DEPLOYMENT_SUMMARY.md** - This file

### 🔧 Configuration Updates

- **railways/config.php** - Updated for production
  - Environment variable support
  - Docker-compatible
  - AWS RDS ready

## 🚀 Quick Start Options

### Option 1: Docker (Recommended - Easiest)

```bash
cd deploy
docker-compose up -d
```

**That's it!** All services start automatically.

### Option 2: Automated Scripts

```bash
cd deploy
chmod +x *.sh
sudo ./production_setup.sh    # Install everything
sudo ./setup_mysql.sh         # Setup database
sudo ./setup_kafka.sh         # Setup Kafka
sudo ./setup_spark.sh         # Setup Spark
sudo ./start_services.sh      # Start all
```

### Option 3: Manual Step-by-Step

Follow `deploy/DEPLOYMENT_GUIDE.md` for detailed manual setup.

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Server/VM with Ubuntu 20.04+
- [ ] Root/sudo access
- [ ] Minimum 4GB RAM
- [ ] 20GB disk space
- [ ] Internet connection
- [ ] Twitter API credentials

### Installation
- [ ] Run `production_setup.sh`
- [ ] Run `setup_mysql.sh`
- [ ] Configure `.env` file
- [ ] Run `setup_kafka.sh`
- [ ] Run `setup_spark.sh`

### Configuration
- [ ] Update `.env` with database credentials
- [ ] Add Twitter API keys to `.env`
- [ ] Configure Kafka brokers
- [ ] Set Spark master URL

### Training
- [ ] Train ML model: `spark-submit train_model.py`

### Startup
- [ ] Run `start_services.sh`
- [ ] Verify with `check_services.sh`
- [ ] Test web interface

## 🔍 Service Endpoints

After deployment, access:

| Service | URL/Port | Purpose |
|---------|----------|---------|
| Web Dashboard | http://localhost/railways/ | Main interface |
| Spark Master UI | http://localhost:8080 | Spark monitoring |
| MySQL | localhost:3306 | Database |
| Kafka | localhost:9092 | Message queue |
| Zookeeper | localhost:2181 | Coordination |

## 📊 What Each Component Does

### MySQL Database
- Stores all processed tweets
- Tracks responses
- Maintains statistics
- **Location**: `database/schema.sql`

### Apache Kafka
- Receives tweets from Twitter stream
- Queues messages for processing
- Topic: `twitterstream`
- **Script**: `kafka_file/stream_data.py`

### Apache Spark
- Processes tweets in real-time
- Classifies as Emergency/Feedback
- Extracts PNR numbers
- Saves to database
- **Script**: `new_live_processing.py`

### PHP Web Interface
- Real-time dashboard
- Tweet management
- Response system
- Statistics display
- **Location**: `railways/`

## 🎯 Production Features

✅ **Scalable Architecture**
- Spark cluster can add workers
- Kafka can scale partitions
- Database can be replicated

✅ **High Availability**
- Services can be restarted independently
- Database backups included
- Log rotation configured

✅ **Monitoring Ready**
- Spark UI for monitoring
- Service status scripts
- Log files in `/var/log/`

✅ **Security**
- Database user permissions
- Environment variable config
- Firewall-ready

## 🔄 Workflow

```
Twitter API → Kafka → Spark → MySQL → Web Dashboard
     ✅         ✅      ✅       ✅         ✅
```

1. **Twitter Stream** (`stream_data.py`)
   - Connects to Twitter API
   - Streams tweets
   - Sends to Kafka topic

2. **Kafka** (Message Queue)
   - Receives tweets
   - Queues for processing
   - Distributes to consumers

3. **Spark Processor** (`new_live_processing.py`)
   - Reads from Kafka
   - Processes each tweet
   - Classifies (Emergency/Feedback)
   - Extracts PNR
   - Saves to MySQL

4. **MySQL Database**
   - Stores all data
   - Tracks status
   - Maintains history

5. **Web Dashboard**
   - Displays real-time data
   - Allows responses
   - Shows statistics

## 📝 Configuration Files

### `.env` File Template

```bash
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=railsewa
DB_PASSWORD=your_password
DB_NAME=twitter

# Kafka
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=twitterstream

# Twitter API
TWITTER_BEARER_TOKEN=your_token
TWITTER_CONSUMER_KEY=your_key
TWITTER_CONSUMER_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_secret

# Spark
SPARK_MASTER=spark://localhost:7077
```

## 🛠️ Maintenance Commands

### Check Status
```bash
sudo ./deploy/check_services.sh
```

### Restart Services
```bash
sudo ./deploy/stop_services.sh
sudo ./deploy/start_services.sh
```

### View Logs
```bash
tail -f /var/log/twitter_stream.log
tail -f /var/log/spark_processing.log
tail -f /var/log/kafka.log
```

### Backup Database
```bash
mysqldump -u railsewa -p twitter > backup.sql
```

## ☁️ AWS Deployment

### RDS Setup
1. Create MySQL RDS instance
2. Update `.env` with RDS endpoint
3. Run schema: `mysql -h endpoint -u user -p < database/schema.sql`

### EC2 Setup
1. Launch instances
2. Run `production_setup.sh` on each
3. Configure security groups
4. Update `.env` with instance IPs

## ✅ Verification

After deployment, verify:

```bash
# Check all services
sudo ./deploy/check_services.sh

# Test database
mysql -u railsewa -p twitter -e "SELECT COUNT(*) FROM tweets;"

# Test Kafka
/opt/kafka/bin/kafka-topics.sh --list --zookeeper localhost:2181

# Test Spark
curl http://localhost:8080

# Test web
curl http://localhost/railways/
```

## 🎉 Success Indicators

You'll know it's working when:
- ✅ All services show "RUNNING" in status check
- ✅ Tweets appear in database
- ✅ Dashboard shows statistics
- ✅ Spark UI shows active jobs
- ✅ Kafka topic has messages

## 📚 Next Steps

1. **Monitor Performance**
   - Check Spark UI
   - Monitor database size
   - Watch Kafka throughput

2. **Scale Up**
   - Add Spark workers
   - Increase Kafka partitions
   - Replicate database

3. **Production Hardening**
   - Setup SSL certificates
   - Configure firewall
   - Setup automated backups
   - Configure monitoring alerts

## 🆘 Support

- **Documentation**: See `deploy/DEPLOYMENT_GUIDE.md`
- **Troubleshooting**: Check service logs
- **Status**: Run `check_services.sh`

---

**All production deployment files are ready!** 🚂

Choose your deployment method and follow the guides. The system is production-ready!

