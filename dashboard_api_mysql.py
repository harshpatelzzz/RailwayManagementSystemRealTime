"""
Dashboard API Server (MySQL Version)
Provides REST API for dashboard to connect to MySQL database (AWS RDS)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from analytics_utils import extract_train_number, extract_delay_minutes, classify_severity

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

# ============================================
# ANALYTICS ENDPOINTS
# ============================================

@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get analytics summary"""
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
        
        cursor.execute('SELECT MAX(time) as last_updated FROM tweets')
        last_updated = cursor.fetchone()['last_updated']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_complaints': total,
            'total_emergency': emergency,
            'total_feedback': feedback,
            'total_processed': responded,
            'last_updated': last_updated.isoformat() if last_updated else None
        })
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/time-series', methods=['GET'])
def get_time_series():
    """Get time series data for complaints"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        window_minutes = int(request.args.get('window_minutes', 60))
        window_hours = int(request.args.get('window_hours', 0))
        
        if window_hours > 0:
            window_minutes = window_hours * 60
        
        # Determine bucket size based on window
        if window_minutes <= 60:
            bucket_minutes = 1
        elif window_minutes <= 360:
            bucket_minutes = 5
        elif window_minutes <= 1440:
            bucket_minutes = 15
        else:
            bucket_minutes = 60
        
        cursor = conn.cursor()
        
        # Get complaints within time window
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        
        query = """
            SELECT 
                DATE_FORMAT(time, '%%Y-%%m-%%d %%H:%%i:00') as bucket,
                COUNT(*) as total,
                SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as emergency_count,
                SUM(CASE WHEN prediction = 0 THEN 1 ELSE 0 END) as feedback_count
            FROM tweets
            WHERE time >= %s
            GROUP BY bucket
            ORDER BY bucket ASC
        """
        
        cursor.execute(query, (cutoff_time,))
        results = cursor.fetchall()
        
        points = []
        for row in results:
            points.append({
                'time': row['bucket'],
                'total': row['total'],
                'emergency': row['emergency_count'],
                'feedback': row['feedback_count']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'points': points})
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/train-stats', methods=['GET'])
def get_train_stats():
    """Get train statistics - top trains by complaint count"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        limit = int(request.args.get('limit', 10))
        cursor = conn.cursor()
        
        # Extract train numbers from tweet text (using analytics_utils logic)
        # Since train_number column may not exist, we'll extract from text
        query = """
            SELECT 
                tweet,
                COUNT(*) as total_complaints,
                SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as emergency_count,
                SUM(CASE WHEN prediction = 0 THEN 1 ELSE 0 END) as feedback_count,
                MAX(time) as last_complaint_time
            FROM tweets
            GROUP BY tweet
            ORDER BY total_complaints DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit * 5,))  # Get more to filter by train number
        results = cursor.fetchall()
        
        # Process results and extract train numbers
        train_stats = {}
        for row in results:
            train_num = extract_train_number(row['tweet'])
            if train_num:
                if train_num not in train_stats:
                    train_stats[train_num] = {
                        'train_number': train_num,
                        'total_complaints': 0,
                        'emergency_count': 0,
                        'feedback_count': 0,
                        'last_complaint_time': None
                    }
                
                train_stats[train_num]['total_complaints'] += row['total_complaints']
                train_stats[train_num]['emergency_count'] += row['emergency_count']
                train_stats[train_num]['feedback_count'] += row['feedback_count']
                
                if not train_stats[train_num]['last_complaint_time'] or \
                   (row['last_complaint_time'] and row['last_complaint_time'] > train_stats[train_num]['last_complaint_time']):
                    train_stats[train_num]['last_complaint_time'] = row['last_complaint_time']
        
        # Convert to list and sort
        train_list = list(train_stats.values())
        train_list.sort(key=lambda x: x['total_complaints'], reverse=True)
        train_list = train_list[:limit]
        
        # Convert datetime to string
        for train in train_list:
            if train['last_complaint_time'] and isinstance(train['last_complaint_time'], datetime):
                train['last_complaint_time'] = train['last_complaint_time'].isoformat()
        
        cursor.close()
        conn.close()
        
        return jsonify(train_list)
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/source-stats', methods=['GET'])
def get_source_stats():
    """Get source (user) statistics"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        limit = int(request.args.get('limit', 10))
        cursor = conn.cursor()
        
        query = """
            SELECT 
                username as source_id,
                user_id,
                COUNT(*) as total_complaints,
                SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as emergency_count,
                SUM(CASE WHEN prediction = 0 THEN 1 ELSE 0 END) as feedback_count
            FROM tweets
            WHERE username IS NOT NULL AND username != ''
            GROUP BY username, user_id
            ORDER BY total_complaints DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        sources = []
        for row in results:
            sources.append({
                'source_id': row['source_id'],
                'user_id': row['user_id'],
                'total_complaints': row['total_complaints'],
                'emergency_count': row['emergency_count'],
                'feedback_count': row['feedback_count']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify(sources)
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/severity', methods=['GET'])
def get_severity_stats():
    """Get severity statistics"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Calculate severity for all tweets (since column may not exist)
        cursor.execute('SELECT tweet FROM tweets')
        tweets = cursor.fetchall()
        
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        total_score = 0.0
        count = 0
        
        for tweet_row in tweets:
            text = tweet_row['tweet']
            if text:
                label, score = classify_severity(text)
                severity_counts[label] += 1
                total_score += score
                count += 1
        
        avg_score = total_score / count if count > 0 else 0.0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'summary': severity_counts,
            'avg_score': round(avg_score, 2)
        })
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/live', methods=['GET'])
def get_live_analytics():
    """Get live analytics for real-time updates"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        window_minutes = int(request.args.get('window_minutes', 5))
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        
        cursor = conn.cursor()
        
        # Global counts
        cursor.execute('SELECT COUNT(*) as total FROM tweets')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as emergency FROM tweets WHERE prediction = 1')
        emergency = cursor.fetchone()['emergency']
        
        cursor.execute('SELECT COUNT(*) as feedback FROM tweets WHERE prediction = 0')
        feedback = cursor.fetchone()['feedback']
        
        cursor.execute('SELECT COUNT(*) as responded FROM tweets WHERE response_status = 1')
        responded = cursor.fetchone()['responded']
        
        # Recent counts (last X minutes)
        cursor.execute('''
            SELECT COUNT(*) as recent_total 
            FROM tweets 
            WHERE time >= %s
        ''', (cutoff_time,))
        recent_total = cursor.fetchone()['recent_total']
        
        cursor.execute('''
            SELECT COUNT(*) as recent_emergency 
            FROM tweets 
            WHERE time >= %s AND prediction = 1
        ''', (cutoff_time,))
        recent_emergency = cursor.fetchone()['recent_emergency']
        
        cursor.execute('''
            SELECT COUNT(*) as recent_feedback 
            FROM tweets 
            WHERE time >= %s AND prediction = 0
        ''', (cutoff_time,))
        recent_feedback = cursor.fetchone()['recent_feedback']
        
        # Most recent complaint
        cursor.execute('SELECT MAX(time) as last_complaint_time FROM tweets')
        last_complaint = cursor.fetchone()['last_complaint_time']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'global': {
                'total': total,
                'emergency': emergency,
                'feedback': feedback,
                'responded': responded
            },
            'recent': {
                'total': recent_total,
                'emergency': recent_emergency,
                'feedback': recent_feedback,
                'window_minutes': window_minutes
            },
            'last_complaint_time': last_complaint.isoformat() if last_complaint else None,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/graph', methods=['GET'])
def get_graph_data():
    """Get graph data for network visualization"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Get all complaints with user and train information
        cursor.execute('''
            SELECT 
                id,
                tweet,
                username,
                user_id,
                prediction,
                time
            FROM tweets
            ORDER BY time DESC
            LIMIT 1000
        ''')
        tweets = cursor.fetchall()
        
        # Build graph structure
        nodes = []
        edges = []
        node_ids = {}
        
        # Categories
        categories = {'emergency': 0, 'feedback': 0}
        
        for tweet in tweets:
            tweet_id = f"tweet_{tweet['id']}"
            text = tweet['tweet']
            user_id = tweet['user_id']
            username = tweet['username'] or f"user_{user_id}"
            train_num = extract_train_number(text)
            category = 'emergency' if tweet['prediction'] == 1 else 'feedback'
            categories[category] += 1
            
            # Add tweet node
            if tweet_id not in node_ids:
                nodes.append({
                    'id': tweet_id,
                    'label': f"Complaint #{tweet['id']}",
                    'type': 'complaint',
                    'category': category,
                    'size': 10
                })
                node_ids[tweet_id] = True
            
            # Add user node
            user_node_id = f"user_{user_id}"
            if user_node_id not in node_ids:
                nodes.append({
                    'id': user_node_id,
                    'label': username,
                    'type': 'user',
                    'size': 15
                })
                node_ids[user_node_id] = True
            
            # Add train node if found
            if train_num:
                train_node_id = f"train_{train_num}"
                if train_node_id not in node_ids:
                    nodes.append({
                        'id': train_node_id,
                        'label': f"Train {train_num}",
                        'type': 'train',
                        'size': 20
                    })
                    node_ids[train_node_id] = True
                
                # Edge: train -> complaint
                edges.append({
                    'source': train_node_id,
                    'target': tweet_id,
                    'type': 'train_complaint'
                })
            
            # Edge: user -> complaint
            edges.append({
                'source': user_node_id,
                'target': tweet_id,
                'type': 'user_complaint'
            })
            
            # Edge: complaint -> category
            category_node_id = f"category_{category}"
            if category_node_id not in node_ids:
                nodes.append({
                    'id': category_node_id,
                    'label': category.capitalize(),
                    'type': 'category',
                    'size': 25
                })
                node_ids[category_node_id] = True
            
            edges.append({
                'source': tweet_id,
                'target': category_node_id,
                'type': 'complaint_category'
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'nodes': nodes,
            'edges': edges,
            'categories': categories
        })
    except Exception as e:
        if conn:
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
    print("\nAnalytics Endpoints:")
    print("  GET  /api/analytics/summary - Analytics summary")
    print("  GET  /api/analytics/time-series - Time series data")
    print("  GET  /api/analytics/train-stats - Train statistics")
    print("  GET  /api/analytics/source-stats - User/source statistics")
    print("  GET  /api/analytics/severity - Severity analysis")
    print("  GET  /api/analytics/live - Live real-time analytics")
    print("  GET  /api/analytics/graph - Network graph data")
    print("="*60)
    print("\nStarting server...\n")
    app.run(debug=True, port=5000, host='0.0.0.0')

