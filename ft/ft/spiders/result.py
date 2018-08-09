# -*- coding: utf-8 -*-
import scrapy
import re

from ..items import ResultItem
from bs4 import BeautifulSoup

class QqSpider(scrapy.Spider):
    name = 'result'
    allowed_domains = ['http://qq.gooooal.com']
    start_urls = ['http://http://qq.gooooal.com/']
    lids = [38]
    seasons = {38:2006,4:2015}
    last_season = 2007

    # start
    def start_requests(self):
        for lid in self.lids:
            start_season = self.seasons[lid]
            for season in range(start_season, self.last_season):

                #for round in range(1, 20):
                    #reslut_url = "http://qq.gooooal.com/resultschedule.do?lid=" + str(lid) + "&sid=" + str(
                    #    season) + "&roundNum=" + str(round) + "&lang=cn"
                    #yield scrapy.Request(reslut_url, callback=self.parse_result,
                    #                     meta={"lid": lid, "season": season, "round": round})

                reslut_url = "http://qq.gooooal.com/resultschedule.do?lid=" + str(lid) + "&sid=" + str(season) + "&pid=112&lang=cn"
                yield scrapy.Request(reslut_url, self.parse_round, meta={"lid" : lid, "season" : season})


    #赛季轮数
    def parse_round(self, response):
        season = response.meta['season']
        lid = response.meta['lid']
        soup = BeautifulSoup(response.body, "lxml")
        s = soup.find("div", class_ = 'match_round').find("script").text
        index = s.find('parseInt') + len('parseInt') + 2
        rounds = s[index : index + 2]
        for round in range(1, int(rounds) + 1):
            reslut_url = "http://qq.gooooal.com/resultschedule.do?lid="+ str(lid) + "&sid=" + str(season) + "&roundNum=" + str(round) + "&lang=cn"
            yield scrapy.Request(reslut_url, callback = self.parse_result, meta={"lid": lid, "season": season, "round": round})


    # 赛程
    def parse_result(self, response):
        soup = BeautifulSoup(response.body, "lxml")
        table = soup.find('table', 'dataSheet')
        for row in table.find_all('tr', class_ = "alt"):
            item = ResultItem()
            item['season'] = response.meta['season']
            item['league'] = response.meta['lid']
            item['round'] = response.meta['round']
            script_list = row.find_all("script")
            if len(script_list) > 0 :
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