from spiders.djchoka_spider import DjChokaSpider
from scrapy.crawler import CrawlerProcess
from title_cleaner import TitleCleaner
from yt_search import YoutubeSearch
from batch_manager import BatchManager
import os
import settings
import unicodecsv as csv


# Check Files
if not os.path.isfile(settings.CHECK_FILE):
    empty_list = zip([' '], [' '], [' '])
    with open(settings.CHECK_FILE, 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(empty_list)

# # Crawl Website / Get Tracks and Links
# process = CrawlerProcess({
#     'USER_AGENT': settings.USER_AGENT
# })
# process.crawl(DjChokaSpider)
# process.start()

# Clean Titles
# title_cleaner = TitleCleaner()
# title_cleaner.clean()
#
# # Get Youtube Links
# yt_search = YoutubeSearch()
# yt_search.get_links()

# Batch Manager
n_tracks_per_batch = 10
batch_manager = BatchManager(n_tracks_per_batch)
batch_manager.make_batches()

# Metadata
# De momento imposible

# LOGS & ERRORS

print('Done!')

