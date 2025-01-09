import sqlite3
from typing import List, Dict
from datetime import datetime

class DatabaseHandler:
    def __init__(self, db_name: str = "daraz_reviews.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
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
            conn.commit()

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
