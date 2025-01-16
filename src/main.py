import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from scraper import get_reviews
from collections import Counter

# Load the sentiment analysis model and tokenizer
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

def evaluate_sentiment(text: str) -> str:
    """Evaluate the sentiment of a given text."""
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_sentiment = torch.argmax(logits, dim=-1).item()
    sentiment_mapping = {
        0: "1 star (very negative)",
        1: "2 stars (negative)",
        2: "3 stars (neutral)",
        3: "4 stars (positive)",
        4: "5 stars (very positive)"
    }
    return sentiment_mapping[predicted_sentiment]

def calculate_sentiment_stats(sentiments: list) -> dict:
    """Calculate sentiment statistics from a list of sentiment ratings."""
    # Convert text ratings to numerical values for averaging
    sentiment_to_score = {
        "1 star (very negative)": 1,
        "2 stars (negative)": 2,
        "3 stars (neutral)": 3,
        "4 stars (positive)": 4,
        "5 stars (very positive)": 5
    }
    
    scores = [sentiment_to_score[s] for s in sentiments]
    sentiment_counts = Counter(sentiments)
    total = len(sentiments)
    
    return {
        "average_score": sum(scores) / len(scores),
        "sentiment_distribution": {k: (v/total)*100 for k, v in sentiment_counts.items()},
        "most_common": sentiment_counts.most_common(1)[0][0]
    }

def process_reviews(url: str = "https://www.daraz.pk/products/-i433806826-s2091231443.html"):
    """Process reviews from a given URL and analyze their sentiment."""
    reviews = get_reviews(url)
    
    if not reviews:
        return None

    sentiments = []
    processed_reviews = []
    
    for review in reviews:
        sentiment = evaluate_sentiment(review['text'])
        sentiments.append(sentiment)
        processed_reviews.append({
            'text': review['text'],
            'sentiment': sentiment
        })
    
    # Calculate sentiment statistics
    stats = calculate_sentiment_stats(sentiments)
    
    return {
        'average_score': stats['average_score'],
        'sentiment_distribution': stats['sentiment_distribution'],
        'most_common': stats['most_common'],
        'reviews': processed_reviews
    }

