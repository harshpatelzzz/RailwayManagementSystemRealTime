# How to Run RailSewa Project

## ✅ Quick Start (Local - No Infrastructure Required)

The easiest way to run the project right now:

```bash
python run_local.py
```

This will:
- Process 10 sample tweets
- Classify them as Emergency/Feedback
- Extract PNR numbers
- Display a dashboard with statistics
- Show recent tweets

**Status**: ✅ **WORKING NOW** - No setup required!

## 🎯 Different Ways to Run

### 1. Local Demo (Works Immediately)
```bash
# Simple functionality demo
python demo.py

# Full local system simulation
python run_local.py
```

### 2. Test Components
```bash
# Test all components and imports
python test_project.py
```

### 3. Full Production System (Requires Setup)

For the complete system with real-time Twitter streaming:

#### Prerequisites:
1. **MySQL Database**
   - Install MySQL or use AWS RDS
   - Run: `database/schema.sql` to create tables
   - Update `.env` with database credentials

2. **Kafka & Zookeeper**
   - Install Apache Kafka
   - Install Apache Zookeeper
   - Start Zookeeper: `zkServer.sh start`
   - Start Kafka: `bin/kafka-server-start.sh config/server.properties &`
   - Create topic: `bin/kafka-topics.sh --create --zookeeper localhost:2181 --topic twitterstream`

3. **Twitter API**
   - Get API credentials from Twitter Developer Portal
   - Update `.env` with your Twitter API keys

4. **Spark (Optional)**
   - Install Apache Spark
   - Install Java JDK 8+
   - Setup Spark cluster

#### Running Full System:

**Step 1: Start Twitter Streaming**
```bash
python kafka_file/stream_data.py &
```

**Step 2: Train Model (One-time)**
```bash
spark-submit train_model.py
```

**Step 3: Start Live Processing**
```bash
spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.0 new_live_processing.py
```

**Step 4: Start Web Interface**
```bash
# Using XAMPP
sudo /opt/lampp/lampp start

# Or PHP built-in server
cd railways
php -S localhost:8000
```

Then open: `http://localhost:8000/index.php`

## 📊 Current Status

| Component | Status | Command |
|-----------|--------|---------|
| Local Demo | ✅ Working | `python demo.py` |
| Local System | ✅ Working | `python run_local.py` |
| Component Test | ✅ Working | `python test_project.py` |
| Full System | ⚠️ Needs Setup | See above |

## 🚀 What's Working Right Now

✅ **Tweet Processing**
- Text cleaning
- PNR extraction
- Classification (Emergency/Feedback)
- Statistics tracking

✅ **Core Functions**
- All processing logic works
- No infrastructure needed for testing

✅ **Project Structure**
- All files created and organized
- Ready for production deployment

## 📝 Next Steps

### For Testing/Development:
1. Run `python run_local.py` to see it work
2. Modify sample tweets in `run_local.py` to test different scenarios
3. Use interactive mode to test responses

### For Production:
1. Follow `QUICKSTART.md` for step-by-step setup
2. Configure `.env` file with real credentials
3. Setup infrastructure (MySQL, Kafka, Spark)
4. Deploy to AWS EC2/RDS

## 🔧 Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt
```

### Spark Not Working
- Install Java JDK first
- Then: `pip install pyspark`

### Database Connection
- Check MySQL is running
- Verify credentials in `.env`
- Test: `mysql -h host -u user -p`

### Kafka Issues
- Verify Zookeeper is running
- Check Kafka broker addresses
- Test topic exists

## 📚 Documentation Files

- `README.md` - Full project documentation
- `QUICKSTART.md` - Step-by-step setup guide
- `RUN_STATUS.md` - Current status of components
- `HOW_TO_RUN.md` - This file (quick reference)

## 💡 Tips

1. **Start Simple**: Use `run_local.py` first to understand the system
2. **Test Components**: Use `test_project.py` to verify setup
3. **Gradual Setup**: Add infrastructure components one at a time
4. **Check Logs**: Monitor output for errors and warnings

## 🎉 Success Indicators

You'll know it's working when:
- ✅ `run_local.py` processes tweets successfully
- ✅ Dashboard shows statistics
- ✅ Tweets are classified correctly
- ✅ PNRs are extracted when present

For full system:
- ✅ Tweets stream from Twitter
- ✅ Data saved to MySQL
- ✅ Web dashboard shows real-time data
- ✅ Responses can be posted to Twitter

