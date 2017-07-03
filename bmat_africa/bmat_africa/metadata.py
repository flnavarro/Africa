import xlwt, xlrd
from xlutils.copy import copy
import os
import discogs_client
from difflib import SequenceMatcher
import string
import requests


class Track(object):
    def __init__(self, artist, title, url):
        self.artist = artist.title()
        self.title = title.title()
        self.youtube_url = url


class TrackMetadata(object):
    def __init__(self):
        self.url = ''
        self.title = ''
        self.artist = ''
        self.album = ''
        self.album_artist = ''
        self.album_upc = ''
        self.label = ''
        self.isrc = ''
        self.language = ''
        self.genres = []
        self.country_producer = ''
        self.release_year = ''
        self.version = ''
        self.composers = []
        self.iswc = ''
        self.publishers = []
        self.performers = []
        self.track_id = ''
        self.work_id = ''


class ManageMetadata(object):
    def __init__(self, get_from_discogs=False):
        self.batch_path = ''
        self.batch_metadata = []
        self.metadata_file_path = ''
        self.metadata_xls = None
        self.sheet = None
        self.row = 1
        self.sheet_to_read = None
        self.metadata = TrackMetadata()
        # Discogs API
        if get_from_discogs:
            self.discogs = discogs_client.Client('YoutubeBatches/1.0', user_token="MPtcrSCmtLPRRnrOcGmjhmRGHoaVZRlsanLSLzcO")
            self.discogs_metadata = True
        else:
            self.discogs_metadata = False
        self.generate_recover = False

    @staticmethod
    def find_name(title_in_xml, track_list):
        sim_ratio = []
        # Find the most similar name to the original title in the xml in album's track list
        for track in track_list:
            sim_ratio.append(SequenceMatcher(None, title_in_xml.lower(), track['title'].lower()).ratio())
        return sim_ratio.index(max(sim_ratio))

    @staticmethod
    def find_upc(barcode_ids):
        album_upc = []
        # Find Album UPC numbers among the 'Barcode and Other Identifiers' from Discogs API
        for barcode_id in barcode_ids:
            n_digits = sum(c.isdigit() for c in barcode_id)
            if n_digits == 12 or n_digits == 13:
                album_upc.append(barcode_id)
        return album_upc

    def initialize(self, batch_path):
        self.batch_path = batch_path
        self.metadata_file_path = self.batch_path + 'metadata.xls'

        self.batch_metadata = []
        self.generate_recover = False

        print('Metadata file initialized for this batch.')
        if not os.path.isfile(self.metadata_file_path):
            # open workbook and add sheet
            self.metadata_xls = xlwt.Workbook()
            self.sheet = self.metadata_xls.add_sheet('Batch Metadata')

            # headers
            self.sheet.write(0, 0, 'URL')
            self.sheet.write(0, 1, 'track title')
            self.sheet.write(0, 2, 'track artist')
            self.sheet.write(0, 3, 'album title')
            self.sheet.write(0, 4, 'album artist')
            self.sheet.write(0, 5, 'album upc')
            self.sheet.write(0, 6, 'label')
            self.sheet.write(0, 7, 'ISRC')
            self.sheet.write(0, 8, 'language')
            self.sheet.write(0, 9, 'genre(s)')
            self.sheet.write(0, 10, 'country producer')
            self.sheet.write(0, 11, 'release year')
            self.sheet.write(0, 12, 'version')
            self.sheet.write(0, 13, 'composer(s)')
            self.sheet.write(0, 14, 'ISWC')
            self.sheet.write(0, 15, 'publisher(s)')
            self.sheet.write(0, 16, 'performer(s)')
            self.sheet.write(0, 17, 'track internal ID')
            self.sheet.write(0, 18, 'work internal ID')
            self.row = 1
        else:
            xls = xlrd.open_workbook(self.metadata_file_path, formatting_info=True)
            self.row = xls.sheet_by_index(0).nrows
            self.sheet_to_read = xls.sheet_by_index(0)  # to read before downloading metadata
            self.metadata_xls = copy(xls)
            self.sheet = self.metadata_xls.get_sheet(0)

    def add_track(self, track, file_url):
        self.metadata = TrackMetadata()
        self.metadata.url = file_url.encode('utf-8')

        # If it doesn't have a download error adds .mp3 to the end of url
        if 'N/A:' not in self.metadata.url:
            self.metadata.url += '.mp3'

        if self.discogs_metadata:
            try:
                # Discogs query
                results = self.discogs.search(artist=track.artist, track=track.title, type='release')
            except (discogs_client.exceptions.HTTPError, requests.exceptions.ConnectionError, ValueError):
                # Discogs error
                print('Discogs API error. Download will continue and recover.metadata will be generated.')
                results = None
                self.generate_recover = True

            try:
                if results is not None and len(results) > 0:
                    # Get metadata from Discogs API
                    found_in_discogs = True
                    data = results[0].data
                    self.metadata.artist = results[0].artists[0].name.encode('utf-8')
                    id_in_tracklist = self.find_name(track.title, data['tracklist'])
                    self.metadata.title = data['tracklist'][id_in_tracklist]['title'].encode('utf-8')
                    self.metadata.album = data['title'].encode('utf-8')
                    self.metadata.album_artist = [artist['name'].encode('utf-8') for artist in data['artists']]
                    self.metadata.album_upc = self.find_upc([barcode.encode('utf-8') for barcode in data['barcode']])
                    self.metadata.label = data['label'][0].encode('utf-8')
                    [self.metadata.genres.append(genre.encode('utf-8')) for genre in data['genre']]
                    [self.metadata.genres.append(style.encode('utf-8')) for style in data['style']]
                    self.metadata.country_producer = data['country']
                    self.metadata.release_year = data['year']
                    self.metadata.version = [format.encode('utf-8') for format in data['format']]
                    self.metadata.publishers = [company['name'].encode('utf-8') for company in data['companies']]
                    self.metadata.performers = [extra_artist['name'].encode('utf-8') for extra_artist in
                                           data['extraartists']]
                    self.metadata.work_id = data['id']  # Discogs release id
                    # Not available:
                    # metadata.isrc
                    # metadata.language
                    # metadata.composers
                    # metadata.iswc
                    # metadata.track_id
                else:
                    found_in_discogs = False

            except requests.exceptions.ConnectionError:
                print('Discogs API error. Download will continue and recover.metadata will be generated.')
                found_in_discogs = False
                self.generate_recover = True
        else:
            found_in_discogs = False

        if not found_in_discogs:
            # If it's not found in discogs then write metadata from xml
            if track.title is not None:
                track.title = string.capwords(track.title)
                self.metadata.title = track.title.encode('utf-8')
            if track.artist is not None:
                track.artist = string.capwords(track.artist)
                self.metadata.artist = track.artist.encode('utf-8')
            if self.generate_recover:
                self.metadata.track_id = 'recover.metadata'  # mark tracks where metadata needs to be recovered
                self.create_recover_metadata()

    def add_to_sheet(self):
        # Adds a single row of information to the metadata file and saves it
        self.sheet.write(self.row, 0, self.metadata.url.decode('utf-8'))
        self.sheet.write(self.row, 1, self.metadata.title.decode('utf-8'))
        self.sheet.write(self.row, 2, self.metadata.artist.decode('utf-8'))
        self.sheet.write(self.row, 3, self.metadata.album.decode('utf-8'))  # album title
        self.sheet.write(self.row, 4,
                         ", ".join([str(item).decode('utf-8') for item in self.metadata.album_artist]))  # album artist
        self.sheet.write(self.row, 5,
                         ", ".join([str(item).decode('utf-8') for item in self.metadata.album_upc]))  # album upc
        self.sheet.write(self.row, 6, self.metadata.label.decode('utf-8'))  # label
        self.sheet.write(self.row, 7, self.metadata.isrc)  # isrc
        self.sheet.write(self.row, 8, self.metadata.language)  # language
        self.sheet.write(self.row, 9,
                         ", ".join([str(item).decode('utf-8') for item in self.metadata.genres]))  # genre(s)
        self.sheet.write(self.row, 10, self.metadata.country_producer)  # country producer
        self.sheet.write(self.row, 11, self.metadata.release_year)  # release year
        self.sheet.write(self.row, 12,
                         ", ".join([str(item).decode('utf-8') for item in self.metadata.version]))  # version
        self.sheet.write(self.row, 13, self.metadata.composers)  # composer(s)
        self.sheet.write(self.row, 14, self.metadata.iswc)  # iswc
        self.sheet.write(self.row, 15,
                         ", ".join([str(item).decode('utf-8') for item in self.metadata.publishers]))  # publisher(s)
        self.sheet.write(self.row, 16, ", ".join([str(item).decode('utf-8') for item in self.metadata.performers]))
        self.sheet.write(self.row, 17, self.metadata.track_id)  # track internal id
        self.sheet.write(self.row, 18, self.metadata.work_id)  # work internal id

        # Write metadata
        print('Saving metadata for this track... ')
        self.row += 1
        self.metadata_xls.save(self.metadata_file_path)
        print('Metadata saved.')

    def create_recover_metadata(self):
        if not os.path.isfile(self.batch_path + 'recover.metadata'):  # if the path doesn't exist
            file_path = self.batch_path + 'recover.metadata'
            open(file_path, 'w').close()  # creates recover file

    def recover(self):
        for row in range(1, self.sheet_to_read.nrows):
            # If we have metadata to recover
            if self.sheet_to_read.cell(row, 17).value == 'recover.metadata':  # value at 'track_id' (17)
                # Write basic info and create a track
                file_url = self.sheet_to_read.cell(row, 0).value
                title = self.sheet_to_read.cell(row, 1).value
                artist = self.sheet_to_read.cell(row, 2).value
                track = Track(artist, title, None)
                # Find metadata in Discogs API
                self.add_track(track, file_url)
                # Get the row where the track is
                self.row = row
                # Save the new information to the metadata file
                self.add_to_sheet()

        # If there is not a metadata API error
        if not self.generate_recover:
            # remove recover file
            file_path = self.batch_path + 'recover.metadata'
            os.remove(file_path)

    def recover_urls(self):
        sheet_row = []
        url_to_dl = []
        track_info = []
        for row in range(1, self.sheet_to_read.nrows):
            # If there is a URLError download error in metadata file
            if 'N/A: URLError' in self.sheet_to_read.cell(row, 0).value:
                # Get the row where the track with error is
                sheet_row.append(row)
                # Get the youtube url which is present in the error info
                url = self.sheet_to_read.cell(row, 0).value
                url = url[len('N/A: URLError - '):]
                url_to_dl.append(url)
                # Get basic info
                title = self.sheet_to_read.cell(row, 1).value
                artist = self.sheet_to_read.cell(row, 2).value
                info = title + ' from artist ' + artist
                track_info.append(info)
        return url_to_dl, track_info, sheet_row

    def write_track_url(self, row, track_url):
        # This is used when recovering a download
        if 'N/A:' not in track_url:
            # If the download didn't give an error then write '.mp3'
            track_url += '.mp3'
        # Write track url in metadata file and save it
        self.sheet.write(row, 0, track_url)
        self.metadata_xls.save(self.metadata_file_path)