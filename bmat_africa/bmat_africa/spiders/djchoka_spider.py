import scrapy
from scrapy.exceptions import CloseSpider
import unicodecsv as csv
import settings
from operator import itemgetter


class DjChokaSpider(scrapy.Spider):
    name = "djchoka_spider"
    page = 1
    # page_limit = 169
    page_limit = 2
    song_list = []
    check_list = []
    check_file = settings.CHECK_FILE
    exec_file = settings.EXEC_FILE
    main_page = True
    download_url = ''
    download_urls = []
    count_tracks = 0

    def start_requests(self):
        with open(self.check_file, 'rb') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.check_list.append(row)

        root_url = settings.ROOT_URL
        while self.main_page:
            url = root_url + 'page/%s/' % str(self.page)
            if self.page < self.page_limit + 1:
                yield scrapy.Request(url=url, callback=self.parse, errback=self.parse_error)
            else:
                self.main_page = False

        for song in self.song_list:
            url = song[2]
            yield scrapy.Request(url=url, callback=self.get_download_link, errback=self.parse_error)

    def parse(self, response):
        # In first page -> Get LAST PAGE number
        # if self.page == 1:
        #     self.page_limit = int(response.css('span.pages::text').extract_first().split(' of ')[1])
        page_songs = response.css('li.first_news').css('h4.pp-title-blog').css('a::text').extract()
        page_dates = response.css('li.first_news').css('a.date::text').extract()
        page_links = response.css('li.first_news').css('h4.pp-title-blog').xpath('a/@href').extract()
        page_songs = zip(page_songs, page_dates, page_links)
        for page_song in page_songs:
            if page_song[0] == self.check_list[0][0] and \
                            page_song[1] == self.check_list[0][1] and \
                            page_song[2] == self.check_list[0][2]:
                self.main_page = False
                break
            else:
                self.song_list.append(page_song)
        self.page += 1

    def get_download_link(self, response):
        print('url -> ' + response.url)
        download_url = response.css('div.inner_post').css('iframe').xpath('@src').extract_first()
        if download_url is not None:
            print('download url -> ' + download_url)

            if 'my.notjustok.com' in download_url:
                download_url = download_url[:31] + 'download' + download_url[36:]
            elif 'youtube.com' in download_url:
                download_url = download_url[:24] + 'watch?v=' + download_url[30:]
            elif 'audiomack' in download_url:
                download_url = download_url[:26] + 'song' + download_url[38:]
            elif 'hulkshare' in download_url:
                download_url = download_url[:25] + 'dl/' + download_url[38:]

            if download_url is not None:
                print('download url -> ' + download_url)
            else:
                print('DOWNLOAD URL IS NONE')

        if download_url is None:
            download_url = 'None'

        links = [i[2] for i in self.song_list]
        index = links.index(response.url)
        self.download_urls.append([download_url, index])
        self.count_tracks += 1
        if self.count_tracks == len(self.song_list):
            self.save_and_close_spider()

    def parse_error(self, response):
        print('PARSE ERROR!')

    def save_and_close_spider(self):
        songs = [i[0] for i in self.song_list]
        dates = [i[1] for i in self.song_list]
        links = [i[2] for i in self.song_list]
        sorted(self.download_urls, key=itemgetter(1))
        self.download_urls = [i[0] for i in self.download_urls]
        self.song_list = zip(songs, dates, links, self.download_urls)
        self.check_list = self.song_list + self.check_list
        with open(self.check_file, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.check_list)
        with open(self.exec_file, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.song_list)
        raise CloseSpider('page limit exceeded!')
