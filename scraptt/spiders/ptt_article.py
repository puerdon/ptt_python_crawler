"""Main crawler."""
import re
import os
import json
from datetime import datetime
from itertools import groupby

import scrapy
import dateutil.parser as dp

from .parsers.post import mod_content, extract_author, extract_ip
from .parsers.comment import parse_comments
from ..items import PostItem
from .ckipws import CKIP
from .json2tei import json2tei

class PttSpider(scrapy.Spider):
    """Crawler for PTT."""

    # 斷詞系統
    ckip = CKIP()
    
    name = 'ptt_article'
    allowed_domains = ['ptt.cc']
    handle_httpstatus_list = [404]
    custom_settings = {
        'ITEM_PIPELINES': {
           # 'scraptt.pipelines.HTMLFilePipeline': 500,
           # 'scraptt.pipelines.JsonExporterPipeline': 500
        },
    }

    def __init__(self, *args, **kwargs):
        """__init__ method.

        :param: boards: comma-separated board list
        
        :param: all: 撈該版所有的文章就對了

        :param: index_from: 如果你很清楚要第幾頁到第幾頁的
        :param: index_to:   就直接指定index的數字

        :param: since: 如果之前已經撈過前面的資料，那就撈某個時間點之後的，值為10位數的timestamp
        """
        self.boards = kwargs.pop('boards').split(',')
        self.all = kwargs.pop('all', None)
        self.index_from = kwargs.pop('index_from', None)
        self.index_to = kwargs.pop('index_to', None)
        self.since = kwargs.pop('since', None)
        self.data_dir = kwargs.pop('data_dir', None)
        self.log_file = kwargs.pop('log', None)

        self.logger.info(f"要爬的版: {self.boards}")
        if self.all is not None:
            self.logger.info(f"是否爬全部? 是")

        if self.index_from is not None and self.index_to is not None:
            self.logger.info(f"是否指定要爬的index? {self.index_from} - {self.index_to}")

        if self.since is not None:
            self.logger.info(f"是否指定要從什麼時候開始爬? {datetime.fromtimestamp(int(self.since))}")
        self.logger.info(f"資料存放位置: {self.data_dir}")
        self.logger.info(f"log檔位置: {self.log_file}")



    def start_requests(self):
        """Request handler."""

        # 有 all 的話 (爬該版的所有就對了)
        if self.all is not None:
            for board in self.boards:
                url = f'https://www.ptt.cc/bbs/{board}/index.html'
                yield scrapy.Request(
                    url,
                    cookies={'over18': '1'},
                    callback=self.parse_latest_index
                )
        
        # 有指定要爬的最早日期
        elif self.since is not None:
            board = self.boards[0]
            url = f'https://www.ptt.cc/bbs/{board}/index.html'

            yield scrapy.Request(
                url,
                cookies={'over18': '1'},
                callback=self.parse_index
            )

        # 
        elif self.index_from is not None and self.index_to is not None:
            board = self.boards[0]
            for i in range(int(self.index_from), int(self.index_to) + 1):
                url = f'https://www.ptt.cc/bbs/{board}/index{i}.html'
                yield scrapy.Request(
                    url,
                    cookies={'over18': '1'},
                    callback=self.parse_index
                )
        else:
            raise Error

    def parse_index(self, response):
        """Parse index pages."""
        # exclude "置底文"
        item_css = '.r-ent .title a'
        if response.url.endswith('index.html'):
            topics = response.dom('.r-list-sep').prev_all(item_css)
        else:
            topics = response.dom(item_css)

        if self.since is not None:
            # reverse order to conform to timeline
            for topic in reversed(list(topics.items())):
                title = topic.text()      # po文標題
                href = topic.attr('href') # po文連結
                timestamp = re.search(r'(\d{10})', href).group(1)
                # post_time = datetime.fromtimestamp(int(timestamp)) # po文日期

                if int(timestamp) < int(self.since):  # 如果po文時間比我們要的最早時間還要早
                    return
                
                self.logger.info(f'+ {title}, {href}, {datetime.fromtimestamp(int(timestamp))}')
                yield scrapy.Request(
                    href, cookies={'over18': '1'}, callback=self.parse_post
                )
            # 找出"上頁"按鈕的連結
            prev_url = response.dom('.btn.wide:contains("上頁")').attr('href')
            self.logger.info(f'index link: {prev_url}')
            if prev_url:

                yield scrapy.Request(
                    prev_url, cookies={'over18': '1'}, callback=self.parse_index
                )
        else: 
            for topic in list(topics.items()):

                title = topic.text()
                href = topic.attr('href')
                yield scrapy.Request(
                    href,
                    cookies={'over18': '1'},
                    callback=self.parse_post
                )

    def parse_latest_index(self, response):
        """Parse index pages."""
        # 找出"上頁"按鈕的連結
        prev_url = response.dom('.btn.wide:contains("上頁")').attr('href')
        self.logger.info(f'index link: {prev_url}')
        latest_index = re.search(r"index(\d{1,6})\.html", prev_url).group(1)
        self.logger.info(f'latest_index: {latest_index}')
        latest_index = int(latest_index)
        self.logger.info(f'response.url: {response.url}')
        board = re.search(r"www\.ptt\.cc\/bbs\/([\w\d\-_]{1,30})\/", response.url).group(1)
        print(f"board: {board}")
        print(f"latest index: {latest_index}")

        for index in range(1, latest_index + 1):
            url = f"https://www.ptt.cc/bbs/{board}/index{index}.html"
            self.logger.info(f"index link: {url}")

            yield scrapy.Request(
                url,
                cookies={'over18': '1'},
                callback=self.parse_index
            )


    def parse_post(self, response):
        """
        """
        board = re.search(r"www\.ptt\.cc\/bbs\/([\w\d\-_]{1,30})\/", response.url).group(1)
        con = response.body.decode(response.encoding)
        timestamp = re.search(r'(\d{10})', response.url).group(1)
        dt = datetime.fromtimestamp(int(timestamp))
        dt_str = dt.strftime("%Y%m%d_%H%M")
        article_id = response.url.split('/')[-1].split('.html')[0]

        # 先存一份html
        data_dir = self.data_dir

        try:
            os.makedirs(f"{data_dir}/{board}/{dt.year}", exist_ok=True)
            with open(f"{data_dir}/{board}/{dt.year}/{dt_str}_{article_id}.html", "wb") as f:
                f.write(response.body)
        except Exception as e:
            print(e)
            print(f"有問題的.html檔: {article_id}")


        # TBD:
        # 要先把已刪除/錯誤的文章給篩掉
        # 像是篩掉那些沒有 .main-content or .article-meta-tag
        html_pq_main_content = response.dom('#main-content')
        if len(html_pq_main_content) == 0:
            return None
        
        ###################
        # PARSE META DATA #
        ###################
        # po文的文章id, po文時間, po文所在的版
        post_id = article_id

        # po文的時間
        post_time = dt

        # 在哪個版
        post_board = board


        # 抓出meta: 作者/標題/時間
        meta = dict(
            (_.text(), _.next().text())
            for _
            in response.dom('.article-meta-tag').items()
        )

        ref = {
            '作者': 'author',
            '標題': 'title',
            '看板': 'board',
        }

        if '作者' in meta:
            post_author = extract_author(meta['作者'].strip())
        else:
            post_author = ""
        
        if '標題' in meta:
            post_title = meta['標題'].strip()
        else:
            post_title = ""
        

        
        ######################
        # PARSE MAIN CONTENT #
        ######################
        
        body = mod_content(
            html_pq_main_content
            .clone()
            .children()
            .remove('span[class^="article-meta-"]')
            .remove('div.push')
            .end()
            .html()
        )
        
        if body == '' or body is None:
            return None
        
        # 篩掉引述的部分
        try:
            qs = re.findall('※ 引述.*|\n: .*', body)
            for q in qs:
                body = body.replace(q, '')
            body = body.strip('\n ')
        except Exception as e:
            print(e)
            
        ###################
        # PARSE COMMENTS  #
        ###################
        comments = parse_comments(response.dom)
        
        post = {
            "post_board": post_board,
            "post_id": post_id,
            "post_time": timestamp,
            "post_title": post_title,
            "post_author": post_author,
            "post_body": body,
            # "meta": meta,
            "post_vote": comments["post_vote"],
            "comments": comments["comments"]
        }

        # article = {
        #     "board": board,
        #     "html_content": con,
        #     "timestamp": timestamp,
        #     "article_id": article_id
        # }

        ###################
        #  SAVE JSON.     #
        ###################
        try:   
            with open(f"{data_dir}/{board}/{dt.year}/_{dt_str}_{article_id}.json", "w") as f:
                json.dump(post, f, ensure_ascii=False)
        except Exception as e:
            print(e)
            print(f"錯誤訊息: {e}")
            error_class = e.__class__.__name__ #取得錯誤類型
            detail = e.args[0] #取得詳細內容
            cl, exc, tb = sys.exc_info() #取得Call Stack
            lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
            fileName = lastCallStack[0] #取得發生的檔案名稱
            lineNum = lastCallStack[1] #取得發生的行號
            funcName = lastCallStack[2] #取得發生的函數名稱
            errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
            print(errMsg)
            
        ###################
        # WS and save XML #
        ###################
        try:   
            tei = json2tei(post, PttSpider.ckip)
            with open(f"{data_dir}/{board}/{dt.year}/_{dt_str}_{article_id}.xml", "w") as f:
                f.write(tei)
        except Exception as e:
            print(e)
            
        
        
        yield PostItem(**post)
