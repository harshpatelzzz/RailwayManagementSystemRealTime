"""
ML Model Predictor Module
Loads trained ML model and provides prediction functions
"""

import os
import joblib
from sparksupport import clean_tweet

class MLPredictor:
    """Machine Learning Model Predictor"""
    
    def __init__(self, model_path=None, vectorizer_path=None):
        """
        Initialize ML Predictor
        
        Args:
            model_path: Path to saved model (.pkl file)
            vectorizer_path: Path to saved vectorizer (.pkl file)
        """
        self.model = None
        self.vectorizer = None
        self.model_loaded = False
        
        # Default paths
        if model_path is None:
            model_path = os.path.join('saved_model', 'complaint_classifier_model.pkl')
        if vectorizer_path is None:
            vectorizer_path = os.path.join('saved_model', 'tfidf_vectorizer.pkl')
        
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        
        # Try to load model
        self.load_model()
    
    def load_model(self):
        """Load ML model and vectorizer from disk"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
                print(f"Loading ML model from {self.model_path}...")
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vectorizer_path)
                self.model_loaded = True
                print("[OK] ML model loaded successfully!")
                return True
            else:
                print(f"[WARNING] ML model files not found at:")
                print(f"   Model: {self.model_path}")
                print(f"   Vectorizer: {self.vectorizer_path}")
                print("   Using rule-based classification as fallback.")
                return False
        except Exception as e:
            print(f"[ERROR] Error loading ML model: {e}")
            print("   Using rule-based classification as fallback.")
            return False
    
    def predict(self, text):
        """
        Predict complaint classification using ML model
        
        Args:
            text: Complaint text
            
        Returns:
            tuple: (prediction, confidence, method)
                - prediction: 0 (Feedback) or 1 (Emergency)
                - confidence: float between 0 and 1
                - method: 'ml' if ML model used, 'rule_based' if fallback
        """
        if not self.model_loaded or self.model is None or self.vectorizer is None:
            # Fallback to rule-based
            from sparksupport import classify_urgency
            prediction = classify_urgency(text)
            return prediction, 0.5, 'rule_based'
        
        try:
            # Clean text
            cleaned_text = clean_tweet(text)
            
            # Vectorize
            X = self.vectorizer.transform([cleaned_text])
            
            # Predict
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            confidence = probabilities[prediction]
            
            return int(prediction), float(confidence), 'ml'
        
        except Exception as e:
            print(f"[WARNING] Error in ML prediction: {e}, using rule-based fallback")
            from sparksupport import classify_urgency
            prediction = classify_urgency(text)
            return prediction, 0.5, 'rule_based'
    
    def is_available(self):
        """Check if ML model is loaded and available"""
        return self.model_loaded and self.model is not None and self.vectorizer is not None

# Global instance (singleton pattern)
_predictor_instance = None

def get_predictor():
    """Get global ML predictor instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = MLPredictor()
    return _predictor_instance

def classify_urgency_ml(text):
    """
    Classify urgency using ML model (with rule-based fallback)
    
    Args:
        text: Complaint text
        
    Returns:
        int: 0 (Feedback) or 1 (Emergency)
    """
    predictor = get_predictor()
    prediction, confidence, method = predictor.predict(text)
    return prediction

