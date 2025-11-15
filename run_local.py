"""
Local Runner for RailSewa Project
Runs the system locally without requiring Kafka, Spark, or MySQL
Simulates the full workflow for testing
"""

import os
import json
import time
from datetime import datetime
from sparksupport import clean_tweet, extract_pnr, classify_urgency
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LocalComplaintProcessor:
    """Local complaint processor that simulates the full system"""
    
    def __init__(self):
        self.complaints = []
        self.stats = {
            'total': 0,
            'emergency': 0,
            'feedback': 0,
            'processed': 0
        }
    
    def process_complaint(self, complaint_text, username="test_user", complaint_id=None):
        """Process a single complaint"""
        if complaint_id is None:
            complaint_id = int(time.time() * 1000)  # Generate ID
        
        # Clean and process
        cleaned = clean_tweet(complaint_text)
        pnr = extract_pnr(complaint_text)
        prediction = classify_urgency(cleaned)
        complaint_type = "Emergency" if prediction == 1 else "Feedback"
        
        # Create complaint record
        complaint_data = {
            'id': len(self.complaints) + 1,
            'tweet_id': complaint_id,
            'tweet': complaint_text,
            'cleaned_tweet': cleaned,
            'username': username,
            'pnr': pnr,
            'prediction': prediction,
            'type': complaint_type,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'response_status': 0,
            'source': 'Telegram'
        }
        
        # Update stats
        self.stats['total'] += 1
        if prediction == 1:
            self.stats['emergency'] += 1
        else:
            self.stats['feedback'] += 1
        self.stats['processed'] += 1
        
        # Store complaint
        self.complaints.append(complaint_data)
        
        return complaint_data
    
    def get_stats(self):
        """Get processing statistics"""
        return self.stats.copy()
    
    def get_complaints(self, filter_type='all', limit=10):
        """Get complaints with optional filtering"""
        complaints = self.complaints.copy()
        
        if filter_type == 'emergency':
            complaints = [c for c in complaints if c['prediction'] == 1]
        elif filter_type == 'feedback':
            complaints = [c for c in complaints if c['prediction'] == 0]
        
        # Sort by time (newest first) and limit
        complaints.sort(key=lambda x: x['time'], reverse=True)
        return complaints[:limit]
    
    def respond_to_complaint(self, complaint_id, response):
        """Simulate responding to a complaint"""
        for complaint in self.complaints:
            if complaint['id'] == complaint_id:
                complaint['response'] = response
                complaint['response_status'] = 1
                return True
        return False

def simulate_telegram_bot(processor, num_complaints=10):
    """Simulate incoming complaints via Telegram Bot"""
    sample_complaints = [
        ("Train 12345 is delayed by 2 hours! PNR: 1234567890 Urgent help needed @RailMinIndia", "user1"),
        ("Great service on Indian Railways! Comfortable journey, clean coaches.", "user2"),
        ("Medical emergency in coach S3. Need immediate assistance. PNR: 9876543210", "user3"),
        ("Excellent food quality and staff behavior. Keep up the good work!", "user4"),
        ("Train breakdown on track. Passengers stranded. PNR: 5555555555", "user5"),
        ("Thank you for the punctual service. Very satisfied with the journey.", "user6"),
        ("AC not working in coach A1. Very uncomfortable. PNR: 1111111111", "user7"),
        ("Clean washrooms and well-maintained stations. Great job!", "user8"),
        ("Train cancelled without notice. Need refund. PNR: 2222222222", "user9"),
        ("Smooth journey, on-time arrival. Highly recommend!", "user10"),
    ]
    
    print("=" * 70)
    print("RailSewa - Local System Runner")
    print("=" * 70)
    print(f"\nSimulating Telegram Bot with {num_complaints} complaints...\n")
    
    for i, (complaint_text, username) in enumerate(sample_complaints[:num_complaints], 1):
        print(f"Processing Complaint {i}/{num_complaints}...")
        result = processor.process_complaint(complaint_text, username)
        
        print(f"  User: {result['username']}")
        print(f"  Text: {result['tweet'][:60]}...")
        print(f"  Type: {result['type']}")
        print(f"  PNR: {result['pnr'] if result['pnr'] else 'Not found'}")
        print()
        
        time.sleep(0.5)  # Simulate processing delay
    
    return processor

