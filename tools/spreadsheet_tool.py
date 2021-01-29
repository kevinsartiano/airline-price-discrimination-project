"""Tool to handle spreadsheet documents."""
import logging
import os
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.worksheet.worksheet import Worksheet


def export_to_csv(scraper, dirname: str = 'output', basename: str = 'raw_data'):
    """
    Export to CSV file.

    Parameters:
        scraper (Scraper): scraper containing the data to export
        basename (str): file name. Example: /foo_1/foo_2/bar.xlsx -> bar
        dirname (str): directory path (defaults to 'output'). Example: /foo_1/foo_2/bar.xlsx -> /foo_1/foo_2
    """
    path = os.path.join(dirname, basename + '.xlsx')
    book = load_workbook(path)
    sheet = book.active
    try:
        sheet.append([scraper.carrier,
                      scraper.itinerary['origin'],
                      scraper.itinerary['destination'],
                      scraper.itinerary['fare_brand'],
                      to_date(scraper.itinerary['departure_date']),
                      to_time(scraper.itinerary['departure_time']),
                      to_date(scraper.itinerary['return_date']),
                      to_time(scraper.itinerary['return_time']),
                      scraper.itinerary['departure_flight'],
                      to_float(scraper.itinerary['departure_price']),
                      scraper.itinerary['return_flight'],
                      to_float(scraper.itinerary['return_price']),
                      to_float(scraper.itinerary['total_price']),
                      to_float(scraper.itinerary['control_price']) - scraper.carrier_dcc,
                      scraper.itinerary['seats_left']])
    except KeyError as error:
        logging.warning(f'{scraper.carrier} - Missing {error}')
    adjust_column_width(sheet)
    sheet.freeze_panes = sheet['A2']
    sheet.auto_filter.ref = sheet.dimensions
    book.save(path)


def to_float(text: str) -> float or str:
    """Convert str to float if possible."""
    try:
        return round(float(text), 2)
    except ValueError:
        return text


def to_date(text: str) -> datetime or str:
    """Convert str to date if possible."""
    date_format = '%d/%m/%Y'
    try:
        return datetime.strptime(text, date_format).date()
    except ValueError:
        return text


def to_time(text: str) -> datetime or str:
    """Convert str to time if possible."""
    date_format = '%H:%M'
    try:
        return datetime.strptime(text, date_format).time()
    except ValueError:
        return text


def adjust_column_width(sheet: Worksheet):
    """Adjust the columns' width."""
    for i, column_cells in enumerate(sheet.columns, 1):
        length = max(len(str(cell.value)) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = length + 3
    for row in sheet.iter_rows(max_col=2):
        for cell in row:
            cell.alignment = Alignment(wrapText=True)
