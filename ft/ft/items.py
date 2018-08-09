# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RankingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    season = scrapy.Field()
    league = scrapy.Field()
    ranking = scrapy.Field()
    name = scrapy.Field()
    score = scrapy.Field()
    game_num = scrapy.Field()
    win = scrapy.Field()
    draw = scrapy.Field()
    lost = scrapy.Field()
    goal = scrapy.Field()
    fumble = scrapy.Field()


class ResultItem(scrapy.Item):
    season = scrapy.Field()
    league = scrapy.Field()
    round = scrapy.Field()
    home_team = scrapy.Field()
    guest_team = scrapy.Field()
    home_goal = scrapy.Field()
    home_half_goal = scrapy.Field()
    guest_goal = scrapy.Field()
    guest_half_goal = scrapy.Field()
