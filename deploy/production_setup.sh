#!/bin/bash
# Production Deployment Script for RailSewa
# This script sets up the complete production infrastructure

set -e

echo "=========================================="
echo "RailSewa Production Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

echo -e "${GREEN}Starting production setup...${NC}"

# Step 1: Install Java (required for Kafka and Spark)
echo -e "${YELLOW}[1/6] Installing Java JDK...${NC}"
if ! command -v java &> /dev/null; then
    apt-get update
    apt-get install -y openjdk-11-jdk
    echo -e "${GREEN}Java installed${NC}"
else
    echo -e "${GREEN}Java already installed${NC}"
fi

# Step 2: Install MySQL
echo -e "${YELLOW}[2/6] Installing MySQL...${NC}"
if ! command -v mysql &> /dev/null; then
    apt-get install -y mysql-server
    systemctl start mysql
    systemctl enable mysql
    echo -e "${GREEN}MySQL installed and started${NC}"
else
    echo -e "${GREEN}MySQL already installed${NC}"
fi

# Step 3: Install Zookeeper
echo -e "${YELLOW}[3/6] Installing Apache Zookeeper...${NC}"
ZOOKEEPER_VERSION="3.8.0"
ZOOKEEPER_DIR="/opt/zookeeper"
if [ ! -d "$ZOOKEEPER_DIR" ]; then
    cd /tmp
    wget https://archive.apache.org/dist/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/apache-zookeeper-${ZOOKEEPER_VERSION}-bin.tar.gz
    tar -xzf apache-zookeeper-${ZOOKEEPER_VERSION}-bin.tar.gz
    mv apache-zookeeper-${ZOOKEEPER_VERSION}-bin $ZOOKEEPER_DIR
    mkdir -p $ZOOKEEPER_DIR/data
    echo "1" > $ZOOKEEPER_DIR/data/myid
    echo -e "${GREEN}Zookeeper installed${NC}"
else
    echo -e "${GREEN}Zookeeper already installed${NC}"
fi

# Step 4: Install Kafka
echo -e "${YELLOW}[4/6] Installing Apache Kafka...${NC}"
KAFKA_VERSION="2.13-3.5.0"
KAFKA_DIR="/opt/kafka"
if [ ! -d "$KAFKA_DIR" ]; then
    cd /tmp
    wget https://downloads.apache.org/kafka/3.5.0/kafka_${KAFKA_VERSION}.tgz
    tar -xzf kafka_${KAFKA_VERSION}.tgz
    mv kafka_${KAFKA_VERSION} $KAFKA_DIR
    echo -e "${GREEN}Kafka installed${NC}"
else
    echo -e "${GREEN}Kafka already installed${NC}"
fi

# Step 5: Install Spark
echo -e "${YELLOW}[5/6] Installing Apache Spark...${NC}"
SPARK_VERSION="3.5.0"
SPARK_DIR="/opt/spark"
if [ ! -d "$SPARK_DIR" ]; then
    cd /tmp
    wget https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop3.tgz
    mv spark-${SPARK_VERSION}-bin-hadoop3 $SPARK_DIR
    echo -e "${GREEN}Spark installed${NC}"
else
    echo -e "${GREEN}Spark already installed${NC}"
fi

# Step 6: Install PHP and Apache
echo -e "${YELLOW}[6/6] Installing PHP and Apache...${NC}"
apt-get install -y apache2 php php-mysql php-curl php-json composer

echo -e "${GREEN}=========================================="
echo "Production setup completed!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Configure MySQL database (see deploy/setup_mysql.sh)"
echo "2. Configure Kafka (see deploy/setup_kafka.sh)"
echo "3. Configure Spark (see deploy/setup_spark.sh)"
echo "4. Update .env file with credentials"
echo "5. Start services (see deploy/start_services.sh)"

