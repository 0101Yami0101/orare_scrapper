import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

def authorize_sheet():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)
    return client

def addItemsToWsheet(jsonfilename):
    """
    Function to items to spreadsheet
    """
    client = authorize_sheet()

    try:
        spreadsheet = client.open("Apple")
    except gspread.exceptions.SpreadsheetNotFound:
        spreadsheet = client.create("Apple")

    try:
        sheet = spreadsheet.worksheet("new")
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title="new", rows="100", cols="10")


    headers = ["channel_name", "channel_link", "email", "tg"]
    try:
        sheet.update('A1:D1', [headers])  # Update headers using the `update` method
    except Exception as e:
        print(f"An error occurred while adding headers: {e}")

    # Load data from processed_data.json
    with open(jsonfilename, 'r') as file:
        data = json.load(file)

    # Prepare data to write to the sheet
    rows = []
    for item in data:
        row = [
            item.get("channel_name", ""),
            item.get("channel_link", ""),
            '\n'.join(item.get("email", [])),  
            '\n'.join(item.get("tg", []))      
        ]
        rows.append(row)

    # Write data to the sheet starting from the second row
    try:
        sheet.update('A2:D', rows)  # Updates from row 2 downwards
        print("Data added successful IndianYT")
    except Exception as e:
        print(f"An error occurred while adding data: {e}")
