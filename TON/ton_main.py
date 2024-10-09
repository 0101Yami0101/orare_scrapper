import os
from ton_games import TonGamesBaseUrlScraper
from extract_bot_links import TonBotLinkScraper
from extract_user_count import BotUserCountScraper
import write_data_on_sheet

class TonMainInit():
    """
    Scrape through 100s of TON projects and extract bot information.
    """
    def __init__(self):
        self.driver_path = 'D:\\chromedriver-win64\\chromedriver.exe'
        self.url = 'https://ton.app/games'
        self.output_folder = 'TON/data'
        self.profile_path = r'C:\Users\Sonit\AppData\Local\Google\Chrome\User Data'
        self.getBaseURLsForTonGames()
        self.scrapeBotLinksFromURLs()
        self.extractUserCountFromBotLinks()
        self.writeProcessedDataToSpreadSheet()
        


    def getBaseURLsForTonGames(self):
        """
        Scrape the base URLs and write in games_data.json

        """
        base_scraper = TonGamesBaseUrlScraper(self.driver_path, self.url, self.output_folder)
        base_scraper.scrape()


    def scrapeBotLinksFromURLs(self):
        """
        Extract TG bot's link from the base URLs

        """
        games_data_path = os.path.join('TON', 'data', 'games_data.json')
        output_file_path = os.path.join('TON', 'data', 'bot_links.json')
        botLink_scrapper = TonBotLinkScraper(self.driver_path, games_data_path, output_file_path)
        botLink_scrapper.scrape()


    def extractUserCountFromBotLinks(self):
        """
        Extract user count from each of the base URLs
        
        """
        bot_links_path = os.path.join('TON\\data', 'bot_links.json')
        output_file_path = os.path.join('TON\\data', 'bot_links_and_counts.json')

        userCount_scraper = BotUserCountScraper(self.driver_path, self.profile_path, bot_links_path, output_file_path)
        userCount_scraper.scrape()




    def writeProcessedDataToSpreadSheet(self):
        """
        Write the processed data to the Spreadsheet

        """
        creds_file = 'creds.json'
        json_file_path = 'TON\\data\\bot_links_and_counts.json'
        google_sheet_bot = write_data_on_sheet.GoogleSheetsBotData(creds_file)
        google_sheet_bot.add_bot_data(json_file_path)



if __name__== '__main__':
    TonMainInit()


