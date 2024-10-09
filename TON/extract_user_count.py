import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BotUserCountScraper:
    def __init__(self, driver_path, profile_path, bot_links_path, output_path):
        self.driver_path = driver_path
        self.profile_path = profile_path
        self.bot_links_path = bot_links_path
        self.output_path = output_path
        self.driver = None

    def load_bot_links(self):
        with open(self.bot_links_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def setup_driver(self):
        chrome_service = Service(self.driver_path)
        chrome_options = Options()
        chrome_options.add_argument(f"user-data-dir={self.profile_path}")
        chrome_options.add_argument("profile-directory=Default")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        self.driver.maximize_window()

    def extract_user_count(self, bot_link, bot_name):
        try:
            self.driver.get(bot_link)
            time.sleep(5)

            action_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'tgme_action_button_new.tgme_action_web_button'))
            )
            action_button.click()

            try:
                open_in_web_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Open in Web')]"))
                )
                open_in_web_button.click()
            except:
                pass

            user_status_span = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'user-status'))
            )
            return user_status_span.text

        except Exception as e:
            print(f"Error for {bot_name} ({bot_link}): {e}")
            return None

    def scrape(self):
        bot_links = self.load_bot_links()
        self.setup_driver()
        bot_links_and_counts = {}

        for bot_name, bot_link in bot_links.items():
            user_status = self.extract_user_count(bot_link, bot_name)
            if user_status:
                bot_links_and_counts[bot_name] = [bot_link, user_status]

        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(bot_links_and_counts, f, ensure_ascii=False, indent=4)

        self.driver.quit()


# if __name__ == '__main__':
#     driver_path = 'D:\\chromedriver-win64\\chromedriver.exe'
#     profile_path = r'C:\Users\Sonit\AppData\Local\Google\Chrome\User Data'
#     bot_links_path = os.path.join('TON\\data', 'bot_links.json')
#     output_path = os.path.join('TON\\data', 'bot_links_and_counts.json')

#     scraper = BotUserCountScraper(driver_path, profile_path, bot_links_path, output_path)
#     scraper.scrape()
