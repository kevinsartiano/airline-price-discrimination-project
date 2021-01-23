"""Ryanair Scraper."""

from time import sleep
from scrapers.scraper import Scraper, ITALIAN_MONTH


class RyanairScraper(Scraper):
    """Ryanair Scraper Class."""

    carrier = 'Ryanair'

    def get_availability(self):
        """Get Ryanair availability."""
        self.driver.find_element_by_css_selector('[class="cookie-popup-with-overlay__button"]').click()
        # Input origin airport #
        origin_selector = self.driver.find_element_by_id('input-button__departure')
        origin_selector.click()
        origin_selector.clear()
        origin_selector.send_keys(self.itinerary['origin'])
        self.driver.find_element_by_css_selector(f'[data-id=\"{self.itinerary["origin"]}\"]').click()
        sleep(2)
        # Input destination airport #
        destination_selector = self.driver.find_element_by_id('input-button__destination')
        destination_selector.send_keys(self.itinerary['destination'])
        self.driver.find_element_by_css_selector(f'[data-id=\"{self.itinerary["destination"]}\"]').click()
        sleep(2)
        # Select departure date #
        day, month, year = self.format_date(self.itinerary['departure_date'])
        self.driver.find_element_by_xpath(f'//div[contains(text(),"{ITALIAN_MONTH[int(month)][:3]}\")]').click()
        self.driver.find_element_by_css_selector(f'[data-id="{year}-{month}-{day}"]').click()
        # Select return date #
        day, month, year = self.format_date(self.itinerary['return_date'])
        # FIXME
        # self.driver.find_element_by_xpath(f'//div[contains(text(),"{ITALIAN_MONTH[int(month)][:3]}\")]').click()
        self.driver.find_element_by_css_selector(f'[data-id="{year}-{month}-{day}"]').click()
        sleep(2)
        # Select passengers #
        self.driver.find_element_by_xpath('//ry-counter[@data-ref="passengers-picker__adults"]/'
                                          'div/div[@data-ref="counter.counter__increment"]').click()
        sleep(2)
        # Submit search #
        self.driver.find_element_by_xpath('//*[text()=" Cerca "]').click()
        sleep(5)

    @staticmethod
    def format_date(date: str):
        """Format weekday and date for Ryanair date picker."""
        date_list = date.split('/')
        day = date_list[0]
        month = date_list[1]
        year = date_list[2]
        return day, month, year

    def get_price(self):
        """Get Ryanair price."""
        # Select departure flight #
        self.driver.find_element_by_xpath(f'//*[text()=" {self.itinerary["departure_time"]} "]').click()
        sleep(2)
        fare_box = self.driver.find_element_by_css_selector('[data-e2e="fare-card--plus"]')
        fare_box_text = fare_box.text.split("\n")
        self.itinerary.update({'departure_price': f'{fare_box_text[-4]}.{fare_box_text[-2]}'})
        fare_box.click()
        sleep(2)
        # Select return flight #
        self.driver.find_element_by_xpath(f'//*[text()=" {self.itinerary["return_time"]} "]').click()
        sleep(2)
        fare_box = self.driver.find_element_by_css_selector('[data-e2e="fare-card--plus"]')
        fare_box_text = fare_box.text.split("\n")
        self.itinerary.update({'return_price': f'{fare_box_text[-4]}.{fare_box_text[-2]}'})
        fare_box.click()
        sleep(2)
