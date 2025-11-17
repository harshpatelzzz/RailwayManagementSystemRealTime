# 🚂 RailSewa - System Design Document

## 📌 Project Overview

**RailSewa** is a real-time railway complaint classification and management system designed to streamline the process of receiving, categorizing, and responding to passenger complaints. The system leverages modern microservices architecture and real-time data processing to provide efficient complaint management.

### Core Purpose

RailSewa serves as a comprehensive platform that:

- **Accepts complaints** from passengers via Telegram Bot interface
- **Classifies complaints** automatically as *Emergency* or *Feedback* using machine learning
- **Stores all data** securely in AWS RDS MySQL database
- **Processes data** in real-time using Apache Kafka and Apache Spark streaming pipeline
- **Provides admin dashboard** for monitoring complaints, generating analytics, and managing responses
- **Enables real-time insights** through live statistics and visualizations

### Key Value Propositions

- **Real-time Processing**: Instant complaint ingestion and classification
- **Scalable Architecture**: Microservices-based design for horizontal scaling
- **User-Friendly Interface**: Simple Telegram Bot for passengers, comprehensive dashboard for admins
- **Data-Driven Decisions**: Analytics and statistics for better complaint management
- **Reliable Storage**: AWS RDS ensures data durability and availability

---

## ✨ Features

### Core Features

#### 1. **Telegram Bot Integration**
- Seamless complaint submission via Telegram
- User-friendly conversational interface
- Automatic acknowledgment and status updates
- Support for text-based complaints with PNR extraction

#### 2. **Intelligent Classification**
- **Emergency Classification**: Identifies urgent complaints requiring immediate attention
- **Feedback Classification**: Categorizes general feedback and suggestions
- **ML-Based Classification**: Rule-based and machine learning models for accurate categorization
- **PNR Extraction**: Automatically extracts PNR numbers from complaint text

#### 3. **Real-Time Data Pipeline**
- **Kafka Streaming**: High-throughput message streaming
- **Spark Processing**: Optional real-time batch processing for large-scale operations
- **Event-Driven Architecture**: Asynchronous processing for better performance

#### 4. **Structured Data Storage**
- **AWS RDS MySQL**: Reliable, managed database service
- **Normalized Schema**: Well-structured tables for efficient queries
- **Data Integrity**: Foreign keys and constraints ensure data consistency
- **Indexed Queries**: Optimized for fast retrieval

#### 5. **Admin Dashboard**
- **Real-Time Monitoring**: Live view of incoming complaints
- **Filtering & Search**: Filter by Emergency/Feedback, search by keywords
- **Statistics Dashboard**: Visual analytics and insights
- **Response Management**: Admin can respond to complaints directly
- **Auto-Refresh**: Dashboard updates every 10 seconds automatically

#### 6. **Scalable Architecture**
- **Microservices Design**: Independent, loosely coupled services
- **Horizontal Scaling**: Each component can scale independently
- **Fault Tolerance**: Services continue operating even if one component fails
- **Container-Ready**: Docker support for easy deployment

#### 7. **Security & Configuration**
- **Environment Variables**: Sensitive data stored in `.env` files
- **Database Security**: Encrypted connections to AWS RDS
- **Token Management**: Secure handling of Telegram Bot tokens
- **Access Control**: Admin authentication for dashboard access

---

## 🏗 Architecture Overview

### System Architecture

