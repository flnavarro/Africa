from spiders.djchoka_spider import DjChokaSpider
from scrapy.crawler import CrawlerProcess
from title_cleaner import TitleCleaner
import os
import settings
import unicodecsv as csv

# Check Files
if not os.path.isfile(settings.CHECK_FILE):
    empty_list = zip([' '], [' '])
    with open(settings.CHECK_FILE, 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(empty_list)

# Crawl Website
quotes_spider = DjChokaSpider()
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(DjChokaSpider)
process.start()
process.stop()

# Clean Titles
title_cleaner = TitleCleaner()
title_cleaner.clean()

# EXECUTION FILE
# will contain all the songs to take into account
# CLEAN THE TITLES
# SAVE SONG LIST -> EXECUTION FILE
# MAKE BATCHES
# SEARCH FOR METADATA
# SAVE SONG LIST -> BATCH METADATA LIST
# SEARCH FOR YOUTUBE LINK
# SAVE SONG LIST -> -> BATCH METADATA LIST
# DOWNLOAD TRACK INTO BATCH
# LOGS & ERRORS

print('Done!')

