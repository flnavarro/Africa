import unicodecsv as csv
import settings

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YoutubeSearch(object):
    def __init__(self):
        self.DEVELOPER_KEY = 'AIzaSyCP4gsM87jyGOJSexWastRbUq1n1Rk92zQ'
        self.YOUTUBE_API_SERVICE_NAME = 'youtube'
        self.YOUTUBE_API_VERSION = 'v3'
        self.youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, developerKey=self.DEVELOPER_KEY, cache_discovery=False)

        self.song_list = []

    def load_exec_file(self):
        with open('exec_file_clean.csv', 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.song_list.append(row)

    def youtube_search(self, query):
        max_results = 20
        search_response = self.youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results
        ).execute()

        # videos = []
        video_result_id = None
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                query_split = query.split(' ')
                all_words_in_result = True
                for word in query_split:
                    if len(word) > 1 and word.lower() not in search_result['snippet']['title'].lower():
                        all_words_in_result = False
                        break
                if all_words_in_result:
                    video_result_id = search_result['id']['videoId']
                    break
                # videos.append({'title': search_result['snippet']['title'], 'id': search_result['id']['videoId'],
                #                'description': search_result['snippet']['description'],
                #                'channel': search_result["snippet"]["channelTitle"]})

        return video_result_id

    def get_links(self):
        self.load_exec_file()
        for song in self.song_list:
            if 'youtube' not in song[3]:
                song_split = song[0].split(' ')
                query = ''
                for word in song_split:
                    if len(word) > 1:
                        query += ' ' + word
                try:
                    video_result_id = self.youtube_search(query)
                    if video_result_id is None:
                        new_query = ''
                        query_split = query.split(' ')
                        for word in query_split:
                            if query_split.index(word) != 2:
                                if word.lower() != 'feat' and word.lower() != 'feat.':
                                    new_query += ' ' + word
                        try:
                            video_result_id = self.youtube_search(new_query)
                        except HttpError:
                            print('Http Error')
                except HttpError:
                    print('HTTP error')
