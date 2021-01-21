"""Scraper Class."""
import browser_cookie3
import datetime
import pickle
import platform
import time
import webbrowser
from selenium import webdriver
# from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import InvalidCookieDomainException

from itineraries import ITINERARIES_ALITALIA, ITINERARIES_LUFTHANSA

BROWSER_DRIVER = {'Linux': {'Chrome': 'driver/chromedriver'},
                  'Windows': {'Chrome': 'driver\\chromedriver.exe'}}

CARRIERS = {'Alitalia': 'https://www.alitalia.com/it_it/homepage.html',
            'Lufthansa': 'https://www.lufthansa.com/it/it/homepage',
            'Ryanair': 'https://www.ryanair.com/it/it'}

ITALIAN_WEEKDAY = {0: 'lunedì', 1: 'martedì', 2: 'mecoledì', 3: 'giovedì', 4: 'venerdì', 5: 'sabato', 6: 'domenica'}

ITALIAN_MONTH = {1: 'gennaio', 2: 'febbraio', 3: 'marzo', 4: 'aprile', 5: 'maggio', 6: 'giugno',
                 7: 'luglio', 8: 'agosto', 9: 'settembre', 10: 'ottobre', 11: 'novembre', 12: 'dicembre'}


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
        # Get search parameters handlers #
        origin_selector = self.driver.find_element_by_id('luogo-partenza--prenota-desk')
        destination_selector = self.driver.find_element_by_id('luogo-arrivo--prenota-desk')
        departure_date_selector = self.driver.find_element_by_id('data-andata--prenota-desk')
        return_date_selector = self.driver.find_element_by_id('data-ritorno--prenota-desk')
        # Input search parameters #
        origin_selector.clear()
        origin_selector.send_keys(self.itinerary['origin'])
        destination_selector.send_keys(self.itinerary['destination'])
        departure_date_selector.send_keys(self.itinerary['departure_date'])
        return_date_selector.send_keys(self.itinerary['return_date'])
        validate_date_button = self.driver.find_element_by_id('validate_date')
        validate_date_button.click()
        add_passenger_button = self.driver.find_element_by_id('addAdults')
        add_passenger_button.click()
        # Replace bot detection cookie with valid one to continue #
        ak_bmsc_cookie = self.driver.get_cookie('ak_bmsc')
        ak_bmsc_cookie['value'] = self.get_ak_bmsc_valid_value()
        time.sleep(5)
        self.driver.delete_cookie('ak_bmsc')
        self.driver.add_cookie(ak_bmsc_cookie)
        # Submit search #
        submit_button = self.driver.find_element_by_id('submitHidden--prenota')
        submit_button.click()

    def get_ak_bmsc_valid_value(self) -> str:
        """Get valid value for ak_bmsc cookie."""
        webbrowser.open_new_tab(CARRIERS[self.carrier])
        cookie_jar = browser_cookie3.chrome()
        # os.system("pkill chrome")
        ak_bmsc_new_value = None
        for cookie in cookie_jar:
            if self.carrier.lower() in cookie.domain:
                if cookie.name == 'ak_bmsc':
                    ak_bmsc_new_value = cookie.value
        return ak_bmsc_new_value.replace('+', ' ')

    def get_alitalia_price(self):
        """Get price for selected flight."""
        # Get departure price #
        departure_node = self.wait_for_element(By.CSS_SELECTOR, EC.presence_of_element_located,
                                               f'[data-flight-time=\"{self.itinerary["departure_time"]}\"]'
                                               f'[data-flight-brandname=\"{self.itinerary["fare_brand"]}\"]')
        self.itinerary.update({'departure_price': departure_node.get_attribute('data-flight-price'),
                               'departure_flight_number': departure_node.get_attribute('data-flight-number')})
        departure_node.find_element_by_class_name('fakeRadio').click()
        time.sleep(5)
        select_button = self.wait_for_element(By.CSS_SELECTOR, EC.element_to_be_clickable,
                                              '[class="firstButton j-goToReturn"]')
        select_button.click()
        time.sleep(10)
        # Get return price #
        return_node = self.wait_for_element(By.CSS_SELECTOR, EC.presence_of_element_located,
                                            f'[data-flight-time=\"{self.itinerary["return_time"]}\"]'
                                            f'[data-flight-brandname=\"{self.itinerary["fare_brand"]}\"]')
        self.itinerary.update({'inbound_price': return_node.get_attribute('data-flight-price'),
                               'inbound_flight_number': return_node.get_attribute('data-flight-number')})
        return_node.find_element_by_class_name('fakeRadio').click()
        time.sleep(5)
        select_button = self.wait_for_element(By.CSS_SELECTOR, EC.element_to_be_clickable,
                                              '[class="firstButton j-selectReturn"]')
        select_button.click()

    def scrape_lufthansa(self):
        """Scrape Lufthansa."""
        self.driver.get(CARRIERS[self.carrier])
        self.get_lufthansa_availability()
        self.get_lufthansa_price()
        self.save_cookies()

    def get_lufthansa_availability(self):
        """Get Lufthansa availability."""
        self.driver.find_element_by_id('cm-acceptAll').click()
        # Input origin airport #
        origin_selector = self.driver.find_element_by_name('flightQuery.flightSegments[0].originCode')
        origin_selector.click()
        origin_selector.send_keys(Keys.CONTROL + "a" + Keys.DELETE)
        origin_selector.send_keys(self.itinerary['origin'])
        time.sleep(2)
        # Input destination airport #
        destination_selector = self.driver.find_element_by_name('flightQuery.flightSegments[0].destinationCode')
        destination_selector.click()
        destination_selector.send_keys(self.itinerary['destination'])
        time.sleep(2)
        # Input departure date #
        self.driver.find_element_by_name('flightQuery.flightSegments[0].travelDatetime').click()
        italian_weekday, day, month, year = self.format_date(self.itinerary['departure_date'])
        self.scroll_to_month(month)
        departure_date = self.driver.find_element_by_css_selector(
            f'[aria-label="Choose {italian_weekday}, {day} {month} {year} as your check-in date. It\'s available."]')
        departure_date.click()
        # Input return date #
        italian_weekday, day, month, year = self.format_date(self.itinerary['return_date'])
        self.scroll_to_month(month)
        return_date = self.driver.find_element_by_css_selector(
            f'[aria-label="Choose {italian_weekday}, {day} {month} {year} as your check-out date. It\'s available."]')
        return_date.click()
        # Input passenger number #
        self.driver.find_element_by_css_selector('[class="icon icon-right lh lh-arrow-expand"]').click()
        self.driver.find_element_by_css_selector('[class="icon lh lh-plus"]').click()
        self.driver.find_element_by_xpath('//span[text()="Avanti"]').click()
        # Remove bot detection cookie #
        self.driver.delete_cookie('ak_bmsc')
        # Submit search #
        self.driver.find_element_by_xpath('//span[text()="Ricerca voli"]').click()
        time.sleep(5)

    def get_lufthansa_price(self):
        """Get price for selected flight."""
        # Select departure #
        departure_row = self.driver.find_element_by_xpath(
            f'//*[contains(text(), "{self.itinerary["departure_time"]}")]/ancestor::pres-avail')
        departure_flight_number = departure_row.find_element_by_xpath('.//div[@class="flightNumber"]').text
        self.itinerary.update({'departure_flight_number': departure_flight_number})
        cabin_identifier = self.itinerary['fare_brand'][0]
        departure_row.find_element_by_xpath(
            f'.//div[@class="container cabin{cabin_identifier} ng-star-inserted"]/div/input').click()
        time.sleep(3)
        departure_price_container = departure_row.find_element_by_xpath(
            f'.//*[contains(text(),\"{self.itinerary["fare_brand"]}\")]/ancestor::cont-fare')
        departure_price_container.find_element_by_xpath('.//button').click()
        departure_price = departure_price_container.text.split('\n')[-1].split(' ')[0]
        self.itinerary.update({'departure_price': departure_price})
        # Remove bot detection cookie #
        self.driver.delete_cookie('ak_bmsc')
        self.driver.find_element_by_xpath('//span[text()="Avanti"]').click()
        time.sleep(3)
        # Select return #
        return_row = self.driver.find_element_by_xpath(
            f'//*[contains(text(), "{self.itinerary["return_time"]}")]/ancestor::pres-avail')
        return_flight_number = return_row.find_element_by_xpath('.//div[@class="flightNumber"]').text
        self.itinerary.update({'return_flight_number': return_flight_number})
        cabin_identifier = self.itinerary['fare_brand'][0]
        return_row.find_element_by_xpath(
            f'.//div[@class="container cabin{cabin_identifier} ng-star-inserted"]/div/input').click()
        time.sleep(3)
        return_price_container = return_row.find_element_by_xpath(
            f'.//*[contains(text(),\"{self.itinerary["fare_brand"]}\")]/ancestor::cont-fare')
        return_price_container.find_element_by_xpath('.//button').click()
        return_price = return_price_container.text.split('\n')[-1].split(' ')[0]
        self.itinerary.update({'return_price': return_price})
        # Remove bot detection cookie #
        self.driver.delete_cookie('ak_bmsc')
        self.driver.find_element_by_xpath('//span[text()="Avanti"]').click()

    @staticmethod
    def format_date(date: str):
        """Format weekday and date for Lufthansa date picker."""
        date_list = date.split('/')
        day = int(date_list[0])
        month = int(date_list[1])
        year = int(date_list[2])
        italian_weekday = ITALIAN_WEEKDAY[datetime.date(year, month, day).weekday()]
        return italian_weekday, f'{day:02d}', ITALIAN_MONTH[month], str(year)

    def scroll_to_month(self, month: str):
        """Scroll to required month for Lufthansa date picker."""
        visible_month = self.visible_month()
        next_month_button = self.driver.find_element_by_css_selector('[aria-label="Vai al mese successivo."]')
        while month not in visible_month:
            next_month_button.click()
            visible_month = self.visible_month()

    def visible_month(self) -> str:
        """Get visible month for Lufthansa date picker.."""
        webelements = self.driver.find_elements_by_tag_name('strong')
        for webelement in webelements:
            if '2021' in webelement.text:
                return webelement.text

    def scrape_ryanair(self):
        """Scrape Ryanair."""
        self.driver.get(CARRIERS[self.carrier])

    def wait_for_element(self, by: By, expected_condition: EC, locator: str) -> WebElement:
        """Wait for element before fetch."""
        return WebDriverWait(self.driver, 10).until(expected_condition((by, locator)))


if __name__ == '__main__':
    start_time = time.time()
    alitalia_scraper = Scraper(carrier='Alitalia', browser='Chrome', itinerary=ITINERARIES_ALITALIA[0])
    alitalia_scraper.scrape()
    lufthansa_scraper = Scraper(carrier='Lufthansa', browser='Chrome', itinerary=ITINERARIES_LUFTHANSA[0])
    lufthansa_scraper.scrape()
    print(alitalia_scraper.itinerary)
    print(lufthansa_scraper.itinerary)
    print('\n', 'Elapsed time:', round(time.time() - start_time, 2), 'sec')
