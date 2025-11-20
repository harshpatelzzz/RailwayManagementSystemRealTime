"""
Analytics Utility Functions
Helper functions for analytics calculations
"""

import re
from datetime import datetime, timedelta

def extract_train_number(text):
    """Extract train number from complaint text"""
    if not text:
        return None
    
    # Common patterns: "Train No 12345", "Train 12345", "Train#12345", "12345"
    patterns = [
        r'train\s*(?:no|number|#)?\s*:?\s*(\d{4,5})\b',
        r'\b(\d{4,5})\s*(?:train|express|mail)\b',
        r'\b(\d{4,5})\b',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            train_num = match.group(1)
            if len(train_num) <= 5:
                return train_num
    
    return None

def extract_delay_minutes(text):
    """Extract delay information in minutes from complaint text"""
    if not text:
        return None
    
    text_lower = text.lower()
    patterns = [
        r'delay(?:ed)?\s*(?:by|of)?\s*(\d+)\s*(?:hour|hr|h)\s*(?:(\d+)\s*(?:min|minute|mins)?)?',
        r'(\d+)\s*(?:hour|hr|h)\s*(?:(\d+)\s*(?:min|minute|mins)?)?\s*delay',
        r'late\s*(?:by)?\s*(\d+)\s*(?:hour|hr|h)\s*(?:(\d+)\s*(?:min|minute|mins)?)?',
        r'(\d+)\s*(?:min|minute|mins)\s*(?:delay|late)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            hours = int(match.group(1)) if match.group(1) else 0
            minutes = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
            total_minutes = hours * 60 + minutes
            if total_minutes > 0:
                return total_minutes
    
    return None

def classify_severity(message: str) -> tuple:
    """
    Returns (severity_label, severity_score).
    severity_label ∈ {'low', 'medium', 'high'}
    severity_score is a float in [0,1] where higher = more severe.
    """
    if not message:
        return ('low', 0.0)
    
    text_lower = message.lower()
    score = 0.0
    
    # High severity keywords
    high_severity_keywords = [
        'emergency', 'accident', 'fire', 'medical', 'critical', 'life',
        'death', 'injured', 'hospital', 'ambulance', 'stuck', 'stranded',
        'breakdown', 'derailment', 'collision'
    ]
    
    # Medium severity keywords
    medium_severity_keywords = [
        'delay', 'late', 'cancelled', 'urgent', 'help', 'problem',
        'issue', 'complaint', 'fault', 'broken', 'not working'
    ]
    
    # Low severity keywords
    low_severity_keywords = [
        'feedback', 'suggestion', 'improve', 'better', 'good', 'satisfied',
        'thank', 'appreciate', 'nice', 'comfortable'
    ]
    
    # Count high severity keywords
    high_count = sum(1 for keyword in high_severity_keywords if keyword in text_lower)
    score += min(high_count * 0.4, 1.0)
    
    # Count medium severity keywords
    if score < 0.8:
        medium_count = sum(1 for keyword in medium_severity_keywords if keyword in text_lower)
        score += min(medium_count * 0.2, 0.6)
    
    # Count low severity keywords (reduces score)
    low_count = sum(1 for keyword in low_severity_keywords if keyword in text_lower)
    score = max(0.0, score - (low_count * 0.1))
    
    # Check for delay information
    delay = extract_delay_minutes(message)
    if delay:
        if delay >= 120:
            score = min(1.0, score + 0.3)
        elif delay >= 60:
            score = min(1.0, score + 0.2)
        elif delay >= 30:
            score = min(1.0, score + 0.1)
    
    # Normalize score to [0, 1]
    score = min(1.0, max(0.0, score))
    
    # Determine label
    if score >= 0.7:
        label = 'high'
    elif score >= 0.4:
        label = 'medium'
    else:
        label = 'low'
    
    return (label, round(score, 2))

