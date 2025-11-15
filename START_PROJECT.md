# 🚀 How to Start RailSewa Project

## ✅ Quick Start (Local Simulation - Just Ran!)

The full system simulation just completed successfully! Here's what happened:

- ✅ Processed 10 Telegram complaints
- ✅ Classified as Emergency (8) and Feedback (12)
- ✅ Extracted PNR numbers
- ✅ Saved to local database (`local_twitter.db`)

## 🌐 Access Web Dashboard

The PHP web dashboard is now running at:
**http://localhost:8000/index.php**

Open this URL in your browser to:
- View all complaints
- Filter by Emergency/Feedback
- Respond to complaints
- See real-time statistics

## 📱 Run Real Telegram Bot (Optional)

To receive real complaints from Telegram users:

### Step 1: Get Telegram Bot Token
1. Open Telegram app
2. Search for **@BotFather**
3. Send `/newbot` command
4. Follow instructions to create your bot
5. Copy the token provided

### Step 2: Configure Token
Add to `.env` file:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Step 3: Start Telegram Bot
```bash
python kafka_file/telegram_stream.py
```

The bot will:
- Listen for messages from users
- Send complaints to Kafka
- Acknowledge receipt to users

## 🔄 Full Production System

For the complete production setup with real infrastructure:

### Prerequisites:
1. **MySQL Database** (AWS RDS or local)
   - Run: `database/schema.sql`
   - Update `.env` with credentials

2. **Apache Kafka & Zookeeper**
   - Install and start Zookeeper
   - Start Kafka broker
   - Create topic: `raw_tweets`

3. **Apache Spark** (Optional for ML processing)
   - Install Spark
   - Run: `spark-submit new_live_processing.py`

### Running Full System:

**Terminal 1: Telegram Bot**
```bash
python kafka_file/telegram_stream.py
```

**Terminal 2: Spark Processing** (if using Spark)
```bash
spark-submit new_live_processing.py
```

**Terminal 3: Web Dashboard**
```bash
cd railways
php -S localhost:8000
```

## 📊 Current Status

| Component | Status | Location |
|-----------|--------|----------|
| ✅ Local Simulation | Running | `run_full_system.py` |
| ✅ Web Dashboard | Running | http://localhost:8000 |
| ✅ Database | Created | `local_twitter.db` |
| ⚠️ Telegram Bot | Needs Token | Configure `.env` |
| ⚠️ Kafka/Spark | Optional | For production |

## 🎯 What's Working Now

✅ **Complaint Processing**
- Text cleaning
- PNR extraction  
- Classification (Emergency/Feedback)
- Statistics tracking

✅ **Web Dashboard**
- View all complaints
- Filter by type
- Respond to complaints
- Real-time updates

✅ **Database**
- SQLite database created
- All complaints stored
- Ready for MySQL migration

## 📝 Next Steps

1. **View Dashboard**: Open http://localhost:8000/index.php
2. **Test Telegram Bot**: Get token from @BotFather and run `telegram_stream.py`
3. **Production Setup**: Follow `QUICKSTART.md` for full infrastructure

## 🔧 Troubleshooting

### Dashboard Not Loading?
- Check PHP server is running: `php -S localhost:8000`
- Verify `railways/index.php` exists
- Check browser console for errors

### Telegram Bot Not Working?
- Verify token in `.env` file
- Check token is correct (from @BotFather)
- Ensure bot is started: `python kafka_file/telegram_stream.py`

### Database Issues?
- Check `local_twitter.db` exists
- Verify SQLite is working
- For MySQL: Update `.env` with credentials

## 📚 Documentation

- `README.md` - Full project documentation
- `QUICKSTART.md` - Production setup guide
- `HOW_TO_RUN.md` - Quick reference
- `HOW_TO_GET_CREDENTIALS.md` - Credential setup

---

**🎉 System is running! Open http://localhost:8000/index.php to view the dashboard!**

