import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TonBotLinkScraper:
    def __init__(self, driver_path, games_data_path, output_path):
        self.driver_path = driver_path
        self.games_data_path = games_data_path
        self.output_path = output_path
        self.driver = None

    def load_games_data(self):
        with open(self.games_data_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def setup_driver(self):
        chrome_service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=chrome_service)
        self.driver.maximize_window()

    def extract_telegram_link(self, game_link, game_name):
        if game_link.startswith('https://t.me/'):
            return {game_name: game_link}
        
        self.driver.get(game_link)
        
        try:
            button_div = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'open__app__btn'))
            )
            button_div.click()
            
            current_url = self.driver.current_url
            if current_url.startswith('https://t.me/'):
                return {game_name: current_url}
            
            try:
                dropdown_menu = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'PageHeadRightSide__drop-container'))
                )
                
                dropdown_links = dropdown_menu.find_elements(By.TAG_NAME, 'a')
                
                for link in dropdown_links:
                    if 'Telegram bot' in link.text:
                        telegram_bot_link = link.get_attribute('href')
                        return {game_name: telegram_bot_link}
            except:
                all_handles = self.driver.window_handles
                if len(all_handles) > 1:
                    self.driver.switch_to.window(all_handles[-1])
                    time.sleep(3)
                    telegram_url = self.driver.current_url
                    self.driver.close()
                    self.driver.switch_to.window(all_handles[0])
                    return {game_name: telegram_url}
        
        except Exception as e:
            return None

    def scrape(self):
        games_data = self.load_games_data()
        self.setup_driver()

        bot_links = {}
        for game_link, game_name in games_data.items():
            bot_link = self.extract_telegram_link(game_link, game_name)
            if bot_link is not None:
                bot_links.update(bot_link)

        self.driver.quit()
        self.save_data(bot_links)

    def save_data(self, data):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Bot links saved to {self.output_path}")


# if __name__ == '__main__':
#     driver_path = 'D:\\chromedriver-win64\\chromedriver.exe'
#     games_data_path = os.path.join('TON', 'data', 'games_data.json')
#     output_path = os.path.join('TON', 'data', 'bot_links.json')

#     scraper = TonBotLinkScraper(driver_path, games_data_path, output_path)
#     scraper.scrape()
