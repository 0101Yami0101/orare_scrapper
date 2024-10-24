import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import re, os

class GoogleSheetsBotData:
    def __init__(self, creds_file, sheet_name="Apple", worksheet_name="mod", youtube_api_key="", rows="100", cols="10"):
        self.creds_file = creds_file
        self.sheet_name = sheet_name
        self.worksheet_name = worksheet_name
        self.rows = rows
        self.cols = cols
        self.client = None
        self.sheet = None
        self.youtube_api_key = youtube_api_key
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
        self._authorize()

    def _authorize(self):
        """Authorize access to Google Sheets using the credentials file."""
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_file, scope)
        self.client = gspread.authorize(creds)
        self._get_sheet()

    def _get_sheet(self):
        """Retrieve the spreadsheet and worksheet."""
        try:
            spreadsheet = self.client.open(self.sheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            spreadsheet = self.client.create(self.sheet_name)

        try:
            self.sheet = spreadsheet.worksheet(self.worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            self.sheet = spreadsheet.add_worksheet(title=self.worksheet_name, rows=self.rows, cols=self.cols)

    def _extract_channel_id(self, url):
        """Extract channel ID from the YouTube URL."""
        channel_id_pattern = r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:channel\/|c\/|user\/)?([a-zA-Z0-9_\-]+)'
        match = re.search(channel_id_pattern, url)
        return match.group(1) if match else None

    def get_channel_views(self, channel_id):
        """Fetch views of the last 5 videos from a YouTube channel."""
        try:
            response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()

            uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            videos_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=5
            ).execute()


            video_ids = [item['snippet']['resourceId']['videoId'] for item in videos_response['items']]
            video_stats_response = self.youtube.videos().list(
                part='statistics',
                id=','.join(video_ids)
            ).execute()

            views = [int(item['statistics']['viewCount']) for item in video_stats_response['items']]
            return views

        except Exception as e:
            print(f"An error occurred while fetching YouTube data: {e}")
            return []

    def process_youtube_channels(self):
        """Read YouTube channel links from the 2nd column, calculate average views, convert to K, and write to the 5th column."""
        try:

            youtube_links = self.sheet.col_values(2)

            for index, url in enumerate(youtube_links, start=1):  
                channel_id = self._extract_channel_id(url)
                if channel_id:
                    views = self.get_channel_views(channel_id)
                    if views:
                        average_views = sum(views) / len(views)
                    else:
                        average_views = 0 

                    average_in_k = average_views / 1000.0

                    row = index  
                    col = 5  
                    self.sheet.update_cell(row, col, round(average_in_k, 1))  
                else:
                    print(f"Could not extract channel ID from {url}")

        except Exception as e:
            print(f"An error occurred while processing YouTube channels: {e}")



#Standalone
   
bot = GoogleSheetsBotData(creds_file="creds.json", youtube_api_key=os.getenv('YT_API'))
bot.process_youtube_channels()
