import sqlite3
from typing import List, Dict
from datetime import datetime
import json
import os

class DatabaseHandler:
    def __init__(self, db_name: str = "daraz_reviews.db"):
        self.db_name = db_name
        # Only initialize the database if it doesn't exist
        if not os.path.exists(self.db_name):
            self.init_database()

    def init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Create tables only if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    last_scraped TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    review_text TEXT NOT NULL,
                    rating INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    product_name TEXT,
                    sentiment_counts TEXT,
                    average_rating FLOAT,
                    review_count INTEGER,
                    reviews TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("Database initialized successfully.")

    # Remove the reset_database method since we don't want to drop tables anymore

    def add_product(self, url: str) -> int:
        """Add a product URL and return its ID."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO products (url, last_scraped) VALUES (?, ?)",
                (url, datetime.now())
            )
            cursor.execute("SELECT id FROM products WHERE url = ?", (url,))
            return cursor.fetchone()[0]

    def add_reviews(self, product_id: int, reviews: List[Dict]):
        """Add multiple reviews for a product."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO reviews (product_id, review_text, rating) VALUES (?, ?, ?)",
                [(product_id, review['text'], review.get('rating')) for review in reviews]
            )
            cursor.execute(
                "UPDATE products SET last_scraped = ? WHERE id = ?",
                (datetime.now(), product_id)
            )
            conn.commit()

    def get_reviews(self, product_id: int) -> List[Dict]:
        """Retrieve all reviews for a product."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT review_text, rating, timestamp FROM reviews WHERE product_id = ?",
                (product_id,)
            )
            return [
                {'text': row[0], 'rating': row[1], 'timestamp': row[2]}
                for row in cursor.fetchall()
            ]

    def add_analysis(self, url: str, results: dict):
        """Add analysis results to the history."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO analysis_history 
                    (url, product_name, sentiment_counts, average_rating, review_count, reviews, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    url,
                    results['product_name'],
                    json.dumps(results['sentiment_counts']),
                    results['average_rating'],
                    results['total_reviews'],
                    json.dumps(results.get('reviews', [])),
                    datetime.now()
                ))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                raise

    def get_analyses(self, page: int, per_page: int):
        """Retrieve paginated analysis history."""
        offset = (page - 1) * per_page
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM analysis_history 
                ORDER BY timestamp DESC 
                LIMIT ? OFFSET ?
            ''', (per_page, offset))
            
            analyses = []
            for row in cursor.fetchall():
                try:
                    timestamp = datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    timestamp = datetime.now()

                # Parse sentiment data
                sentiment_counts = json.loads(row[3])
                most_common_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0]

                analyses.append({
                    'id': row[0],
                    'url': row[1],
                    'product_name': row[2],
                    'sentiment_counts': sentiment_counts,
                    'most_common_sentiment': most_common_sentiment,  # Add this field
                    'average_rating': row[4],
                    'review_count': row[5],
                    'timestamp': timestamp
                })
            return analyses

    def get_total_pages(self, per_page: int):
        """Get total number of pages for analysis history."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM analysis_history')
            total_records = cursor.fetchone()[0]
            return (total_records + per_page - 1) // per_page

    def delete_analysis(self, analysis_id: int):
        """Delete an analysis record by ID."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM analysis_history WHERE id = ?', (analysis_id,))
            conn.commit()