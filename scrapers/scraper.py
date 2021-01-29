"""Abstract Scraper."""
import json
import logging
import os
import pickle
import platform
import time
from abc import ABC, abstractmethod
from amadeus import Client, ResponseError
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import InvalidCookieDomainException, NoSuchElementException, TimeoutException

BROWSER_DRIVER = {'Linux': {'Chrome': 'driver/chromedriver'},
                  'Windows': {'Chrome': 'driver\\chromedriver.exe'}}

ITALIAN_WEEKDAY = {0: 'lunedì', 1: 'martedì', 2: 'mecoledì', 3: 'giovedì', 4: 'venerdì', 5: 'sabato', 6: 'domenica'}

ITALIAN_MONTH = {1: 'gennaio', 2: 'febbraio', 3: 'marzo', 4: 'aprile', 5: 'maggio', 6: 'giugno',
                 7: 'luglio', 8: 'agosto', 9: 'settembre', 10: 'ottobre', 11: 'novembre', 12: 'dicembre'}


class Scraper(ABC):
    """Abstract scraper class."""

    carrier: str = NotImplemented
    carrier_url: str = NotImplemented

    def __init__(self, browser: str, itinerary: dict):
        """Init."""
        if browser not in BROWSER_DRIVER[platform.system()].keys():
            raise Exception(f'Allowed browsers are {BROWSER_DRIVER[platform.system()].keys()}')
        self.browser = browser
        self.itinerary = itinerary
        self.os = platform.system()
        self.driver: webdriver
        self.driver_options: webdriver
        self._load_configuration()

    def _load_configuration(self):
        """Load required configuration."""
        self._load_driver_options()
        self.driver = webdriver.Chrome(executable_path=BROWSER_DRIVER[self.os][self.browser],
                                       options=self.driver_options)
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
            logging.warning(f'{self.carrier} cookie file is missing.')
        finally:
            pass

    def save_cookies(self):
        """Save cookies for future sessions."""
        pickle.dump(self.driver.get_cookies(), open(f"cookies_jar/{self.carrier.lower()}_cookies.pkl", "wb"))

    def scrape(self):
        """Start scraping."""
        try:
            logging.info(f'Scraping {self.carrier}')
            start_time = time.time()
            self.driver.get(self.carrier_url)
            self.get_availability()
            self.get_price()
            self.save_cookies()
            self.driver.quit()
            logging.info(f'Getting {self.carrier} control price')
            self.get_control_price()
            logging.info(f'{self.carrier}: {round(time.time() - start_time)} sec')
        except (NoSuchElementException, TimeoutException):
            logging.error(f'{self.carrier} scraper crashed')

    @abstractmethod
    def get_availability(self):
        """Get availability."""

    @abstractmethod
    def get_price(self):
        """Get price."""

    def get_control_price(self):
        """Get control price."""
        try:
            amadeus = Client(client_id=os.environ['AMADEUS_API_KEY'], client_secret=os.environ['AMADEUS_API_SECRET'],
                             hostname='production')
            body = self.populate_amadeus_request_body()
            response = amadeus.shopping.flight_offers_search.post(body)
            flight = None
            for flight_element in response.data:
                if self.itinerary['departure_time'] in json.dumps(flight_element):
                    if self.itinerary['return_time'] in json.dumps(flight_element):
                        flight = flight_element
                        break
            self.itinerary.update({'control_price': flight['price']['grandTotal'],
                                   'seats_left': flight['numberOfBookableSeats']})
        except (ResponseError, KeyError) as error:
            logging.error(f'Amadeus API Error while scraping {self.carrier}: {error}')
            self.itinerary.update({'control_price': 'Error with Amadeus API'})

    def populate_amadeus_request_body(self) -> dict:
        """Populate the body for the Amadeus request."""
        day, month, year = self.itinerary['departure_date'].split('/')
        departure_date = f'{year}-{month}-{day}'
        day, month, year = self.itinerary['return_date'].split('/')
        return_date = f'{year}-{month}-{day}'
        body = {
            "currencyCode": "EUR",
            "originDestinations": [
                {
                    "id": "1",
                    "originLocationCode": self.itinerary['origin'],
                    "destinationLocationCode": self.itinerary['destination'],
                    "departureDateTimeRange": {
                        "date": departure_date,
                        "time": self.itinerary['departure_time'] + ':00',
                        "timeWindow": "1H"
                    }
                },
                {
                    "id": "2",
                    "originLocationCode": self.itinerary['destination'],
                    "destinationLocationCode": self.itinerary['origin'],
                    "departureDateTimeRange": {
                        "date": return_date,
                        "time": self.itinerary['return_time'] + ':00',
                        "timeWindow": "1H"
                    }
                }
            ],
            "travelers": [
                {
                    "id": "1",
                    "travelerType": "ADULT"
                },
                {
                    "id": "2",
                    "travelerType": "ADULT"
                },
            ],
            "sources": ["GDS"],
            "searchCriteria": {
                "flightFilters": {
                    "cabinRestrictions": [
                        {
                            "cabin": "ECONOMY",
                            "originDestinationIds": ["1", "2"]
                        }
                    ],
                    "carrierRestrictions": {
                        "includedCarrierCodes": ["AZ", "LH"]
                    }
                },
                "pricingOptions": {
                    "includedCheckedBagsOnly": True
                }
            }
        }
        return body

    def wait_for_element(self, by: By, expected_condition: expected_conditions, locator: str) -> WebElement:
        """Wait for element before fetch."""
        return WebDriverWait(self.driver, 60).until(expected_condition((by, locator)))
