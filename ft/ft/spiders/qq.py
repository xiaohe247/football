# -*- coding: utf-8 -*-
import scrapy
import re

from ..items import RankingItem
from ..items import ResultItem
from bs4 import BeautifulSoup

class QqSpider(scrapy.Spider):
    name = 'qq'
    allowed_domains = ['http://qq.gooooal.com']
    start_urls = ['http://http://qq.gooooal.com/']

    LEAGUES = {1: {'lid':1, 'name': 'yijia', 'start_season': 2015},
               2: {'lid':2, 'name': 'xijia', 'start_season': 2015},
               3: {'lid':3, 'name': 'dejia', 'start_season': 2015},
               4: {'lid':4, 'name': 'yingchao', 'start_season': 2015},
               5: {'lid':5, 'name': 'fajia', 'start_season': 2015},
               38: {'lid':38, 'name': 'meiguodalianmen', 'start_season': 2017},
               213: {'lid':213, 'name': 'zhongchao', 'start_season': 2018}}
    ROUNDS = 38
    LAST_SEASON = 2019

    CRAWL_LID = 38

    # leagues = { '意甲':1,'中超':213, '美国大联盟':38, '德甲':3, '英超': 4, '西甲': 2, '法甲':5}
    # lids = [1,2,3,4,5,38,213]
    # seasons = {1:2015, 2:2015,3:2015,4:2015,5:2015,38:2006,213:2010}
    # rounds = 38
    # last_season = 2019
    # league = 213

    # start
    def start_requests(self):
        leagues = []
        if self.LEAGUES.has_key(self.CRAWL_LID):
            leagues.append(self.LEAGUES[self.CRAWL_LID])
        else:
            leagues = self.LEAGUES.values()

        for league in leagues:
            start_season = league['start_season']
            lid = league['lid']
            # 遍历各个赛季
            for season in range(start_season, self.LAST_SEASON):
                ranking_url = "http://qq.gooooal.com/competition.do?lid=" + str(lid) + "&sid=" + str(season) + "&pid=112&lang=cn"
                yield scrapy.Request(ranking_url, self.parse_ranking, meta={"lid" : lid, "season" : season})

                # 遍历单个赛季中的轮次比赛
                for round in range(1, self.ROUNDS + 1):
                    reslut_url = "http://qq.gooooal.com/resultschedule.do?lid=" + str(lid) + "&sid=" + str(season) + "&roundNum=" + str(round) + "&lang=cn"
                    yield scrapy.Request(reslut_url, self.parse_result,
                                             meta={"lid": lid, "season": season, "round": round})


    # 赛季排行榜
    def parse_ranking(self, response):
        soup = BeautifulSoup(response.body, "lxml")
        show_div_0 = soup.find('div', id = 'show_div_0')
        rows = show_div_0.find_all('tr')
        for row in rows:
            td_list = row.find_all('td')
            if(len(td_list) > 0):
                item = RankingItem()
                item['season'] = response.meta['season']
                item['league'] = response.meta['lid']
                item['ranking'] = td_list[0].find('strong').text
                item['name'] = td_list[1].find('a').text
                item['score'] = td_list[2].text
                item['game_num'] = td_list[3].text
                item['win'] = td_list[4].text
                item['draw'] = td_list[5].text
                item['lost'] = td_list[6].text
                item['goal'] = td_list[7].text
                item['fumble'] = td_list[8].text
                yield item

    # 赛季轮数
    def parse_round(self, response):
        season = response.meta['season']
        lid = response.meta['lid']
        soup = BeautifulSoup(response.body, "lxml")
        s = soup.find("div", class_ = 'match_round').find("script").text
        index = s.find('parseInt') + len('parseInt') + 2
        rounds = s[index : index + 2]
        for round in range(1, int(rounds) + 1):
            reslut_url = "http://qq.gooooal.com/resultschedule.do?lid="+ str(lid) + "&sid=" + str(season) + "&roundNum=" + str(round) + "&lang=cn"
            yield scrapy.Request(reslut_url, self.parse_result, meta={"lid": lid, "season": season, "round": round})


    # 赛程
    def parse_result(self, response):
        soup = BeautifulSoup(response.body, "lxml")
        table = soup.find('table', 'dataSheet')
        for row in table.find_all('tr'):
            script_list = row.find_all("script")
            if len(script_list) > 0 :
                item = ResultItem()
                item['season'] = response.meta['season']
                item['league'] = response.meta['lid']
                item['round'] = response.meta['round']

                td_list = re.findall(r"document.write\('(.+?)'\);", script_list[1].text)
                item['home_team'] = BeautifulSoup(td_list[0], "lxml").find('a').text
                item['guest_team'] = BeautifulSoup(td_list[3], "lxml").find('a').text
                scores = BeautifulSoup(td_list[2], "lxml").text.split('-')
                item['home_goal'] = scores[0]
                item['guest_goal'] = scores[1]
                half_scores = BeautifulSoup(td_list[20], "lxml").text.split('-')
                item['home_half_goal'] = half_scores[0]
                item['guest_half_goal'] = half_scores[1]
                yield item