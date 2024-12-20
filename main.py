from Telegram.scrapper import Scrapper
import json
from Telegram.writespreadsheet import addItemsToSpreadSheet
from Telegram.sheetformat import formatTheWorksheet
from Youtube.start_process import start_fetch_and_write_sheet
from TON.ton_main import TonMainInit


with open('Telegram/categories.json', 'r') as file:
    data = json.load(file)


if __name__== '__main__':

    #TelegramPROCESS
    # if data:
    #     for category, cat_link in data['categories'].items():
            
    #         scrap_category= Scrapper(url= cat_link)
    #         current_cat_chLinks_subs= scrap_category.channel_id_links  #{link : subs}   
    #         addItemsToSpreadSheet(category, current_cat_chLinks_subs) # Add items to SPREADSHEET
    #     formatTheWorksheet()


    # Youtube PROCESS
    queries = [
    "SEED App - Mine SEED",
    "Rocky Rabbit",
    "GAMEE Ton Telegram",
    "Clayton",
    "TON Station",
    "Tongotchi",
    "CITY Holder",
    "Dotcoin",
    "Boinkers Parody Game",
    "TapCoins",
    "Notcoin",
    "Banana",
    "Dragonz Land",
    "Crypto Critters",
    "Token Tycoon",
    "Golden Goose",
    "Pixel Pirates",
    "Puffin Prodigy",
    "Peanut Coin",
    "Rocket Raccoon",
    "Diamond Diggers",
    "Coin Climber",
    "Berry Bank",
    "Gem Gamers",
    "Pixel Pets",
    "Token Toss",
    "Space Seeds",
    "Coin Catcher",
    "Prize Pop",
    "Lucky Lemur",
    "Egg Empires"
]


    start_fetch_and_write_sheet(search_queries= queries)


    # # TON PROCESS
    # TonMainInit()
#SnakeTON, Cat gold miner

# Instead of processing each link and adding corresponding items to spreadsheet in each iteration, we can store all the processed links and subs in a dictionary and use batch update of spreadsheet to push all the dict[cat-links-subs] in one go (batch)