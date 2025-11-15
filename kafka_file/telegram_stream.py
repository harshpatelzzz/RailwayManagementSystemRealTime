"""
Telegram Bot Data Ingestion for RailSewa
Receives complaints from Telegram users and sends them to Kafka
"""

import os
import json
from kafka import KafkaProducer
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'PUT_YOUR_BOT_TOKEN_HERE')

# Kafka Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'raw_tweets')  # Keep topic name for compatibility

class TelegramComplaintHandler:
    """Handles Telegram messages and sends to Kafka"""
    
    def __init__(self):
        # Initialize Kafka Producer
        self.producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"Connected to Kafka broker: {KAFKA_BROKER}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming Telegram messages"""
        try:
            message = update.message
            if not message or not message.text:
                return
            
            # Extract message data
            text = message.text
            user = message.from_user
            
            # Create complaint data structure
            complaint_data = {
                'complaint_id': message.message_id,
                'text': text,
                'user_id': user.id,
                'username': user.username or f"user_{user.id}",
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'chat_id': message.chat.id,
                'timestamp': message.date.isoformat() if message.date else None
            }
            
            # Send to Kafka
            self.producer.send(KAFKA_TOPIC, value=complaint_data)
            self.producer.flush()
            
            print(f"Sent to Kafka: {text[:50]}... (User: {complaint_data['username']})")
            
            # Send acknowledgment to user
            await message.reply_text(
                "✅ Your complaint has been received and is being processed. "
                "We will get back to you soon!"
            )
            
        except Exception as e:
            print(f"Error processing message: {e}")
            if update.message:
                await update.message.reply_text(
                    "❌ Sorry, there was an error processing your complaint. Please try again."
                )

def main():
    """Main function to start Telegram bot"""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == 'PUT_YOUR_BOT_TOKEN_HERE':
        print("ERROR: Telegram Bot Token not found!")
        print("Please set TELEGRAM_BOT_TOKEN in your .env file")
        print("\nTo get a bot token:")
        print("1. Open Telegram and search for @BotFather")
        print("2. Send /newbot command")
        print("3. Follow instructions to create a bot")
        print("4. Copy the token and add to .env file")
        return
    
    # Initialize handler
    handler = TelegramComplaintHandler()
    
    # Create Telegram application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_message))
    
    # Add start command handler
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🚂 Welcome to RailSewa Complaint System!\n\n"
            "Send your railway complaint and we'll process it immediately.\n\n"
            "Your complaint will be classified and forwarded to the appropriate department."
        )
    
    application.add_handler(MessageHandler(filters.COMMAND & filters.Regex("^/start$"), start_command))
    
    print("=" * 60)
    print("Telegram Bot is starting...")
    print("=" * 60)
    print(f"Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"Kafka Broker: {KAFKA_BROKER}")
    print(f"Kafka Topic: {KAFKA_TOPIC}")
    print("=" * 60)
    print("\nBot is running. Send messages to your bot to test!")
    print("Press Ctrl+C to stop.\n")
    
    # Start polling
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\nStopping bot...")
        handler.producer.close()
    except Exception as e:
        print(f"Error: {e}")
        handler.producer.close()

if __name__ == "__main__":
    main()

