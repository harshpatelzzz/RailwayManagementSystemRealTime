#!/bin/bash
# MySQL Database Setup Script

set -e

echo "=========================================="
echo "MySQL Database Setup"
echo "=========================================="

# Read database credentials
read -p "Enter MySQL root password: " MYSQL_ROOT_PASSWORD
read -p "Enter database name [twitter]: " DB_NAME
DB_NAME=${DB_NAME:-twitter}
read -p "Enter database user [railsewa]: " DB_USER
DB_USER=${DB_USER:-railsewa}
read -p "Enter database password: " DB_PASSWORD

# Create database and user
mysql -u root -p${MYSQL_ROOT_PASSWORD} <<EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME};
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

# Run schema
echo "Creating tables..."
mysql -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME} < ../database/schema.sql

echo "=========================================="
echo "MySQL setup completed!"
echo "=========================================="
echo "Database: ${DB_NAME}"
echo "User: ${DB_USER}"
echo ""
echo "Update .env file with these credentials:"
echo "DB_HOST=localhost"
echo "DB_USER=${DB_USER}"
echo "DB_PASSWORD=${DB_PASSWORD}"
echo "DB_NAME=${DB_NAME}"

