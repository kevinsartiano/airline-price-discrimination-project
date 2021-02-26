"""Itineraries."""

"""
Itinerary model.

<carrier name>_ITINERARIES = [{'carrier': '<carrier name>', 'fare_brand': '<fare name>',
                               'origin': '<IATA airport code>', 'destination': '<IATA airport code>',
                               'departure_date': '<DD/MM/YYYY>', 'departure_time': '<HH:MM>',
                               'return_date': '<DD/MM/YYYY>', 'return_time': '<HH:MM>'}]
"""

ALITALIA_ITINERARIES = [{'carrier': 'Alitalia', 'fare_brand': 'Economy Light',
                         'origin': 'FCO', 'destination': 'CTA',
                         'departure_date': '16/07/2021', 'departure_time': '17:00',
                         'return_date': '18/07/2021', 'return_time': '20:20'}]

RYANAIR_ITINERARIES = [{'carrier': 'Ryanair', 'fare_brand': 'Regular',
                        'origin': 'FCO', 'destination': 'CTA',
                        'departure_date': '16/07/2021', 'departure_time': '17:50',
                        'return_date': '18/07/2021', 'return_time': '20:10'}]

LUFTHANSA_ITINERARIES = [{'carrier': 'Lufthansa', 'fare_brand': 'Economy Light',
                          'origin': 'FCO', 'destination': 'MUC',
                          'departure_date': '23/07/2021', 'departure_time': '18:05',
                          'return_date': '25/07/2021', 'return_time': '20:25'}]

ITINERARIES = {'Alitalia': ALITALIA_ITINERARIES, 'Ryanair': RYANAIR_ITINERARIES, 'Lufthansa': LUFTHANSA_ITINERARIES}
