import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

class GoogleSheetsBotData:
    def __init__(self, creds_file, sheet_name="Apple", worksheet_name="TON-2", rows="100", cols="10"):
        self.creds_file = creds_file
        self.sheet_name = sheet_name
        self.worksheet_name = worksheet_name
        self.rows = rows
        self.cols = cols
        self.client = None
        self.sheet = None
        self._authorize()

    def _authorize(self):
        """Authorize access to Google Sheets using the credentials file."""
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_file, scope)
        self.client = gspread.authorize(creds)
        self._get_sheet()

    def _get_sheet(self):
        """Retrieve the spreadsheet and worksheet, creating them if necessary."""
        try:
            spreadsheet = self.client.open(self.sheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            spreadsheet = self.client.create(self.sheet_name)

        try:
            self.sheet = spreadsheet.worksheet(self.worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            self.sheet = spreadsheet.add_worksheet(title=self.worksheet_name, rows=self.rows, cols=self.cols)
            self._add_headers()

    def _add_headers(self):
        """Add headers to the Google Sheets worksheet."""
        headers = ["NAME", "BOT-LINK", "USER COUNT"]
        try:
            self.sheet.update('A1:C1', [headers])
        except Exception as e:
            print(f"An error occurred while adding headers: {e}")

    @staticmethod
    def _clean_user_count(user_count):
        """Remove 'monthly users' from the user count string."""
        if user_count and user_count != '-':
            return user_count.replace('monthly users', '').strip()
        return user_count

    def add_bot_data(self, json_file_path):
        """Add bot data from the JSON file to the Google Sheets worksheet."""
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        rows = []
        for bot_name, bot_info in data.items():
            user_count = bot_info[1] if bot_info[1].lower() != 'bot' else '-'
            cleaned_user_count = self._clean_user_count(user_count)
            row = [
                bot_name,          # Bot name
                bot_info[0],       # Bot link
                cleaned_user_count # Cleaned user count/status text (or '-')
            ]
            rows.append(row)

        try:
            self.sheet.update('A2:C', rows)  # Updates the rows from A2 onward
            print("Data added successfully to the worksheet.")
        except Exception as e:
            print(f"An error occurred while adding data: {e}")

# Example of how to use the class:
# if __name__ == '__main__':
#     creds_file = 'creds.json'
#     json_file_path = 'TON\\data\\bot_links_and_counts.json'
#     google_sheet_bot = GoogleSheetsBotData(creds_file)
#     google_sheet_bot.add_bot_data(json_file_path)
