"""Run Scrapers."""

import time
from itineraries.itineraries import ITINERARIES_ALITALIA, ITINERARIES_LUFTHANSA, ITINERARIES_RYANAIR
from scrapers.alitalia_scraper import AlitaliaScraper
from scrapers.lufthansa_scraper import LufthansaScraper
from scrapers.ryanair_scraper import RyanairScraper
from tools.spreadsheet_tool import export_to_csv

if __name__ == '__main__':
    start_time = time.time()

    alitalia_scraper = AlitaliaScraper(browser='Chrome', itinerary=ITINERARIES_ALITALIA[0])
    alitalia_scraper.scrape()
    export_to_csv(data=[alitalia_scraper.itinerary], basename='alitalia')

    lufthansa_scraper = LufthansaScraper(browser='Chrome', itinerary=ITINERARIES_LUFTHANSA[0])
    lufthansa_scraper.scrape()
    export_to_csv(data=[lufthansa_scraper.itinerary], basename='lufthansa')

    ryanair_scraper = RyanairScraper(browser='Chrome', itinerary=ITINERARIES_RYANAIR[0])
    ryanair_scraper.scrape()
    export_to_csv(data=[ryanair_scraper.itinerary], basename='ryanair')

    print('\n', 'Elapsed time:', round(time.time() - start_time, 2), 'sec')
