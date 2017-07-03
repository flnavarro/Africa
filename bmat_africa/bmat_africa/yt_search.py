import unicodecsv as csv
import settings

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YoutubeSearch(object):
    def __init__(self):
        self.DEVELOPER_KEY = 'AIzaSyCP4gsM87jyGOJSexWastRbUq1n1Rk92zQ'
        self.YOUTUBE_API_SERVICE_NAME = 'youtube'
        self.YOUTUBE_API_VERSION = 'v3'
        self.youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, developerKey=self.DEVELOPER_KEY,
                             cache_discovery=False)

        self.check_list = []
        self.exec_list = []
        self.song_list = []
        self.youtube_links = []

    def load_exec_file(self):
        with open('exec_file.csv', 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.exec_list.append(row)
        with open('check_file.csv', 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.check_list.append(row)
        for exec_track in self.exec_list:
            is_new = True
            for check_track in self.check_list:
                if exec_track[0].lower() == check_track[0].lower() \
                        and exec_track[1].lower() == check_track[1].lower():
                    is_new = False
                    break
            if is_new:
                self.song_list.append(exec_track)

    def youtube_search(self, query):
        max_results = 20
        search_response = self.youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results
        ).execute()

        # videos = []
        yt_link = ''
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                query_split = query.split(' ')
                word_count = 0
                word_total = 0
                print('QUERY -> ' + query)
                for word in query_split:
                    if len(word) > 1:
                        word_total += 1
                        if word.lower() in search_result['snippet']['title'].lower():
                            word_count += 1
                if word_total != 0:
                    if float(word_count) / float(word_total) > 0.55:
                        all_words_in_result = True
                    else:
                        all_words_in_result = False
                    if all_words_in_result:
                        yt_link = 'https://www.youtube.com/watch?v=' + search_result['id']['videoId']
                        break
                    # videos.append({'title': search_result['snippet']['title'], 'id': search_result['id']['videoId'],
                    #                'description': search_result['snippet']['description'],
                    #                'channel': search_result["snippet"]["channelTitle"]})

        return yt_link

    def get_links(self):
        self.load_exec_file()
        for song in self.song_list:
            yt_link = ''
            # if 'youtube' not in song[3]:
            query = song[0] + ' ' + song[1]
            try:
                yt_link = self.youtube_search(query)
                if yt_link == '' and 'FEAT.' in song[0]:
                    new_query = song[0].split('FEAT.')[0] + ' ' + song[1]
                    try:
                        yt_link = self.youtube_search(new_query)
                    except HttpError:
                        yt_link = ''
                        print('Http Error')
            except HttpError:
                yt_link = ''
                print('HTTP error')
            # else:
            #    yt_link = song[3]
            print('YOUTUBE LINK ->' + yt_link)
            self.youtube_links.append(yt_link)
        self.save_links()

    def save_links(self):
        artists = [i[0] for i in self.song_list]
        titles = [i[1] for i in self.song_list]
        dates = [i[2] for i in self.song_list]
        posts = [i[3] for i in self.song_list]
        # dl_url = [i[3] for i in self.song_list]
        self.song_list = zip(artists, titles, self.youtube_links)
        with open('exec_file_links.csv', 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.song_list)
