"""Tool to handle spreadsheet documents."""
import logging
import os
from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.worksheet.worksheet import Worksheet


def export_to_csv(data: list, basename: str, dirname: str = 'output'):
    """
    Export to CSV file.

    Parameters:
        data (dict): data to export
        basename (str): file name. Example: /foo_1/foo_2/bar.xlsx -> bar
        dirname (str): directory path (defaults to 'output'). Example: /foo_1/foo_2/bar.xlsx -> /foo_1/foo_2
    """
    book = Workbook()
    sheet = book.active
    headers = ['carrier', 'origin', 'destination', 'fare_brand',
               'departure_date', 'departure_time', 'return_date', 'return_time',
               'departure_flight', 'departure_price', 'return_flight', 'return_price',
               'total_price', 'control_price', 'seats_left']
    sheet.append(headers)
    for row in data:
        try:
            sheet.append([row['carrier'], row['origin'], row['destination'], row['fare_brand'],
                          row['departure_date'], row['departure_time'], row['return_date'], row['return_time'],
                          row['departure_flight'], row['departure_price'], row['return_flight'], row['return_price'],
                          row['total_price'], row['control_price'], row['seats_left']])

        except KeyError as error:
            logging.warning(f'Missing {error} for {row["carrier"]}')
    adjust_column_width(sheet)
    sheet.freeze_panes = sheet['A2']
    sheet.auto_filter.ref = sheet.dimensions
    path = os.path.join(dirname, basename + '.xlsx')
    book.save(path)


def adjust_column_width(sheet: Worksheet):
    """Adjust the columns' width."""
    for i, column_cells in enumerate(sheet.columns, 1):
        length = max(len(str(cell.value)) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = length + 3
    for row in sheet.iter_rows(max_col=2):
        for cell in row:
            cell.alignment = Alignment(wrapText=True)
