import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from Scraper import get_reviews
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
        print("No reviews found to analyze")
        return

    print(f"\nAnalyzing {len(reviews)} reviews...\n")
    
    sentiments = []
    for review in reviews:
        sentiment = evaluate_sentiment(review['text'])
        sentiments.append(sentiment)
        print(f"\nReview: {review['text'][:100]}...")
        print(f"Sentiment: {sentiment}")
    
    # Calculate and display sentiment statistics
    stats = calculate_sentiment_stats(sentiments)
    print("\n=== Sentiment Analysis Summary ===")
    print(f"Average Rating: {stats['average_score']:.1f} / 5.0")
    print(f"Most Common Sentiment: {stats['most_common']}")
    print("\nSentiment Distribution:")
    for sentiment, percentage in stats['sentiment_distribution'].items():
        print(f"{sentiment}: {percentage:.1f}%")

if __name__ == "__main__":
    target_url = "https://www.daraz.pk/products/-i433806826-s2091231443.html"
    process_reviews(target_url)