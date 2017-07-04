import scrapy
from scrapy.exceptions import CloseSpider
import unicodecsv as csv
import settings
import os


class DjChokaSpider(scrapy.Spider):
    name = "djchoka_spider"
    page = 1
    # Loads the actual page_limit in self.parse function
    page_limit = 100
    crawl_pages = True
    last_posts = []
    track_list = []
    embed_urls = []

    def start_requests(self):
        # Last posts data
        if not os.path.isfile(settings.LAST_POSTS):
            # Create new if it doesn't exist
            empty_list = zip([' '], [' '], [' '])
            with open(settings.LAST_POSTS, 'w') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerows(empty_list)
        # Load last posts data
        with open(settings.LAST_POSTS, 'rb') as f:
            print('Loading last execution data...')
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                self.last_posts.append(row)

        # Crawl pages until page limit
        while self.crawl_pages:
            url = settings.ROOT_URL + 'page/%s/' % str(self.page)
            if self.page < self.page_limit + 1:
                yield scrapy.Request(url=url, callback=self.parse, errback=self.parse_error)
            else:
                self.crawl_pages = False

        # Crawl posts for each track
        for track in self.track_list:
            url = track[2]
            yield scrapy.Request(url=url, callback=self.get_track_link, errback=self.parse_error)

        # Save and close spider
        self.save_and_close_spider()

    def parse(self, response):
        print('Crawling page ' + str(self.page) + ' ...')
        # Get page limit from first page request
        if self.page == 1:
            self.page_limit = int(response.css('span.pages::text').extract_first().split(' of ')[1])
        # Get all posts titles, dates and links from this page
        page_tracks = response.css('li.first_news').css('h4.pp-title-blog').css('a::text').extract()
        page_dates = response.css('li.first_news').css('a.date::text').extract()
        page_links = response.css('li.first_news').css('h4.pp-title-blog').xpath('a/@href').extract()
        page_tracks = zip(page_tracks, page_dates, page_links)
        for page_track in page_tracks:
            if page_track[0] == self.last_posts[0][0] and \
                            page_track[1] == self.last_posts[0][1] and \
                            page_track[2] == self.last_posts[0][2]:
                # If track is the first in last posts data,
                # is the last downloaded track,
                # so don't save track and finish crawling pages
                self.crawl_pages = False
                break
            else:
                # Otherwise save track in track_list
                self.track_list.append(page_track)
        self.page += 1

    def get_track_link(self, response):
        # Get youtube embed url from track post
        embed_url = response.css('div.inner_post').css('iframe').xpath('@src').extract_first()
        if embed_url is not None:
            if 'youtube' in embed_url:
                embed_url = embed_url[:24] + 'watch?v=' + embed_url[30:]
            else:
                embed_url = ''
        else:
            embed_url = ''
            # if 'my.notjustok.com' in download_url:
            #     download_url = download_url[:31] + 'download' + download_url[36:]
            # elif 'youtube.com' in download_url:
            #     download_url = download_url[:24] + 'watch?v=' + download_url[30:]
            # elif 'audiomack' in download_url:
            #     download_url = download_url[:26] + 'song' + download_url[38:]
            # elif 'hulkshare' in download_url:
            #     download_url = download_url[:25] + 'dl/' + download_url[38:]

        # Get track index in track_list
        links = [i[2] for i in self.track_list]
        index = links.index(response.url)
        # Add url and its track index
        self.embed_urls.append([embed_url, index])
        # Save embed urls
        with open(settings.EMBED_URLS, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.embed_urls)

    def parse_error(self, response):
        print('Unknown spider error!')

    def save_and_close_spider(self):
        print('Saving crawling data...')
        with open(settings.NEW_POSTS, 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(self.track_list)
        raise CloseSpider('Spider process completed!')
