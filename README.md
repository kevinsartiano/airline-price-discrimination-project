# Airline Price Discrimination Project

Collection of scripts to gather data for a project in price discrimination in the airline market.

Before you can run the script, you must install the requirements as follows:

```
pip install -r requirements.txt
```
Download the latest Chrome webdriver for your OS from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads)
and place it in the  *./drivers* folder.

## Run Scrapers

You can run the scrapers as follows:

```
python run_scrapers.py
```

It currently supports Chrome for Linux and Windows

## Amadeus API

To activate the Amadeus API, you must set up an account for the Amadeus Self-Service APIs.
Follow the instructions at this link:

[https://developers.amadeus.com/get-started/get-started-with-self-service-apis-335](https://developers.amadeus.com/get-started/get-started-with-self-service-apis-335)

Once you have your *API Key* and *API Secret*, 
create the [environment variables](https://www.schrodinger.com/kb/1842) **AMADEUS_API_KEY** and **AMADEUS_API_SECRET**.
