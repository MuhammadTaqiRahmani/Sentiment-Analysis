import os
import random
import time
from enum import Enum
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

class Direction(Enum):
    FORWARD = 1
    BACKWARD = 0

class Status(Enum):
    SUCCESS = 0
    FAILURE = 1

class URLElement:
    def __init__(self, url: str, url_id: str, url_class: str) -> None:
        """
        A class to encapsulate URLs with their class and id attributes.
        :param url: str     |   The URL of the page
        :param url_id:      |   The ID of the URL href
        :param url_class:   |   The class of the URL href
        """
        self.url = url
        self.url_id = url_id
        self.url_class = url_class

    def __str__(self) -> str:
        return f"\n{self.url}\nID: {self.url_id}\nClass:{self.url_class}"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self):
        return {"url": self.url, "url_id": self.url_id, "url_class": self.url_class}

def get_current_ip(driver):
    """
    Get the current IP address being used by the WebDriver.

    :param driver: The WebDriver instance.
    :return: The IP address as a string.
    """
    driver.get("https://api.ipify.org")  # Use a service to get the IP address
    ip_element = driver.find_element(By.TAG_NAME, "pre")
    return ip_element.text

def init_driver(adblock_path: str = None) -> webdriver.Chrome:
    """
    Initialize a Chrome WebDriver with optimizations and optional adblocker extension.

    :param adblock_path: Path to the adblocker .crx file, if available. Defaults to None.
    :return: Configured WebDriver instance.
    """
    max_retries = 5
    retries = 0

    while retries < max_retries:
        options = Options()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
        options.page_load_strategy = 'eager'

        # Randomized user agent for better anonymity
        ua = UserAgent()
        user_agent = ua.chrome
        options.add_argument(f'user-agent={user_agent}')

        # Disable images and CSS for performance optimization
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.cookies": 2,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.popups": 2,
        }
        options.add_experimental_option("prefs", prefs)

        # Add uBlock Origin adblocker extension if the path is provided
        if adblock_path and os.path.exists(adblock_path):
            options.add_extension(adblock_path)

        try:
            driver = webdriver.Chrome(options=options)
            print("Driver initialized successfully.")
            return driver

        except WebDriverException as e:
            print(f"Driver initialization failed: {str(e)}")
            retries += 1
            time.sleep(2)

    raise Exception("Max retries reached, unable to initialize a driver.")