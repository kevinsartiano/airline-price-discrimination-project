"""Amadeus API Interface."""
import argparse
import json
import os
import time
from amadeus import Client, ResponseError
from tools.spreadsheet_tool import export_to_csv

from airline_codes import AIRLINE_TABLE


def basic_search_flight(origin: str, destination: str, departure_date: str, return_date: str):
    """Search flight from origin to destination on desired date."""
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            returnDate=return_date,
            adults=1,
            # includedAirlineCodes='LH'
        )
        dirname = os.path.join('output', 'amadeus_search_result')
        basename = f'{origin}-{destination}_{departure_date}_{return_date}'
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        export_to_json(data=response.data, basename=basename, dirname=dirname)
        export_to_csv(data=parse_data(response.data), basename=basename, dirname=dirname)
    except ResponseError as error:
        print(error)


def parse_data(data):
    """Parse relevant data."""
    parsed_data = []
    for result in data:
        parsed_data.append(
            {'carrier': AIRLINE_TABLE[result['validatingAirlineCodes'][0]],
             'departure': get_itinerary(result['itineraries'][0]),
             'return': get_itinerary(result['itineraries'][1]),
             'departure_stops': len(result['itineraries'][0]['segments']) - 1,
             'return_stops': len(result['itineraries'][1]['segments']) - 1,
             'seats_left': float(result['numberOfBookableSeats']),
             'base_price': float(result['price']['base']),
             'total_price': float(result['price']['total']),
             'class': result['travelerPricings'][0]['fareDetailsBySegment'][0]['class'],
             'fare_basis': result['travelerPricings'][0]['fareDetailsBySegment'][0]['fareBasis'],
             # 'fare_brand': result['travelerPricings'][0]['fareDetailsBySegment'][0]['brandedFare']
             })
    return parsed_data


def get_itinerary(way):
    """Get itinerary details."""
    itinerary = ''
    for segment in way['segments']:
        itinerary += f'{segment["departure"]["iataCode"]}-{segment["arrival"]["iataCode"]} ' \
                     f'{segment["departure"]["at"][11:-3]}-{segment["arrival"]["at"][11:-3]}\n'
    itinerary += f'duration: {way["duration"][2:]}'
    return itinerary


def export_to_json(data, basename: str, dirname: str = 'output'):
    """Export to JSON file."""
    path = os.path.join(dirname, basename + '.json')
    with open(path, 'w') as j:
        json.dump(data, j, indent=4)


def parse_args():
    """Parse the CLI arguments."""
    parser = argparse.ArgumentParser(description='Search flight based on input criteria.')
    parser.add_argument('-o', '--origin', dest='origin', type=str, required=True,
                        help='The city/airport IATA code from which the traveler will depart, e.g. FCO for Rome')
    parser.add_argument('-d', '--destination', dest='destination', type=str, required=True,
                        help='The city/airport IATA code  to which the traveler is going, e.g. JFK for New York')
    parser.add_argument('-dd', '--departure-date', dest='departure_date', type=str, required=True,
                        help='The date on which the traveler will depart from the origin to go to the destination. '
                             'Dates are specified in the ISO 8601 YYYY-MM-DD format, e.g. 2021-12-31')
    parser.add_argument('-rd', '--return-date', dest='return_date', type=str, required=True,
                        help='the date on which the traveler will depart from the destination to return to the origin. '
                             'If this parameter is not specified, only one-way itineraries are found. '
                             'If this parameter is specified, only round-trip itineraries are found. '
                             'Dates are specified in the ISO 8601 YYYY-MM-DD format, e.g. 2021-12-31')
    return parser.parse_args()


if __name__ == '__main__':
    start_time = time.time()
    amadeus = Client(client_id=os.environ['AMADEUS_API_KEY'], client_secret=os.environ['AMADEUS_API_SECRET'])
    args = parse_args()
    basic_search_flight(origin=args.origin, destination=args.destination,
                        departure_date=args.departure_date, return_date=args.return_date)
    print('\n', 'Elapsed time:', round(time.time() - start_time, 2), 'sec')
