from Telegram.scrapper import Scrapper
import json
from Telegram.writespreadsheet import addItemsToSpreadSheet
from Telegram.sheetformat import formatTheWorksheet
with open('Telegram/categories.json', 'r') as file:
    data = json.load(file)


if __name__== '__main__':

    #TG SCRAP PROCESS
    if data:
        for category, cat_link in data['categories'].items():
            
            scrap_category= Scrapper(url= cat_link)
            current_cat_chLinks_subs= scrap_category.channel_id_links  #{link : subs}
            # Add items to SPREADSHEET
            addItemsToSpreadSheet(category, current_cat_chLinks_subs) 

        formatTheWorksheet()


# Instead of processing each link and adding corresponding items to spreadsheet in each iteration, we can store all the processed links and subs in a dictionary and use batch update of spreadsheet to push all the dict[cat-links-subs] in one go (batch)