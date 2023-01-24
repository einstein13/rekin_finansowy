# -*- coding: UTF-8 -*-

from calculator.models import Share



from calculator.models import Game

class PaycheckCalculator(object):

    def get_game(self, game_link):
        if game_link is None or game_link == "":
            return None
        g = Game.objects.filter(link=game_link)
        if g.count() == 0:
            return None
        return g[0]

    def get_players(self, game_object):
        players = game_object.players.all()
        players = players.order_by('pk')
        return list(players)

    def get_turns(self, game_object):
        turns = game_object.turns.all()
        turns = turns.order_by('number')
        return list(turns)

    def initialize_players(self, game_object):
        result = []
        players = game_object.players.all()
        players = players.order_by('pk')
        for player in players:
            result.append([player.pk, player.name, player, 0, 0, 0])
        return result

    def get_stocks_value(self, player_object, turn_object):
        stocks = player_object.stocks.filter(turn=turn_object)
        result = 0
        for st in stocks:
            result += st.amount * st.share.cost
        return result

    def full_calculate_turn(self, turn_object):
        from random import randint
        players_data = self.initialize_players(turn_object.game)
        for player in players_data:
            player[4] = self.get_stocks_value(player[2], turn_object)
        return players_data

    def get_results(self, game_object):
        turns = self.get_turns(game_object)
        result = []
        for turn in turns:
            result.append(self.full_calculate_turn(turn))
        return result


class PaycheckPlot(object):

    plt = None
    io = None
    b64 = None
    initialized = False

    def __init__(self):

        try:
            from matplotlib import pyplot
            self.plt = pyplot
            import io
            self.io = io
            import base64
            self.b64 = base64
            self.initialized = True
        except Exception as e:
            print(e)

    def extract_players_names(self, data_list):
        result = []
        for el in data_list[0]:
            result.append(el[1])
        return result

    def extract_turns(self, data_list):
        result = list(range(1, len(data_list)+1))
        return result

    def extract_values(self, data_list):
        result = []
        for pl in data_list[0]:
            result.append([])

        for turn in data_list:
            for itr in range(len(turn)):
                result[itr].append(turn[itr][4])
        return result

    # [player_id, player_name, player_object, player_turn_balance, player_spent_value, player_current_value]
    def plot_values(self, data_list):
        if self.initialized == False:
            return ""
        if len(data_list) == 0:
            return ""
        if len(data_list[0]) == 0:
            return ""

        players = self.extract_players_names(data_list)
        turns = self.extract_turns(data_list)
        values = self.extract_values(data_list)

        fig, ax = self.plt.subplots(figsize=(10,6))
        for itr in range(len(values)):
            val_list = values[itr]
            player = players[itr]
            ax.plot(turns, val_list, '-o', label=player)

        # ax.set_title('By date')
        ax.set_ylabel("Wartość portfela akcji")
        ax.set_xlabel("Tura")
        ax.legend()

        flike = self.io.BytesIO()
        fig.savefig(flike)
        result = self.b64.b64encode(flike.getvalue()).decode()
        return result