RailSewa follows a **microservices architecture** with clear separation of concerns. The system is designed to handle high-throughput complaint processing while maintaining low latency and high availability.

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAILSEWA SYSTEM                           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Telegram   │
│     Bot      │
│   (Users)    │
└──────┬───────┘
       │
       │ Messages
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INGESTION LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Telegram Bot Service (Python)                           │   │
│  │  - Receives user messages                                 │   │
│  │  - Validates and formats                                  │   │
│  │  - Produces to Kafka                                      │   │
│  └──────────────────┬───────────────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      │ Kafka Producer
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMING LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Apache Kafka Broker                                      │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  Topic: raw_tweets                                 │  │   │
│  │  │  - High-throughput message queue                   │  │   │
│  │  │  - Fault-tolerant storage                           │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────┬───────────────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌──────────────┐          ┌──────────────────────┐
│   Kafka     │          │  Spark Structured    │
│  Consumer   │          │    Streaming        │
│  (Python)   │          │  (Optional)          │
│             │          │                      │
│ - Immediate │          │ - Batch Processing   │
│   Processing│          │ - ML Classification  │
│ - Simple    │          │ - High Throughput    │
└──────┬──────┘          └──────────┬───────────┘
       │                             │
       └─────────────┬───────────────┘
                     │
                     │ Processed Data
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Complaint Processor                                      │   │
│  │  - Text Cleaning                                          │   │
│  │  - PNR Extraction                                         │   │
│  │  - Classification (Emergency/Feedback)                    │   │
│  │  - Data Enrichment                                        │   │
│  └──────────────────┬───────────────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      │ SQL INSERT
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  AWS RDS MySQL Database                                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │   │
│  │  │ tweets   │  │  admin   │  │  stats   │               │   │
│  │  └──────────┘  └──────────┘  └──────────┘               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      │ REST API
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API LAYER                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Flask REST API (Python)                                   │   │
│  │  - /api/stats - Statistics                                │   │
│  │  - /api/tweets - Complaint listing                        │   │
│  │  - /api/respond - Admin responses                         │   │
│  └──────────────────┬───────────────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      │ HTTP/JSON
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Admin Dashboard (HTML/JavaScript)                         │   │
│  │  - Real-time complaint view                               │   │
│  │  - Statistics & analytics                                 │   │
│  │  - Filtering & search                                     │   │
│  │  - Response management                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

1. **Event-Driven**: Components communicate through events (Kafka messages)
2. **Loose Coupling**: Services are independent and can be developed/deployed separately
3. **Scalability**: Each layer can scale independently based on load
4. **Fault Tolerance**: System continues operating even if one component fails
5. **Data Consistency**: ACID transactions ensure data integrity

---

## 🧩 Components Breakdown

### 4.1 Telegram Bot Service

**Location**: `kafka_file/telegram_stream.py`

**Responsibilities**:
- Receives messages from Telegram users via Bot API
- Validates message format and content
- Formats messages into standardized JSON structure
- Produces messages to Kafka topic `raw_tweets`
- Sends acknowledgment to users

**Key Features**:
- Asynchronous message handling
- Error handling and retry logic
- Message validation
- User-friendly responses

**Message Format**:
```json
{
  "complaint_id": 1234567890,
  "text": "Train No 9166 is delayed...",
  "user_id": 6491883832,
  "username": "user_6491883832",
  "first_name": "John",
  "last_name": "Doe",
  "chat_id": 6491883832,
  "timestamp": "2025-11-17T18:00:00Z"
}
```

### 4.2 Kafka Layer

**Configuration**:
- **Broker**: `localhost:9092` (local) or AWS MSK (production)
- **Topic**: `raw_tweets`
- **Partitions**: 1 (configurable for scaling)
- **Replication Factor**: 1 (local) or 3 (production)

**Components**:

#### Kafka Producer
- **Location**: `kafka_file/telegram_stream.py`
- **Function**: Publishes complaint messages to Kafka
- **Serialization**: JSON format

#### Kafka Broker
- **Mode**: KRaft (Kafka 4.1.0+) - No Zookeeper required
- **Storage**: Local filesystem or cloud storage
- **Features**: High throughput, fault tolerance, message retention

#### Kafka Consumer
- **Location**: `kafka_consumer.py`
- **Function**: Consumes messages from Kafka
- **Processing**: Immediate processing and database insertion
- **Alternative**: Spark Structured Streaming for batch processing

### 4.3 Spark/ML Processing

**Location**: `new_live_processing_structured.py`

**Purpose**: Optional high-throughput processing using Apache Spark

**Features**:
- **Structured Streaming**: Modern Spark API for stream processing
- **Batch Processing**: Processes messages in 10-second batches
- **Scalability**: Can handle millions of messages per second
- **ML Integration**: Ready for machine learning model integration

**Processing Pipeline**:
1. Read from Kafka topic
2. Parse JSON messages
3. Clean text (remove URLs, mentions, special chars)
4. Extract PNR numbers (10-digit patterns)
5. Classify urgency (Emergency vs Feedback)
6. Save to MySQL database

