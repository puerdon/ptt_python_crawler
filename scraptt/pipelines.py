"""Scrapy pipeilnes."""
from hashlib import sha256
import logging
import os
import urllib
from datetime import datetime
import json
logger = logging.getLogger(__name__)

# from scrapy.exporters import JsonLinesItemExporter
from scrapy.exporters import JsonItemExporter

# class CustomJsonLinesItemExporter(JsonLinesItemExporter):
#     def __init__(self, file, **kwargs):
#         # 將超類的ensure_ascii屬性設置為False， 確保輸出中文而不是其unicode編碼
#         super(CustomJsonLinesItemExporter, self).__init__(file, ensure_ascii=False, **kwargs)

# class HTMLFilePipeline:
#     def process_item(self, item, spider):
#         board = item['post_board']
#         article_id = item['post_id']
#         dt = item['post_time']
#         dt_str = dt.strftime("%Y%m%d_%H%M")

#         # 要存放檔案的位置:
#         # 由command line的參數決定: -a data_dir=...
#         data_dir = spider.data_dir

#         try:
#             logger.info(f"{board}-{dt}-{article_id}")
#             os.makedirs(f"{data_dir}/{board}/{dt.year}", exist_ok=True)
#             with open(f"{data_dir}/{board}/{dt.year}/{dt_str}_{article_id}.html", "w") as f:
#                 item['post_time'] = int(datetime.timestamp(item['post_time']))
#                 f.write(json.dumps(dict(item), ensure_ascii=False))
#         except Exception as e:
#             print(e)
#             print(f"有問題的文章: {article_id}")

#         return item

class JsonExporterPipeline(object):
    # 调用Scrapy提供的JsonExporter导出Json文件。

    def process_item(self, item, spider):
        board = item['post_board']
        article_id = item['post_id']
        dt = item['post_time']
        dt_str = dt.strftime("%Y%m%d_%H%M")

        # 要存放檔案的位置:
        # 由command line的參數決定: -a data_dir=...
        data_dir = spider.data_dir

        try:
            logger.info(f"{board}-{dt}-{article_id}")
            os.makedirs(f"{data_dir}/{board}/{dt.year}", exist_ok=True)
            with open(f"{data_dir}/{board}/{dt.year}/{dt_str}_{article_id}.json", "w") as f:
                item['post_time'] = int(datetime.timestamp(item['post_time']))
                f.write(json.dumps(dict(item), ensure_ascii=False))
        except Exception as e:
            print(e)
            print(f"有問題的文章: {article_id}")

        return item
