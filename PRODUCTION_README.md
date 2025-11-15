# RailSewa Production Deployment

Complete production deployment setup for RailSewa with real infrastructure.

## 🚀 Quick Start

### Option 1: Docker (Easiest)

```bash
cd deploy
docker-compose up -d
```

### Option 2: Manual Installation

```bash
cd deploy
chmod +x *.sh
sudo ./production_setup.sh
sudo ./setup_mysql.sh
sudo ./setup_kafka.sh
sudo ./setup_spark.sh
```

## 📋 What's Included

### Deployment Scripts

1. **production_setup.sh** - Installs all required software
2. **setup_mysql.sh** - Configures MySQL database
3. **setup_kafka.sh** - Sets up Kafka and Zookeeper
4. **setup_spark.sh** - Configures Spark cluster
5. **start_services.sh** - Starts all services
6. **stop_services.sh** - Stops all services
7. **check_services.sh** - Checks service status

### Docker Setup

- **docker-compose.yml** - Complete Docker setup
- All services in containers
- Easy to deploy and scale

## 🔧 Configuration

### 1. Environment Variables

Create/update `.env` file:

```bash
# Database
DB_HOST=localhost
DB_USER=railsewa
DB_PASSWORD=your_password
DB_NAME=twitter

# Kafka
KAFKA_BROKER=localhost:9092

# Twitter API
TWITTER_BEARER_TOKEN=your_token
TWITTER_CONSUMER_KEY=your_key
TWITTER_CONSUMER_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_secret
```

### 2. Twitter API Setup

1. Go to https://developer.twitter.com/
2. Create a new app
3. Get API keys and tokens
4. Add to `.env` file

## 📊 Services

### MySQL Database
- Port: 3306
- Database: twitter
- Tables: tweets, admin

### Apache Kafka
- Port: 9092
- Topic: twitterstream
- Zookeeper: 2181

### Apache Spark
- Master UI: http://localhost:8080
- Master Port: 7077
- Workers: Auto-configured

### Web Interface
- URL: http://localhost/railways/
- PHP: 8.1+
- Apache: 2.4+

## 🎯 Deployment Steps

### Step 1: Install Dependencies
```bash
sudo ./deploy/production_setup.sh
```

### Step 2: Setup Database
```bash
sudo ./deploy/setup_mysql.sh
```

### Step 3: Configure Environment
```bash
# Edit .env file with your credentials
nano .env
```

### Step 4: Setup Services
```bash
sudo ./deploy/setup_kafka.sh
sudo ./deploy/setup_spark.sh
```

### Step 5: Train Model
```bash
/opt/spark/bin/spark-submit --master spark://localhost:7077 train_model.py
```

### Step 6: Start All Services
```bash
sudo ./deploy/start_services.sh
```

### Step 7: Verify
```bash
sudo ./deploy/check_services.sh
```

## 🔍 Monitoring

### Check Service Status
```bash
sudo ./deploy/check_services.sh
```

### View Logs
```bash
# Twitter Stream
tail -f /var/log/twitter_stream.log

# Spark Processing
tail -f /var/log/spark_processing.log

# Kafka
tail -f /var/log/kafka.log
```

### Access UIs
- Spark Master: http://localhost:8080
- Web Dashboard: http://localhost/railways/

## 🐳 Docker Deployment

### Start Services
```bash
cd deploy
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
```

### Create Kafka Topic
```bash
docker exec -it railsewa-kafka kafka-topics.sh --create \
    --zookeeper railsewa-zookeeper:2181 \
    --topic twitterstream \
    --partitions 1 \
    --replication-factor 1
```

## ☁️ AWS Deployment

### RDS Setup
1. Create MySQL RDS instance
2. Note endpoint and credentials
3. Update `.env` with RDS details
4. Run schema: `mysql -h endpoint -u user -p < database/schema.sql`

### EC2 Setup
1. Launch instances (master, workers, web)
2. Run `production_setup.sh` on each
3. Configure security groups
4. Update `.env` with instance IPs

## 📝 Next Steps

1. ✅ Infrastructure deployed
2. ⏭️ Configure monitoring
3. ⏭️ Setup backups
4. ⏭️ Configure SSL
5. ⏭️ Setup auto-scaling
6. ⏭️ Configure alerts

## 📚 Documentation

- **DEPLOYMENT_GUIDE.md** - Detailed deployment guide
- **QUICKSTART.md** - Quick start instructions
- **README.md** - Project documentation

## 🆘 Troubleshooting

See `deploy/DEPLOYMENT_GUIDE.md` for troubleshooting steps.

## ✅ Verification Checklist

- [ ] MySQL running and accessible
- [ ] Kafka topic created
- [ ] Spark cluster running
- [ ] Twitter API configured
- [ ] Web interface accessible
- [ ] Services processing tweets
- [ ] Database storing data

All systems ready for production! 🚂

