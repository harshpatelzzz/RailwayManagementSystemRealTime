# RailSewa Production Deployment Guide

Complete guide for deploying RailSewa with real infrastructure.

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Root/sudo access
- Minimum 4GB RAM
- 20GB free disk space
- Internet connection

## Option 1: Docker Deployment (Recommended)

### Quick Start with Docker

```bash
# 1. Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo apt-get install -y docker-compose

# 2. Navigate to deploy directory
cd deploy

# 3. Create .env file
cat > .env <<EOF
MYSQL_ROOT_PASSWORD=your_secure_password
DB_NAME=twitter
DB_USER=railsewa
DB_PASSWORD=your_secure_password
EOF

# 4. Start all services
docker-compose up -d

# 5. Create Kafka topic
docker exec -it railsewa-kafka kafka-topics.sh --create \
    --zookeeper railsewa-zookeeper:2181 \
    --topic twitterstream \
    --partitions 1 \
    --replication-factor 1

# 6. Check services
docker-compose ps
```

### Access Services

- **Web Dashboard**: http://localhost/railways/
- **Spark Master UI**: http://localhost:8080
- **MySQL**: localhost:3306
- **Kafka**: localhost:9092

## Option 2: Manual Installation

### Step 1: Run Production Setup

```bash
cd deploy
chmod +x *.sh
sudo ./production_setup.sh
```

### Step 2: Setup MySQL Database

```bash
sudo ./setup_mysql.sh
```

Follow prompts to:
- Enter MySQL root password
- Create database and user
- Tables will be created automatically

### Step 3: Configure Environment

Edit `.env` file in project root:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=railsewa
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

# Spark Configuration
SPARK_MASTER=spark://localhost:7077
```

### Step 4: Setup Kafka

```bash
sudo ./setup_kafka.sh
```

This will:
- Start Zookeeper
- Start Kafka
- Create `twitterstream` topic

### Step 5: Setup Spark

```bash
sudo ./setup_spark.sh
```

This will:
- Configure Spark
- Start Spark Master
- Start Spark Worker

### Step 6: Train Model

```bash
/opt/spark/bin/spark-submit --master spark://localhost:7077 train_model.py
```

### Step 7: Start All Services

```bash
sudo ./start_services.sh
```

This starts:
- Zookeeper
- Kafka
- Spark
- Twitter Stream
- Spark Processing

### Step 8: Setup PHP Web Interface

```bash
# Install PHP dependencies
cd railways
composer install

# Copy files to web root
sudo cp -r ../railways/* /var/www/html/railways/
sudo cp -r ../assets /var/www/html/

# Set permissions
sudo chown -R www-data:www-data /var/www/html/railways
sudo chmod -R 755 /var/www/html/railways

# Restart Apache
sudo systemctl restart apache2
```

## Option 3: AWS Deployment

### Setup AWS RDS MySQL

1. Create RDS MySQL instance
2. Note endpoint, port, username, password
3. Update `.env` with RDS credentials
4. Run schema: `mysql -h endpoint -u user -p < database/schema.sql`

### Setup EC2 Instances

1. **Master Node** (for Kafka, Spark Master, Twitter Stream)
   - Instance type: t3.medium or larger
   - Install: Kafka, Spark, Zookeeper

2. **Worker Nodes** (for Spark Workers)
   - Instance type: t3.medium or larger
   - Install: Spark Worker

3. **Web Server** (for PHP interface)
   - Instance type: t3.small
   - Install: Apache, PHP, MySQL client

### Configure Security Groups

- MySQL: Allow port 3306 from web server
- Kafka: Allow port 9092 from master/workers
- Spark: Allow ports 7077, 8080 from workers
- Web: Allow port 80/443 from internet

## Verification

### Check MySQL
```bash
mysql -h localhost -u railsewa -p
USE twitter;
SELECT COUNT(*) FROM tweets;
```

### Check Kafka
```bash
/opt/kafka/bin/kafka-topics.sh --list --zookeeper localhost:2181
/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic twitterstream --from-beginning
```

### Check Spark
```bash
curl http://localhost:8080
/opt/spark/bin/spark-submit --master spark://localhost:7077 --version
```

### Check Twitter Stream
```bash
tail -f /var/log/twitter_stream.log
```

### Check Web Interface
```bash
curl http://localhost/railways/
```

## Troubleshooting

### Services Not Starting
```bash
# Check logs
sudo journalctl -u kafka
sudo journalctl -u spark
tail -f /var/log/twitter_stream.log

# Check ports
sudo netstat -tulpn | grep -E '2181|9092|7077|3306'
```

### Database Connection Issues
```bash
# Test connection
mysql -h localhost -u railsewa -p twitter

# Check MySQL status
sudo systemctl status mysql
```

### Kafka Issues
```bash
# Check Zookeeper
/opt/zookeeper/bin/zkServer.sh status

# Check Kafka logs
tail -f /var/log/kafka.log
```

### Spark Issues
```bash
# Check Spark Master
curl http://localhost:8080

# Check Spark logs
tail -f /opt/spark/logs/*
```

## Monitoring

### Service Status
```bash
# All services
sudo ./deploy/check_services.sh

# Individual services
sudo systemctl status mysql
sudo systemctl status kafka
sudo systemctl status spark
```

### Performance Monitoring
- Spark UI: http://localhost:8080
- Kafka Manager: Install separately
- MySQL: Use phpMyAdmin or MySQL Workbench

## Maintenance

### Stop All Services
```bash
sudo ./deploy/stop_services.sh
```

### Restart Services
```bash
sudo ./deploy/stop_services.sh
sudo ./deploy/start_services.sh
```

### Backup Database
```bash
mysqldump -u railsewa -p twitter > backup_$(date +%Y%m%d).sql
```

## Next Steps

1. Configure monitoring and alerts
2. Setup automated backups
3. Configure load balancing (if multiple workers)
4. Setup SSL certificates for web interface
5. Configure firewall rules
6. Setup log rotation
7. Configure auto-scaling (AWS)

## Support

For issues:
- Check logs in `/var/log/`
- Review service status
- Check network connectivity
- Verify credentials in `.env`

