#!/bin/bash
# Service Status Check Script

echo "=========================================="
echo "RailSewa Services Status"
echo "=========================================="

# Check MySQL
echo -n "MySQL: "
if systemctl is-active --quiet mysql; then
    echo -e "\033[0;32mRUNNING\033[0m"
else
    echo -e "\033[0;31mSTOPPED\033[0m"
fi

# Check Zookeeper
echo -n "Zookeeper: "
if pgrep -f "zookeeper" > /dev/null; then
    echo -e "\033[0;32mRUNNING\033[0m"
else
    echo -e "\033[0;31mSTOPPED\033[0m"
fi

# Check Kafka
echo -n "Kafka: "
if pgrep -f "kafka-server-start" > /dev/null; then
    echo -e "\033[0;32mRUNNING\033[0m"
else
    echo -e "\033[0;31mSTOPPED\033[0m"
fi

# Check Spark Master
echo -n "Spark Master: "
if pgrep -f "spark.*master" > /dev/null; then
    echo -e "\033[0;32mRUNNING\033[0m"
else
    echo -e "\033[0;31mSTOPPED\033[0m"
fi

# Check Spark Worker
echo -n "Spark Worker: "
if pgrep -f "spark.*worker" > /dev/null; then
    echo -e "\033[0;32mRUNNING\033[0m"
else
    echo -e "\033[0;31mSTOPPED\033[0m"
fi

# Check Twitter Stream
echo -n "Twitter Stream: "
if pgrep -f "stream_data.py" > /dev/null; then
    echo -e "\033[0;32mRUNNING\033[0m"
else
    echo -e "\033[0;31mSTOPPED\033[0m"
fi

# Check Spark Processing
echo -n "Spark Processing: "
if pgrep -f "spark-submit.*new_live_processing" > /dev/null; then
    echo -e "\033[0;32mRUNNING\033[0m"
else
    echo -e "\033[0;31mSTOPPED\033[0m"
fi

# Check Apache
echo -n "Apache Web Server: "
if systemctl is-active --quiet apache2; then
    echo -e "\033[0;32mRUNNING\033[0m"
else
    echo -e "\033[0;31mSTOPPED\033[0m"
fi

echo "=========================================="

