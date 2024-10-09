import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TonGamesBaseUrlScraper:
    """
    From the link, Get all the TON games links
    """
    def __init__(self, driver_path, url, output_folder):
        self.driver_path = driver_path
        self.url = url
        self.output_folder = output_folder
        self.driver = None

    def start_driver(self):
        chrome_service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=chrome_service)

    def scrape(self):
        self.start_driver()
        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'CategoryAppsWrapper__list'))
            )
        except Exception as e:
            print(f"Error: {e}")
            self.driver.quit()
            return

        time.sleep(3)
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        category_apps_div = soup.find('div', class_='CategoryAppsWrapper__list')
        data = {}

        if category_apps_div:
            links = category_apps_div.find_all('a', href=True)
            for link in links:
                href = link['href']
                title_div = link.find('div', class_='title-app')
                if title_div:
                    title_text = title_div.find('h5')
                    if title_text:
                        data[href] = title_text.text.strip()
                    else:
                        data[href] = "Title not found"
                else:
                    data[href] = "Title div not found"

        self.driver.quit()
        self.save_data(data)

    def save_data(self, data):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        json_file_path = os.path.join(self.output_folder, 'games_data.json')
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

        print(f"Data saved to {json_file_path}")