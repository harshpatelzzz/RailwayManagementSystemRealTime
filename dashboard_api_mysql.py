"""
Dashboard API Server (MySQL Version)
Provides REST API for dashboard to connect to MySQL database (AWS RDS)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for dashboard.html

# Database Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'twitter')

def get_db_connection():
    """Get MySQL database connection"""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total FROM tweets')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as emergency FROM tweets WHERE prediction = 1')
        emergency = cursor.fetchone()['emergency']
        
        cursor.execute('SELECT COUNT(*) as feedback FROM tweets WHERE prediction = 0')
        feedback = cursor.fetchone()['feedback']
        
        cursor.execute('SELECT COUNT(*) as responded FROM tweets WHERE response_status = 1')
        responded = cursor.fetchone()['responded']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total': total,
            'emergency': emergency,
            'feedback': feedback,
            'responded': responded,
            'pending': total - responded
        })
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tweets', methods=['GET'])
def get_tweets():
    """Get tweets with optional filtering"""
    filter_type = request.args.get('filter', 'all')
    limit = int(request.args.get('limit', 100))
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        if filter_type == 'emergency':
            query = 'SELECT * FROM tweets WHERE prediction = 1 ORDER BY time DESC LIMIT %s'
        elif filter_type == 'feedback':
            query = 'SELECT * FROM tweets WHERE prediction = 0 ORDER BY time DESC LIMIT %s'
        else:
            query = 'SELECT * FROM tweets ORDER BY time DESC LIMIT %s'
        
        cursor.execute(query, (limit,))
        tweets = cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        for tweet in tweets:
            if 'time' in tweet and tweet['time']:
                if isinstance(tweet['time'], datetime):
                    tweet['time'] = tweet['time'].isoformat()
        
        cursor.close()
        conn.close()
        
        return jsonify(tweets)
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/respond', methods=['POST'])
def respond_to_tweet():
    """Respond to a tweet"""
    data = request.json
    tweet_id = data.get('tweet_id')
    response = data.get('response')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tweets 
            SET response = %s, response_status = 1 
            WHERE id = %s
        ''', (response, tweet_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Response saved'})
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Serve dashboard HTML"""
    try:
        with open('dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({'error': 'dashboard.html not found'}), 404

if __name__ == '__main__':
    print("="*60)
    print("🚂 RailSewa - Dashboard API Server (MySQL)")
    print("="*60)
    print(f"Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"API available at: http://localhost:5000")
    print(f"Dashboard: http://localhost:5000")
    print("="*60)
    print("Endpoints:")
    print("  GET  /api/stats - Get statistics")
    print("  GET  /api/tweets?filter=all|emergency|feedback - Get tweets")
    print("  POST /api/respond - Respond to tweet")
    print("="*60)
    print("\nStarting server...\n")
    app.run(debug=True, port=5000, host='0.0.0.0')

