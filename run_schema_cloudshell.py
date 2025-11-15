#!/usr/bin/env python3
"""
RDS Schema Runner for AWS CloudShell
Runs database schema without needing MySQL client
"""

import pymysql
import getpass
import sys
import os

# RDS Configuration
# Update these values with your RDS details
RDS_ENDPOINT = "your-endpoint.rds.amazonaws.com"  # Replace with your RDS endpoint
RDS_USER = "admin"  # Replace with your RDS master username
RDS_DATABASE = "twitter"
SCHEMA_FILE = "database/schema.sql"

def main():
    print("=" * 60)
    print("RailSewa RDS Schema Setup - CloudShell")
    print("=" * 60)
    print(f"\nEndpoint: {RDS_ENDPOINT}")
    print(f"Database: {RDS_DATABASE}")
    print(f"User: {RDS_USER}")
    print()
    
    # Get password
    try:
        password = getpass.getpass("Enter RDS password: ")
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
    
    if not password:
        print("❌ Password cannot be empty")
        sys.exit(1)
    
    # Check if schema file exists
    if not os.path.exists(SCHEMA_FILE):
        print(f"❌ Schema file not found: {SCHEMA_FILE}")
        print("\nOptions:")
        print("1. Upload schema.sql to CloudShell")
        print("2. Clone your repository: git clone <your-repo>")
        print("3. Create file manually: nano database/schema.sql")
        sys.exit(1)
    
    # Read schema file
    try:
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
            schema = f.read()
        print(f"✅ Schema file loaded: {SCHEMA_FILE}")
    except Exception as e:
        print(f"❌ Error reading schema file: {e}")
        sys.exit(1)
    
    # Connect to RDS
    print("\nConnecting to RDS...")
    try:
        conn = pymysql.connect(
            host=RDS_ENDPOINT,
            user=RDS_USER,
            password=password,
            database=RDS_DATABASE,
            connect_timeout=10,
            read_timeout=30,
            write_timeout=30
        )
        print("✅ Connected to RDS!")
    except pymysql.Error as e:
        print(f"❌ MySQL Connection Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check security group allows CloudShell IP")
        print("2. Verify endpoint is correct")
        print("3. Check username and password")
        print("4. Ensure RDS instance is 'Available'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("\nPossible issues:")
        print("- Security group blocking connection")
        print("- Network timeout")
        print("- RDS instance not accessible")
        sys.exit(1)
    
    # Execute schema
    print("\nExecuting schema...")
    cursor = conn.cursor()
    
    # Split schema into statements
    statements = [s.strip() for s in schema.split(';') if s.strip() and not s.strip().startswith('--')]
    
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        if not statement:
            continue
            
        try:
            cursor.execute(statement)
            success_count += 1
            if i % 5 == 0:  # Progress indicator
                print(f"  Processed {i}/{len(statements)} statements...")
        except pymysql.Error as e:
            error_msg = str(e)
            # Ignore "already exists" errors (table/view might already exist)
            if "already exists" not in error_msg.lower() and "duplicate" not in error_msg.lower():
                print(f"  ⚠️  Statement {i} error: {error_msg}")
                error_count += 1
            else:
                # Table/view already exists - this is OK
                success_count += 1
    
    # Commit changes
    try:
        conn.commit()
        print(f"\n✅ Schema execution complete!")
        print(f"   Successful: {success_count}")
        if error_count > 0:
            print(f"   Errors: {error_count} (some may be expected)")
    except Exception as e:
        print(f"❌ Commit error: {e}")
        conn.rollback()
        conn.close()
        sys.exit(1)
    
    # Verify tables
    print("\nVerifying tables...")
    try:
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table}")
        
        # Check required tables
        required = ['tweets', 'admin']
        missing = [t for t in required if t not in tables]
        
        if missing:
            print(f"\n⚠️  Missing tables: {missing}")
        else:
            print("\n✅ All required tables exist!")
        
        # Check record count
        cursor.execute("SELECT COUNT(*) FROM tweets")
        count = cursor.fetchone()[0]
        print(f"✅ Records in 'tweets' table: {count}")
        
    except Exception as e:
        print(f"⚠️  Verification error: {e}")
    
    # Close connection
    conn.close()
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update .env file with your RDS password")
    print("2. Test connection: python test_db.py")
    print("3. Start your application")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

