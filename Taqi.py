import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import json  # Import json to load reviews from a file
from Scrapper import main as scrape_reviews_main  # Import the main function from Scrapper.py

# Load the sentiment analysis model and tokenizer
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
model = AutoModelForSequenceClassification.from_pretrained(model_name)  # Correct class
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

def main():
    # Get the scraped reviews by calling the main function from Scrapper.py
    reviews = scrape_reviews_main()

    # Evaluate the sentiment of the reviews
    for review in reviews:
        sentiment = evaluate_sentiment(review['text'])
        print(f"Review: {review['text'][:50]}... Sentiment: {sentiment}")

if __name__ == "__main__":
    main()


