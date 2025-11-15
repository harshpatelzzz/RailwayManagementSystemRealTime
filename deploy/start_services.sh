#!/bin/bash
# Start All Services Script

set -e

echo "=========================================="
echo "Starting RailSewa Services"
echo "=========================================="

ZOOKEEPER_DIR="/opt/zookeeper"
KAFKA_DIR="/opt/kafka"
SPARK_DIR="/opt/spark"
PROJECT_DIR=$(pwd)

# Start Zookeeper
echo "[1/5] Starting Zookeeper..."
$ZOOKEEPER_DIR/bin/zkServer.sh start
sleep 3

# Start Kafka
echo "[2/5] Starting Kafka..."
nohup $KAFKA_DIR/bin/kafka-server-start.sh $KAFKA_DIR/config/server.properties > /var/log/kafka.log 2>&1 &
sleep 5

# Start Spark
echo "[3/5] Starting Spark..."
$SPARK_DIR/sbin/start-master.sh
sleep 3
$SPARK_DIR/sbin/start-worker.sh spark://localhost:7077
sleep 3

# Start Twitter Stream
echo "[4/5] Starting Twitter Stream..."
cd $PROJECT_DIR
source .env
nohup python kafka_file/stream_data.py > /var/log/twitter_stream.log 2>&1 &
sleep 2

# Start Spark Processing
echo "[5/5] Starting Spark Processing..."
nohup $SPARK_DIR/bin/spark-submit \
    --master spark://localhost:7077 \
    --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.0 \
    new_live_processing.py > /var/log/spark_processing.log 2>&1 &

echo "=========================================="
echo "All services started!"
echo "=========================================="
echo "Zookeeper: Running"
echo "Kafka: Running"
echo "Spark: Running"
echo "Twitter Stream: Running"
echo "Spark Processing: Running"
echo ""
echo "Check logs:"
echo "  tail -f /var/log/twitter_stream.log"
echo "  tail -f /var/log/spark_processing.log"
echo "  tail -f /var/log/kafka.log"

