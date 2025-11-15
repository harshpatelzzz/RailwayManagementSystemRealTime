#!/bin/bash
# Stop All Services Script

echo "=========================================="
echo "Stopping RailSewa Services"
echo "=========================================="

ZOOKEEPER_DIR="/opt/zookeeper"
KAFKA_DIR="/opt/kafka"
SPARK_DIR="/opt/spark"

# Stop Spark Processing
echo "[1/5] Stopping Spark Processing..."
pkill -f "spark-submit.*new_live_processing.py" || true

# Stop Twitter Stream
echo "[2/5] Stopping Twitter Stream..."
pkill -f "stream_data.py" || true

# Stop Spark
echo "[3/5] Stopping Spark..."
$SPARK_DIR/sbin/stop-worker.sh || true
$SPARK_DIR/sbin/stop-master.sh || true

# Stop Kafka
echo "[4/5] Stopping Kafka..."
pkill -f "kafka-server-start" || true

# Stop Zookeeper
echo "[5/5] Stopping Zookeeper..."
$ZOOKEEPER_DIR/bin/zkServer.sh stop || true

echo "=========================================="
echo "All services stopped!"
echo "=========================================="

