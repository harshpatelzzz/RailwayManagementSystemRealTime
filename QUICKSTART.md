# Quick Start Guide

## Prerequisites Checklist

- [ ] Python 3.x installed
- [ ] Apache Spark cluster (3+ nodes)
- [ ] Apache Kafka & Zookeeper installed
- [ ] MySQL database (AWS RDS or local)
- [ ] XAMPP server (for web interface)
- [ ] Twitter API credentials

## Step-by-Step Setup

### 1. Clone and Setup Project

```bash
# Run setup script
python setup.py

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `.env` file with your credentials:
- Database connection details
- Kafka broker addresses
- Twitter API keys

### 3. Setup Database

```bash
# Connect to your MySQL database
mysql -h your-rds-endpoint -u username -p

# Run schema
source database/schema.sql
```

### 4. Start Zookeeper

On all nodes (master, slave1, slave2):
```bash
zkServer.sh start
```

### 5. Start Kafka

On master:
```bash
cd kafka
nohup bin/kafka-server-start.sh config/server.properties &
```

On slaves:
```bash
cd kafka
nohup bin/kafka-server-start.sh config/server.properties &
```

Create topic (on master, once):
```bash
cd kafka
bin/kafka-topics.sh --create --zookeeper localhost:2181 --partitions 1 --topic twitterstream --replication-factor 1
```

### 6. Start Kafka Consumers

On all nodes:
```bash
cd kafka
bin/kafka-console-consumer.sh --bootstrap-server localhost:2181 --topic twitterstream --from-beginning &
```

### 7. Start Twitter Streaming

On master:
```bash
python kafka_file/stream_data.py &
```

### 8. Train Model (One-time)

On master:
```bash
spark-submit train_model.py
```

### 9. Start Live Processing

On master:
```bash
spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.0 new_live_processing.py
```

### 10. Start Web Server

On XAMPP server:
```bash
sudo /opt/lampp/lampp start
```

### 11. Access Web Interface

Open browser:
- Website: `http://your-server-ip/railways/`
- phpMyAdmin: `http://your-server-ip/phpmyadmin/`

## Troubleshooting

### Kafka Connection Issues
- Check if Zookeeper is running: `zkServer.sh status`
- Verify Kafka brokers are accessible
- Check firewall settings

### Database Connection Issues
- Verify RDS endpoint and credentials
- Check security group allows connections
- Test connection: `mysql -h endpoint -u user -p`

### Twitter API Issues
- Verify API credentials in `.env`
- Check rate limits
- Ensure Twitter Developer account is active

### Spark Issues
- Verify Spark cluster is running
- Check worker nodes are connected
- Review Spark logs

## Testing

### Test Twitter Streaming
```bash
# Check Kafka topic
cd kafka
bin/kafka-console-consumer.sh --bootstrap-server localhost:2181 --topic twitterstream --from-beginning
```

### Test Database
```sql
SELECT COUNT(*) FROM tweets;
SELECT * FROM tweets ORDER BY time DESC LIMIT 10;
```

### Test Web Interface
- Open dashboard
- Check statistics update
- Try filtering tweets
- Test response functionality

## Next Steps

1. Add more training data to improve model accuracy
2. Configure Twitter API for automated responses
3. Set up monitoring and alerts
4. Deploy to production AWS environment
5. Configure auto-scaling for Spark cluster

## Support

For issues and questions:
- Check README.md for detailed documentation
- Review error logs
- Check GitHub issues

