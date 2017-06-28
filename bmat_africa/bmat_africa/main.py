from spiders.djchoka_spider import DjChokaSpider
from scrapy.crawler import CrawlerProcess

quotes_spider = DjChokaSpider()
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(DjChokaSpider)
process.start()
process.stop()

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

