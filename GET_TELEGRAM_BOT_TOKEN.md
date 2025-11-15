# 📱 How to Get Telegram Bot Token - Step by Step Guide

## 🎯 Overview

To run the RailSewa Telegram Bot, you need a **Bot Token** from Telegram's BotFather. This token allows your bot to receive messages from users.

---

## 📋 Step-by-Step Procedure

### **Step 1: Open Telegram**

1. Open the **Telegram** app on your phone, tablet, or computer
   - Download from: https://telegram.org/apps
   - Or use web version: https://web.telegram.org

2. **Sign in** to your Telegram account (or create one if you don't have it)

---

### **Step 2: Find BotFather**

1. In Telegram, click the **Search** icon (🔍) at the top
2. Type: **`@BotFather`** (with the @ symbol)
3. Click on the official **BotFather** bot (it has a blue checkmark ✓)

   > **Note**: Make sure it's the official BotFather with the verified badge

---

### **Step 3: Start Conversation with BotFather**

1. Click **"Start"** or send `/start` command
2. BotFather will send you a welcome message with available commands

---

### **Step 4: Create a New Bot**

1. Send this command to BotFather:
   ```
   /newbot
   ```

2. BotFather will ask: **"Alright, a new bot. How are we going to call it? Please choose a name for your bot."**

3. **Type a name** for your bot (e.g., "RailSewa Complaint Bot" or "My Railway Bot")
   - This is the display name users will see
   - Press **Enter** or **Send**

---

### **Step 5: Choose Bot Username**

1. BotFather will ask: **"Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot."**

2. **Type a username** ending with `bot` (e.g., `railsewa_bot` or `my_railway_bot`)
   - Must be unique (not taken by another bot)
   - Must end with `bot`
   - Can contain letters, numbers, and underscores
   - Press **Enter** or **Send**

   > **Tip**: If the username is taken, try variations like `railsewa_complaint_bot` or `railsewa123_bot`

---

### **Step 6: Get Your Bot Token**

1. If successful, BotFather will send you a message like:
   ```
   Done! Congratulations on your new bot. You will find it at t.me/your_bot_username.
   
   Use this token to access the HTTP API:
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   
   Keep your token secure and store it safely, it can be used by anyone to control your bot.
   ```

2. **Copy the token** (the long string of numbers and letters)
   - Example format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
   - This is your **Bot Token** - keep it secret!

---

### **Step 7: Configure Token in Project**

1. Open the `.env` file in your project root directory

2. Find or add this line:
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

3. Replace `your_bot_token_here` with the token you copied:
   ```bash
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

4. **Save** the `.env` file

---

### **Step 8: Test Your Bot**

1. In Telegram, search for your bot using its username (e.g., `@railsewa_bot`)

2. Click **"Start"** to begin chatting with your bot

3. Send a test message like: "Hello, this is a test complaint"

4. If your bot is running (`python kafka_file/telegram_stream.py`), it should:
   - Receive your message
   - Send it to Kafka
   - Reply with: "✅ Your complaint has been received..."

---

## 🔒 Security Tips

### ⚠️ **IMPORTANT: Keep Your Token Secret!**

- ❌ **NEVER** share your token publicly
- ❌ **NEVER** commit it to GitHub (it's in `.gitignore`)
- ❌ **NEVER** post it in chat groups or forums
- ✅ **DO** store it only in `.env` file
- ✅ **DO** keep `.env` file private

### If Your Token is Compromised:

1. Go back to BotFather
2. Send: `/revoke`
3. Select your bot
4. BotFather will generate a new token
5. Update `.env` with the new token

---

## 📸 Visual Guide

### BotFather Commands You'll Use:

```
/start          - Start conversation
/newbot         - Create a new bot
/token          - Get current bot token (if you lose it)
/revoke         - Revoke and get new token
/setdescription - Set bot description
/setabouttext   - Set bot about text
/setcommands    - Set bot commands menu
```

---

## ✅ Verification Checklist

After completing the steps, verify:

- [ ] Bot created successfully
- [ ] Token copied correctly
- [ ] Token added to `.env` file
- [ ] `.env` file saved
- [ ] Can find your bot in Telegram search
- [ ] Bot responds when you send `/start`

---

## 🚀 Next Steps

Once you have the token configured:

1. **Start the Telegram Bot:**
   ```bash
   python kafka_file/telegram_stream.py
   ```

2. **Test it:**
   - Open Telegram
   - Search for your bot
   - Send a complaint message
   - Check if it's received

3. **View in Dashboard:**
   - Open http://localhost:8000/index.php
   - See your complaint appear in real-time

---

## 🆘 Troubleshooting

### Problem: "Token not found" error

**Solution:**
- Check `.env` file exists
- Verify token is on one line (no line breaks)
- Make sure there are no extra spaces
- Restart the bot script

### Problem: "Unauthorized" error

**Solution:**
- Verify token is correct (copy again from BotFather)
- Check for typos in `.env`
- Use `/token` command in BotFather to get current token

### Problem: Bot doesn't respond

**Solution:**
- Make sure bot script is running
- Check if Kafka is running (if using real Kafka)
- Verify token in `.env` matches BotFather's token
- Check console for error messages

### Problem: Username already taken

**Solution:**
- Try different variations
- Add numbers or underscores
- Examples: `railsewa1_bot`, `railsewa_complaint_bot`

---

## 📞 Need Help?

- **BotFather Help**: Send `/help` to @BotFather
- **Telegram Bot API Docs**: https://core.telegram.org/bots/api
- **Project Documentation**: See `README.md` or `QUICKSTART.md`

---

## 🎉 Success!

Once you complete these steps, you'll have:
- ✅ A working Telegram bot
- ✅ Bot token configured
- ✅ Ready to receive complaints from users

**Your bot is now ready to process railway complaints!** 🚂

