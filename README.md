# Real Time Indian Railways Telegram Complaint Administration System

Automated Real-Time classification of Indian Railways complaints received via Telegram Bot into emergency and feedback using Apache Spark, Kafka, MySQL and PHP. The complete cluster is deployed on AWS EC2 and it uses AWS RDS for database operations.

## Project Overview

This system processes real-time complaints from Telegram users about Indian Railways, classifies them into emergency and feedback categories, and provides an interactive web interface for administrators to manage and respond to complaints via Telegram.

## Technology Stack

- **Backend Processing**: Apache Spark, Apache Kafka, Zookeeper
- **Database**: MySQL (AWS RDS)
- **Web Interface**: PHP, HTML, CSS, Bootstrap, jQuery, JavaScript, AJAX
- **Machine Learning**: Python (scikit-learn, Spark MLlib)
- **Deployment**: AWS EC2, AWS RDS
- **Telegram Bot API**: For receiving complaints and sending responses

## Project Structure

```
RailSewa-FinalYearProject/
├── kafka_file/          # Kafka streaming scripts (Telegram Bot)
├── railways/            # PHP web interface
├── parsing_raw_tweets/  # Complaint parsing utilities
├── saved_model/         # Trained ML models
├── data/                # Training data and datasets
├── assets/              # Static assets (CSS, JS, images)
├── live_processing.py   # Live complaint processing
├── new_live_processing.py  # Updated live processing
├── train_model.py       # Model training script
├── sparksupport.py      # Spark utility functions
└── IR-Complaint-Feedback-Mgmt-System.ipynb  # Jupyter notebook
```

## Pre-Requisites

### System Requirements
- Python 3.x
- Apache Spark (3+ nodes cluster)
- Apache Kafka & Zookeeper
- MySQL (AWS RDS)
- XAMPP server
- Telegram Bot Token (from BotFather)

### AWS Setup
1. Launch EC2 instances (master, slave1, slave2, xampp server)
2. Setup AWS RDS for MySQL database
3. Configure SSH communication between instances
4. Setup Spark cluster (minimum 3 nodes)

### Telegram Bot Setup
1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow instructions to create a bot
4. Copy the Bot Token provided
5. Add token to `.env` file as `TELEGRAM_BOT_TOKEN`

## Installation

### 1. Database Setup

Login to AWS RDS:
```bash
mysql -h "your-database-ip" -P 3306 -u "username" -p
```

Create database and tables:
```sql
CREATE DATABASE twitter;
USE twitter;

CREATE TABLE tweets (
    id int AUTO_INCREMENT PRIMARY KEY,
    tweet varchar(280),
    username varchar(50),
    pnr bigint(10),
    prediction int(1),
    tweet_id bigint(10),
    latitude decimal(10,8),
    longitude decimal(11,8),
    time TIMESTAMP,
    response_status int(1),
    response varchar(280)
);

CREATE TABLE admin (
    id int AUTO_INCREMENT PRIMARY KEY,
    username varchar(50),
    password varchar(255),
    email varchar(100)
);
```

### 2. Zookeeper Setup

On master, slave1, and slave2:
```bash
zkServer.sh start
```

### 3. Kafka Setup

On master:
```bash
cd kafka
nohup bin/kafka-server-start.sh config/server.properties &
```

On slave1 and slave2:
```bash
cd kafka
nohup bin/kafka-server-start.sh config/server.properties &
```

Create Kafka topic (on master, only once):
```bash
cd kafka
bin/kafka-topics.sh --create --zookeeper localhost:2181 --partitions 1 --topic twitterstream --replication-factor 1
```

### 4. Start Kafka Consumers

On master, slave1, slave2:
```bash
cd kafka
bin/kafka-console-consumer.sh --bootstrap-server localhost:2181 --topic twitterstream --from-beginning &
```

### 5. Start Streaming

On master:
```bash
python kafka_file/stream_data.py &
```

### 6. Train Model (One-time)

On master:
```bash
spark-submit train_model.py
```

### 7. Start Live Processing

On master:
```bash
spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.0 new_live_processing.py
```

### 8. Install PHP Dependencies

On xampp server:
```bash
# Install Composer if not already installed
# Then install PHP dependencies
composer install
```

### 9. Start Web Server

On xampp server:
```bash
sudo /opt/lampp/lampp start
```

Access:
- Website: `http://IP-Address/railways/`
- phpMyAdmin: `http://IP-Address/phpmyadmin/`

## PHP Dependencies

Install PHP dependencies using Composer:
```bash
composer install
```

This will install the TwitterOAuth library required for posting responses to Twitter.

## Configuration

### Telegram Bot Configuration

Update `.env` file with your Telegram Bot Token:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
```

To get a bot token:
1. Open Telegram → Search for @BotFather
2. Send `/newbot` command
3. Follow instructions
4. Copy the token provided

### Database Configuration

Update database connection details in:
- `new_live_processing.py`
- `railways/config.php`

## Usage

1. Users send complaints to your Telegram Bot
2. Complaints are automatically sent to Kafka for processing
3. Spark classifies complaints as emergency (1) or feedback (0)
4. Complaints are stored in MySQL database
5. Administrators can view and respond to complaints via the web interface
6. Responses are automatically sent back to users via Telegram

## Features

- Real-time complaint reception via Telegram Bot
- Automatic classification using ML models
- Interactive web dashboard for administrators
- Automated response system via Telegram
- PNR extraction from complaints
- Location tracking (latitude/longitude) - optional
- Historical data analysis
- User-friendly Telegram interface

## License

MIT License

## Contributing

PRs and Issues are welcome!

## Acknowledgments

- Apache Spark Community
- Apache Kafka Community
- Telegram Bot API

