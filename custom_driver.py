import os
import random
import time
from enum import Enum
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

def init_driver() -> webdriver.Chrome:
    """
    Initialize a Chrome WebDriver with optimizations and optional adblocker extension.

    :param adblock_path: Path to the adblocker .crx file, if available. Defaults to None.
    :return: Configured WebDriver instance.
    """
    max_retries = 5
    retries = 0

    while retries < max_retries:
        options = Options()
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')  
        options.page_load_strategy = 'eager'

        # Randomized user agent for better anonymity
        ua = UserAgent()
        user_agent = ua.chrome
        options.add_argument(f'user-agent={user_agent}')

        try:
            driver = webdriver.Chrome(options=options)
            print("Driver initialized successfully.")
            return driver

        except WebDriverException as e:
            print(f"Driver initialization failed: {str(e)}")
            retries += 1
            time.sleep(2)

    raise Exception("Max retries reached, unable to initialize a driver.")