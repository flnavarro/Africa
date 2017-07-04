import unicodecsv as csv
import settings
from yt_downloader import YoutubeDownloader
from metadata import ManageMetadata
import time
import os
import logging


class Track(object):
    def __init__(self, artist, title, url):
        self.artist = artist.title()
        self.title = title.title()
        self.youtube_url = url


class BatchManager(object):
    def __init__(self, n_tracks_per_batch, batches_path):
        self.n_tracks_per_batch = n_tracks_per_batch
        self.batches_path = batches_path

        self.global_log = None
        self.open_global_log()

        self.dl_list = []
        with open(settings.DL_LIST, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.dl_list.append(row)
        self.dl_list.reverse()

        self.all_tracks = []
        with open(settings.ALL_TRACKS, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.all_tracks.append(row)

        self.tracks = []
        for dl_track in self.dl_list:
            self.tracks.append(Track(dl_track[0], dl_track[1], dl_track[2]))

        self.yt_downloader = YoutubeDownloader()
        self.metadata = ManageMetadata()

        self.current_batch_log = None
        self.current_batch_number = 1
        self.current_batch_size = 0
        self.current_batch_path = ''
        self.tracks_path = ''
        self.date = ''
        self.date_previous_batch = ''
        self.create_batch()

    def open_global_log(self):
        # Create global log
        self.global_log = logging.getLogger(self.batches_path)
        file_handler = logging.FileHandler(self.batches_path + 'global.log', mode='w')
        self.global_log.setLevel(logging.WARNING)
        self.global_log.addHandler(file_handler)

    def open_batch_log(self):
        # Create batch log
        self.current_batch_log = logging.getLogger(self.current_batch_path)
        file_handler = logging.FileHandler(self.current_batch_path + 'batch_log.log', mode='w')
        self.current_batch_log.setLevel(logging.WARNING)
        self.current_batch_log.addHandler(file_handler)

    def create_batch(self):
        while True:
            self.date = time.strftime('%Y%m%d')
            if self.date != self.date_previous_batch:
                self.current_batch_number = 1
            else:
                self.current_batch_number += 1
            self.date_previous_batch = self.date
            batch_number_4d = str(self.current_batch_number).zfill(4)
            current_batch_name = self.date + '_' + batch_number_4d
            self.current_batch_path = self.batches_path + current_batch_name + '/'
            self.tracks_path = self.current_batch_path + 'tracks/'
            if not os.path.exists(self.current_batch_path):
                os.makedirs(self.current_batch_path)
                if not os.path.exists(self.tracks_path):
                    os.makedirs(self.tracks_path)
                self.current_batch_size = 0
                self.metadata.initialize(self.current_batch_path)
                self.open_batch_log()
                break

    def delivery_complete(self):
        filename = self.current_batch_path + 'delivery.complete'
        open(filename, 'w').close()

    def update_all_tracks(self, track):
        new_track = [track.artist, track.title, track.youtube_url]
        self.all_tracks.reverse()
        self.all_tracks.append(new_track)
        self.all_tracks.reverse()
        with open(settings.ALL_TRACKS, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.all_tracks)

    def update_files(self):
        new_posts = []
        with open(settings.NEW_POSTS, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                new_posts.append(row)
        with open(settings.LAST_POSTS, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(new_posts)
        os.remove(settings.NEW_POSTS)
        os.remove(settings.EMBED_URLS)
        os.remove(settings.DL_LIST)

    def make_batches(self):
        print('Obtaining batches...')
        for track in self.tracks:
            track_info = track.title + ' - ' + track.artist
            if track.youtube_url != '':
                print('Found Youtube URL for ' + track_info)
                self.yt_downloader.download(track.youtube_url, self.tracks_path, self.current_batch_log, track_info)

                # Write metadata and update only if there's no download error
                if self.yt_downloader.file_url[:2] != 'N/A':
                    self.metadata.add_track(track, self.yt_downloader.file_url)
                    self.metadata.add_to_sheet()

                    self.update_all_tracks(track)
                    self.current_batch_size += 1
            else:
                # Track with no youtube url
                self.global_log.warning('TRACK: ' + track_info + ' - ' +
                                        'ERROR: Missing Youtube URL.')

            if self.current_batch_size == self.n_tracks_per_batch \
                    or self.tracks.index(track) == len(self.tracks)-1:
                print('Batch completed.')
                self.delivery_complete()
                if self.tracks.index(track) != len(self.tracks) - 1:
                    self.create_batch()

        self.update_files()
