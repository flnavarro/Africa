from spiders.djchoka_spider import DjChokaSpider
from spiders.djchoka_track_spider import DjChokaTrackSpider
from scrapy.crawler import CrawlerProcess
from title_cleaner import TitleCleaner
import os
import settings
import unicodecsv as csv

# Check Files
if not os.path.isfile(settings.CHECK_FILE):
    empty_list = zip([' '], [' '], [' '])
    with open(settings.CHECK_FILE, 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(empty_list)

# Crawl Website / Get Tracks and Links
process = CrawlerProcess({
    'USER_AGENT': settings.USER_AGENT
})
process.crawl(DjChokaSpider)
process.start()

# Clean Titles
title_cleaner = TitleCleaner()
title_cleaner.clean()

# Batches
# Dejar para el final

# Metadata
# De momento imposible

# Crawl Song Link
#   Check Download Type
#       Youtube // Wasafi // notjustok
#       TRY Download
#   IF NOT WORK
#       TRY search in youtube

# LOGS & ERRORS

print('Done!')

