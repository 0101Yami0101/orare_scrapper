import re
import requests
from bs4 import BeautifulSoup
from collections import deque

import requests

class DataFetcher:
    """
    Scrap additional data if needed after default GET request
    """
    def __init__(self,cat_url, channel_links, minSub ):
        self.categoryUrl= cat_url
        self.base_url = f"{self.categoryUrl}items"
        self.channel_links= channel_links
        self.minSubs= minSub
        self.session = requests.Session()
        self.csrf_token = self.get_csrf_token()  
        self.page= 1
        self.post_request_for_additional_page()
        

    def get_csrf_token(self):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = self.session.get("https://in.tgstat.com", headers= header)
        soup = BeautifulSoup(response.text, 'html.parser')
        token_element = soup.find('meta', {'name': 'csrf-token'})
        if token_element:
            token = token_element.get('content')
        else:
            token_element = soup.find('input', {'name': '_tgstat_csrk'})
            if token_element:
                token = token_element.get('value')
            else:
                raise ValueError("CSRF token not found")
        
        return token


    def post_request_for_additional_page(self):
       
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://in.tgstat.com",
            "Referer": self.categoryUrl,
            "X-Requested-With": "XMLHttpRequest",
        }

        cookies = {
            "_gid": "GA1.2.625564187.1725351805",
            "_ym_uid": "1725351806388510174",
            "_ym_d": "1725351806",
            "_ym_isad": "2",
            "tgstat_idrk": "7e3eafd64414013cf91daf043c570214145d753611f0371f2d35b99b7ceed7b9a%3A2%3A%7Bi%3A0%3Bs%3A11%3A%22tgstat_idrk%22%3Bi%3A1%3Bs%3A52%3A%22%5B8182905%2C%222CrG_0vrWZk1Y8T2MyZRcI7ray3701Do%22%2C2592000%5D%22%3B%7D",
            "tgstat_sirk": "n866kunqsfd3gt61ck1a7h70ob",
            "_tgstat_csrk": self.csrf_token,
        }

        data = {
            "_tgstat_csrk": self.csrf_token,
            "peer_type": "channel",
            "sort_channel": "members",
            "sort_chat": "members",
            "page": self.page,
            "offset": "0"
        }

        response = self.session.post(self.base_url, headers=headers, cookies=cookies, data=data)

        if response.status_code == 200:
            # Process the JSON 
            json_data = response.json()  
            html_content = json_data.get('html', '')
            # Make soup/Parsing to html
            soup = BeautifulSoup(html_content, 'html.parser')
            links = soup.find_all('a', href=True, class_='text-body')
            for link in links:
                currentChannelLink = link['href']
                currentChannelSubsStr= link.find('div', class_='font-12 text-truncate').get_text(strip=True)
                currentChannelSubs = int ( re.sub(r'\D', '', currentChannelSubsStr))
                if currentChannelSubs > self.minSubs: #Keep higher for lower recursive calls
                    self.channel_links[currentChannelLink]= currentChannelSubs
                else:  
                    # print("Returning", self.channel_links)       
                    return self.channel_links

            self.page+=1
            self.post_request_for_additional_page()


class Scrapper():
    """
    Scrap telegram channel id and subscribers count from https://in.tgstat.com
    """
    def __init__(self, url):
        self.url= url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.targetMinSubs= 100000
        self.channel_links= {}
        self.channel_id_links= {}
        self.getRequestForDefaultPage()
        self.makeIDsFromAllChannelLinks()


    def getRequestForDefaultPage(self):

        response = requests.get(url= self.url, headers= self.headers)
        soup= BeautifulSoup(response.text, features="lxml")

        forms = soup.find_all('form')
        for form in forms:
            links = form.find_all('a', href=True, class_='text-body')  # Finds all <a> tags with an href attribute within the form
            for link in links:
                currentChannelLink = link['href']
                currentChannelSubsStr= link.find('div', class_='font-12 text-truncate').get_text(strip=True)
                currentChannelSubs = int ( re.sub(r'\D', '', currentChannelSubsStr))
                if currentChannelSubs > self.targetMinSubs:
                    self.channel_links[currentChannelLink]= currentChannelSubs
                else:
                    
                    return 

        fetcher = DataFetcher(self.url, self.channel_links, self.targetMinSubs)
        self.channel_links = fetcher.channel_links
        return 
    

    def makeIDsFromAllChannelLinks(self):

        for key, value in self.channel_links.items():
            channel_name = key.split('@')[-1]
            self.channel_id_links[f"https://t.me/{channel_name}"] = value

        return 

    