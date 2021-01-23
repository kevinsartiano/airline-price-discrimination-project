"""Run Scrapers."""

import time
from itineraries.itineraries import ITINERARIES_ALITALIA, ITINERARIES_LUFTHANSA, ITINERARIES_RYANAIR
from scrapers.alitalia_scraper import AlitaliaScraper
from scrapers.lufthansa_scraper import LufthansaScraper
from scrapers.ryanair_scraper import RyanairScraper

if __name__ == '__main__':
    start_time = time.time()
    alitalia_scraper = AlitaliaScraper(browser='Chrome', itinerary=ITINERARIES_ALITALIA[0])
    alitalia_scraper.scrape()
    lufthansa_scraper = LufthansaScraper(browser='Chrome', itinerary=ITINERARIES_LUFTHANSA[0])
    lufthansa_scraper.scrape()
    ryanair_scraper = RyanairScraper(browser='Chrome', itinerary=ITINERARIES_RYANAIR[0])
    ryanair_scraper.scrape()
    print(alitalia_scraper.itinerary)
    print(lufthansa_scraper.itinerary)
    print(ryanair_scraper.itinerary)
    print('\n', 'Elapsed time:', round(time.time() - start_time, 2), 'sec')