**When to Use**:
- High message volume (>1000 messages/second)
- Complex ML model inference
- Batch analytics requirements
- Production-scale deployments

### 4.4 Backend API

**Location**: `dashboard_api_mysql.py`

**Technology**: Flask (Python) REST API

**Endpoints**:

#### GET `/api/stats`
Returns system statistics:
```json
{
  "total": 150,
  "emergency": 45,
  "feedback": 105,
  "responded": 30,
  "pending": 120
}
```

#### GET `/api/tweets`
Returns complaint list with filtering:
- Query Parameters:
  - `filter`: `all` | `emergency` | `feedback`
  - `limit`: Number of records (default: 100)

#### POST `/api/respond`
Admin response to complaint:
```json
{
  "tweet_id": 123,
  "response": "We have forwarded your complaint to the concerned department."
}
```

**Features**:
- CORS enabled for frontend access
- MySQL connection pooling
- Error handling and validation
- JSON serialization

### 4.5 Database (AWS RDS)

**Technology**: MySQL 8.0+ on AWS RDS

**Connection Details**:
- **Host**: `railway-db.cqtm4ssyoba3.us-east-1.rds.amazonaws.com`
- **Port**: `3306`
- **Database**: `twitter`
- **Engine**: MySQL 8.0

**Key Features**:
- Managed service (backups, updates, monitoring)
- High availability (multi-AZ option)
- Automated backups
- Encryption at rest
- Security groups for access control

### 4.6 Frontend Dashboard

**Location**: `dashboard.html`

**Technology**: HTML5, JavaScript (jQuery), Bootstrap 5

**Features**:
- **Real-Time Updates**: Auto-refreshes every 10 seconds
- **Filtering**: Filter by All/Emergency/Feedback
- **Statistics Cards**: Total, Emergency, Feedback, Processed counts
- **Complaint Cards**: Display with badges, timestamps, PNR info
- **Responsive Design**: Works on desktop and mobile
- **Dark Theme**: Modern matte black design

**UI Components**:
- Statistics dashboard
- Filter buttons
- Complaint list with cards
- Loading states
- Empty states
- Error handling

---

## 🗃 Database Schema

### Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      DATABASE SCHEMA                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                         tweets                               │
├─────────────────────────────────────────────────────────────┤
│ PK  id                  INT AUTO_INCREMENT                   │
│     tweet               VARCHAR(500) NOT NULL                │
│     username            VARCHAR(50)                           │
│     pnr                 BIGINT(10)                           │
│     prediction          INT(1) DEFAULT 0                     │
│     tweet_id            BIGINT(10) UNIQUE                    │
│     user_id             BIGINT(20)                           │
│     chat_id             BIGINT(20)                           │
│     source              VARCHAR(20) DEFAULT 'Telegram'      │
│     latitude            DECIMAL(10,8)                        │
│     longitude           DECIMAL(11,8)                        │
│     time                TIMESTAMP DEFAULT CURRENT_TIMESTAMP  │
│     response_status     INT(1) DEFAULT 0                     │
│     response            VARCHAR(500)                         │
│                                                              │
│ INDEX idx_prediction (prediction)                            │
│ INDEX idx_response_status (response_status)                  │
│ INDEX idx_time (time)                                        │
│ INDEX idx_tweet_id (tweet_id)                                │
│ INDEX idx_user_id (user_id)                                  │
│ INDEX idx_source (source)                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                         admin                                │
├─────────────────────────────────────────────────────────────┤
│ PK  id                  INT AUTO_INCREMENT                   │
│     username            VARCHAR(50) UNIQUE NOT NULL          │
│     password            VARCHAR(255) NOT NULL                │
│     email               VARCHAR(100)                         │
│     created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP  │
│     last_login          TIMESTAMP NULL                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    tweet_stats (VIEW)                       │
├─────────────────────────────────────────────────────────────┤
│     total_tweets        INT                                  │
│     emergency_count     INT                                  │
│     feedback_count      INT                                  │
│     responded_count     INT                                  │
│     pending_count       INT                                  │
└─────────────────────────────────────────────────────────────┘
```

### Table Descriptions

#### `tweets` Table
Primary table storing all complaint data.

**Key Fields**:
- `id`: Auto-increment primary key
- `tweet`: Complaint text (max 500 characters)
- `username`: Telegram username
- `pnr`: Extracted PNR number (if found)
- `prediction`: Classification (0=Feedback, 1=Emergency)
- `tweet_id`: Unique Telegram message ID
- `user_id`: Telegram user ID
- `chat_id`: Telegram chat ID
- `source`: Source of complaint (default: 'Telegram')
- `time`: Timestamp of complaint
- `response_status`: 0=Not responded, 1=Responded
- `response`: Admin response text

**Indexes**: Optimized for common queries (prediction, status, time)

#### `admin` Table
Stores admin user credentials and information.

**Key Fields**:
- `id`: Auto-increment primary key
- `username`: Unique admin username
- `password`: Hashed password (bcrypt)
- `email`: Admin email address
- `created_at`: Account creation timestamp
- `last_login`: Last login timestamp

#### `tweet_stats` View
Pre-computed statistics view for dashboard.

**Computed Fields**:
- Total complaints count
- Emergency complaints count
- Feedback complaints count
- Responded complaints count
- Pending complaints count

---

## 🔄 Data Flow

### User Complaint Flow

```
┌──────────┐
│  User    │
└────┬─────┘
     │
     │ 1. Sends message via Telegram
     ▼
