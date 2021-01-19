"""Scraper Class."""
import browser_cookie3
import pickle
import platform
import time
import webbrowser
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import InvalidCookieDomainException

from itineraries import ITINERARIES


BROWSER_DRIVER = {'Linux': {'Chrome': 'driver/chromedriver'},
                  'Windows': {'Chrome': 'driver\chromedriver.exe'}}

CARRIERS = {'Alitalia': 'https://www.alitalia.com/it_it/homepage.html',
            'Lufthansa': 'https://www.lufthansa.com/it/it/homepage',
            'Ryanair': 'https://www.ryanair.com/it/it'}


class Scraper:
    """Scraper class."""

    def __init__(self, carrier: str, browser: str, itinerary: dict) -> None:
        """Init."""
        if carrier not in CARRIERS.keys():
            raise Exception(f'Allowed carriers are {CARRIERS.keys()}')
        if browser not in BROWSER_DRIVER[platform.system()].keys():
            raise Exception(f'Allowed browsers are {BROWSER_DRIVER[platform.system()].keys()}')
        self.carrier = carrier
        self.browser = browser
        self.itinerary = itinerary
        self.search_result = {'outbound': None, 'inbound': None}
        self.os = platform.system()
        self.driver = None
        self.driver_options = None
        self._load_configuration()

    def _load_configuration(self):
        """Load required configuration."""
        self._load_driver_options()
        self.driver = webdriver.Chrome(executable_path=BROWSER_DRIVER[self.os][self.browser],
                                       options=self.driver_options)
        # self.driver.implicitly_wait(10)
        self._load_cookies()

    def _load_driver_options(self):
        """Load driver options."""
        self.driver_options = webdriver.ChromeOptions()
        self.driver_options.add_argument("start-maximized")

    def _load_cookies(self):
        """Load cookies from previous sessions."""
        try:
            cookies = pickle.load(open("cookies_jar/cookies.pkl", "rb"))
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except InvalidCookieDomainException:
                    continue
        except FileNotFoundError:
            print('Cookie jar is empty.')

    def save_cookies(self):
        """Save cookies for future sessions."""
        pickle.dump(self.driver.get_cookies(), open("cookies_jar/cookies.pkl", "wb"))

    def scrape(self):
        """Start scraping."""
        if self.carrier == 'Alitalia':
            self.scrape_alitalia()
        elif self.carrier == 'Lufthansa':
            self.scrape_lufthansa()
        elif self.carrier == 'Ryanair':
            self.scrape_ryanair()

    def scrape_alitalia(self):
        """Scrape Alitalia."""
        self.driver.get(CARRIERS[self.carrier])
        self.get_alitalia_availability()
        self.get_alitalia_price()
        self.save_cookies()

    def get_alitalia_availability(self):
        """Get Alitalia availability."""
        origin_selector = self.driver.find_element_by_id('luogo-partenza--prenota-desk')
        destination_selector = self.driver.find_element_by_id('luogo-arrivo--prenota-desk')
        departure_date_selector = self.driver.find_element_by_id('data-andata--prenota-desk')
        return_date_selector = self.driver.find_element_by_id('data-ritorno--prenota-desk')
        ###
        origin_selector.clear()
        origin_selector.send_keys(self.itinerary['origin'])
        destination_selector.send_keys(self.itinerary['destination'])
        departure_date_selector.send_keys(self.itinerary['departure_date'])
        return_date_selector.send_keys(self.itinerary['return_date'])
        ###
        validate_date_button = self.driver.find_element_by_id('validate_date')
        validate_date_button.click()
        add_passenger_button = self.driver.find_element_by_id('addAdults')
        add_passenger_button.click()
        ###
        ak_bmsc_cookie = self.driver.get_cookie('ak_bmsc')
        ak_bmsc_cookie['value'] = self.get_ak_bmsc_valid_value()
        time.sleep(3)
        self.driver.delete_cookie('ak_bmsc')
        self.driver.add_cookie(ak_bmsc_cookie)
        ###
        search_button = self.driver.find_element_by_id('submitHidden--prenota')
        search_button.click()

    def get_ak_bmsc_valid_value(self) -> str:
        """Get valid value for ak_bmsc cookie."""
        webbrowser.open_new_tab(CARRIERS[self.carrier])
        cookie_jar = browser_cookie3.chrome()
        # os.system("pkill chrome")
        ak_bmsc_new_value = None
        for cookie in cookie_jar:
            if 'alitalia' in cookie.domain:
                if cookie.name == 'ak_bmsc':
                    ak_bmsc_new_value = cookie.value
        return ak_bmsc_new_value.replace('+', ' ')

    def get_alitalia_price(self):
        """Get price for selected flight."""
        outbound = self.wait_for_element(By.CSS_SELECTOR, EC.presence_of_element_located,
                                         f'[data-flight-time=\"{self.itinerary["departure_time"]}\"]'
                                         f'[data-flight-brandname=\"{self.itinerary["fare_brand"]}\"]')
        self.itinerary.update({'outbound_price': outbound.get_attribute('data-flight-price'),
                               'outbound_flight_number': outbound.get_attribute('data-flight-number')})
        outbound.find_element_by_class_name('fakeRadio').click()
        time.sleep(5)
        select_button = self.wait_for_element(By.CSS_SELECTOR, EC.element_to_be_clickable,
                                              '[class="firstButton j-goToReturn"]')
        select_button.click()
        time.sleep(10)
        inbound = self.wait_for_element(By.CSS_SELECTOR, EC.presence_of_element_located,
                                        f'[data-flight-time=\"{self.itinerary["return_time"]}\"]'
                                        f'[data-flight-brandname=\"{self.itinerary["fare_brand"]}\"]')
        self.itinerary.update({'inbound_price': inbound.get_attribute('data-flight-price'),
                               'inbound_flight_number': inbound.get_attribute('data-flight-number')})
        inbound.find_element_by_class_name('fakeRadio').click()
        time.sleep(5)
        select_button = self.wait_for_element(By.CSS_SELECTOR, EC.element_to_be_clickable,
                                              '[class="firstButton j-selectReturn"]')
        select_button.click()

    def scrape_lufthansa(self):
        """Scrape Lufthansa."""
        self.driver.get(CARRIERS[self.carrier])

    def scrape_ryanair(self):
        """Scrape Ryanair."""
        self.driver.get(CARRIERS[self.carrier])

    def wait_for_element(self, by: By, expected_condition: EC, locator: str) -> WebElement:
        """Wait for element before fetch."""
        return WebDriverWait(self.driver, 10).until(expected_condition((by, locator)))


if __name__ == '__main__':
    start_time = time.time()
    alitalia_scraper = Scraper(carrier='Alitalia', browser='Chrome', itinerary=ITINERARIES[0])
    alitalia_scraper.scrape()
    print(alitalia_scraper.itinerary)
    print('\n', 'Elapsed time:', round(time.time() - start_time, 2), 'sec')
