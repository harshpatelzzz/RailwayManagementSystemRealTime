"""
Test Database Connection Script
Tests connection to RDS MySQL database
"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
# Update these values with your database details
# For AWS RDS:
RDS_ENDPOINT = "your-endpoint.rds.amazonaws.com"  # Replace with your RDS endpoint
# For Local MySQL:
# RDS_ENDPOINT = "localhost"
RDS_PORT = 3306
RDS_DATABASE = "twitter"

def test_connection():
    """Test database connection"""
    print("=" * 60)
    print("RailSewa Database Connection Test")
    print("=" * 60)
    print(f"\nEndpoint: {RDS_ENDPOINT}")
    print(f"Port: {RDS_PORT}")
    print(f"Database: {RDS_DATABASE}")
    print()
    
    # Get credentials from .env or use defaults
    db_user = os.getenv('DB_USER', 'admin')
    db_password = os.getenv('DB_PASSWORD', '')
    
    if not db_password:
        print("⚠️  Warning: DB_PASSWORD not found in .env file")
        print("   Please update .env file with your RDS password")
        db_password = input("Enter password (or press Enter to skip): ").strip()
        if not db_password:
            print("❌ Cannot test without password")
            return False
    
    try:
        print("Connecting to database...")
        conn = pymysql.connect(
            host=RDS_ENDPOINT,
            port=RDS_PORT,
            user=db_user,
            password=db_password,
            database=RDS_DATABASE,
            connect_timeout=10
        )
        print("✅ Connection successful!")
        print()
        
        cursor = conn.cursor()
        
        # Test 1: Check MySQL version
        print("Test 1: MySQL Version")
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"   ✅ MySQL Version: {version}")
        print()
        
        # Test 2: Check databases
        print("Test 2: Available Databases")
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        print(f"   ✅ Found {len(databases)} databases")
        if RDS_DATABASE in databases:
            print(f"   ✅ Database '{RDS_DATABASE}' exists")
        else:
            print(f"   ❌ Database '{RDS_DATABASE}' not found!")
        print()
        
        # Test 3: Check tables
        print("Test 3: Tables in 'twitter' database")
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"   ✅ Found {len(tables)} tables")
        for table in tables:
            print(f"      - {table}")
        
        if 'tweets' in tables:
            print("   ✅ 'tweets' table exists")
        else:
            print("   ❌ 'tweets' table not found!")
        
        if 'admin' in tables:
            print("   ✅ 'admin' table exists")
        else:
            print("   ❌ 'admin' table not found!")
        print()
        
        # Test 4: Check table structure
        if 'tweets' in tables:
            print("Test 4: 'tweets' table structure")
            cursor.execute("DESCRIBE tweets")
            columns = cursor.fetchall()
            print(f"   ✅ Table has {len(columns)} columns:")
            for col in columns[:5]:  # Show first 5 columns
                print(f"      - {col[0]} ({col[1]})")
            if len(columns) > 5:
                print(f"      ... and {len(columns) - 5} more columns")
            print()
        
        # Test 5: Count records
        if 'tweets' in tables:
            print("Test 5: Record count")
            cursor.execute("SELECT COUNT(*) FROM tweets")
            count = cursor.fetchone()[0]
            print(f"   ✅ Found {count} records in 'tweets' table")
            print()
        
        conn.close()
        print("=" * 60)
        print("✅ All tests passed! Database is ready.")
        print("=" * 60)
        return True
        
    except pymysql.Error as e:
        print(f"❌ MySQL Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check RDS endpoint is correct")
        print("2. Verify security group allows your IP")
        print("3. Check username and password in .env")
        print("4. Ensure RDS instance is 'Available' status")
        return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check internet connection")
        print("2. Verify RDS endpoint is accessible")
        print("3. Check firewall settings")
        return False

if __name__ == "__main__":
    success = test_connection()
    if not success:
        exit(1)

