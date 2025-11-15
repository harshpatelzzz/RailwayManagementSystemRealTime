"""
Dashboard API Server
Provides REST API for dashboard to connect to local database
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for dashboard.html

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('local_twitter.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    total = cursor.execute('SELECT COUNT(*) FROM tweets').fetchone()[0]
    emergency = cursor.execute('SELECT COUNT(*) FROM tweets WHERE prediction = 1').fetchone()[0]
    feedback = cursor.execute('SELECT COUNT(*) FROM tweets WHERE prediction = 0').fetchone()[0]
    responded = cursor.execute('SELECT COUNT(*) FROM tweets WHERE response_status = 1').fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total': total,
        'emergency': emergency,
        'feedback': feedback,
        'responded': responded,
        'pending': total - responded
    })

@app.route('/api/tweets', methods=['GET'])
def get_tweets():
    """Get tweets with optional filtering"""
    filter_type = request.args.get('filter', 'all')
    limit = int(request.args.get('limit', 100))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if filter_type == 'emergency':
        query = 'SELECT * FROM tweets WHERE prediction = 1 ORDER BY time DESC LIMIT ?'
    elif filter_type == 'feedback':
        query = 'SELECT * FROM tweets WHERE prediction = 0 ORDER BY time DESC LIMIT ?'
    else:
        query = 'SELECT * FROM tweets ORDER BY time DESC LIMIT ?'
    
    cursor.execute(query, (limit,))
    tweets = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify(tweets)

@app.route('/api/respond', methods=['POST'])
def respond_to_tweet():
    """Respond to a tweet"""
    data = request.json
    tweet_id = data.get('tweet_id')
    response = data.get('response')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE tweets 
        SET response = ?, response_status = 1 
        WHERE id = ?
    ''', (response, tweet_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Response saved'})

if __name__ == '__main__':
    print("Starting Dashboard API Server...")
    print("API available at: http://localhost:5000")
    print("Endpoints:")
    print("  GET  /api/stats - Get statistics")
    print("  GET  /api/tweets?filter=all|emergency|feedback - Get tweets")
    print("  POST /api/respond - Respond to tweet")
    app.run(debug=True, port=5000)

