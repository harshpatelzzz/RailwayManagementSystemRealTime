<?php
/**
 * Database Configuration
 * Update these values with your AWS RDS credentials
 */

// Load from environment variables or use defaults
define('DB_HOST', getenv('DB_HOST') ?: (getenv('MYSQL_HOST') ?: 'localhost'));
define('DB_PORT', getenv('DB_PORT') ?: (getenv('MYSQL_PORT') ?: '3306'));
define('DB_USER', getenv('DB_USER') ?: (getenv('MYSQL_USER') ?: 'railsewa'));
define('DB_PASSWORD', getenv('DB_PASSWORD') ?: (getenv('MYSQL_PASSWORD') ?: ''));
define('DB_NAME', getenv('DB_NAME') ?: (getenv('MYSQL_DATABASE') ?: 'twitter'));

// Telegram Bot Configuration
define('TELEGRAM_BOT_TOKEN', getenv('TELEGRAM_BOT_TOKEN') ?: '');

// Application Configuration
define('APP_NAME', 'RailSewa - Indian Railways Complaint Management');
define('TIMEZONE', 'Asia/Kolkata');
date_default_timezone_set(TIMEZONE);

// Database Connection Function
function getDBConnection() {
    try {
        $conn = new mysqli(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT);
        
        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }
        
        $conn->set_charset("utf8mb4");
        return $conn;
    } catch (Exception $e) {
        die("Database connection error: " . $e->getMessage());
    }
}

?>

