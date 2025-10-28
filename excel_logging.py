import os
from datetime import datetime
from openpyxl import Workbook, load_workbook


def initiate_excel(filename="measurements.xlsx"):
    """
    Creates the Excel file with a header row if it doesn't exist.
    """
    if not os.path.exists(filename):
        print(f"Creating new Excel file: {filename}")
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Data"
        sheet.append(["Timestamp", "Value"])
        workbook.save(filename)


def write_to_excel(value, filename="measurements.xlsx"):
    """
    Appends a timestamp and a value to the specified Excel file.
    """
    try:
        workbook = load_workbook(filename)
        sheet = workbook.active
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append([timestamp, float(value)])
        workbook.save(filename)
        print(f"✓ Saved: {timestamp}, {value}")
        return True
    except PermissionError:
        print(f"ERROR: Could not save to Excel. Is '{filename}' open?")
        return False
    except Exception as e:
        print(f"An error occurred while writing to Excel: {e}")
        return False