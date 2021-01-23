"""Scraper."""

import pickle
import platform
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import InvalidCookieDomainException

BROWSER_DRIVER = {'Linux': {'Chrome': 'driver/chromedriver'},
                  'Windows': {'Chrome': 'driver\\chromedriver.exe'}}

CARRIERS = {'Alitalia': 'https://www.alitalia.com/it_it/homepage.html',
            'Lufthansa': 'https://www.lufthansa.com/it/it/homepage',
            'Ryanair': 'https://www.ryanair.com/it/it'}

ITALIAN_WEEKDAY = {0: 'lunedì', 1: 'martedì', 2: 'mecoledì', 3: 'giovedì', 4: 'venerdì', 5: 'sabato', 6: 'domenica'}

ITALIAN_MONTH = {1: 'gennaio', 2: 'febbraio', 3: 'marzo', 4: 'aprile', 5: 'maggio', 6: 'giugno',
                 7: 'luglio', 8: 'agosto', 9: 'settembre', 10: 'ottobre', 11: 'novembre', 12: 'dicembre'}


class Scraper(ABC):
    """Scraper class."""

    carrier = None

    def __init__(self, browser: str, itinerary: dict) -> None:
        """Init."""
        if browser not in BROWSER_DRIVER[platform.system()].keys():
            raise Exception(f'Allowed browsers are {BROWSER_DRIVER[platform.system()].keys()}')
        self.browser = browser
        self.itinerary = itinerary
        self.os = platform.system()
        self.driver = None
        self.driver_options = None
        self._load_configuration()

    def _load_configuration(self):
        """Load required configuration."""
        self._load_driver_options()
        self.driver = webdriver.Chrome(executable_path=BROWSER_DRIVER[self.os][self.browser],
                                       options=self.driver_options)
        # FIXME
        # self.driver.implicitly_wait(10)
        self._load_cookies()

    def _load_driver_options(self):
        """Load driver options."""
        self.driver_options = webdriver.ChromeOptions()
        self.driver_options.add_argument("start-maximized")

    def _load_cookies(self):
        """Load cookies from previous sessions."""
        try:
            cookies = pickle.load(open(f"cookies_jar/{self.carrier.lower()}_cookies.pkl", "rb"))
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except InvalidCookieDomainException:
                    continue
        except FileNotFoundError:
            print(f'{self.carrier.capitalize()} cookie file is missing.')
        finally:
            pass

    def save_cookies(self):
        """Save cookies for future sessions."""
        pickle.dump(self.driver.get_cookies(), open(f"cookies_jar/{self.carrier.lower()}_cookies.pkl", "wb"))

    def scrape(self):
        """Start scraping."""
        self.driver.get(CARRIERS[self.carrier])
        self.get_availability()
        self.get_price()
        self.save_cookies()

    @abstractmethod
    def get_availability(self):
        """Get availability."""

    @abstractmethod
    def get_price(self):
        """Get price."""

    def wait_for_element(self, by: By, expected_condition: expected_conditions, locator: str) -> WebElement:
        """Wait for element before fetch."""
        return WebDriverWait(self.driver, 15).until(expected_condition((by, locator)))