┌─────────────────────────────────────┐
│  Telegram Bot Service               │
│  - Receives message                 │
│  - Validates format                 │
│  - Formats JSON                     │
└────┬────────────────────────────────┘
     │
     │ 2. Produces to Kafka
     ▼
┌─────────────────────────────────────┐
│  Kafka Topic: raw_tweets            │
│  - Message queued                   │
│  - Persistent storage               │
└────┬────────────────────────────────┘
     │
     │ 3. Consumer reads message
     ▼
┌─────────────────────────────────────┐
│  Kafka Consumer / Spark Processor   │
│  - Reads from Kafka                 │
│  - Parses JSON                      │
│  - Cleans text                      │
│  - Extracts PNR                     │
│  - Classifies (Emergency/Feedback)  │
└────┬────────────────────────────────┘
     │
     │ 4. INSERT INTO database
     ▼
┌─────────────────────────────────────┐
│  AWS RDS MySQL                       │
│  - Stores complaint                 │
│  - Updates statistics               │
└────┬────────────────────────────────┘
     │
     │ 5. API fetches data
     ▼
┌─────────────────────────────────────┐
│  Flask REST API                     │
│  - /api/tweets                      │
│  - /api/stats                       │
└────┬────────────────────────────────┘
     │
     │ 6. Dashboard displays
     ▼
┌─────────────────────────────────────┐
│  Admin Dashboard                     │
│  - Shows complaint                  │
│  - Updates statistics               │
└─────────────────────────────────────┘
```

### Admin Response Flow

```
┌──────────────────┐
│  Admin Dashboard │
└────────┬─────────┘
         │
         │ 1. Admin clicks "Respond"
         ▼
┌─────────────────────────────────────┐
│  Frontend JavaScript                │
│  - Collects response text           │
│  - Sends POST request               │
└────┬────────────────────────────────┘
     │
     │ 2. POST /api/respond
     ▼
┌─────────────────────────────────────┐
│  Flask REST API                     │
│  - Validates request                 │
│  - Updates database                 │
└────┬────────────────────────────────┘
     │
     │ 3. UPDATE tweets table
     ▼
┌─────────────────────────────────────┐
│  AWS RDS MySQL                       │
│  - Sets response_status = 1         │
│  - Stores response text             │
└────┬────────────────────────────────┘
     │
     │ 4. Dashboard refreshes
     ▼
