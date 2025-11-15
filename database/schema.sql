-- RailSewa Database Schema
-- Create this database on your AWS RDS instance

CREATE DATABASE IF NOT EXISTS twitter;
USE twitter;

-- Tweets table
CREATE TABLE IF NOT EXISTS tweets (
    id int AUTO_INCREMENT PRIMARY KEY,
    tweet varchar(280) NOT NULL,
    username varchar(50),
    pnr bigint(10),
    prediction int(1) DEFAULT 0 COMMENT '0=Feedback, 1=Emergency',
    tweet_id bigint(10) UNIQUE,
    latitude decimal(10,8),
    longitude decimal(11,8),
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_status int(1) DEFAULT 0 COMMENT '0=Not Responded, 1=Responded',
    response varchar(280),
    INDEX idx_prediction (prediction),
    INDEX idx_response_status (response_status),
    INDEX idx_time (time),
    INDEX idx_tweet_id (tweet_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Admin table
CREATE TABLE IF NOT EXISTS admin (
    id int AUTO_INCREMENT PRIMARY KEY,
    username varchar(50) UNIQUE NOT NULL,
    password varchar(255) NOT NULL,
    email varchar(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default admin (password: admin123 - change this!)
-- Password should be hashed using password_hash() in PHP
INSERT INTO admin (username, password, email) 
VALUES ('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin@railsewa.com')
ON DUPLICATE KEY UPDATE username=username;

-- Statistics view
CREATE OR REPLACE VIEW tweet_stats AS
SELECT 
    COUNT(*) as total_tweets,
    SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as emergency_count,
    SUM(CASE WHEN prediction = 0 THEN 1 ELSE 0 END) as feedback_count,
    SUM(CASE WHEN response_status = 1 THEN 1 ELSE 0 END) as responded_count,
    SUM(CASE WHEN response_status = 0 THEN 1 ELSE 0 END) as pending_count
FROM tweets;

