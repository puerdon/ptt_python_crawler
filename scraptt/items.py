# -*- coding: utf-8 -*-
"""Scrapy scraped items."""
import scrapy


class PostItem(scrapy.Item):
    """Item for "POST"."""


    post_board = scrapy.Field()
    post_id = scrapy.Field()
    post_time = scrapy.Field()
    post_title = scrapy.Field()
    post_author = scrapy.Field()
    post_body = scrapy.Field()
    post_vote = scrapy.Field()
    comments = scrapy.Field()


class MetaItem(scrapy.Item):
    """Item for "META"."""

    name = scrapy.Field()

class _ArticleItem(scrapy.Item):
    """Item for "META"."""
    board = scrapy.Field()
    html_content = scrapy.Field()
    timestamp = scrapy.Field()
    article_id = scrapy.Field()