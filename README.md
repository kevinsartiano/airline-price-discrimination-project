# Airline Price Discrimination Thesis

Collection of scripts to gather data for my bachelor's thesis on price discrimination in the airline market.

Before you can run the script, you must set up an account for the Amadeus Self-Service APIs.
Follow the instructions at this link:

[https://developers.amadeus.com/get-started/get-started-with-self-service-apis-335](https://developers.amadeus.com/get-started/get-started-with-self-service-apis-335)

Once you have your *API Key* and *API Secret*, 
create the [environment variables](https://www.schrodinger.com/kb/1842) **AMADEUS_API_KEY** and **AMADEUS_API_SECRET**.

Finally, you must install the requirements as follows:

```
pip install requirements.txt
```

You can run the main script as shown in the following example:

```
python amadeus_api_interface.py -o FCO -d JFK -dd 2021-06-01 -rd 2021-06-08
```

You will find the results in the output folder.

For info on the command line arguments:

```
python amadeus_api_interface.py -h
```