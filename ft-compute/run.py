# -*- coding: UTF-8 -*-

from script.feature import Feature
from league.league import League
import sys


reload(sys)
sys.setdefaultencoding('utf-8')

#feature = Feature(4)
# feature.prepare_team_level()
# feature.prepare_team_games()
# feature.check_score(80,45)
# feature.output_hit('38')
#feature.score_fenbu('4', '2017')
#feature.ranking_score('4', '2017')

zhongchao = League(213, 'zhongchao','input/zhongchao_result.csv', 'input/zhongchao_ranking.csv')
zhongchao.parse()

this_season = zhongchao.get_season(2018)
this_season.parse_games()