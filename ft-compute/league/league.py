# -*- coding: UTF-8 -*-

import codecs

# 联赛
class League:

    LEVEL_GAP = 5

    def __init__(self, lid, l_name, games_filename, ranking_filename):
        self.lid = lid
        self.l_name = l_name
        self.games_filename = games_filename
        self.ranking_filename = ranking_filename
        self.season_map = {}


    # 解析联赛数据
    def parse(self):
        self.__parse_level_and_ranking()
        self.__parse_games()

    # 获取赛季对象
    def get_season(self, year):
        if self.season_map.has_key(year):
            return self.season_map[year]

    # 球队名称合规
    @staticmethod
    def team_name_clear(name):
        if name == '贵州人和茅台':
            return '贵州人和'
        return name


    # 球队分级和排名
    def __parse_level_and_ranking(self):
        with codecs.open(self.ranking_filename, 'rb', 'utf-8') as file:
            next(file)
            for row in file:
                columns = row.split(',')
                lid = int(columns[1])
                if self.lid == lid:
                    year = int(columns[0])
                    season = self.__find_season(year)
                    ranking = int(columns[2])
                    level = (ranking - 1) / self.LEVEL_GAP + 1
                    team_name = self.team_name_clear(columns[3])
                    season.set_team_level(team_name, level)
                    season.set_team_ranking(team_name, ranking)


    # 联赛所有比赛
    def __parse_games(self):
        with codecs.open(self.games_filename, 'rb', 'utf-8') as file:
            next(file)
            for row in file:
                row = row.strip('\r\n')
                columns = row.split(',')
                lid = int(columns[1])
                if self.lid == lid:
                    season = self.__find_season(year = int(columns[0]))

                    home_team = self.team_name_clear(columns[3])
                    guest_team = self.team_name_clear(columns[4])
                    goal = columns[5]
                    guest_goal = columns[6]
                    round_num = columns[2]
                    game = Game(home_team, guest_team, goal, guest_goal, round_num)
                    season.put_game(game)


    # 赛季对象
    def __find_season(self, year):
        if self.season_map.has_key(year):
            season = self.season_map[year]
        else:
            season = Season(self.lid, year)
            self.season_map[year] = season
        return season



