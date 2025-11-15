# 🗄️ MySQL Database Setup - Step by Step Guide

## 📋 Overview

This guide will help you set up MySQL database for RailSewa project. You can use either:
- **Local MySQL** (for development/testing)
- **AWS RDS** (for production)

---

## ☁️ AWS RDS Setup

### **Step 1: Verify RDS Instance**

1. Go to **AWS Console** → **RDS**
2. Find your database instance
3. Verify status is **"Available"**
4. Copy your endpoint (e.g., `your-db.xxxxx.us-east-1.rds.amazonaws.com`)
5. Note your master username (usually `admin`)
6. Have your master password ready

---

### **Step 2: Configure Security Group**

**IMPORTANT:** Before connecting, allow access to RDS:

1. Go to **EC2 Console** → **Security Groups**
2. Find the security group attached to your RDS instance
3. Click **"Edit inbound rules"**
4. Click **"Add rule"**
5. Configure:
   - **Type**: MySQL/Aurora
   - **Port**: 3306
   - **Source**: 
     - For EC2: Select your **EC2 security group**
     - For CloudShell: Your **IP address** (0.0.0.0/0 for testing - not recommended for production)
6. Click **"Save rules"**

---

### **Step 3: Test Connection**

#### **Option A: From AWS EC2 Instance**

```bash
# Connect to your EC2 instance
ssh -i your-key.pem ec2-user@your-ec2-ip

# Install MySQL client (if not installed)
sudo yum install mysql -y  # Amazon Linux
# or
sudo apt-get install mysql-client -y  # Ubuntu

# Test connection (replace with your endpoint)
mysql -h your-endpoint.rds.amazonaws.com -u admin -p -e "SELECT VERSION();"
```

#### **Option B: From AWS CloudShell**

1. Open **AWS CloudShell** (icon in top right of AWS Console)
2. Run:
```bash
mysql -h your-endpoint.rds.amazonaws.com -u admin -p -e "SELECT VERSION();"
```

#### **Option C: Using AWS RDS Query Editor**

1. Go to **RDS Console** → Click your database instance
2. Click **"Query Editor"** tab
3. Connect with:
   - Database: `twitter`
   - Username: `admin`
   - Password: Your RDS master password
4. Run: `SELECT VERSION();`

---

### **Step 4: Create Database (if not exists)**

If the `twitter` database doesn't exist, create it:

#### **From Command Line:**
```bash
mysql -h your-endpoint.rds.amazonaws.com -u admin -p -e "CREATE DATABASE IF NOT EXISTS twitter;"
```

#### **From Query Editor:**
```sql
CREATE DATABASE IF NOT EXISTS twitter;
USE twitter;
```

---

### **Step 5: Verify Database**

```bash
mysql -h your-endpoint.rds.amazonaws.com -u admin -p -e "SHOW DATABASES;"
```

You should see `twitter` in the list.

---

### **Step 6: Get Schema File Ready**

Make sure you have the schema file. It should be at: `database/schema.sql`

If you're on EC2, upload it:
```bash
# From your local machine
scp -i your-key.pem database/schema.sql ec2-user@your-ec2-ip:~/
```

Or clone your repository on EC2:
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

---

## 🚀 Step 7: Run Database Schema

This will create all necessary tables (`tweets`, `admin`) and indexes.

### **Method 1: Using Python in CloudShell (Recommended if MySQL hangs)**

If `mysql` command hangs after entering password, use Python instead:

```bash
# In CloudShell, install PyMySQL
pip3 install pymysql

# First, upload schema.sql to CloudShell or clone your repo
# Then run the schema using Python script
python3 run_schema_cloudshell.py
```

**Note:** Update `run_schema_cloudshell.py` with your RDS endpoint before running.

This script:
- ✅ Works even if MySQL client has issues
- ✅ Shows clear error messages
- ✅ Verifies tables after execution
- ✅ Handles connection timeouts properly

**When prompted, enter your RDS master password.**

---

### **Method 2: From AWS EC2 Instance**

```bash
# From your EC2 instance (replace with your endpoint)
mysql -h your-endpoint.rds.amazonaws.com -u admin -p twitter < database/schema.sql
```

**When prompted, enter your RDS master password.**

> **⚠️ Note**: If MySQL command hangs in CloudShell, use Method 1 (Python) or Method 3 (Query Editor) instead!

---

### **Method 2: Using AWS RDS Query Editor (Easiest - No Installation)**

1. Go to **AWS Console** → **RDS** → Your database instance
2. Click **"Query Editor"** tab
3. Connect:
   - Database: `twitter`
   - Username: `admin`
   - Password: Your RDS master password
4. Open `database/schema.sql` file from your project
5. **Copy all SQL content** from the file
6. **Paste into Query Editor**
7. Click **"Run"** button
8. Wait for execution to complete

**This method doesn't require MySQL client installation!**

---

### **Method 3: Using Python Script**

If you have Python on your EC2 or local machine:

```python
import pymysql
import getpass

# Get password
password = getpass.getpass("Enter RDS password: ")

# Read schema file
with open('database/schema.sql', 'r', encoding='utf-8') as f:
    schema = f.read()

# Connect and execute
conn = pymysql.connect(
    host='your-endpoint.rds.amazonaws.com',  # Replace with your RDS endpoint
    user='admin',
    password=password,
    database='twitter'
)

cursor = conn.cursor()

# Execute each statement
for statement in schema.split(';'):
    statement = statement.strip()
    if statement and not statement.startswith('--'):
        try:
            cursor.execute(statement)
        except Exception as e:
            print(f"Warning: {e}")

conn.commit()
print("✅ Schema executed successfully!")
conn.close()
```

