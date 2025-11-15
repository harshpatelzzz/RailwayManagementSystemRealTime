#!/bin/bash
# Kafka Setup Script

set -e

KAFKA_DIR="/opt/kafka"
ZOOKEEPER_DIR="/opt/zookeeper"

echo "=========================================="
echo "Kafka Setup"
echo "=========================================="

# Start Zookeeper
echo "[1/3] Starting Zookeeper..."
$ZOOKEEPER_DIR/bin/zkServer.sh start
sleep 5

# Start Kafka
echo "[2/3] Starting Kafka..."
nohup $KAFKA_DIR/bin/kafka-server-start.sh $KAFKA_DIR/config/server.properties > /var/log/kafka.log 2>&1 &
sleep 10

# Create topic
echo "[3/3] Creating Kafka topic..."
$KAFKA_DIR/bin/kafka-topics.sh --create \
    --zookeeper localhost:2181 \
    --topic twitterstream \
    --partitions 1 \
    --replication-factor 1 \
    --if-not-exists

echo "=========================================="
echo "Kafka setup completed!"
echo "=========================================="
echo "Zookeeper: Running on port 2181"
echo "Kafka: Running on port 9092"
echo "Topic: twitterstream created"
echo ""
echo "To verify:"
echo "  $KAFKA_DIR/bin/kafka-topics.sh --list --zookeeper localhost:2181"

