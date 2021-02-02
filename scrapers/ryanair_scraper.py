"""Ryanair Scraper."""
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from scrapers.scraper import Scraper, ITALIAN_MONTH


class RyanairScraper(Scraper):
    """Ryanair Scraper Class."""

    carrier_url = 'https://www.ryanair.com/it/it'
    carrier_dcc = 0.00

    def get_availability(self):
        """Get Ryanair availability."""
        self.driver.find_element_by_css_selector('[class="cookie-popup-with-overlay__button"]').click()
        # Input origin airport #
        if self.user['user'] in ['Android-Chrome', 'iOS-Safari', 'Android-Chrome(control)', 'iOS-Safari(control)']:
            self.mobile_search()
        else:
            self.desktop_search()

    def mobile_search(self):
        """Start search for mobile user profile."""
        self.driver.find_element_by_css_selector('[aria-label="Inizia a cercare"]').click()
        sleep(2)
        self.driver.find_element_by_css_selector('[data-ref="flight-search-controls__route-from"]').click()
        sleep(2)
        origin_selector = self.driver.find_element_by_css_selector('[data-ref="search-filter__input"]')
        origin_selector.send_keys(self.itinerary['origin'])
        self.driver.find_element_by_css_selector('[class="airport__name h3"]').click()
        self.driver.find_element_by_css_selector('[data-ref="flight-search-controls__route-to"]').click()
        sleep(2)
        destination_selector = self.driver.find_element_by_css_selector('[data-ref="search-filter__input"]')
        destination_selector.send_keys(self.itinerary['destination'])
        self.driver.find_element_by_css_selector('[class="airport__name h3"]').click()
        sleep(2)
        self.driver.find_element_by_css_selector('[data-ref="flight-search-controls__calendar"]').click()
        day, month, year = self.format_date(self.itinerary['departure_date'])
        while ITALIAN_MONTH[int(month)].capitalize() not in self.driver.find_element_by_tag_name(
                'ry-datepicker').text:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(1)
        self.driver.find_element_by_css_selector(
            f'[aria-label="{str(int(day))} {str(int(month))} {year}"]').click()
        day, month, year = self.format_date(self.itinerary['return_date'])
        self.driver.find_element_by_css_selector(
            f'[aria-label="{str(int(day))} {str(int(month))} {year}"]').click()
        sleep(3)
        # Submit search #
        self.driver.find_element_by_css_selector('[data-ref="continue-flow__button"]').click()
        sleep(5)

    def desktop_search(self):
        """Start search for desktop user profile."""
        origin_selector = self.driver.find_element_by_id('input-button__departure')
        origin_selector.click()
        origin_selector.clear()
        origin_selector.send_keys(self.itinerary['origin'])
        self.wait_for_element(
            By.CSS_SELECTOR, ec.element_to_be_clickable, f'[data-id="{self.itinerary["origin"]}"]').click()
        sleep(3)
        # Input destination airport #
        destination_selector = self.driver.find_element_by_id('input-button__destination')
        destination_selector.send_keys(self.itinerary['destination'])
        self.wait_for_element(
            By.CSS_SELECTOR, ec.element_to_be_clickable, f'[data-id="{self.itinerary["destination"]}"]').click()
        sleep(3)
        # Select departure date #
        day, month, year = self.format_date(self.itinerary['departure_date'])
        self.driver.find_element_by_xpath(f'//div[text()=" {ITALIAN_MONTH[int(month)][:3]} "]').click()
        self.driver.find_element_by_css_selector(f'[data-id="{year}-{month}-{day}"]').click()
        # Select return date #
        day, month, year = self.format_date(self.itinerary['return_date'])
        self.driver.find_element_by_css_selector(f'[data-id="{year}-{month}-{day}"]').click()
        sleep(3)
        # TODO: select number of passengers
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
        if self.user['user'] in ['Android-Chrome', 'iOS-Safari', 'Android-Chrome(control)', 'iOS-Safari(control)']:
            self.get_mobile_price()
        else:
            self.get_desktop_price()

    def get_mobile_price(self):
        """Get Ryanair mobile price."""
        # Select departure flight #
        flight_row = self.driver.find_element_by_xpath(
            f'//*[contains(text()," {self.itinerary["departure_time"]}")]/ancestor::flights-flight-card')
        departure_flight_number = flight_row.find_element_by_css_selector(
            '[class="card-info__flight ng-star-inserted"]').text
        self.itinerary.update({'departure_flight': departure_flight_number})
        flight_row.click()
        sleep(3)
        fare_box = self.driver.find_element_by_css_selector(
            f'[data-e2e="fare-card--{self.itinerary["fare_brand"].lower()}"]')
        fare_price_box_text = fare_box.find_element_by_css_selector('[class="fare-card__header"]').text.split("\n")
        departure_price = f'{fare_price_box_text[-4]}.{fare_price_box_text[-2]}'
        self.itinerary.update({'departure_price': departure_price})
        fare_box.find_element_by_css_selector('[class="fare-card__header"]').click()
        sleep(1)
        self.driver.find_element_by_xpath('//*[text()=" Continua "]').click()
        sleep(3)
        # Select return flight #
        flight_row = self.driver.find_element_by_xpath(
            f'//*[contains(text()," {self.itinerary["return_time"]}")]/ancestor::flights-flight-card')
        return_flight_number = flight_row.find_element_by_css_selector(
            '[class="card-info__flight ng-star-inserted"]').text
        self.itinerary.update({'return_flight': return_flight_number})
        flight_row.click()
        sleep(3)
        fare_box = self.driver.find_element_by_css_selector(
            f'[data-e2e="fare-card--{self.itinerary["fare_brand"].lower()}"]')
        fare_price_box_text = fare_box.find_element_by_css_selector('[class="fare-card__header"]').text.split("\n")
        return_price = f'{fare_price_box_text[-4]}.{fare_price_box_text[-2]}'
        self.itinerary.update({'return_price': return_price})
        fare_box.find_element_by_css_selector('[class="fare-card__header"]').click()
        sleep(1)
        self.driver.find_element_by_xpath('//*[text()=" Continua "]').click()
        sleep(3)
        total_price_box = self.driver.find_element_by_css_selector('[class="ng-tns-c6-0 price ng-star-inserted"]')
        total_price_text = total_price_box.text.split('\n')
        total_price = f'{total_price_text[1]}.{total_price_text[3]}'
        self.itinerary.update({'total_price': total_price})

    def get_desktop_price(self):
        """Get Ryanair desktop price."""
        # Select departure flight #
        flight_row = self.driver.find_element_by_xpath(
            f'//*[text()=" {self.itinerary["departure_time"]} "]/ancestor::flight-card')
        base_price = float(flight_row.text.split('\n')[-1][:-2].replace(',', '.'))
        departure_flight_number = flight_row.find_element_by_css_selector('[class="card-flight-num__content"]').text
        self.itinerary.update({'departure_flight': departure_flight_number})
        flight_row.click()
        sleep(3)
        fare_box = self.driver.find_element_by_css_selector(
            f'[data-e2e="fare-card--{self.itinerary["fare_brand"].lower()}"]')
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
        fare_box = self.driver.find_element_by_css_selector(
            f'[data-e2e="fare-card--{self.itinerary["fare_brand"].lower()}"]')
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
        # HACK: missing feature
        self.itinerary.update({'seats_left': -1})
        control_user = self.user
        control_user['user'] += '(control)'
        control_scraper = RyanairScraper(user=control_user, selenium_browser='Chrome', itinerary=self.itinerary,
                                         run_with_cookies=False, export=False)
        control_scraper.scrape()
        self.itinerary['control_price'] = control_scraper.itinerary['total_price']
