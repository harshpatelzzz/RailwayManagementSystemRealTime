"""
Train Machine Learning Model for Complaint Classification
Uses scikit-learn (lighter and faster for real-time inference)
Classifies complaints as Emergency (1) or Feedback (0)
"""

import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sparksupport import clean_tweet
import numpy as np

def create_training_data():
    """Create comprehensive training dataset"""
    # Emergency complaints (label = 1)
    emergency_samples = [
        # Delays and cancellations
        ("train is delayed by 2 hours urgent help needed", 1),
        ("train cancelled without notice need refund", 1),
        ("train running 3 hours late stranded at station", 1),
        ("train delay causing major inconvenience", 1),
        ("train no 12345 delayed urgent assistance required", 1),
        
        # Accidents and emergencies
        ("accident on track emergency services needed", 1),
        ("medical emergency in coach s3 need ambulance", 1),
        ("fire in train compartment urgent help", 1),
        ("passenger injured in train accident", 1),
        ("critical medical situation in train", 1),
        
        # Breakdowns and technical issues
        ("train breakdown on track passengers stranded", 1),
        ("engine failure train stopped middle of track", 1),
        ("train stuck between stations urgent help", 1),
        ("technical fault train not moving", 1),
        ("derailment risk urgent evacuation needed", 1),
        
        # Safety and security
        ("suspicious activity in train need security", 1),
        ("theft in train compartment report immediately", 1),
        ("passenger harassment urgent complaint", 1),
        ("unsafe conditions in train coach", 1),
        
        # Service failures
        ("no water in train urgent complaint", 1),
        ("ac not working in summer heat emergency", 1),
        ("toilet blocked train unsanitary conditions", 1),
        ("no food available train journey 12 hours", 1),
        
        # Urgent requests
        ("urgent help needed train delayed", 1),
        ("emergency situation in train coach", 1),
        ("critical issue need immediate attention", 1),
        ("train problem urgent assistance required", 1),
    ]
    
    # Feedback complaints (label = 0)
    feedback_samples = [
        # Positive feedback
        ("excellent service on railway thank you", 0),
        ("great service comfortable journey", 0),
        ("thank you for good service", 0),
        ("clean and tidy coach appreciate", 0),
        ("punctual train service satisfied", 0),
        ("excellent food quality staff behavior", 0),
        ("smooth journey on time arrival", 0),
        ("highly recommend railway service", 0),
        ("best train journey experience", 0),
        ("outstanding service keep it up", 0),
        
        # Suggestions and improvements
        ("suggestion improve wifi connectivity", 0),
        ("feedback better food options needed", 0),
        ("recommendation add more charging points", 0),
        ("suggestion improve cleanliness", 0),
        ("feedback comfortable seats needed", 0),
        
        # Minor complaints (not urgent)
        ("ac could be better in coach", 0),
        ("food quality needs improvement", 0),
        ("suggestion for better facilities", 0),
        ("minor issue with seat reservation", 0),
        ("feedback on ticket booking system", 0),
        
        # General feedback
        ("good service but can improve", 0),
        ("satisfied with journey overall", 0),
        ("nice experience will travel again", 0),
        ("appreciate railway services", 0),
        ("thank you railway staff", 0),
        
        # Non-urgent issues
        ("wifi not working in train", 0),
        ("seat reservation issue minor", 0),
        ("food menu could be better", 0),
        ("suggestion for coach maintenance", 0),
        ("feedback on station facilities", 0),
    ]
    
    # Combine all samples
    all_samples = emergency_samples + feedback_samples
    
    # Convert to DataFrame
    df = pd.DataFrame(all_samples, columns=['text', 'label'])
    
    # Clean the text
    df['cleaned_text'] = df['text'].apply(clean_tweet)
    
    return df

def train_model():
    """Train ML model for complaint classification"""
    print("="*60)
    print("RailSewa - ML Model Training")
    print("="*60)
    
    # Create or load training data
    data_path = os.getenv('TRAINING_DATA_PATH', 'data/training_data.csv')
    
    if os.path.exists(data_path):
        print(f"Loading training data from {data_path}...")
        df = pd.read_csv(data_path)
        if 'cleaned_text' not in df.columns:
            df['cleaned_text'] = df['text'].apply(clean_tweet)
    else:
        print("Creating training dataset...")
        df = create_training_data()
        # Save for future use
        os.makedirs('data', exist_ok=True)
        df.to_csv(data_path, index=False)
        print(f"Training data saved to {data_path}")
    
    print(f"\nTotal training samples: {len(df)}")
    print(f"Emergency samples: {df[df['label'] == 1].shape[0]}")
    print(f"Feedback samples: {df[df['label'] == 0].shape[0]}")
    
    # Prepare features and labels
    X = df['cleaned_text'].values
    y = df['label'].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Create TF-IDF vectorizer
    print("\nCreating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),  # Unigrams and bigrams
        min_df=1,
        max_df=0.95
    )
    
    # Fit and transform training data
    print("Vectorizing training data...")
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    # Train Logistic Regression model
    print("Training Logistic Regression model...")
    model = LogisticRegression(
        random_state=42,
        max_iter=1000,
        C=1.0,
        solver='lbfgs'
    )
    
    model.fit(X_train_tfidf, y_train)
    
    # Evaluate model
    print("\nEvaluating model...")
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n{'='*60}")
    print(f"Model Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"{'='*60}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Feedback', 'Emergency']))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"                Predicted")
    print(f"              Feedback  Emergency")
    print(f"Actual Feedback   {cm[0][0]:4d}      {cm[0][1]:4d}")
    print(f"       Emergency  {cm[1][0]:4d}      {cm[1][1]:4d}")
    
    # Test with sample predictions
    print("\n" + "="*60)
    print("Sample Predictions:")
    print("="*60)
    
    test_samples = [
        "train is delayed by 2 hours urgent help needed",
        "excellent service on railway thank you",
        "medical emergency in coach number 5",
        "thank you for the excellent food",
        "train breakdown passengers stranded",
        "comfortable journey smooth ride"
    ]
    
    for sample in test_samples:
        cleaned = clean_tweet(sample)
        X_sample = vectorizer.transform([cleaned])
        prediction = model.predict(X_sample)[0]
        proba = model.predict_proba(X_sample)[0]
        
        label = "Emergency" if prediction == 1 else "Feedback"
        confidence = proba[prediction] * 100
        
        print(f"\nText: {sample}")
        print(f"Prediction: {label} (Confidence: {confidence:.2f}%)")
    
    # Save model and vectorizer
    print("\n" + "="*60)
    print("Saving model...")
    print("="*60)
    
    os.makedirs('saved_model', exist_ok=True)
    
    model_path = os.path.join('saved_model', 'complaint_classifier_model.pkl')
    vectorizer_path = os.path.join('saved_model', 'tfidf_vectorizer.pkl')
    
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    
    print(f"[OK] Model saved to: {model_path}")
    print(f"[OK] Vectorizer saved to: {vectorizer_path}")
    print("\nModel training completed successfully!")
    print("="*60)

if __name__ == "__main__":
    train_model()

