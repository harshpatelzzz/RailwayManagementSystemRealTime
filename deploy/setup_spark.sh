#!/bin/bash
# Spark Cluster Setup Script

set -e

SPARK_DIR="/opt/spark"
SPARK_HOME=${SPARK_DIR}

echo "=========================================="
echo "Spark Cluster Setup"
echo "=========================================="

# Set environment variables
export SPARK_HOME=$SPARK_DIR
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

# Create Spark directories
mkdir -p $SPARK_HOME/work
mkdir -p $SPARK_HOME/logs

# Configure Spark (standalone mode)
echo "[1/3] Configuring Spark..."
cat > $SPARK_HOME/conf/spark-env.sh <<EOF
export SPARK_MASTER_HOST=localhost
export SPARK_WORKER_CORES=2
export SPARK_WORKER_MEMORY=2g
EOF

# Start Spark Master
echo "[2/3] Starting Spark Master..."
$SPARK_HOME/sbin/start-master.sh
sleep 5

# Start Spark Worker
echo "[3/3] Starting Spark Worker..."
$SPARK_HOME/sbin/start-worker.sh spark://localhost:7077
sleep 5

echo "=========================================="
echo "Spark setup completed!"
echo "=========================================="
echo "Spark Master: http://localhost:8080"
echo "Spark Worker: Connected"
echo ""
echo "To verify:"
echo "  curl http://localhost:8080"
echo ""
echo "To submit jobs:"
echo "  $SPARK_HOME/bin/spark-submit --master spark://localhost:7077 train_model.py"

