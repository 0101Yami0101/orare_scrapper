import os
from Youtube.data_fetcher_api import YouTubeDataFetcher
from Youtube.data_fetcher_api_2 import YouTubeDataFetcher2


api_key = os.getenv('YT_API')

def start_fetch_and_write_sheet(search_queries):
    """
    Function to initialise the Youtube scrapping process
    """

    queries= search_queries
    # YouTubeDataFetcher(api_key, queries)
    YouTubeDataFetcher2(api_key, queries)
