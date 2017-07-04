from __future__ import unicode_literals
import youtube_dl
import os
from os.path import splitext
import logging


class MyLogger(object):
    def __init__(self, logger, track_info, path):
        # Log
        self.track_info = track_info
        self.logger = logger
        self.temp_file_path = path

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        # Print error into batch log
        self.logger.warning('TRACK: ' + self.track_info + ' - ' + msg)
        print(msg)
        # Types of error
        if 'copyright' in msg:
            error_type = 'error_1'
        elif 'Please sign in to view' in msg:
            error_type = 'error_2'
        elif 'URLError' in msg:
            error_type = 'error_3'
        elif 'account associated with this video has been terminated' in msg:
            error_type = 'error_4'
        else:
            error_type = 'error_5'
        # Creates a temporary error file to be read by downloader
        file_path = self.temp_file_path + error_type + '.temp'
        open(file_path, 'w').close()


class YoutubeDownloader(object):
    def __init__(self):
        self.file_url = ''
        self.error_type = ['error_1', 'error_2', 'error_3', 'error_4', 'error_5']
        self.error_meaning = ['N/A: Copyright (Blocked)', 'N/A: Sign in to view', 'N/A: URLError - ',
                              'N/A: Account terminated', 'N/A: Unknown Error']
        self.tracks_path = ''
        self.error_count = 0

    def my_hook(self, d):
        if d['status'] == 'finished':
            root, ext = splitext(d['filename'])
            self.file_url = root[root.find('tracks'):]
            print('Done downloading, now converting... ')

    def download(self, track_url, path, logger, track_info):
        self.tracks_path = path

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': MyLogger(logger, track_info, path),
            'progress_hooks': [self.my_hook],
            'ignoreerrors': True,
            'noplaylist': True,
            'forcetitle': True,
            'max_downloads': 1,
            'outtmpl': path + '%(title)s.%(ext)s',
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print('Downloading track... ')
                ydl.download([track_url])
        except youtube_dl.utils.DownloadError:
            print('Download Error')

        for error in self.error_type:
            if os.path.isfile(path + error + '.temp'):  # check if there is an error of this type
                index = self.error_type.index(error)  # if there is, store the error index
                if index is not 2:
                    self.file_url = self.error_meaning[index]  # write error into file_url
                else:
                    self.file_url = self.error_meaning[index] + track_url  # write error into file_url + link
                    # self.create_recover_download()  # create recover download file only if it's error 2
                os.remove(path + error + '.temp')  # remove temp error file
                self.error_count += 1
                break

    def create_recover_download(self):
        batch_path = self.tracks_path[:len(self.tracks_path)-len('tracks/')]
        if not os.path.isfile(batch_path + 'recover.download'):  # if the path doesn't exist
            file_path = batch_path + 'recover.download'  # create file
            open(file_path, 'w').close()

    @staticmethod
    def remove_recover_download(batch_path):
        # remove file
        file_path = batch_path + 'recover.download'
        os.remove(file_path)