┌─────────────────────────────────────┐
│  Admin Dashboard                     │
│  - Shows "Responded" badge           │
│  - Displays response                │
└─────────────────────────────────────┘
```

### Step-by-Step Processing Flow

#### Step 1: Message Reception
1. User opens Telegram
2. Finds RailSewa bot
3. Sends complaint message
4. Bot receives message via Telegram Bot API

#### Step 2: Message Processing
1. Bot validates message (non-empty, text format)
2. Extracts user information (user_id, username, chat_id)
3. Creates complaint JSON object
4. Generates unique complaint_id (message_id)

#### Step 3: Kafka Production
1. Bot connects to Kafka broker
2. Serializes message to JSON
3. Produces to `raw_tweets` topic
4. Receives acknowledgment from Kafka

#### Step 4: Consumer Processing
1. Consumer subscribes to `raw_tweets` topic
2. Reads message from Kafka
3. Deserializes JSON
4. Processes complaint:
   - Cleans text (removes URLs, mentions)
   - Extracts PNR (10-digit pattern)
   - Classifies urgency (keyword-based or ML)
5. Formats data for database

#### Step 5: Database Storage
1. Connects to AWS RDS MySQL
2. Executes INSERT statement
3. Commits transaction
4. Handles duplicates (if any)

#### Step 6: Dashboard Display
1. Dashboard polls API every 10 seconds
2. API queries database
3. Returns JSON response
4. Dashboard renders complaints
5. Updates statistics

---

## 🛠 Tech Stack

### Backend Technologies

#### Python 3.8+
- **Purpose**: Primary backend language
- **Why**: 
  - Excellent libraries for data processing
  - Easy integration with Kafka, Spark, Telegram
  - Rapid development
  - Strong ML ecosystem

#### Flask (Python Web Framework)
- **Purpose**: REST API server
- **Why**:
  - Lightweight and fast
  - Easy to deploy
  - Good for microservices
  - CORS support built-in

#### Apache Kafka 4.1.0+
- **Purpose**: Message streaming and event bus
- **Why**:
  - High throughput (millions of messages/sec)
  - Fault tolerance
  - Scalable and distributed
  - KRaft mode (no Zookeeper needed)

#### Apache Spark 4.0+
- **Purpose**: Large-scale data processing
- **Why**:
  - Structured Streaming for real-time processing
  - MLlib for machine learning
  - Handles big data workloads
  - Integrates with Kafka

### Database Technologies

#### AWS RDS MySQL 8.0+
- **Purpose**: Primary data storage
- **Why**:
  - Managed service (no maintenance)
  - Automated backups
  - High availability
  - Scalable (vertical and horizontal)
  - Security features

### Frontend Technologies

#### HTML5 / CSS3 / JavaScript
- **Purpose**: Admin dashboard
- **Why**:
  - No build process needed
  - Fast development
  - Works everywhere
  - Modern browser APIs

#### Bootstrap 5
- **Purpose**: UI framework
- **Why**:
  - Responsive design
  - Pre-built components
  - Consistent styling
  - Mobile-friendly

#### jQuery
- **Purpose**: DOM manipulation and AJAX
- **Why**:
  - Simple API
  - Cross-browser compatibility
  - Easy AJAX calls

### Integration Technologies

#### Telegram Bot API
- **Purpose**: User interface for complaints
- **Why**:
  - Widely used messaging platform
  - Easy bot creation
  - Free API
  - Good documentation

#### python-telegram-bot
- **Purpose**: Python wrapper for Telegram API
- **Why**:
  - Easy to use
  - Async support
  - Well-maintained

#### kafka-python
- **Purpose**: Kafka client library
- **Why**:
  - Pure Python implementation
  - Easy integration
  - Good performance

#### PyMySQL
- **Purpose**: MySQL database connector
- **Why**:
  - Pure Python (no C dependencies)
  - Fast and reliable
  - Good error handling

### DevOps & Configuration

#### .env Files
- **Purpose**: Environment configuration
- **Why**:
  - Secure credential storage
  - Environment-specific configs
  - Easy deployment

#### Docker (Optional)
- **Purpose**: Containerization
- **Why**:
  - Consistent environments
  - Easy deployment
  - Scalability

### Development Tools

#### Git
- Version control
- Code collaboration

#### Python Virtual Environment
- Dependency isolation
- Reproducible builds

---

## 🚀 How to Run the Project (Local)

### Prerequisites

- Python 3.8 or higher
- Java JDK 8+ (for Kafka and Spark)
- MySQL client (optional, for direct DB access)
- Git

### Step-by-Step Setup

#### 1. Clone Repository

```bash
git clone https://github.com/harshpatelzzz/RailwayManagementSystemRealTime.git
cd RailwayManagementSystemRealTime
```

#### 2. Set Up Environment

Create `.env` file in project root:

```bash
# Database Configuration
DB_HOST=railway-db.cqtm4ssyoba3.us-east-1.rds.amazonaws.com
DB_PORT=3306
DB_USER=harshpatelzzz
DB_PASSWORD=your_password_here
DB_NAME=twitter

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Kafka Configuration
KAFKA_BROKER=localhost:9092
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=raw_tweets
```

#### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Key packages:
- `python-telegram-bot`
- `kafka-python`
- `pymysql`
- `flask`
- `flask-cors`
- `python-dotenv`
- `pyspark` (optional, for Spark processing)

#### 4. Set Up Kafka

**Option A: Local Kafka (KRaft Mode)**

```bash
# Download and extract Kafka 4.1.0+
cd ~/kafka/kafka

