"""Run Scrapers."""
import os
import time
from datetime import timedelta
from itineraries.itineraries import ITINERARIES
from scrapers.alitalia_scraper import AlitaliaScraper
from scrapers.lufthansa_scraper import LufthansaScraper
from scrapers.ryanair_scraper import RyanairScraper
from tools.logger_tool import get_logger
from users.user_profiles import USER_LIST

CARRIER_SCRAPERS = {'Alitalia': AlitaliaScraper, 'Ryanair': RyanairScraper, 'Lufthansa': LufthansaScraper}
# CARRIER_SCRAPERS = {'Alitalia': AlitaliaScraper}


if __name__ == '__main__':
    logger = get_logger(filename=os.path.join('output', 'logbook.log'))
    logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    total_start_time = time.time()
    for carrier, scraper_class in CARRIER_SCRAPERS.items():
        start_time = time.time()
        logger.info(f'{carrier} scraping session started'.upper())
        for user in USER_LIST:
            os.system(f'nordvpn connect {user["vpn_server"]}')
            time.sleep(3)
            ip_address = os.popen('curl -s ifconfig.me').read()
            if ip_address != user["ip_address"]:
                logger.error(f'{user["user"]}: IP address should be {user["ip_address"]} instead of {ip_address}!')
            for itinerary in ITINERARIES[carrier]:
                scraper = scraper_class(user=user, selenium_browser='Chrome', itinerary=itinerary)
                scraper.scrape()
        logger.info(f'{carrier} scraping session completed in {timedelta(seconds=round(time.time() - start_time))}')
        logger.info('- - - - - - - - - - - - - - - - - - - - - -')
    logger.info(f'Total scraping completed in {timedelta(seconds=round(time.time() - total_start_time))}')
    logger.info('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
