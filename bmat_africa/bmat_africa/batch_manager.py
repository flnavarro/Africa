import unicodecsv as csv
import settings
from yt_downloader import YoutubeDownloader
from metadata import ManageMetadata
import time
import os


class Track(object):
    def __init__(self, artist, title, url):
        self.artist = artist.title()
        self.title = title.title()
        self.youtube_url = url


class BatchManager(object):
    def __init__(self, n_tracks_per_batch):
        self.n_tracks_per_batch = n_tracks_per_batch

        self.song_list = []
        with open('exec_file_links.csv', 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.song_list.append(row)
        self.song_list.reverse()

        self.all_tracks_log = []
        with open('check_file.csv', 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.all_tracks_log.append(row)

        self.tracks = []
        for track in self.song_list:
            self.tracks.append(Track(track[0], track[1], track[2]))

        self.yt_downloader = YoutubeDownloader()
        self.metadata = ManageMetadata()

        self.batches_path = 'batches/'
        self.current_batch_number = 1
        self.current_batch_size = 0
        self.current_batch_path = ''
        self.tracks_path = ''
        self.date = ''
        self.date_previous_batch = ''
        self.create_batch()

    def create_batch(self):
        self.date = time.strftime('%Y%m%d')
        if self.date != self.date_previous_batch:
            self.current_batch_number = 1
        else:
            self.current_batch_number += 1
        batch_number_4d = str(self.current_batch_number).zfill(4)
        current_batch_name = self.date + '_' + batch_number_4d
        self.current_batch_path = self.batches_path + current_batch_name + '/'
        self.tracks_path = self.current_batch_path + 'tracks/'
        if not os.path.exists(self.current_batch_path):
            os.makedirs(self.current_batch_path)
        if not os.path.exists(self.tracks_path):
            os.makedirs(self.tracks_path)
        self.date_previous_batch = self.date
        self.current_batch_size = 0
        self.metadata.initialize(self.current_batch_path)

    def update_track_log(self, track):
        new_track = [track.artist, track.title, track.youtube_url]
        self.all_tracks_log.reverse()
        self.all_tracks_log.append(new_track)
        self.all_tracks_log.reverse()
        with open('check_file.csv', 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.all_tracks_log)

    def make_batches(self):
        for track in self.tracks:
            if track.youtube_url != '':
                track_info = track.title + ' from artist ' + track.artist
                self.yt_downloader.download(track.youtube_url, self.tracks_path, track_info)

                self.metadata.add_track(track, self.yt_downloader.file_url)
                self.metadata.add_to_sheet()

                self.update_track_log(track)

                self.current_batch_size += 1

            if self.current_batch_size == self.n_tracks_per_batch:
                # Delivery complete etc
                print('Batch completed.')