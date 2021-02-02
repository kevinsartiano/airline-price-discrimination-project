"""Run Scrapers."""
import os
import subprocess
import time
import requests
from datetime import timedelta
from itineraries.itineraries import ITINERARIES
from scrapers.alitalia_scraper import AlitaliaScraper
from scrapers.lufthansa_scraper import LufthansaScraper
from scrapers.ryanair_scraper import RyanairScraper
from tools.logger_tool import get_logger
from users.user_profiles import USER_LIST

# HACK: for testing
# CARRIER_SCRAPERS = {'Ryanair': RyanairScraper}
CARRIER_SCRAPERS = {'Alitalia': AlitaliaScraper, 'Ryanair': RyanairScraper, 'Lufthansa': LufthansaScraper}


if __name__ == '__main__':
    logger = get_logger(filename=os.path.join('output', 'logbook.log'))
    logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    total_start_time = time.time()
    for carrier, scraper_class in CARRIER_SCRAPERS.items():
        start_time = time.time()
        logger.info(f'{carrier} scraping session started'.upper())
        for user in USER_LIST:
            # FIXME: keep an eye on it
            # subprocess.run(['nordvpn', 'disconnect'])
            # time.sleep(3)
            subprocess.run(['nordvpn', 'connect', f'{user["vpn_server"]}'])
            time.sleep(3)
            try:
                ip_address = requests.get('https://ifconfig.me').text
            except requests.exceptions.ConnectionError:
                ip_address = 'Error'
            if ip_address != user["ip_address"]:
                logger.error(f'{user["user"]}: IP address should be {user["ip_address"]} instead of {ip_address}!')
            for itinerary in ITINERARIES[carrier]:
                scraper = scraper_class(user=user, selenium_browser='Chrome', itinerary=itinerary)
                scraper.scrape()
        logger.info(f'{carrier} scraping session completed in {timedelta(seconds=round(time.time() - start_time))}')
        logger.info('- - - - - - - - - - - - - - - - - - - - - -')
    logger.info(f'Total scraping completed in {timedelta(seconds=round(time.time() - total_start_time))}')
    logger.info('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
