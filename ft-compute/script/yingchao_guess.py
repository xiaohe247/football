# -*- coding: UTF-8 -*-

import codecs
import csv
from feature import Feature

class YingchaoGuess:

    WIN_LINE = -3

    LOST_LINE = 4

    def guess_three(self, season, round_num):

        feature = Feature(4)
        feature.prepare_team_ranking()

        with codecs.open('input/yingchao_result.csv', 'rb', 'utf-8') as file:
            next(file)
            for row in file:
                row = row.strip('\r\n')
                columns = row.split(',')

                if season == int(columns[0]) and round_num == int(columns[2]) and int(columns[1]) == 4:
                    home_team = Feature.team_name_clear(columns[3])
                    guest_team = Feature.team_name_clear(columns[4])

                    home_key = Feature.create_team_id('2017', columns[1], home_team)
                    guest_key = Feature.create_team_id('2017', columns[1], guest_team)

                    home_ranking = feature.get_team_ranking(home_key)
                    guest_ranking = feature.get_team_ranking(guest_key)
                    diff_ranking = home_ranking - guest_ranking

                    print home_team + '\t' + guest_team  + '\t' + str(home_ranking) + '\t' + str(guest_ranking)  + '\t' + str(diff_ranking)


