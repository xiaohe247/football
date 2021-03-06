# -*- coding: UTF-8 -*-

from league.league import League

import csv
import sys


reload(sys)
sys.setdefaultencoding('utf-8')

fajia = League(5, 'fajia', 'input/fajia_games.csv', 'input/fajia_ranking.csv')
fajia.parse()
season_2017 = fajia.get_season(2017)
season_2017.parse_games()
season_2018 = fajia.get_season(2018)
season_2018.parse_games()
games = season_2018.get_unfinished_games('1')

forcast_file = open('output/fajia_cai.csv', 'w')
forcast_write = csv.writer(forcast_file)
forcast_write.writerow(['轮次','主队','客队','主排名','客排名','主球','客球','胜负'])

for game in games:
    for a in season_2017.forecast(game):
        forcast_write.writerow(a.to_row())
    forcast_write.writerow([])

forcast_file.close()
