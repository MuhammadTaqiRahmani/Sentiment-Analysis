from textblob import TextBlob

def analyze_review(review):
    """
    Analyzes the sentiment of a given review and returns a rating.
    
    Parameters:
    review (str): The review text to analyze.

    Returns:
    str: Sentiment rating - 'Very Good', 'Neutral', or 'Very Bad'.
    """
    analysis = TextBlob(review)
    polarity = analysis.sentiment.polarity

    if polarity > 0.1:
        return 'Very Good'
    elif polarity < -0.1:
        return 'Very Bad'
    else:
        return 'Neutral'