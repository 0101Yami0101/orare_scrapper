import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *
import time


sheetname= "apple"
worksheet= "tg"
# Auth
def authorize_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)
    return client


def addItemsToSpreadSheet(category, links_and_subs):
    """
    Function to add category - links - subscribers to spreadsheet
    """
    client = authorize_google_sheet()
    print("Here")
    # Open/Create a new spreadsheet
    spreadsheet_name = sheetname
    print(spreadsheet_name)
    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        spreadsheet = client.create(spreadsheet_name)

    # Select/Create worksheet
    worksheet_name = worksheet
    try:
        sheet = spreadsheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=worksheet_name, rows="100", cols="3")

    # Update worksheet with headers
    headers = ["Category", "Channel Link", "Subscribers"]
    sheet.batch_update([{
        'range': f'A1:C1',
        'values': [headers]
    }])

    
    if links_and_subs:
        #find first empty row in the worksheet
        next_row = len(sheet.col_values(1)) + 1
        required_rows = next_row + len(links_and_subs) - 1
        # Resize if needed
        if required_rows > sheet.row_count:
            sheet.add_rows(required_rows - sheet.row_count)

        updates = [] #Batch

        # Write data in batch
        for idx, (link, subs) in enumerate(links_and_subs.items(), start=next_row):
            updates.append({
                'range': f'A{idx}:C{idx}',
                'values': [[category, link, subs]]
            })

        sheet.batch_update(updates)
        time.sleep(5) #Sleep to handle excessive API calls


