"""
RailSewa - RDS Database Connection Test (Local)
"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# ============================================
# RDS Database Configuration
# ============================================
RDS_ENDPOINT = "railway-db.cqtm4ssyoba3.us-east-1.rds.amazonaws.com"
RDS_PORT = 3306
RDS_DATABASE = "twitter"

def test_connection():
    """Test database connection"""
    print("=" * 60)
    print("RailSewa Database Connection Test")
    print("=" * 60)
    print(f"\nEndpoint: {RDS_ENDPOINT}")
    print(f"Port: {RDS_PORT}")
    print(f"Database: {RDS_DATABASE}\n")
    
    # Get credentials from environment
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    # Validate environment variables
    if not db_user:
        print("❌ ERROR: DB_USER not found in .env")
        return False

    if not db_password:
        print("❌ ERROR: DB_PASSWORD not found in .env")
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
        print("✅ Connection successful!\n")
        
        cursor = conn.cursor()

        # Test 1: MySQL Version
        print("Test 1: MySQL Version")
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"   ✅ MySQL Version: {version}\n")

        # Test 2: List Databases
        print("Test 2: Databases in RDS")
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        print(f"   Databases: {databases}")
        if RDS_DATABASE in databases:
            print(f"   ✅ Database '{RDS_DATABASE}' exists\n")
        else:
            print(f"   ❌ Database '{RDS_DATABASE}' NOT found!\n")

        # Test 3: List Tables
        print("Test 3: Tables in 'twitter'")
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"   Tables: {tables}\n")

        # Test 4: Table Structure (tweets)
        if "tweets" in tables:
            print("Test 4: Structure of 'tweets'")
            cursor.execute("DESCRIBE tweets")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col[0]} ({col[1]})")
            print()
        else:
            print("❌ 'tweets' table not found\n")

        # Test 5: Record Count
        if "tweets" in tables:
            print("Test 5: Record Count in 'tweets'")
            cursor.execute("SELECT COUNT(*) FROM tweets")
            count = cursor.fetchone()[0]
            print(f"   ✅ Records found: {count}\n")

        conn.close()
        print("=" * 60)
        print("✅ All tests completed successfully.")
        print("=" * 60)
        return True

    except pymysql.MySQLError as e:
        print(f"❌ MySQL Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check RDS endpoint")
        print("2. Check your username/password in .env")
        print("3. Ensure your IP is allowed in RDS security group")
        print("4. Ensure RDS instance status = 'Available'")
        return False

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("\nTroubleshooting:")
        print("1. Internet connection")
        print("2. RDS accessibility")
        print("3. Firewall issues")
        return False

if __name__ == "__main__":
    test_connection()
    if not success:
        exit(1)
    else:
        print("✅ All tests completed successfully.")
        exit(0)
