import scrapy
from scrapy.exceptions import CloseSpider
import unicodecsv as csv
import settings


class DjChokaSpider(scrapy.Spider):
    name = "djchoka_spider"
    page = 1
    page_limit_debug = 200
    song_list = []
    check_list = []
    check_file = settings.CHECK_FILE
    exec_file = settings.EXEC_FILE

    def start_requests(self):
        with open(self.check_file, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.check_list.append(row)

        root_url = settings.ROOT_URL
        while True:
            url = root_url + 'page/%s/' % str(self.page)
            if self.page != self.page_limit_debug:
                yield scrapy.Request(url=url, callback=self.parse, errback=self.parse_error)
            else:
                self.save_and_close_spider()

    def parse(self, response):
        page_songs = response.css('li.first_news').css('h4.pp-title-blog').css('a::text').extract()
        page_dates = response.css('li.first_news').css('a.date::text').extract()
        page_songs = zip(page_songs, page_dates)
        for page_song in page_songs:
            if page_song[0] == self.check_list[0][0] and page_song[1] == self.check_list[0][1]:
                self.save_and_close_spider()
                pass
            else:
                self.song_list.append(page_song)
        self.page += 1

    def parse_error(self, response):
        self.save_and_close_spider()

    def save_and_close_spider(self):
        self.check_list = self.song_list + self.check_list
        with open(self.check_file, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.check_list)
        with open(self.exec_file, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.song_list)
        raise CloseSpider('page limit exceeded!')
