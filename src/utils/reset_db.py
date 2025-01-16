import os
from db_handler import DatabaseHandler

def reset_database():
    """Utility function to reset the database when needed."""
    db_name = "daraz_reviews.db"
    
    # Remove existing database file
    if os.path.exists(db_name):
        try:
            os.remove(db_name)
            print(f"Existing database {db_name} removed.")
        except Exception as e:
            print(f"Error removing database: {e}")
            return
    
    # Initialize new database
    try:
        db = DatabaseHandler(db_name)
        print("New database initialized successfully.")
    except Exception as e:
        print(f"Error initializing new database: {e}")

if __name__ == "__main__":
    reset_database()
