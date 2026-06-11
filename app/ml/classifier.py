import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from pathlib import Path

# Model paths
MODEL_DIR = Path("app/ml/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

CATEGORY_MODEL_PATH = MODEL_DIR / "category_model.pkl"
PRIORITY_MODEL_PATH = MODEL_DIR / "priority_model.pkl"
VECTORIZER_PATH = MODEL_DIR / "vectorizer.pkl"

class TicketClassifier:
    def __init__(self):
        self.category_model = None
        self.priority_model = None
        self.vectorizer = None
        self.load_or_train()
    
    def load_or_train(self):
        """Load pre-trained models or train new ones."""
        if (CATEGORY_MODEL_PATH.exists() and 
            PRIORITY_MODEL_PATH.exists() and 
            VECTORIZER_PATH.exists()):
            self._load_models()
        else:
            self._train_models()
    
    def _load_models(self):
        """Load pre-trained models from disk."""
        with open(VECTORIZER_PATH, 'rb') as f:
            self.vectorizer = pickle.load(f)
        with open(CATEGORY_MODEL_PATH, 'rb') as f:
            self.category_model = pickle.load(f)
        with open(PRIORITY_MODEL_PATH, 'rb') as f:
            self.priority_model = pickle.load(f)
        print("✓ Models loaded from disk")
    
    def _train_models(self):
        """Train models on synthetic training data."""
        print("Training models on synthetic data...")
        
        # Synthetic training data
        training_texts = [
            # Network
            "Cannot connect to network", "Network is down", "Internet not working",
            "WiFi disconnected", "VPN connection failed", "Slow internet connection",
            "Router not responding", "DNS resolution error", "Network cable unplugged",
            "Unable to access corporate intranet",
            # Software
            "Software crashes on startup", "Application error", "Program not responding",
            "System freeze", "Memory leak", "Database connection error",
            "Software license expired", "Installation failed", "Excel macro not working",
            "Application throwing 500 error",
            # Hardware
            "Monitor not working", "Keyboard broken", "Mouse not responding",
            "Printer offline", "Hardware malfunction", "Laptop battery not charging",
            "Hard drive making noise", "Blue screen of death", "Overheating issues",
            "USB port not working",
            # Access
            "Cannot access file share", "Permission denied", "Login failed",
            "Account locked", "Access restricted", "Password reset required",
            "MFA token not working", "SSH access denied", "Folder permissions missing",
            "Unable to login to portal"
        ]
        
        categories = [
            "network"] * 10 + ["software"] * 10 + ["hardware"] * 10 + ["access"] * 10
        
        priorities = [
            "high", "critical", "high", "medium", "high", "medium", "medium", "high", "low", "high",
            "medium", "high", "high", "critical", "medium", "high", "low", "medium", "low", "high",
            "low", "low", "low", "medium", "medium", "high", "critical", "critical", "high", "medium",
            "high", "high", "high", "critical", "high", "medium", "high", "medium", "medium", "high"
        ]
        
        # Train vectorizer
        self.vectorizer = TfidfVectorizer(max_features=100, lowercase=True)
        X = self.vectorizer.fit_transform(training_texts)
        
        # Train category classifier
        self.category_model = MultinomialNB()
        self.category_model.fit(X, categories)
        
        # Train priority classifier
        self.priority_model = MultinomialNB()
        self.priority_model.fit(X, priorities)
        
        # Save models
        with open(VECTORIZER_PATH, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        with open(CATEGORY_MODEL_PATH, 'wb') as f:
            pickle.dump(self.category_model, f)
        with open(PRIORITY_MODEL_PATH, 'wb') as f:
            pickle.dump(self.priority_model, f)
        
        print("✓ Models trained and saved")
    
    def classify(self, subject: str, description: str):
        """
        Classify ticket and return category, priority, and confidence scores.
        
        Returns:
            tuple: (category, priority, category_confidence, priority_confidence)
        """
        # Combine subject and description
        text = f"{subject} {description}"
        
        # Vectorize
        X = self.vectorizer.transform([text])
        
        # Predict
        category = self.category_model.predict(X)[0]
        priority = self.priority_model.predict(X)[0]
        
        # Get confidence scores
        category_proba = self.category_model.predict_proba(X).max()
        priority_proba = self.priority_model.predict_proba(X).max()
        
        return category, priority, float(category_proba), float(priority_proba)

# Global classifier instance
_classifier = None

def get_classifier():
    """Get or initialize the global classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = TicketClassifier()
    return _classifier

def classify_ticket(subject: str, description: str):
    """Classify a ticket using the global classifier."""
    classifier = get_classifier()
    return classifier.classify(subject, description)

