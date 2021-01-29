"""Run Scrapers."""
import os
import time
from datetime import datetime
from itineraries.itineraries import ALITALIA_ITINERARIES, LUFTHANSA_ITINERARIES, RYANAIR_ITINERARIES
from scrapers.alitalia_scraper import AlitaliaScraper
from scrapers.lufthansa_scraper import LufthansaScraper
from scrapers.ryanair_scraper import RyanairScraper
from tools.logger_tool import get_logger
from tools.spreadsheet_tool import export_to_csv

if __name__ == '__main__':
    logger = get_logger(filename=os.path.join('output', 'logbook.log'))

    logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    logger.info('Scraping started')
    start_time = time.time()

    alitalia_scraper = AlitaliaScraper(browser='Chrome', itinerary=ALITALIA_ITINERARIES[0])
    alitalia_scraper.scrape()

    lufthansa_scraper = LufthansaScraper(browser='Chrome', itinerary=LUFTHANSA_ITINERARIES[0])
    lufthansa_scraper.scrape()

    ryanair_scraper = RyanairScraper(browser='Chrome', itinerary=RYANAIR_ITINERARIES[0])
    ryanair_scraper.scrape()

    logger.info('Exporting data to spreadsheet')
    export_to_csv(data=[alitalia_scraper.itinerary, lufthansa_scraper.itinerary, ryanair_scraper.itinerary],
                  basename='raw_data')

    logger.info(f'Scraping completed in {round(time.time() - start_time, 2)} sec')
    logger.info('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
