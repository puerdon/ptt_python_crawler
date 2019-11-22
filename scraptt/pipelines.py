"""Scrapy pipeilnes."""
from hashlib import sha256
import logging
import os
import urllib
from scraptt import settings
from datetime import datetime
logger = logging.getLogger(__name__)

from scrapy.exporters import JsonLinesItemExporter

class CustomJsonLinesItemExporter(JsonLinesItemExporter):
    def __init__(self, file, **kwargs):
        # 將超類的ensure_ascii屬性設置為False， 確保輸出中文而不是其unicode編碼
        super(CustomJsonLinesItemExporter, self).__init__(file, ensure_ascii=False, **kwargs)

class HTMLFilePipeline:
    def process_item(self, item, spider):
        board = item['board']
        article_id = item['article_id']
        timestamp = item['timestamp']
        dt = datetime.fromtimestamp(int(timestamp))
        dt_str = dt.strftime("%Y%m%d_%H%M")

        data_dir = settings.DATA_DIR

        try:
            logger.info(f"{board}-{dt}-{article_id}")
            os.makedirs(f"{data_dir}/{board}/{dt.year}", exist_ok=True)
            with open(f"data/{board}/{dt.year}/{dt_str}_{article_id}.html", "w+") as f:
                f.write(item['html_content'])
        except Exception as e:
            print(e)
            print(f"有問題的文章: {article_id}")

        return item