def display_dashboard(processor):
    """Display a simple dashboard"""
    stats = processor.get_stats()
    complaints = processor.get_complaints(limit=5)
    
    print("=" * 70)
    print("DASHBOARD - Real-time Statistics")
    print("=" * 70)
    print(f"\nTotal Complaints Processed: {stats['total']}")
    print(f"Emergency Complaints:       {stats['emergency']}")
    print(f"Feedback Complaints:        {stats['feedback']}")
    print(f"Processing Rate:            {stats['processed']} complaints")
    
    print("\n" + "-" * 70)
    print("Recent Complaints (Last 5)")
    print("-" * 70)
    
    for complaint in complaints:
        type_badge = "[EMERGENCY]" if complaint['prediction'] == 1 else "[FEEDBACK]"
        pnr_info = f"PNR: {complaint['pnr']}" if complaint['pnr'] else "No PNR"
        
        print(f"\n[{complaint['id']}] {type_badge} - {complaint['time']}")
        print(f"  User: {complaint['username']} (Telegram)")
        print(f"  Text: {complaint['tweet'][:70]}...")
        print(f"  {pnr_info}")

def interactive_mode(processor):
    """Interactive mode for testing"""
    print("\n" + "=" * 70)
    print("Interactive Mode")
    print("=" * 70)
    print("\nCommands:")
    print("  'stats' - Show statistics")
    print("  'complaints [all|emergency|feedback]' - Show complaints")
    print("  'process <complaint_text>' - Process a new complaint")
    print("  'respond <id> <response>' - Respond to a complaint")
    print("  'quit' - Exit")
    print()
    
    while True:
        try:
            command = input("RailSewa> ").strip()
            
            if not command:
                continue
            
            if command == 'quit' or command == 'exit':
                break
            elif command == 'stats':
                stats = processor.get_stats()
                print(f"\nStatistics:")
                print(f"  Total: {stats['total']}")
                print(f"  Emergency: {stats['emergency']}")
                print(f"  Feedback: {stats['feedback']}")
            elif command.startswith('complaints'):
                parts = command.split()
                filter_type = parts[1] if len(parts) > 1 else 'all'
                complaints = processor.get_complaints(filter_type=filter_type, limit=10)
                print(f"\nShowing {len(complaints)} complaints (filter: {filter_type}):")
                for complaint in complaints:
                    type_badge = "[EMERGENCY]" if complaint['prediction'] == 1 else "[FEEDBACK]"
                    print(f"  [{complaint['id']}] {type_badge} - {complaint['username']}: {complaint['tweet'][:50]}...")
            elif command.startswith('process '):
                complaint_text = command[8:]
                result = processor.process_complaint(complaint_text)
                print(f"\nProcessed complaint #{result['id']}:")
                print(f"  Type: {result['type']}")
                print(f"  PNR: {result['pnr'] if result['pnr'] else 'Not found'}")
            elif command.startswith('respond '):
                parts = command.split(' ', 2)
                if len(parts) >= 3:
                    complaint_id = int(parts[1])
                    response = parts[2]
                    if processor.respond_to_complaint(complaint_id, response):
                        print(f"\nResponse added to complaint #{complaint_id}")
                    else:
                        print(f"\nComplaint #{complaint_id} not found")
                else:
                    print("Usage: respond <id> <response_text>")
            else:
                print("Unknown command. Type 'quit' to exit.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main function"""
    processor = LocalComplaintProcessor()
    
    print("\n" + "=" * 70)
    print("RailSewa - Local System Runner")
    print("=" * 70)
    print("\nThis runs the system locally without requiring:")
    print("  - Kafka/Zookeeper")
    print("  - Spark cluster")
    print("  - MySQL database")
    print("  - Telegram Bot API")
    print("\nIt simulates the full workflow for testing purposes.")
    print()
    
    # Run simulation
    processor = simulate_telegram_bot(processor, num_complaints=10)
    
    # Display dashboard
    display_dashboard(processor)
    
    # Ask for interactive mode (skip if not in interactive terminal)
    print("\n" + "=" * 70)
    try:
        response = input("Enter interactive mode? (y/n): ").strip().lower()
        
        if response == 'y' or response == 'yes':
            interactive_mode(processor)
        else:
            print_summary(processor)
    except (EOFError, KeyboardInterrupt):
        # Not in interactive terminal, just show summary
        print_summary(processor)

def print_summary(processor):
    """Print summary and next steps"""
    print("\n" + "=" * 70)
    print("System Running Successfully!")
    print("=" * 70)
    print("\nThe local system has processed complaints successfully.")
    print("\nTo run the full system with real infrastructure:")
    print("  1. Setup MySQL database (see database/schema.sql)")
    print("  2. Install and start Kafka/Zookeeper")
    print("  3. Configure Telegram Bot Token in .env")
    print("  4. Run: python kafka_file/telegram_stream.py")
    print("  5. Run: spark-submit new_live_processing.py")
    print("\nFor interactive mode, run: python run_local.py")
    print("See README.md or QUICKSTART.md for detailed instructions.")

if __name__ == "__main__":
    main()

