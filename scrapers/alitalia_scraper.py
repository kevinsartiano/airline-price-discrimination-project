"""Alitalia Scraper."""
import os
import webbrowser
import browser_cookie3
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from scrapers.scraper import Scraper


class AlitaliaScraper(Scraper):
    """Alitalia Scraper Class."""

    carrier = 'Alitalia'
    carrier_url = 'https://www.alitalia.com/it_it/homepage.html'

    def get_availability(self):
        """Get availability."""
        # Replace bot detection cookie with valid one to continue #
        ak_bmsc_cookie = self.driver.get_cookie('ak_bmsc')
        ak_bmsc_cookie['value'] = self.get_ak_bmsc_valid_value()
        sleep(5)
        self.driver.delete_cookie('ak_bmsc')
        self.driver.add_cookie(ak_bmsc_cookie)
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
        # Submit search #
        submit_button = self.driver.find_element_by_id('submitHidden--prenota')
        submit_button.click()

    def get_ak_bmsc_valid_value(self) -> str:
        """Get valid value for ak_bmsc cookie."""
        webbrowser.open_new_tab(self.carrier_url)
        cookie_jar = browser_cookie3.chrome()
        os.system("wmctrl -c :ACTIVE:")  # close chrome window used to get valid cookie
        ak_bmsc_new_value = None
        for cookie in cookie_jar:
            if self.carrier.lower() in cookie.domain:
                if cookie.name == 'ak_bmsc':
                    ak_bmsc_new_value = cookie.value
        if ak_bmsc_new_value:
            return ak_bmsc_new_value.replace('+', ' ')
        return ''

    def get_price(self):
        """Get price for selected flight."""
        # Get departure price #
        departure_node = self.wait_for_element(By.CSS_SELECTOR, ec.presence_of_element_located,
                                               f'[data-flight-time=\"{self.itinerary["departure_time"]}\"]'
                                               f'[data-flight-brandname=\"{self.itinerary["fare_brand"]}\"]')
        self.itinerary.update({'departure_price': departure_node.get_attribute('data-flight-price'),
                               'departure_flight_number': departure_node.get_attribute('data-flight-number')})
        departure_node.find_element_by_class_name('fakeRadio').click()
        sleep(5)
        select_button = self.wait_for_element(By.CSS_SELECTOR, ec.element_to_be_clickable,
                                              '[class="firstButton j-goToReturn"]')
        select_button.click()
        sleep(5)
        # Get return price #
        return_node = self.wait_for_element(By.CSS_SELECTOR, ec.presence_of_element_located,
                                            f'[data-flight-time=\"{self.itinerary["return_time"]}\"]'
                                            f'[data-flight-brandname=\"{self.itinerary["fare_brand"]}\"]')
        self.itinerary.update({'inbound_price': return_node.get_attribute('data-flight-price'),
                               'inbound_flight_number': return_node.get_attribute('data-flight-number')})
        return_node.find_element_by_class_name('fakeRadio').click()
        sleep(5)
        select_button = self.wait_for_element(By.CSS_SELECTOR, ec.element_to_be_clickable,
                                              '[class="firstButton j-selectReturn"]')
        select_button.click()
