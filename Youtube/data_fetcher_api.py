import googleapiclient.discovery
import os
import json
from Youtube.info_extractor import extract_and_process_data
from Youtube.write_on_sheet import addItemsToWsheet

class YouTubeDataFetcher:
    """
    Youtube search scrapper class
    """
    def __init__(self, api_key, queries, min_view_count=500, region_code='US', language='en', country='US'):
     
        self.api_key = api_key
        self.queries = queries
        self.min_view_count = min_view_count
        self.region_code = region_code
        self.language = language
        self.country = country
        self.youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=self.api_key)
        self.video_ids = []
        self.video_details = []
        self.video_stats = {}
        self.video_descs = {}
        self.channel_info = {}
        self.data_to_store = []
        self.existing_channel_names = set()
        self.fetch_data()
        self.save_to_file() #Generates query results saves as yt_data.json
        self.process_data_and_add_to_sheet() #Generates processed_data.json and add it to spreadsheet

    def search_videos(self, query):
        request = self.youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=300,
            order="viewCount",
            # regionCode=self.region_code,
            # relevanceLanguage=self.language
        )
        response = request.execute()
        return response['items']

    def get_video_stats(self, video_ids):
        video_id_batches = [video_ids[i:i + 50] for i in range(0, len(video_ids), 50)]
        video_stats = {}
        for batch in video_id_batches:
            request = self.youtube.videos().list(
                part="statistics",
                id=','.join(batch)
            )
            try:
                response = request.execute()
                video_stats.update({item['id']: item['statistics'] for item in response['items']})
            except googleapiclient.errors.HttpError as e:
                print(f"Error fetching video stats: {e}")
        return video_stats

    def get_video_details(self, video_ids):
        video_id_batches = [video_ids[i:i + 50] for i in range(0, len(video_ids), 50)]
        video_details = {}
        for batch in video_id_batches:
            request = self.youtube.videos().list(
                part="snippet",
                id=','.join(batch)
            )
            try:
                response = request.execute()
                video_details.update({item['id']: item['snippet']['description'] for item in response['items']})
            except googleapiclient.errors.HttpError as e:
                print(f"Error fetching video details: {e}")
        return video_details

    def get_channels_about(self, channel_ids):
        channel_id_batches = [channel_ids[i:i + 50] for i in range(0, len(channel_ids), 50)]
        channel_info = {}
        for batch in channel_id_batches:
            request = self.youtube.channels().list(
                part="snippet",
                id=','.join(batch),
                maxResults=50
            )
            try:
                response = request.execute()
                if 'items' in response:
                    channel_info.update({
                        item['id']: {
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description']
                        } for item in response['items']
                    })
                else:
                    print("No channels found or unexpected response structure:", response)
            except googleapiclient.errors.HttpError as e:
                print(f"Error fetching channel info: {e}")
        return channel_info

    def fetch_data(self):
        for query in self.queries:
            videos = self.search_videos(query)
            
            for video in videos:
                video_id = video['id']['videoId']
                self.video_ids.append(video_id)
                self.video_details.append({
                    'video_id': video_id,
                    'channel_id': video['snippet']['channelId'],
                    'video_title': video['snippet']['title']
                })

            self.video_stats = self.get_video_stats(self.video_ids)
            self.video_descs = self.get_video_details(self.video_ids)
            
            videos_with_views = [
                {
                    'video_id': video['video_id'],
                    'view_count': int(self.video_stats.get(video['video_id'], {}).get('viewCount', 0)),
                    'channel_id': video['channel_id'],
                    'video_title': video['video_title']
                }
                for video in self.video_details
                if int(self.video_stats.get(video['video_id'], {}).get('viewCount', 0)) > self.min_view_count
            ]
            
            videos_with_views.sort(key=lambda x: x['view_count'], reverse=True)
            
            unique_channel_ids = {video['channel_id'] for video in videos_with_views}
            
            self.channel_info = self.get_channels_about(list(unique_channel_ids))
            
            for video in videos_with_views:
                video_id = video['video_id']
                channel_id = video['channel_id']
                
                channel_data = self.channel_info.get(channel_id, {
                    "title": "Unknown Channel",
                    "description": "No description available"
                })
                
                channel_name = channel_data['title']
                channel_link = f"https://www.youtube.com/channel/{channel_id}"
                
                if channel_name not in self.existing_channel_names:
                    self.existing_channel_names.add(channel_name)
                    self.data_to_store.append({
                        "video_id": video_id,
                        "video_description": self.video_descs.get(video_id, "No description available"),
                        "channel_name": channel_name,
                        "channel_about": channel_data['description'],
                        "channel_link": channel_link
                    })

    def save_to_file(self, filename='yt_data.json'):
        """
        Function to write yt_data.json from scraped data
        """
        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                existing_data = json.load(json_file)
        else:
            existing_data = []

        existing_data.extend(self.data_to_store)

        with open(filename, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)


    def process_data_and_add_to_sheet(self, filename= 'processed_data.json'):
        """
        Function to read yt_data.json, process the data and write it in spreadsheet
        """
        #processes yt_data.json and find emails and links corresponding to it
        extract_and_process_data("yt_data.json") # (generates processed_data.json)
        #Write processed results to Worksheet
        addItemsToWsheet(jsonfilename=filename)
        