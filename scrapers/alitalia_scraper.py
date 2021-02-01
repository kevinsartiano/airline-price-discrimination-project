"""Alitalia Scraper."""
import os
import webbrowser
import browser_cookie3
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from scrapers.scraper import Scraper, ITALIAN_MONTH


class AlitaliaScraper(Scraper):
    """Alitalia Scraper Class."""

    carrier_url = 'https://www.alitalia.com/it_it/homepage.html'
    carrier_dcc = 0.00

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
        self.driver.find_element_by_id('data-andata--prenota-desk').click()
        if self.user['user'] in ['Android-Chrome', 'iOS-Safari']:
            day, month, year = self.format_alitalia_date(self.itinerary['departure_date'])
            self.scroll_to_month(month.capitalize())
            self.driver.find_element_by_xpath(f'//a[text()="{day}"]').click()
            day, month, year = self.format_alitalia_date(self.itinerary['return_date'])
            self.driver.find_element_by_xpath(f'//a[text()="{day}"]').click()
        else:
            departure_date_selector.send_keys(self.itinerary['departure_date'])
            return_date_selector.send_keys(self.itinerary['return_date'])
            validate_date_button = self.driver.find_element_by_id('validate_date')
            validate_date_button.click()
        sleep(2)
        # add_passenger_button = self.driver.find_element_by_id('addAdults')
        # add_passenger_button.click()
        # Submit search #
        submit_button = self.driver.find_element_by_id('submitHidden--prenota')
        submit_button.click()
        sleep(10)

    def get_ak_bmsc_valid_value(self) -> str:
        """Get valid value for ak_bmsc cookie."""
        webbrowser.open_new(self.carrier_url)
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

    @staticmethod
    def format_alitalia_date(date: str):
        """Format weekday and date for Alitalia date picker."""
        date_list = date.split('/')
        day = int(date_list[0])
        month = int(date_list[1])
        year = int(date_list[2])
        return f'{day:02d}', ITALIAN_MONTH[month], str(year)

    def scroll_to_month(self, month: str):
        """Scroll to required month for Alitalia date picker."""
        visible_month = self.visible_month()
        while month not in visible_month:
            next_button = self.driver.find_element_by_css_selector('[title="Succ>"]')
            next_button.click()
            visible_month = self.visible_month()

    def visible_month(self) -> str:
        """Get visible month for Lufthansa date picker.."""
        return self.driver.find_element_by_css_selector('[class="ui-datepicker-month"]').text

    def get_price(self):
        """Get price for selected flight."""
        # Get departure price #
        departure_node = self.wait_for_element(By.CSS_SELECTOR, ec.presence_of_element_located,
                                               f'[data-flight-time=\"{self.itinerary["departure_time"]}\"]'
                                               f'[data-flight-brandname=\"{self.itinerary["fare_brand"]}\"]')
        self.itinerary.update({'departure_price': departure_node.get_attribute('data-flight-price'),
                               'departure_flight': departure_node.get_attribute('data-flight-number')})
        departure_node.click()
        sleep(5)
        select_button = self.wait_for_element(By.CSS_SELECTOR, ec.element_to_be_clickable,
                                              '[class="firstButton j-goToReturn"]')
        select_button.click()
        sleep(5)
        # Show hidden flights #
        load_more_button = self.wait_for_element(
            By.XPATH, ec.element_to_be_clickable,
            '//a[@data-details-route="1"][@class="bookingTable__bodyRowLoadMoreLink j-loadMoreBookingRow"]')
        self.driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
        load_more_button.click()
        # Get return price #
        return_node = self.wait_for_element(By.CSS_SELECTOR, ec.presence_of_element_located,
                                            f'[data-flight-time=\"{self.itinerary["return_time"]}\"]'
                                            f'[data-flight-brandname=\"{self.itinerary["fare_brand"]}\"]')
        self.itinerary.update({'return_price': return_node.get_attribute('data-flight-price'),
                               'return_flight': return_node.get_attribute('data-flight-number')})
        self.driver.execute_script("arguments[0].scrollIntoView();", return_node)
        return_node.click()
        sleep(5)
        select_button = self.wait_for_element(By.CSS_SELECTOR, ec.element_to_be_clickable,
                                              '[class="firstButton j-selectReturn"]')
        select_button.click()
        sleep(10)
        # Get total price
        total_price_box = self.wait_for_element(By.ID, ec.presence_of_element_located, 'basketPrice-text')
        total_price = total_price_box.text[2:].replace(',', '.')
        self.itinerary.update({'total_price': total_price})
