from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
from custom_driver import init_driver
from typing import List
from db_handler import DatabaseHandler
from typing import List, Dict

def extract_review_data(review_element) -> Dict:
    """Extract review data from a review element."""
    try:
        review_text = review_element.find_element(By.CLASS_NAME, 'content').text.strip()
        rating = None
        return {'text': review_text, 'rating': rating}
    except StaleElementReferenceException:
        return None

def scroll_to_load_reviews(driver, max_scrolls: int = 5):
    """Scroll the page to load more reviews."""
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

def scrape_reviews(url: str, driver, db: DatabaseHandler) -> List[str]:
    """
    Scrape reviews from a Daraz product page and save them to the database.
    """
    try:
        driver.get(url)
        product_id = db.add_product(url)

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'item-content'))
        )

        scroll_to_load_reviews(driver)

        reviews_data = []
        review_elements = driver.find_elements(By.CLASS_NAME, 'item-content')

        for review_elem in review_elements:
            review_data = extract_review_data(review_elem)
            if review_data and review_data['text']:
                reviews_data.append(review_data)
                print(f"Found review: {review_data['text'][:50]}...")

        if reviews_data:
            db.add_reviews(product_id, reviews_data)
            print(f"Saved {len(reviews_data)} reviews to database")
            return reviews_data
        else:
            print("No reviews found")

    except TimeoutException:
        print("Timeout while waiting for the reviews section to load.")
    except Exception as e:
        print(f"An error occurred while scraping: {str(e)}")

def get_reviews(url: str = "https://www.daraz.pk/products/-i433806826-s2091231443.html") -> List[str]:
    db = DatabaseHandler()
    
    driver = init_driver()

    try:
        product_url = url
        
        return scrape_reviews(product_url, driver, db)
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()