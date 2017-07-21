import unicodecsv as csv
import settings
import os
from operator import itemgetter
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YoutubeSearch(object):
    def __init__(self):
        self.DEVELOPER_KEY = 'AIzaSyCP4gsM87jyGOJSexWastRbUq1n1Rk92zQ'
        self.YOUTUBE_API_SERVICE_NAME = 'youtube'
        self.YOUTUBE_API_VERSION = 'v3'
        self.youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, developerKey=self.DEVELOPER_KEY,
                             cache_discovery=False)

        self.dl_list = []
        self.all_tracks = []
        self.embed_urls = []
        self.track_list = []
        self.yt_links = []
        self.yt_titles = []
        self.load_tracks()

    def load_tracks(self):
        # Load download list of tracks
        with open(settings.DL_LIST, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.dl_list.append(row)

        # All tracks crawled
        if not os.path.isfile(settings.ALL_TRACKS):
            # Create new if it doesn't exist
            empty_list = zip([' '], [' '], [' '])
            with open(settings.ALL_TRACKS, 'w') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerows(empty_list)
        # Load all tracks crawled
        with open(settings.ALL_TRACKS, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.all_tracks.append(row)

        # Load embed urls for download list of tracks
        if os.path.isfile(settings.EMBED_URLS):
            with open(settings.EMBED_URLS, 'rb') as f:
                reader = csv.reader(f, delimiter='\t')
                embed_urls = []
                for row in reader:
                    embed_urls.append(row)
                embed_urls = sorted(embed_urls, key=itemgetter(1))
        else:
            self.embed_urls = None

        # Check if tracks in download list have ever been downloaded
        for dl_track in self.dl_list:
            is_new = True
            for track in self.all_tracks:
                if dl_track[0].lower() == track[0].lower() \
                        and dl_track[1].lower() == track[1].lower():
                    is_new = False
                    break
            if is_new:
                # It the track is new, append to search for youtube link
                self.track_list.append(dl_track)
                if self.embed_urls is not None:
                    self.embed_urls.append(embed_urls[self.dl_list.index(dl_track)])

    def youtube_search(self, query):
        # Search query in Youtube
        max_results = 20
        search_response = self.youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results
        ).execute()

        yt_link = ''
        yt_title = ''
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                query_split = query.split(' ')
                word_count = 0
                word_total = 0
                # Check that words in query are in the resulting video title
                for word in query_split:
                    if len(word) > 1:
                        word_total += 1
                        if word.lower() in search_result['snippet']['title'].lower():
                            word_count += 1
                if word_total != 0:
                    if float(word_count) / float(word_total) > 0.6:
                        all_words_in_result = True
                    else:
                        all_words_in_result = False
                    if all_words_in_result:
                        # Get youtube link
                        yt_link = 'https://www.youtube.com/watch?v=' + search_result['id']['videoId']
                        yt_title = search_result['snippet']['title']
                        break
        return yt_link, yt_title

    def save_links(self):
        artists = [i[0] for i in self.track_list]
        titles = [i[1] for i in self.track_list]
        post_links = [i[2] for i in self.track_list]
        post_titles = [i[3] for i in self.track_list]
        post_dates = [i[4] for i in self.track_list]
        self.track_list = zip(artists, titles, self.yt_links, self.yt_titles, post_titles, post_links)
        with open(settings.DL_LIST, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.track_list)

    def get_links(self):
        print('Obtaining youtube links for tracks...')
        for track in self.track_list:
            if self.embed_urls is not None:
                if self.embed_urls[self.track_list.index(track)][0] != '':
                    # If we already have a youtube link in embed, get link
                    yt_link = self.embed_urls[self.track_list.index(track)][0]
                    self.yt_links.append(yt_link)
                    self.yt_titles.append('')
                    continue
            # Otherwise search in youtube
            query = track[0] + ' ' + track[1]
            yt_link = ''
            yt_title = ''
            try:
                yt_link, yt_title = self.youtube_search(query)
                # If there's no result
                if yt_link == '':
                    new_query = ''
                    if 'FEAT.' in track[0]:
                        # If it's a FEAT. in artist, take it away
                        new_query = track[0].split('FEAT.')[0] + ' ' + track[1]
                    else:
                        # If there's no title
                        if track[1] == '':
                            for word in track[0].strip().split():
                                # Get capitalized words in artist as title
                                if word.isupper():
                                    track[1] += word + ' '
                        # If there's a title now
                        if track[1] != '':
                            # If there's more words in artist, just use first and use new query
                            track[0] = track[0].split(' ')[0]
                            new_query = track[0] + ' ' + track[1]
                    if new_query != '':
                        try:
                            yt_link, yt_title = self.youtube_search(new_query)
                        except HttpError:
                            print('Http Error')
            except HttpError:
                print('HTTP error')
            self.yt_links.append(yt_link)
            self.yt_titles.append(yt_title)
        self.save_links()
