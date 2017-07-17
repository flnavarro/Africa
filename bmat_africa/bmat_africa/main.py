from spiders.djchoka_spider import DjChokaSpider
from scrapy.crawler import CrawlerProcess
from title_cleaner import TitleCleaner
from yt_search import YoutubeSearch
from batch_manager import BatchManager
import os
import settings
import argparse


class ChokaCrawler(object):

    def __init__(self, n_tracks_per_batch, batches_path):
        self.n_tracks_per_batch = n_tracks_per_batch
        self.batches_path = batches_path

    def get_batches(self):
        # Crawl Website / Get Posts
        process = CrawlerProcess({
            'USER_AGENT': settings.USER_AGENT
        })
        process.crawl(DjChokaSpider)
        process.start()

        # Clean Titles - Get Track Artist & Title
        title_cleaner = TitleCleaner()
        title_cleaner.clean()

        # Get Youtube Links
        yt_search = YoutubeSearch()
        yt_search.get_links()

        # Get Batches
        batch_manager = BatchManager(self.n_tracks_per_batch, self.batches_path)
        batch_manager.make_batches()


class InputParser(object):

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Download youtube audio tracks from DjChokaMusic.')
        self.batches_path = ''
        self.batch_size = 10

    def add_arguments(self):
        # Arguments to parse
        self.parser.add_argument('-batches_path', action='store', dest='batches_path', default='batches/',
                                 help='path for batches folder where the tracks will be downloaded')
        self.parser.add_argument('-batch_size', metavar='batch_size', type=int, default=10,
                                 help='number of tracks per batch')

    def parse_input(self):
        # Add arguments to parser
        self.add_arguments()

        # Parse arguments from input
        args = self.parser.parse_args()

        # Get Batches path and check if exists
        self.batches_path = args.batches_path
        if not self.batches_path == 'batches/':
            if not os.path.exists(self.batches_path):
                print('The path specified as batches_path does not exist.')
                if not os.path.exists('batches/'):
                    self.batches_path = 'batches/'
                    os.makedirs('batches/')
                    print('Batches folder created inside this script folder.')

        # Get batch size and check its value
        self.batch_size = args.batch_size
        if self.batch_size <= 0:
            print('Incorrect batch size. Setting batch size to a minimum of 10.')
            self.batch_size = 10

args_input = True

if args_input:
    # Get input from user and parse arguments
    input_parser = InputParser()
    input_parser.parse_input()
    # Get batch size
    batch_size = input_parser.batch_size
    # Get batches path
    batches_path = input_parser.batches_path
else:
    batch_size = 10
    # batches_path = 'batches/'
    batches_path = '/Volumes/HD2/Batches_AFR_3/'

choka_crawler = ChokaCrawler(batch_size, batches_path)
choka_crawler.get_batches()