# Format storage
bin/windows/kafka-storage.bat format -t <cluster-id> -c config/server.properties --standalone

# Start Kafka
bin/windows/kafka-server-start.bat config/server.properties
```

**Option B: Docker**

```bash
docker-compose -f docker-compose-kafka.yml up -d
```

**Create Topic:**

```bash
bin/windows/kafka-topics.bat --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --topic raw_tweets
```

#### 5. Set Up Database

**If using AWS RDS:**
- Database should already be created
- Run schema: `mysql -h <endpoint> -u <user> -p < database/schema.sql`

**If using local MySQL:**
```bash
mysql -u root -p < database/schema.sql
```

#### 6. Start Services

**Terminal 1: Telegram Bot**
```bash
python kafka_file/telegram_stream.py
```

**Terminal 2: Kafka Consumer (Python)**
```bash
python kafka_consumer.py
```

**Terminal 3: Spark Processing (Optional)**
```bash
python new_live_processing_structured.py
```

**Terminal 4: Dashboard API**
```bash
python dashboard_api_mysql.py
```

#### 7. Access Dashboard

Open browser: `http://localhost:5000`

#### 8. Test the System

1. Open Telegram and find your bot
2. Send a test message: "Train No 9166 is delayed. PNR: 1234567890"
3. Check Kafka Consumer window - should process message
4. Check Dashboard - complaint should appear
5. Verify in database - record should be saved

### Verification Checklist

- [ ] Kafka broker running on port 9092
- [ ] Kafka topic `raw_tweets` created
- [ ] Database connection successful
- [ ] Telegram Bot token configured
- [ ] All Python services started
- [ ] Dashboard accessible at http://localhost:5000
- [ ] Test message processed successfully

---

## ☁️ Deployment (Production)

### AWS Infrastructure

#### 1. AWS RDS Setup

**Steps:**
1. Create RDS MySQL instance in AWS Console
2. Choose instance class (db.t3.small for production)
3. Configure security group (allow port 3306)
4. Set master username and password
5. Enable automated backups
6. Note endpoint and credentials

**Configuration:**
- Engine: MySQL 8.0
- Instance: db.t3.small or larger
- Storage: 20GB+ (with autoscaling)
- Multi-AZ: Enabled for high availability
- Backup retention: 7 days

#### 2. Kafka Deployment

**Option A: AWS MSK (Managed Streaming for Kafka)**
- Fully managed Kafka service
- Automatic scaling
- High availability
- Recommended for production

**Option B: Kafka on EC2**
- Install Kafka on EC2 instance
- Use KRaft mode (no Zookeeper)
- Configure security groups
- Set up monitoring

#### 3. Application Deployment

**EC2 Instance Setup:**
1. Launch EC2 instance (t3.medium or larger)
2. Install Python 3.8+, Java JDK
3. Clone repository
4. Configure `.env` with production values
5. Install dependencies
6. Set up systemd services or PM2

