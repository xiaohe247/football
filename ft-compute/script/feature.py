# -*- coding: UTF-8 -*-

import codecs
import csv

class Feature:

    # <key, value>; key = 2015-1-国际米兰；"赛季-联赛ID-球队"
    team_level = {}
    team_ranking = {}

    # <key, []> key = 1-国际米兰；"联赛ID-球队"
    teams_games = {}

    hit_result = {}


    lookback =30
    gametime = 2014



    RANKING_FILENAME = {0: 'input/ranking.csv',
                        4: 'input/yingchao_ranking.csv',
                        38: 'input/meiguodalianmen_ranking.csv',
                        213:'input/zhongchao_ranking.csv'}

    GAME_FILNAME = {0:'input/result.csv',
                    4: 'input/yingchao_result.csv',
                    38: 'input/meiguodalianmen_result.csv',
                    213:'input/zhongchao_result.csv' }

    LID_FILENAME = {0:'',
                    4: 'yingchao_',
                    38: 'meiguodalianmen_',
                    213: 'zhongchao_'
                    }

    def __init__(self, lid):
        self.ranking_filename = self.RANKING_FILENAME[lid]
        self.result_filename = self.GAME_FILNAME[lid]


    # 球队分级
    def prepare_team_level(self):
        level_gap = 5
        with codecs.open(self.ranking_filename, 'rb', 'utf-8') as file:
            next(file)
            for row in file:
                columns = row.split(',')
                season = columns[0]
                lid = columns[1]
                team_name = columns[3]
                ranking = columns[2]
                key = Feature.create_team_id(season, lid, self.team_name_clear(team_name))
                level = (int(ranking) - 1) / level_gap + 1
                self.team_level[key] = level


    # 球队排名
    def prepare_team_ranking(self):
        with codecs.open(self.ranking_filename, 'rb', 'utf-8') as file:
            next(file)
            for row in file:
                columns = row.split(',')
                season = columns[0]
                lid = columns[1]
                team_name = columns[3]
                key = Feature.create_team_id(season, lid, self.team_name_clear(team_name))
                ranking = int(columns[2])
                self.team_ranking[key] = ranking


    def get_team_ranking(self, key):
        if self.team_ranking.has_key(key):
            return self.team_ranking[key]
        return 30


    # 球队赛程,按时间排序，不分主客场
    def prepare_team_games(self):
        with codecs.open('input/result.csv', 'rb', 'utf-8') as file:
            next(file)
            for row in file:
                row = row.strip('\r\n')
                columns = row.split(',')
                if columns[5] != '':
                    season = columns[0]
                    lid = columns[1]
                    round = columns[2]
                    home_team = self.team_name_clear(columns[3])
                    guest_team = self.team_name_clear(columns[4])
                    goal = columns[5]
                    guest_goal = columns[6]
                    half_goal = columns[7]
                    half_guest_goal = columns[8]

                    if int(season) > self.gametime :
                        sort_key = int(season) * 100 + int(round)
                        home_id = lid + '-' + home_team
                        guest_id = lid + '-' + guest_team

                        home_level_key = Feature.create_team_id(season, lid, home_team)
                        guest_level_key = Feature.create_team_id(season, lid, guest_team)
                        home_level = self.team_level[home_level_key]
                        guest_level = self.team_level[guest_level_key]

                        self.put_in_team_game(home_id, guest_team, guest_level, goal, guest_goal, half_goal,half_guest_goal, sort_key)
                        self.put_in_team_game(guest_id, home_team, home_level, guest_goal, goal, half_guest_goal, half_goal, sort_key)

            for key, list in self.teams_games.items():
                sorted_list = sorted(list, key = lambda x:x['sort_key'])
                self.teams_games[key] = sorted_list


    # 猜球队进球
    def guess_result(self):
        with codecs.open('input/games.csv', 'rb', 'utf-8') as file:
            for row in file:
                row = row.strip('\r\n')
                columns = row.split(',')
                season = columns[0]
                lid = columns[1]
                round_num = columns[2]
                home_team = self.team_name_clear(columns[3])
                guest_team = self.team_name_clear(columns[4])

                home_goal, guest_goal = self.compute_score(season, lid, round_num, home_team, guest_team, 80, 45)
                print home_team + '\t' + guest_team + '\t' + str(home_goal) + '-' + str(guest_goal)


    # 联赛单赛季比分分布
    def score_fenbu(self, in_lid, in_season):
        fenbu = {}
        with codecs.open('input/' + self.LID_FILENAME[int(in_lid)] +'result.csv', 'rb', 'utf-8') as file:
            next(file)
            for row in file:
                row = row.strip('\r\n')
                columns = row.split(',')
                if columns[5] != '':
                    season = columns[0]
                    lid = columns[1]
                    goal = columns[5]
                    guest_goal = columns[6]

                    key = lid + '-' + season
                    score = goal + '-' + guest_goal
                    if fenbu.has_key(key):
                        aa = fenbu[key]
                    else:
                        aa = {}
                        fenbu[key] = aa

                    if aa.has_key(score):
                        aa[score] += 1
                    else:
                        aa[score] = 1

        for k, v in fenbu[in_lid + '-' + in_season].items():
            print k + "\t" + str(v)



    def ranking_score(self, in_lid, in_season):
        fenbu = {}
        fenbu2 = []
        for i in range(25):
            fenbu2.append({'total':0,'win':0, 'lost':0, 'ping': 0})

        self.prepare_team_ranking()
        with codecs.open(self.GAME_FILNAME[int(in_lid)], 'rb', 'utf-8') as file:
            next(file)
            for row in file:
                row = row.strip('\r\n')
                columns = row.split(',')
                if columns[5] != '':
                    season = columns[0]
                    lid = columns[1]
                    home_team = self.team_name_clear(columns[3])
                    guest_team = self.team_name_clear(columns[4])
                    goal = columns[5]
                    guest_goal = columns[6]

                    home_team_key = self.create_team_id(season, lid, home_team)
                    if self.team_ranking.has_key(home_team_key):
                        home_ranking = self.team_ranking[home_team_key]
                    else:
                        print home_team_key
                        home_ranking = 0


                    guest_team_key = self.create_team_id(season, lid, guest_team)
                    if self.team_ranking.has_key(guest_team_key):
                        guest_ranking = self.team_ranking[guest_team_key]
                    else:
                        print guest_team_key
                        guest_ranking = 0


                    key = lid + '-' + season
                    score = goal + '-' + guest_goal
                    three = self.three_status(goal, guest_goal)

                    ranking_diff = home_ranking - guest_ranking

                    if fenbu.has_key(key):
                        aa = fenbu[key]
                    else:
                        aa = []
                        fenbu[key] = aa

                    c = []
                    c.append(home_team)
                    c.append(guest_team)
                    c.append(home_ranking)
                    c.append(guest_ranking)
                    c.append(score)
                    c.append(three)
                    c.append(ranking_diff)
                    #c = home_team + "\t" + guest_team + "\t" + str(home_ranking) + "\t" + str(guest_ranking) + "\t" + score + '\t' + str(three) + '\t' + str(ranking_diff)
                    aa.append(c)

                    if season == in_season and lid == in_lid:
                        min = ranking_diff if ranking_diff > 0 else 0
                        for i in range(min, 25):
                            fenbu2[i]['total'] += 1
                            if three == 1:
                                fenbu2[i]['win'] += 1
                            if three == -1:
                                fenbu2[i]['lost'] += 1
                            if three == 0:
                                fenbu2[i]['ping'] += 1


        for i in range(25):
            if fenbu2[i]['total'] != 0:
                print i
                print 'total:' + str(fenbu2[i]['total'])
                print 'win:' + str(fenbu2[i]['win']) + '\t' + str((fenbu2[i]['win'] + 0.0) / fenbu2[i]['total'] )
                print 'lost:' + str(fenbu2[i]['lost']) + '\t' + str((fenbu2[i]['lost'] + 0.0) / fenbu2[i]['total'] )
                print 'ping:' + str(fenbu2[i]['ping']) + '\t' + str((fenbu2[i]['ping'] + 0.0) / fenbu2[i]['total'])
                print '-------------------------'

        ranking_score_file = open('output/' + self.LID_FILENAME[int(in_lid)] + 'ranking_score.csv', 'w')
        write = csv.writer(ranking_score_file)
        for v in fenbu[in_lid + '-' + in_season]:
            write.writerow(v)
        ranking_score_file.close()



    # 猜分数
    def compute_score(self, season, lid, round_num, home_team, guest_team, home_weight, guest_weight):
        sort_key = int(season) * 100 + int(round_num)
        home_id = lid + '-' + home_team
        guest_id = lid + '-' + guest_team
        home_level_key = Feature.create_team_id(season, lid, home_team)
        guest_level_key = Feature.create_team_id(season, lid, guest_team)
        home_level = self.team_level[home_level_key]
        guest_level = self.team_level[guest_level_key]

        home_goal_agv, home_fumble_avg = self.get_avg_goal(home_id, sort_key, guest_level)

        guest_goal_agv, guest_fumble_avg = self.get_avg_goal(guest_id, sort_key, home_level)

        if home_goal_agv != -1.0:
            home_goal_guess = int(round((home_goal_agv * home_weight + guest_fumble_avg * (100 - home_weight)) / 100))
            guest_goal_guess = int(round((guest_goal_agv * guest_weight + home_fumble_avg * (100 - guest_weight)) / 100))
            return home_goal_guess, guest_goal_guess
        return -1, -1


    # 检查准确性
    def check_score(self, home_weight, guest_weight):
        with codecs.open('input/result.csv', 'rb', 'utf-8') as file:
            next(file)
            for row in file:
                row = row.strip('\r\n')
                columns = row.split(',')
                if columns[5] != '':
                    season = columns[0]
                    lid = columns[1]
                    round_num = columns[2]
                    home_team = columns[3]
                    guest_team = columns[4]
                    goal = int(columns[5])
                    guest_goal = int(columns[6])
                    half_goal = columns[7]
                    half_guest_goal = columns[8]

                    if int(season) > self.gametime:
                        home_goal_guess, guest_goal_guess = self.compute_score(season, lid, round_num, home_team, guest_team, home_weight, guest_weight)
                        if home_goal_guess != -1:
                            self.w_hit_result(0, goal, guest_goal, home_goal_guess, guest_goal_guess)
                            self.w_hit_result(lid, goal, guest_goal, home_goal_guess, guest_goal_guess)



    #
    def put_in_team_game(self, team, oppo, oppo_level, goal, fumble, half_goal, half_fumble, sort_key):
        if self.teams_games.has_key(team):
            team_games = self.teams_games[team]
        else:
            team_games = []
            self.teams_games[team] = team_games
        game = {}
        game['oppo'] = oppo
        game['oppo_level'] = oppo_level
        game['goal'] = goal
        game['fumble'] = fumble
        game['half_goal'] = half_goal
        game['half_fumble'] = half_fumble
        game['sort_key'] = sort_key
        team_games.append(game)

        if fumble == '':
            print team
            print oppo
            print sort_key
            print goal
            print fumble


    def get_avg_goal(self, team, sort_key, oppo_level):
        team_games = self.teams_games[team]
        index = 0
        for game in team_games:
            if game['sort_key'] < sort_key:
                index = index + 1
            else:
                break
        if index < self.lookback:
            return -1.0, -1.0

        goal_sum = 0.0
        fumble_sum = 0.0
        game_num = 0
        for i in range(index - self.lookback, index):
            game = team_games[i]
            if game['oppo_level'] == oppo_level:
                goal_sum = goal_sum + int(game['goal'])
                fumble_sum = fumble_sum + int(game['fumble'])
                game_num = game_num + 1

        if game_num == 0:
            return -1.0, -1.0

        return goal_sum/game_num, fumble_sum/game_num


    def three_status(self, home, guest):
        if home > guest:
            return 1
        if home == guest:
            return 0
        return -1


    def w_hit_result(self, lid, goal, guest_goal, home_guess, guest_guess):
        if self.hit_result.has_key(lid):
            lid_hit = self.hit_result[lid]
        else:
            lid_hit = {}
            self.hit_result[lid] = lid_hit

        if lid_hit.has_key('game_sum'):
            lid_hit['game_sum'] += 1
        else:
            lid_hit['game_sum'] = 1

        if home_guess == goal:
            if lid_hit.has_key('home_hit'):
                lid_hit['home_hit'] += 1
            else:
                lid_hit['home_hit'] = 1

        if guest_guess == guest_goal:
            if lid_hit.has_key('guest_hit'):
                lid_hit['guest_hit'] += 1
            else:
                lid_hit['guest_hit'] = 1

        if home_guess == goal and guest_guess == guest_goal:
            if lid_hit.has_key('all_hit'):
                lid_hit['all_hit'] += 1
            else:
                lid_hit['all_hit'] = 1

        if self.three_status(goal, guest_goal) == self.three_status(home_guess, guest_guess):
            if lid_hit.has_key('three_hit'):
                lid_hit['three_hit'] += 1
            else:
                lid_hit['three_hit'] = 1

    # 输出结果
    def output_hit(self, key):
        v = self.hit_result[key]
        print key
        print 'total: \t' + str(v['game_sum'])
        print 'three_hit: \t' + str(v['three_hit'])+ '\t' + str((v['three_hit'] + 0.0) / v['game_sum'])
        print 'all_hit: \t' + str(v['all_hit'])+ '\t'+ str((v['all_hit'] + 0.0) / v['game_sum'])
        print 'home_hit: \t' + str(v['home_hit'])+ '\t'+ str((v['home_hit'] + 0.0) / v['game_sum'])
        print 'guest_hit: \t' + str(v['guest_hit'])+ '\t'+ str((v['guest_hit'] + 0.0) / v['game_sum'])


    def write_game(self, writer, key, game):
        row = []
        row.append(key)
        row.append(game['sort_key'])
        row.append(game['oppo'])
        row.append(game['oppo_level'])
        row.append(game['goal'])
        row.append(game['fumble'])
        row.append(game['half_goal'])
        row.append(game['half_fumble'])
        writer.writerow(row)


    @staticmethod
    def create_team_id(season, lid, team):
        return season + "-" + lid + "-" + team

    # 球队名称合规
    @staticmethod
    def team_name_clear(name):
        if name == '贵州人和茅台':
            return '贵州人和'
        return name
