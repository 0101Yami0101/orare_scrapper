import os
from Youtube.data_fetcher_api import YouTubeDataFetcher


api_key = os.getenv('YT_API')

def start_fetch_and_write_sheet(search_queries):
    """
    Function to initialise the Youtube scrapping process
    """

    queries= search_queries
    YouTubeDataFetcher(api_key, queries)
