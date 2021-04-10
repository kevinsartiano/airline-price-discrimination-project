"""Run Scrapers."""
import os
import subprocess
import time
from datetime import timedelta

import requests

from itineraries.itineraries import ITINERARIES
from scrapers.alitalia_scraper import AlitaliaScraper
from scrapers.lufthansa_scraper import LufthansaScraper
from scrapers.ryanair_scraper import RyanairScraper
from tools.logger_tool import get_logger
from tools.spreadsheet_tool import OUTPUT_FOLDER
from users.user_profiles import USER_LIST

CARRIER_SCRAPERS = {
    'Alitalia': AlitaliaScraper,
    'Ryanair': RyanairScraper,
    'Lufthansa': LufthansaScraper
}


if __name__ == '__main__':
    logger = get_logger(filename=os.path.join(OUTPUT_FOLDER, 'logbook.log'))
    logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    total_start_time = time.time()
    for carrier, scraper_class in CARRIER_SCRAPERS.items():
        start_time = time.time()
        logger.info(f'{carrier} scraping session started'.upper())
        for user in USER_LIST:
            try:
                subprocess.run(['nordvpn', 'disconnect'])
                time.sleep(5)
                subprocess.run(['nordvpn', 'connect', f'{user["vpn_server"]}'])
                time.sleep(5)
                try:
                    ip_address = os.popen('curl -s ifconfig.me').read()
                except requests.exceptions.ConnectionError:
                    ip_address = 'Error'
                if ip_address != user["ip_address"]:
                    logger.error(f'{user["user"]}: IP address should be {user["ip_address"]} '
                                 f'instead of {ip_address}!')
                for itinerary in ITINERARIES[carrier]:
                    scraper = scraper_class(
                        user=user, selenium_browser='Chrome', itinerary=itinerary)
                    scraper.scrape()
                    time.sleep(5)
            except Exception as e:
                logger.error(f'Error: {e}')
        logger.info(f'{carrier} scraping session completed in '
                    f'{timedelta(seconds=round(time.time() - start_time))}')
        logger.info('- - - - - - - - - - - - - - - - - - - - - -')
        time.sleep(5)
    logger.info(f'Total scraping completed in '
                f'{timedelta(seconds=round(time.time() - total_start_time))}')
    logger.info('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
