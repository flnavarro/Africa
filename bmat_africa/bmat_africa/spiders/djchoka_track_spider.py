import scrapy
from scrapy.exceptions import CloseSpider
import unicodecsv as csv
import settings


class DjChokaTrackSpider(scrapy.Spider):
    name = "djchoka_track_spider"
    exec_file = settings.EXEC_FILE
    song_list = []

    def start_requests(self):
        with open(self.exec_file, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.song_list.append(row)

        for song in self.song_list:
            url = song[3]
            yield scrapy.Request(url=url, callback=self.parse, errback=self.parse_error)

    def parse(self, response):
        pass

    def parse_error(self, response):
        pass

    def save_and_close_spider(self):
        pass
