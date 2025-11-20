-- Migration: Add Analytics Columns to tweets table
-- Run this migration to add support for analytics features
-- 
-- These columns are optional - the application will work without them,
-- but analytics features will be enhanced with these columns.

USE twitter;

-- Add train_number column (extracted from complaint text)
ALTER TABLE tweets 
ADD COLUMN IF NOT EXISTS train_number VARCHAR(10) NULL 
COMMENT 'Train number extracted from complaint text' 
AFTER pnr;

-- Add delay_minutes column (extracted delay information)
ALTER TABLE tweets 
ADD COLUMN IF NOT EXISTS delay_minutes INT NULL 
COMMENT 'Delay in minutes extracted from complaint text' 
AFTER train_number;

-- Add severity_label column (low/medium/high)
ALTER TABLE tweets 
ADD COLUMN IF NOT EXISTS severity_label VARCHAR(10) NULL 
COMMENT 'Severity label: low, medium, or high' 
AFTER delay_minutes;

-- Add severity_score column (0.0 to 1.0)
ALTER TABLE tweets 
ADD COLUMN IF NOT EXISTS severity_score DECIMAL(3,2) NULL 
COMMENT 'Severity score from 0.0 (low) to 1.0 (high)' 
AFTER severity_label;

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_train_number ON tweets(train_number);
CREATE INDEX IF NOT EXISTS idx_severity_label ON tweets(severity_label);
CREATE INDEX IF NOT EXISTS idx_delay_minutes ON tweets(delay_minutes);

-- Note: If your MySQL version doesn't support IF NOT EXISTS in ALTER TABLE,
-- you may need to check if columns exist first or handle errors gracefully.
-- 
-- For MySQL 8.0+, you can use:
-- ALTER TABLE tweets ADD COLUMN train_number VARCHAR(10) NULL COMMENT '...' AFTER pnr;
-- 
-- For older versions, wrap in try-catch or check information_schema first.

