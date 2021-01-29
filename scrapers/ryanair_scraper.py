"""Ryanair Scraper."""

from time import sleep
from scrapers.scraper import Scraper, ITALIAN_MONTH


class RyanairScraper(Scraper):
    """Ryanair Scraper Class."""

    carrier = 'Ryanair'
    carrier_url = 'https://www.ryanair.com/it/it'

    def get_availability(self):
        """Get Ryanair availability."""
        self.driver.find_element_by_css_selector('[class="cookie-popup-with-overlay__button"]').click()
        # Input origin airport #
        origin_selector = self.driver.find_element_by_id('input-button__departure')
        origin_selector.click()
        origin_selector.clear()
        origin_selector.send_keys(self.itinerary['origin'])
        self.driver.find_element_by_css_selector(f'[data-id=\"{self.itinerary["origin"]}\"]').click()
        sleep(3)
        # Input destination airport #
        destination_selector = self.driver.find_element_by_id('input-button__destination')
        destination_selector.send_keys(self.itinerary['destination'])
        self.driver.find_element_by_css_selector(f'[data-id=\"{self.itinerary["destination"]}\"]').click()
        sleep(3)
        # Select departure date #
        day, month, year = self.format_date(self.itinerary['departure_date'])
        self.driver.find_element_by_xpath(f'//div[contains(text(),"{ITALIAN_MONTH[int(month)][:3]}\")]').click()
        self.driver.find_element_by_css_selector(f'[data-id="{year}-{month}-{day}"]').click()
        # Select return date #
        day, month, year = self.format_date(self.itinerary['return_date'])
        self.driver.find_element_by_css_selector(f'[data-id="{year}-{month}-{day}"]').click()
        sleep(3)
        # Select passengers #
        # self.driver.find_element_by_xpath('//ry-counter[@data-ref="passengers-picker__adults"]/'
        #                                   'div/div[@data-ref="counter.counter__increment"]').click()
        # sleep(3)
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
        flight_row = self.driver.find_element_by_xpath(
            f'//*[text()=" {self.itinerary["departure_time"]} "]/ancestor::flight-card')
        base_price = float(flight_row.text.split('\n')[-1][:-2].replace(',', '.'))
        departure_flight_number = flight_row.find_element_by_css_selector('[class="card-flight-num__content"]').text
        self.itinerary.update({'departure_flight': departure_flight_number})
        flight_row.click()
        sleep(3)
        fare_box = self.driver.find_element_by_css_selector('[data-e2e="fare-card--plus"]')
        fare_box_text = fare_box.text.split("\n")
        add_on_price = float(f'{fare_box_text[-5]}.{fare_box_text[-3]}')
        departure_price = str(round(base_price + add_on_price, 2))
        self.itinerary.update({'departure_price': departure_price})
        fare_box.click()
        sleep(3)
        # Select return flight #
        flight_row = self.driver.find_element_by_xpath(
            f'//*[text()=" {self.itinerary["return_time"]} "]/ancestor::flight-card')
        base_price = float(flight_row.text.split('\n')[-1][:-2].replace(',', '.'))
        return_flight_number = flight_row.find_element_by_css_selector('[class="card-flight-num__content"]').text
        self.itinerary.update({'return_flight': return_flight_number})
        flight_row.click()
        sleep(3)
        fare_box = self.driver.find_element_by_css_selector('[data-e2e="fare-card--plus"]')
        fare_box_text = fare_box.text.split("\n")
        add_on_price = float(f'{fare_box_text[-5]}.{fare_box_text[-3]}')
        return_price = str(round(base_price + add_on_price, 2))
        self.itinerary.update({'return_price': return_price})
        fare_box.click()
        sleep(3)
        total_price_box = self.driver.find_element_by_css_selector('[class="ng-tns-c17-1 price ng-star-inserted"]')
        total_price_text = total_price_box.text.split('\n')
        total_price = f'{total_price_text[1]}.{total_price_text[3]}'
        self.itinerary.update({'total_price': total_price})

    def get_control_price(self):
        """Unable to use Amadeus API for Ryanair's control price."""
        self.itinerary.update({'control_price': 'Unknown', 'seats_left': 'Unknown'})
