"""Run Scrapers."""

import time
from datetime import datetime
from itineraries.itineraries import ITINERARIES_ALITALIA, ITINERARIES_LUFTHANSA, ITINERARIES_RYANAIR
from scrapers.alitalia_scraper import AlitaliaScraper
from scrapers.lufthansa_scraper import LufthansaScraper
from scrapers.ryanair_scraper import RyanairScraper
from tools.spreadsheet_tool import export_to_csv

if __name__ == '__main__':
    start_time = time.time()

    alitalia_scraper = AlitaliaScraper(browser='Chrome', itinerary=ITINERARIES_ALITALIA[0])
    alitalia_scraper.scrape()

    lufthansa_scraper = LufthansaScraper(browser='Chrome', itinerary=ITINERARIES_LUFTHANSA[0])
    lufthansa_scraper.scrape()

    ryanair_scraper = RyanairScraper(browser='Chrome', itinerary=ITINERARIES_RYANAIR[0])
    ryanair_scraper.scrape()

    export_to_csv(data=[alitalia_scraper.itinerary, lufthansa_scraper.itinerary, ryanair_scraper.itinerary],
                  basename=str(datetime.now().strftime("%m-%d-%Y_%H:%M:%S")))

    print('\n', 'Total time:', round(time.time() - start_time, 2), 'sec')