# 赛季
class Season:

    WEIGHT_DIFF = 1
    WEIGHT_HOME = 1
    WEIGHT_GUEST = 1

    def __init__(self, lid, year):
        self.lid = lid
        self.year = year
        self.team_ranking = {}
        self.team_level = {}
        self.game_list = []
        # <轮次，比赛列表>，即 <round, [games]>
        self.finished_games = {}
        self.unfinished_games = {}
        # <主队， 比赛列表>，即 <home_team, [games]>
        self.home_games = {}
        # <客队， 比赛列表>，即 <guest_team, [games]>
        self.guest_games = {}
        # <排名差， 比赛列表>
        self.diff_games = {}
        self.parsed = False

    # 分析比赛，不同维度归类
    def parse_games(self):
        if not self.parsed:
            for game in self.game_list:
                game.home_team_ranking = self.team_ranking[game.home_team]
                game.guest_team_ranking = self.team_ranking[game.guest_team]

                if game.home_goal != '':
                    self.__put_finished_game(game)
                    self.__put_home_games(game)
                    self.__put_guest_games(game)
                    self.__put_diff_games(game)
                else:
                    self.__put_unfinished_game(game)

            self.parsed = True


    # 预测
    def forecast(self, game):
        home_team = game.home_team
        guest_team = game.guest_team
        home_team_ranking = self.get_team_ranking(home_team)
        guest_team_ranking = self.get_team_ranking(guest_team)
        ranking_diff = guest_team_ranking - home_team_ranking
        ab_diff_games = self.diff_games[ranking_diff] if self.diff_games.has_key(ranking_diff) else []
        a_home_games = self.home_games[home_team] if self.home_games.has_key(home_team) else []
        b_guest_games = self.guest_games[guest_team] if self.guest_games.has_key(guest_team) else []

        w_d_l = self.forecast_w_d_l(ab_diff_games, a_home_games, b_guest_games)
        goals = self.forecast_goal(ab_diff_games, a_home_games, b_guest_games)
        game.three_result = w_d_l
        game.home_goal = goals[0]
        game.guest_goal = goals[1]

        return [game] + ab_diff_games + a_home_games + b_guest_games



    # 预测胜平负
    def forecast_w_d_l(self, ab_diff_games, a_home_games, b_guest_games):
        feature1 = self.__feature1(ab_diff_games)
        feature2 = self.__feature1(a_home_games)
        feature3 = self.__feature1(b_guest_games)

        w_times = feature1[0] * self.WEIGHT_DIFF + feature2[0] * self.WEIGHT_HOME + feature3[0] * self.WEIGHT_GUEST
        d_times = feature1[1] * self.WEIGHT_DIFF + feature2[1] * self.WEIGHT_HOME + feature3[1] * self.WEIGHT_GUEST
        l_times = feature1[2] * self.WEIGHT_DIFF + feature2[2] * self.WEIGHT_HOME + feature3[2] * self.WEIGHT_GUEST

        if w_times >= d_times + l_times:  # 主队胜率超 50%
            return 1
        elif l_times >= w_times + d_times:  # 客队胜率超 50%
            return -1
        elif 2 * d_times >= w_times + d_times:  # 平的概率超 1/3
            return 0
        elif w_times == l_times:  # 主客队胜率一样
            return 0
        else:
            max_value = max(w_times, d_times, l_times)
            if max_value == w_times:
                return 1
            elif max_value == l_times:
                return -1
            else:
                return 0

    def forecast_goal(self, ab_diff_games, a_home_games, b_guest_games):
        feature1 = self.__feature2(ab_diff_games)
        feature2 = self.__feature2(a_home_games)
        feature3 = self.__feature2(b_guest_games)
        a = (feature1[0] + feature2[0]) / 2
        b = (feature1[1] + feature3[1]) / 2
        return [a, b]


    #[主队赢场次, 平场次, 客队赢场次]
    def __feature1(self, games):
        feature_value=[0,0,0]
        for game in games:
            result = game.three_result
            if result == 1:
                feature_value[0] += 1
            elif result == 0:
                feature_value[1] += 1
            elif result == -1:
                feature_value[2] += 1
        return feature_value


    #[主队平均进球, 客队平均进球]
    def __feature2(self, games):
        home_goals = []
        guest_goals = []
        for game in games:
            home_goals.append(int(game.home_goal))
            guest_goals.append(int(game.guest_goal))
        if len(home_goals) == 0:
            return [0, 0]
        if len(home_goals) == 1:
            return [home_goals[0], guest_goals[0]]
        if len(home_goals) == 2:
            a = (sum(home_goals) + 0.0) / 2
            b = (sum(guest_goals) + 0.0) / 2
            return [a, b]

        a = (sum(home_goals) - max(home_goals) - min(home_goals) + 0.0) / (len(home_goals) - 2)
        b = (sum(guest_goals) - max(guest_goals) - min(guest_goals) + 0.0) / (len(guest_goals) - 2)
        return [a, b]


    # 球队分级
    def set_team_level(self, team_name, level):
        self.team_level[team_name] = level

    # 球队排名
    def set_team_ranking(self, team_name, ranking):
        self.team_ranking[team_name] = ranking

    def get_team_level(self, team_name):
        return self.team_level[team_name]

    def get_team_ranking(self, team_name):
        if self.team_ranking.has_key(team_name):
            return self.team_ranking[team_name]
        return max(self.team_ranking.values())

    def put_game(self, game):
        self.game_list.append(game)

    def get_unfinished_games(self, round_num):
        if self.unfinished_games.has_key(round_num):
            return self.unfinished_games[round_num]


    # 完赛的比赛
    def __put_finished_game(self, game):
        round_num = game.round_num
        if self.finished_games.has_key(round_num):
            self.finished_games[round_num].append(game)
        else:
            games = [game]
            self.finished_games[round_num] = games

    # 未完赛比赛
    def __put_unfinished_game(self, game):
        round_num = game.round_num
        if self.unfinished_games.has_key(round_num):
            self.unfinished_games[round_num].append(game)
        else:
            games = [game]
            self.unfinished_games[round_num] = games

    # 主队所有比赛
    def __put_home_games(self, game):
        home_team = game.home_team
        if self.home_games.has_key(home_team):
            self.home_games[home_team].append(game)
        else:
            games = [game]
            self.home_games[home_team] = games

    # 客队所有比赛
    def __put_guest_games(self, game):
        guest_team = game.guest_team
        if self.guest_games.has_key(guest_team):
            self.guest_games[guest_team].append(game)
        else:
            games = [game]
            self.guest_games[guest_team] = games

    # 排名差距相同的比赛
    def __put_diff_games(self, game):
        diff = game.guest_team_ranking - game.home_team_ranking
        if self.diff_games.has_key(diff):
            self.diff_games[diff].append(game)
        else:
            games = [game]
            self.diff_games[diff] = games


class Game:

    def __init__(self, home_team, guest_team, home_goal, guest_goal, round_num):
        self.home_team = home_team
        self.guest_team = guest_team
        self.home_goal = home_goal
        self.guest_goal = guest_goal
        self.round_num = round_num
        self.home_team_ranking = 0
        self.guest_team_ranking = 0
        self.three_result = self.__three_result()


    def __three_result(self):
        if self.home_goal == '':
            return -2
        if self.home_goal > self.guest_goal:
            return 1
        if self.home_goal == self.guest_goal:
            return 0
        if self.home_goal < self.guest_goal:
            return -1
        return -2

    def to_row(self):
        return [self.round_num,
               self.home_team,
               self.guest_team,
               self.home_team_ranking,
               self.guest_team_ranking,
               self.home_goal,
               self.guest_goal,
               self.three_result]


    def output(self):
        print str(self.round_num) + '\t' + \
              self.home_team + '\t' + \
              self.guest_team + '\t' + \
              str(self.home_team_ranking) + '\t' + \
              str(self.guest_team_ranking) + '\t'+ \
              str(self.home_goal) + '\t' + \
              str(self.guest_goal) + '\t' + \
              str(self.three_result)