**Systemd Service Example:**
```ini
[Unit]
Description=RailSewa Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/railsewa
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 kafka_file/telegram_stream.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 4. Environment Variables

Production `.env`:
```bash
# Production Database
DB_HOST=production-db.xxxxx.us-east-1.rds.amazonaws.com
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=<secure_password>
DB_NAME=twitter

# Production Kafka
KAFKA_BROKER=production-kafka:9092
KAFKA_BROKERS=production-kafka:9092
KAFKA_TOPIC=raw_tweets

# Telegram Bot
TELEGRAM_BOT_TOKEN=<production_token>
```

#### 5. Security Considerations

- **Database**: Use security groups, enable SSL
- **Kafka**: Enable SASL/SSL authentication
- **Secrets**: Use AWS Secrets Manager or Parameter Store
- **Network**: VPC with private subnets
- **Monitoring**: CloudWatch for logs and metrics

#### 6. Scaling Strategy

**Horizontal Scaling:**
- Multiple Kafka consumers (consumer groups)
- Multiple Spark workers
- Load balancer for API
- Read replicas for database

**Vertical Scaling:**
- Increase EC2 instance size
- Increase RDS instance class
- Increase Kafka broker resources

---

## 📦 Final Notes

### Security Considerations

#### 1. Credential Management
- **Never commit** `.env` files to Git
- Use environment variables or secrets management
- Rotate credentials regularly
- Use strong passwords (16+ characters)

#### 2. Database Security
- Enable SSL/TLS for database connections
- Use security groups to restrict access
- Enable encryption at rest
- Regular security updates

#### 3. API Security
- Implement rate limiting
- Add authentication for admin endpoints
- Use HTTPS in production
- Validate all inputs

#### 4. Network Security
- Use VPC with private subnets
- Implement network ACLs
- Use security groups properly
- Enable DDoS protection

### Handling Sensitive Tokens

**Best Practices:**
1. Store tokens in `.env` file (not in code)
2. Add `.env` to `.gitignore`
3. Use AWS Secrets Manager for production
4. Rotate tokens periodically
5. Use different tokens for dev/prod

**Example `.gitignore`:**
```
.env
*.env
.env.local
.env.production
```

### Scaling Suggestions

#### For High Volume (1000+ messages/second)

1. **Kafka Scaling:**
   - Increase partitions (10+)
   - Multiple Kafka brokers
   - Use AWS MSK

2. **Processing Scaling:**
   - Multiple Spark workers
   - Consumer groups with multiple consumers
   - Parallel processing

3. **Database Scaling:**
   - Read replicas for queries
   - Connection pooling
   - Query optimization
   - Indexing strategy

4. **API Scaling:**
   - Load balancer
   - Multiple API instances
   - Caching layer (Redis)
   - CDN for static assets

#### Performance Optimization

1. **Database:**
   - Proper indexing
   - Query optimization
   - Connection pooling
   - Batch inserts

2. **Kafka:**
   - Tune batch sizes
   - Optimize serialization
   - Configure retention policies

3. **Spark:**
   - Tune executor memory
   - Optimize batch intervals
   - Use broadcast variables

### Monitoring & Logging

**Recommended Tools:**
- **CloudWatch**: AWS metrics and logs
- **Grafana**: Visualization and dashboards
- **Prometheus**: Metrics collection
- **ELK Stack**: Log aggregation

**Key Metrics to Monitor:**
- Message throughput (Kafka)
- Processing latency
- Database connection pool
- Error rates
- API response times

### Future Enhancements

1. **Machine Learning:**
   - Train custom classification model
   - Sentiment analysis
   - Priority scoring

2. **Advanced Features:**
   - Multi-language support
   - Image/video complaint support
   - Automated responses
   - Integration with railway systems

3. **Analytics:**
   - Advanced dashboards
   - Predictive analytics
   - Trend analysis
   - Reporting

---

## 📚 Additional Resources

- **Project Repository**: https://github.com/harshpatelzzz/RailwayManagementSystemRealTime
- **Kafka Documentation**: https://kafka.apache.org/documentation/
- **Spark Documentation**: https://spark.apache.org/docs/latest/
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **AWS RDS Documentation**: https://docs.aws.amazon.com/rds/

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Maintained By**: RailSewa Development Team

