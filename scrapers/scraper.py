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
from selenium.common.exceptions import InvalidCookieDomainException, NoSuchElementException, TimeoutException, \
    StaleElementReferenceException, ElementNotInteractableException
from tools.spreadsheet_tool import export_to_csv

BROWSER_DRIVER = {'Linux': {'Chrome': os.path.join('drivers', 'chromedriver')},
                  'Windows': {'Chrome': os.path.join('drivers', 'chromedriver.exe')}}

ITALIAN_WEEKDAY = {0: 'lunedì', 1: 'martedì', 2: 'mecoledì', 3: 'giovedì', 4: 'venerdì', 5: 'sabato', 6: 'domenica'}

ITALIAN_MONTH = {1: 'gennaio', 2: 'febbraio', 3: 'marzo', 4: 'aprile', 5: 'maggio', 6: 'giugno',
                 7: 'luglio', 8: 'agosto', 9: 'settembre', 10: 'ottobre', 11: 'novembre', 12: 'dicembre'}

AIRLINE_CODES = {'Airfrance': 'AF', 'Alitalia': 'AZ', 'Lufthansa': 'LH', 'Ryanair': 'FR'}


class Scraper(ABC):
    """Abstract scraper class."""

    carrier_url: str = NotImplemented
    carrier_dcc: float = NotImplemented  # GDS Distribution Cost Charge per passenger

    def __init__(self, user: dict, selenium_browser: str, itinerary: dict,
                 run_with_cookies: bool = True, export: bool = True):
        """Init."""
        if selenium_browser not in BROWSER_DRIVER[platform.system()].keys():
            raise Exception(f'Allowed browsers are {BROWSER_DRIVER[platform.system()].keys()}')
        self.selenium_browser = selenium_browser
        self.user = user
        self.itinerary = itinerary
        self.run_with_cookies = run_with_cookies
        self.export = export
        self.carrier = itinerary['carrier']
        self.identifier = f'{self.carrier} | {self.user["user"]}'
        self.os = platform.system()
        self.driver: webdriver
        self.driver_options: webdriver
        self._load_configuration()

    def _load_configuration(self):
        """Load required configuration."""
        self._load_driver_options()
        self.driver = webdriver.Chrome(executable_path=BROWSER_DRIVER[self.os][self.selenium_browser],
                                       options=self.driver_options)
        if self.run_with_cookies:
            self._load_cookies()

    def _load_driver_options(self):
        """Load driver options."""
        self.driver_options = webdriver.ChromeOptions()
        self.driver_options.add_argument("start-maximized")
        self.driver_options.add_argument(f"user-agent={self.user['user_agent']}")

    def _load_cookies(self):
        """Load cookies from previous sessions."""
        try:
            cookie_jar_path = os.path.join(
                f'{self.user["cookie_jar"]}', f'{self.user["user"].lower()}_{self.carrier.lower()}_cookies.pkl')
            cookies = pickle.load(open(cookie_jar_path, "rb"))
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except InvalidCookieDomainException:
                    continue
        except FileNotFoundError:
            logging.warning(f'{self.identifier} | Cookie file is missing.')

    def save_cookies(self):
        """Save cookies for future sessions."""
        cookie_jar_path = os.path.join(
            f'{self.user["cookie_jar"]}', f'{self.user["user"].lower()}_{self.carrier.lower()}_cookies.pkl')
        pickle.dump(self.driver.get_cookies(), open(cookie_jar_path, "wb"))

    def scrape(self):
        """Start scraping."""
        try:
            logging.info(f'{self.identifier} | Scraping')
            start_time = time.time()
            self.driver.get(self.carrier_url)
            self.get_availability()
            self.get_price()
            if self.run_with_cookies:
                self.save_cookies()
            if self.export:
                logging.info(f'{self.identifier} | Getting control price')
                self.get_control_price()
                logging.info(f'{self.identifier} | Exporting data to spreadsheet')
                export_to_csv(self)
                logging.info(f'{self.identifier} | Completed in {round(time.time() - start_time)} sec')
            self.driver.quit()
        # HACK: for testing
        # except ValueError as error:
        except (NoSuchElementException, TimeoutException, StaleElementReferenceException,
                ElementNotInteractableException) as error:
            logging.error(f'{self.identifier} | Scraper crashed: {error.__class__.__name__} > {error}')
            self.driver.quit()

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
            self.itinerary.update(
                {'control_price': flight['price']['grandTotal'],
                 'seats_left': flight['numberOfBookableSeats'],
                 'dep_control_fare_basis': flight['travelerPricings'][0]['fareDetailsBySegment'][0]['fareBasis'],
                 'ret_control_fare_basis': flight['travelerPricings'][0]['fareDetailsBySegment'][1]['fareBasis']})
        except (ResponseError, KeyError) as error:
            logging.error(f'{self.identifier} | Amadeus API Error while scraping: {error.__class__.__name__} > {error}')
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
                }
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
                        "includedCarrierCodes": [f"{AIRLINE_CODES[self.carrier]}"]
                    },
                    "connectionRestriction": {
                        "maxNumberOfConnections": 0
                    }
                },
                "pricingOptions": {
                    "includedCheckedBagsOnly": False
                }
            }
        }
        return body

    def wait_for_element(self, by: By, expected_condition: expected_conditions, locator: str) -> WebElement:
        """Wait for element before fetch."""
        return WebDriverWait(self.driver, 30).until(expected_condition((by, locator)))
