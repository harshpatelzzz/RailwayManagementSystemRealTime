# RailSewa Project - Complete Implementation

## Project Overview

This is a complete implementation of the **Real-Time Indian Railways Twitter Complaint Administration System** based on the original repository. The system processes real-time Twitter complaints, classifies them using machine learning, and provides a web interface for administrators to manage and respond to complaints.

## What Has Been Created

### Core Components

1. **Kafka Streaming** (`kafka_file/stream_data.py`)
   - Streams tweets from Twitter API
   - Sends tweets to Kafka topic for processing
   - Configurable via environment variables

2. **Spark Processing** 
   - `new_live_processing.py`: Main live processing script using Spark Streaming
   - `live_processing.py`: Alternative processing implementation
   - `train_model.py`: ML model training script
   - `sparksupport.py`: Utility functions for Spark operations

3. **Web Interface** (`railways/`)
   - `index.php`: Main dashboard with real-time tweet management
   - `config.php`: Database and API configuration
   - `twitter_api.php`: Twitter API integration for responses

4. **Data Processing**
   - `parsing_raw_tweets/parse_tweets.py`: Tweet parsing utilities
   - Jupyter notebook for data analysis and model development

5. **Database**
   - `database/schema.sql`: Complete database schema with indexes

6. **Frontend Assets** (`assets/`)
   - Modern CSS styling
   - Interactive JavaScript for dashboard
   - Bootstrap-based responsive design

### Configuration Files

- `README.md`: Comprehensive documentation
- `QUICKSTART.md`: Step-by-step setup guide
- `requirements.txt`: Python dependencies
- `composer.json`: PHP dependencies
- `setup.py`: Automated setup script
- `.gitignore`: Git ignore rules
- `.env.example`: Environment variable template (via setup.py)

## Key Features

✅ Real-time Twitter streaming  
✅ Automatic tweet classification (Emergency/Feedback)  
✅ PNR extraction from tweets  
✅ Interactive web dashboard  
✅ Real-time statistics  
✅ Tweet filtering and management  
✅ Automated Twitter responses  
✅ Spark-based distributed processing  
✅ Kafka-based message queuing  
✅ MySQL database integration  

## Technology Stack

- **Backend**: Python, Apache Spark, Apache Kafka
- **Database**: MySQL (AWS RDS compatible)
- **Frontend**: PHP, HTML, CSS, Bootstrap, jQuery
- **ML**: Spark MLlib, scikit-learn
- **Deployment**: AWS EC2, AWS RDS ready

## Project Structure

```
RailSewa-FinalYearProject/
├── assets/                    # Frontend assets
│   ├── css/style.css
│   └── js/main.js
├── data/                      # Training data
├── database/                  # Database schema
│   └── schema.sql
├── kafka_file/               # Kafka streaming
│   └── stream_data.py
├── parsing_raw_tweets/       # Tweet parsing
│   └── parse_tweets.py
├── railways/                 # Web interface
│   ├── config.php
│   ├── index.php
│   └── twitter_api.php
├── saved_model/              # Trained models
├── IR-Complaint-Feedback-Mgmt-System.ipynb
├── live_processing.py
├── new_live_processing.py
├── sparksupport.py
├── train_model.py
├── setup.py
├── README.md
├── QUICKSTART.md
├── requirements.txt
├── composer.json
└── LICENSE
```

## Next Steps

1. **Setup Environment**
   ```bash
   python setup.py
   pip install -r requirements.txt
   composer install
   ```

2. **Configure Credentials**
   - Update `.env` file with your credentials
   - Configure database connection
   - Add Twitter API keys

3. **Setup Infrastructure**
   - Deploy Spark cluster
   - Setup Kafka and Zookeeper
   - Configure AWS RDS database

4. **Train Model**
   ```bash
   spark-submit train_model.py
   ```

5. **Start Services**
   - Start Zookeeper
   - Start Kafka
   - Start Twitter streaming
   - Start Spark processing
   - Start web server

6. **Access Dashboard**
   - Open `http://your-server/railways/`

## Improvements Over Original

- ✅ Better error handling
- ✅ Environment variable configuration
- ✅ Graceful Twitter API fallback
- ✅ Comprehensive documentation
- ✅ Setup automation script
- ✅ Database schema with indexes
- ✅ Modern web interface
- ✅ Real-time statistics
- ✅ Better code organization

## Notes

- The system is designed to work with AWS EC2 and RDS but can be adapted for local deployment
- Twitter API v2 is used for better compatibility
- The ML model can be improved with more training data
- All sensitive credentials should be stored in `.env` file (not committed to git)

## License

MIT License - Same as original repository

