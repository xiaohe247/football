# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from items import RankingItem
from items import ResultItem
from spiders.qq import QqSpider

import csv
import codecs
import sys



class FtPipeline(object):

    def __init__(self):

        reload(sys)
        sys.setdefaultencoding('utf-8')

        self.ranking_filename = 'data/ranking.csv'
        self.result_filename = 'data/games.csv'
        if QqSpider.LEAGUES.has_key(QqSpider.CRAWL_LID):
            self.ranking_filename = 'data/' + QqSpider.LEAGUES[QqSpider.CRAWL_LID]['name'] + '_ranking.csv'
            self.result_filename = 'data/' + QqSpider.LEAGUES[QqSpider.CRAWL_LID]['name'] + '_games.csv'

        self.ranking_file = open(self.ranking_filename, 'w')
        self.ranking_write = csv.writer(self.ranking_file)
        self.ranking_write.writerow(['赛季','联赛','排名','球队','积分','场数','胜','平','负','进球','失球'])

        self.result_file = open(self.result_filename, 'w')
        self.result_write = csv.writer(self.result_file)
        self.result_write.writerow(['赛季','联赛','轮次','主队','客队','主队进球','客队进球','主队半场进球','客队半场进球'])

    def process_item(self, item, spider):
        if isinstance(item, RankingItem):
            ranking = []
            ranking.append(item['season'])
            ranking.append(item['league'])
            ranking.append(item['ranking'])
            ranking.append(item['name'])
            ranking.append(item['score'])
            ranking.append(item['game_num'])
            ranking.append(item['win'])
            ranking.append(item['draw'])
            ranking.append(item['lost'])
            ranking.append(item['goal'])
            ranking.append(item['fumble'])
            self.ranking_write.writerow(ranking)

        if isinstance(item, ResultItem):
            result = []
            result.append(item['season'])
            result.append(item['league'])
            result.append(item['round'])
            result.append(item['home_team'])
            result.append(item['guest_team'])
            result.append(item['home_goal'])
            result.append(item['guest_goal'])
            result.append(item['home_half_goal'])
            result.append(item['guest_half_goal'])
            self.result_write.writerow(result)

    def close_spider(self, spider):
        # 关闭爬虫时顺便将文件保存退出
        self.ranking_file.close()
        self.result_file.close()