Save as `run_schema.py` and run:
```bash
python run_schema.py
```

---

### **What Step 7 Does:**

- ✅ Creates `tweets` table (stores Telegram complaints)
- ✅ Creates `admin` table (stores admin users)
- ✅ Creates `tweet_stats` view (for statistics)
- ✅ Sets up all indexes for performance
- ✅ Inserts default admin user

---

## 📝 Step 8: Update .env File

Update your `.env` file with your RDS credentials:

```bash
# Database Configuration
# For AWS RDS:
DB_HOST=your-endpoint.rds.amazonaws.com
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=your_master_password_here
DB_NAME=twitter

# For Local MySQL:
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=railsewa
# DB_PASSWORD=your_local_password
# DB_NAME=twitter
```

**⚠️ Important:** Replace `your_master_password_here` with your actual RDS master password!

---

## ✅ Step 9: Verify Tables Created

### **From Command Line:**
```bash
mysql -h your-endpoint.rds.amazonaws.com -u admin -p twitter -e "SHOW TABLES;"
```

You should see:
- `tweets`
- `admin`

### **From Query Editor:**
```sql
USE twitter;
SHOW TABLES;
```

### **Check Table Structure:**
```bash
mysql -h your-endpoint.rds.amazonaws.com -u admin -p twitter -e "DESCRIBE tweets;"
```

---

## 🧪 Step 10: Test Database Connection

### **Using Python Test Script**

Create `test_db.py`:

```python
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

RDS_ENDPOINT = "your-endpoint.rds.amazonaws.com"  # Replace with your RDS endpoint
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
```

Run it:
```bash
python test_db.py
```

---

## ✅ Verification Checklist

After completing all steps:

- [ ] RDS instance is "Available" status
- [ ] Security group allows connections (EC2 security group or your IP)
- [ ] Can connect via `mysql` command or Query Editor
- [ ] Database `twitter` exists
- [ ] Schema file executed successfully
- [ ] Tables `tweets` and `admin` exist
- [ ] `.env` file updated with correct credentials
- [ ] `python test_db.py` shows all tests passing

---

## 🆘 Troubleshooting

### **Can't connect to RDS?**

**Check these:**

1. **Security Group:**
   - Go to EC2 → Security Groups
   - Find your RDS security group
   - Verify inbound rule allows MySQL/Aurora on port 3306
   - Source should be your EC2 security group (for EC2) or your IP (for CloudShell)

2. **RDS Status:**
   - Go to RDS Console
   - Check instance status is "Available"
   - Wait if it's "Creating" or "Modifying"

3. **Endpoint:**
   - Verify endpoint is correct
   - No typos in the address

4. **Credentials:**
   - Username: `admin` (or what you set)
   - Password: Your master password

---

### **Access denied error?**

- Verify username is `admin`
- Check password is correct (case-sensitive)
- Try resetting password in RDS Console if needed

---

### **Database doesn't exist?**

Create it:
```sql
CREATE DATABASE IF NOT EXISTS twitter;
```

Or from command line:
```bash
mysql -h your-endpoint.rds.amazonaws.com -u admin -p -e "CREATE DATABASE IF NOT EXISTS twitter;"
```

---

### **Tables not created?**

- Re-run schema: `mysql -h your-endpoint.rds.amazonaws.com -u admin -p twitter < database/schema.sql`
- Check for errors in output
- Verify you're connected to correct database

---

### **Schema execution fails?**

**Common issues:**

1. **File not found:**
   - Verify `database/schema.sql` exists
   - Check you're in project root directory

2. **Permission errors:**
   - Ensure user `admin` has CREATE privileges
   - RDS master user should have all privileges

3. **Syntax errors:**
   - Check schema file is valid SQL
   - Try running in Query Editor to see specific errors

---

## 📚 Additional Resources

- **MySQL Documentation**: https://dev.mysql.com/doc/
- **AWS RDS Documentation**: https://docs.aws.amazon.com/rds/
- **PyMySQL Documentation**: https://pymysql.readthedocs.io/
- **RDS Query Editor Guide**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/query-editor.html

---

## 🎉 Success!

Once you complete these steps, your database is ready! The RailSewa project can now:

- ✅ Store complaints from Telegram Bot
- ✅ Track emergency vs feedback classifications
- ✅ Store admin responses
- ✅ Generate real-time statistics
- ✅ Handle multiple users and complaints

---

## 🚀 Next Steps

After database setup is complete:

1. **Configure Telegram Bot:**
   - Get bot token from @BotFather
   - Add to `.env`: `TELEGRAM_BOT_TOKEN=your_token`

2. **Setup Kafka (if using):**
   - See `SETUP_KAFKA.md` for instructions

3. **Start Application:**
   ```bash
   # Start Telegram Bot
   python kafka_file/telegram_stream.py
   
   # Start Spark Processing (if using)
   spark-submit new_live_processing.py
   
   # Start Web Dashboard
   cd railways
   php -S localhost:8000
   ```

4. **Test Full Pipeline:**
   - Send message to Telegram Bot
   - Check it appears in database
   - View in web dashboard

---

## 📝 Configuration Summary

**For AWS RDS:**
```
Endpoint: your-endpoint.rds.amazonaws.com
Port: 3306
Username: admin (or your master username)
Database: twitter
```

**For Local MySQL:**
```
Host: localhost
Port: 3306
Username: railsewa
Database: twitter
```

**Keep this information secure and update your `.env` file!**

---

**Your database setup is complete!** 🚂

