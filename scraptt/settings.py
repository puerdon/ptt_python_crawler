# -*- coding: utf-8 -*-
"""Scrapy settings for scraptt project."""

BOT_NAME = 'scraptt'
SPIDER_MODULES = ['scraptt.spiders']
NEWSPIDER_MODULE = 'scraptt.spiders'
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 0.4
COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = True
# cookies
COOKIES_ENABLED = True
COOKIES_DEBUG = False
# logging
LOG_LEVEL = 'INFO'
# LOG_FILE = '/var/log/scraptt.log'
LOG_FILE = './scraptt.log'


# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#     'scraptt.middlewares.ScrapttSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scraptt.middlewares.PyqueryMiddleware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
}


RETRY_ENABLED = True
RETRY_HTTP_CODES = [500, 502, 503, 504, 520, 521, 522, 524, 525 , 408, 429]
RETRY_TIMES = 5

