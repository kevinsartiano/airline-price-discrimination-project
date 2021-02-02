"""Lufthansa Scraper."""
import datetime
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from scrapers.scraper import Scraper, ITALIAN_WEEKDAY, ITALIAN_MONTH


class LufthansaScraper(Scraper):
    """Lufthansa Scraper Class."""

    carrier_url = 'https://www.lufthansa.com/it/it/homepage'
    carrier_dcc = 79.00  # 19.00 DCC + 20.00 Fare + 40.00 Extra baggage

    def get_availability(self):
        """Get Lufthansa availability."""
        self.driver.delete_cookie('ak_bmsc')
        self.driver.find_element_by_id('cm-acceptAll').click()
        sleep(3)
        try:
            self.driver.find_element_by_xpath('//button[@aria-label="Chiudi "]').click()
        except NoSuchElementException:
            pass
        # Input origin airport #
        origin_selector = self.driver.find_element_by_name('flightQuery.flightSegments[0].originCode')
        origin_selector.click()
        origin_selector.send_keys(Keys.CONTROL + "a" + Keys.DELETE)
        origin_selector.send_keys(self.itinerary['origin'])
        sleep(3)
        # Input destination airport #
        destination_selector = self.driver.find_element_by_name('flightQuery.flightSegments[0].destinationCode')
        destination_selector.click()
        destination_selector.send_keys(self.itinerary['destination'])
        sleep(3)
        # Input departure date #
        self.driver.find_element_by_name('flightQuery.flightSegments[0].travelDatetime').click()
        italian_weekday, day, month, year = self.format_lufthansa_date(self.itinerary['departure_date'])
        self.scroll_to_month(month)
        departure_date = self.driver.find_element_by_css_selector(
            f'[aria-label="Choose {italian_weekday}, {day} {month} {year} as your check-in date. It\'s available."]')
        departure_date.click()
        # Input return date #
        italian_weekday, day, month, year = self.format_lufthansa_date(self.itinerary['return_date'])
        self.scroll_to_month(month)
        return_date = self.driver.find_element_by_css_selector(
            f'[aria-label="Choose {italian_weekday}, {day} {month} {year} as your check-out date. It\'s available."]')
        return_date.click()
        # TODO: select number of passengers
        # Input passenger number #
        # self.driver.find_element_by_css_selector('[class="icon icon-right lh lh-arrow-expand"]').click()
        # self.driver.find_element_by_css_selector('[class="icon lh lh-plus"]').click()
        # self.driver.find_element_by_xpath('//span[text()="Avanti"]').click()
        # Submit search #
        self.driver.find_element_by_xpath('//span[text()="Ricerca voli"]').click()
        sleep(5)

    def get_price(self):
        """Get price for selected flight."""
        # Select departure #
        departure_row = self.driver.find_element_by_xpath(
            f'//*[contains(text(), "{self.itinerary["departure_time"]}")]/ancestor::pres-avail')
        departure_flight_number = departure_row.find_element_by_xpath('.//div[@class="flightNumber"]').text
        self.itinerary.update({'departure_flight': departure_flight_number})
        cabin_identifier = self.itinerary['fare_brand'][0]
        departure_row.find_element_by_xpath(
            f'.//div[@class="container cabin{cabin_identifier} ng-star-inserted"]/div/input').click()
        sleep(3)
        departure_price_container = departure_row.find_element_by_xpath(
            f'.//*[contains(text(),\"{self.itinerary["fare_brand"]}\")]/ancestor::cont-fare')
        if self.itinerary['fare_brand'] != 'Economy Light':
            departure_price_container.find_element_by_xpath('.//button').click()
        departure_price = departure_price_container.text.split('\n')[-1].split(' ')[0].replace(',', '.')
        self.itinerary.update({'departure_price': departure_price})
        # Remove bot detection cookie #
        self.driver.delete_cookie('ak_bmsc')
        self.driver.find_element_by_xpath('//span[text()="Avanti"]').click()
        sleep(3)
        # Select return #
        return_row = self.driver.find_element_by_xpath(
            f'//*[contains(text(), "{self.itinerary["return_time"]}")]/ancestor::pres-avail')
        return_flight_number = return_row.find_element_by_xpath('.//div[@class="flightNumber"]').text
        self.itinerary.update({'return_flight': return_flight_number})
        cabin_identifier = self.itinerary['fare_brand'][0]
        return_row.find_element_by_xpath(
            f'.//div[@class="container cabin{cabin_identifier} ng-star-inserted"]/div/input').click()
        sleep(3)
        return_price_container = return_row.find_element_by_xpath(
            f'.//*[contains(text(),\"{self.itinerary["fare_brand"]}\")]/ancestor::cont-fare')
        if self.itinerary['fare_brand'] != 'Economy Light':
            return_price_container.find_element_by_xpath('.//button').click()
        return_price = return_price_container.text.split('\n')[-1].split(' ')[0].replace(',', '.')
        self.itinerary.update({'return_price': return_price})
        # Remove bot detection cookie #
        self.driver.delete_cookie('ak_bmsc')
        self.driver.find_element_by_xpath('//span[text()="Avanti"]').click()
        sleep(3)
        total_price_box = self.driver.find_element_by_css_selector(
            '[class="shopping-cart-total-price__totalPrice ng-scope ng-isolate-scope"]')
        total_price = total_price_box.text[:-4].replace(',', '.')
        self.itinerary.update({'total_price': total_price})

    @staticmethod
    def format_lufthansa_date(date: str):
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
        """Get visible month for Lufthansa date picker."""
        webelements = self.driver.find_elements_by_tag_name('strong')
        for webelement in webelements:
            if '2021' in webelement.text:
                return webelement.text
