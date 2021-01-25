"""Tool to handle spreadsheet documents."""

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
    sheet.append([header for header in data[0].keys()])
    for row in data:
        sheet.append(list(row.values()))
    adjust_column_width(sheet)
    sheet.freeze_panes = sheet['A2']
    sheet.auto_filter.ref = sheet.dimensions
    path = os.path.join(dirname, basename + '.xlsx')
    book.save(path)


def adjust_column_width(sheet: Worksheet):
    """Adjust the columns' width."""
    for i, column_cells in enumerate(sheet.columns, 1):
        if i <= 3:
            sheet.column_dimensions[column_cells[0].column_letter].width = 25
            continue
        length = max(len(str(cell.value)) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = length + 3
    for row in sheet.iter_rows(max_col=2):
        for cell in row:
            cell.alignment = Alignment(wrapText=True)
