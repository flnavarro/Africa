import scrapy
from scrapy.exceptions import CloseSpider
import unicodecsv as csv

class DjChokaSpider(scrapy.Spider):
    name = "djchoka_spider"
    page = 1
    song_list = []
    #
    # LOAD check_file
    #
    check_file = 'check_file_2.csv'

    def start_requests(self):
        root_url = 'http://djchokamusic.com/category/music/'
        while True:
            url = root_url + 'page/%s/' % str(self.page)
            yield scrapy.Request(url=url, callback=self.parse, errback=self.parse_error)

    def parse(self, response):
        page_songs = response.css('li.first_news').css('h4.pp-title-blog').css('a::text').extract()
        page_dates = response.css('li.first_news').css('a.date::text').extract()
        page_songs = zip(page_songs, page_dates)
        for page_song in page_songs:
            self.song_list.append(page_song)
        #
        # MAYBE JUST CONTROL DATE
        # IF song_list & date_list are already in check_file
        #   check following tracks
        #       IF following N tracks are also the same
        #           Delete repeated tracks from song_list
        #           RAISE CloseSpider
        # ELSE continue
        #
        self.page += 1

    def parse_error(self, response):
        #
        # SAVE tracks from song_list into CHECK_FILE
        # SAVE tracks from song_list into EXECUTION_FILE
        #
        with open(self.check_file, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.song_list)
        raise CloseSpider('page limit exceeded!')