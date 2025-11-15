"""
Train Machine Learning Model for Tweet Classification
Classifies tweets as Emergency (1) or Feedback (0)
"""

from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from sparksupport import create_spark_session, clean_tweet_udf
import os

def load_training_data(spark, data_path):
    """Load training data from CSV or JSON"""
    try:
        if data_path.endswith('.csv'):
            df = spark.read.csv(data_path, header=True, inferSchema=True)
        elif data_path.endswith('.json'):
            df = spark.read.json(data_path)
        else:
            raise ValueError("Unsupported file format")
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def create_training_pipeline():
    """Create ML pipeline for tweet classification"""
    
    # Tokenize tweets
    tokenizer = Tokenizer(inputCol="cleaned_text", outputCol="words")
    
    # Remove stop words
    remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
    
    # Convert words to features using HashingTF
    hashingTF = HashingTF(inputCol="filtered_words", outputCol="rawFeatures", numFeatures=1000)
    
    # Apply IDF
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    
    # Logistic Regression classifier
    lr = LogisticRegression(featuresCol="features", labelCol="label", maxIter=100)
    
    # Create pipeline
    pipeline = Pipeline(stages=[tokenizer, remover, hashingTF, idf, lr])
    
    return pipeline

def train_model():
    """Main training function"""
    
    # Create Spark session
    spark = create_spark_session("TweetClassificationTraining")
    
    print("Loading training data...")
    
    # Load training data
    # Update path to your training data
    data_path = os.getenv('TRAINING_DATA_PATH', 'data/training_data.csv')
    
    df = load_training_data(spark, data_path)
    
    if df is None:
        print("Creating sample training data...")
        # Create sample data if no training data exists
        from pyspark.sql.types import StructType, StructField, StringType, IntegerType
        
        schema = StructType([
            StructField("tweet", StringType(), True),
            StructField("label", IntegerType(), True)
        ])
        
        sample_data = [
            ("train is delayed urgent help needed", 1),
            ("excellent service on railway", 0),
            ("accident on track emergency", 1),
            ("thank you for good service", 0),
            ("train breakdown help required", 1),
            ("comfortable journey", 0),
            ("medical emergency in train", 1),
            ("clean and tidy coach", 0)
        ]
        
        df = spark.createDataFrame(sample_data, schema)
    
    # Clean tweets
    df = df.withColumn("cleaned_text", clean_tweet_udf(col("tweet")))
    
    # Split data into training and testing sets
    (training_data, test_data) = df.randomSplit([0.8, 0.2], seed=42)
    
    print(f"Training samples: {training_data.count()}")
    print(f"Test samples: {test_data.count()}")
    
    # Create and train pipeline
    print("Creating ML pipeline...")
    pipeline = create_training_pipeline()
    
    print("Training model...")
    model = pipeline.fit(training_data)
    
    # Make predictions on test data
    print("Evaluating model...")
    predictions = model.transform(test_data)
    
    # Evaluate model
    evaluator = BinaryClassificationEvaluator(labelCol="label")
    accuracy = evaluator.evaluate(predictions)
    
    print(f"Model Accuracy: {accuracy:.4f}")
    
    # Save model
    model_path = os.getenv('MODEL_PATH', 'saved_model/tweet_classifier_model')
    print(f"Saving model to {model_path}...")
    model.write().overwrite().save(model_path)
    
    print("Model training completed successfully!")
    
    spark.stop()

if __name__ == "__main__":
    train_model()

