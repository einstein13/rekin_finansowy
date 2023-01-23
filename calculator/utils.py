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

    def initialize_players(self, players_list):
        result = []
        players = game_object.players.all()
        players = players.sort_by('pk')
        for player in players:
            result.append([player.pk, player.name, player, 0, 0, 0])
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

    def plot_values(self, data_list):
        if self.initialized == False:
            return ""
        data_x = [1,2,3,4,5]
        data_y = [3,1,5,3,2]
        fig, ax = self.plt.subplots(figsize=(10,4))
        ax.plot(data_x, data_y, '--bo')

        ax.set_title('By date')
        ax.set_ylabel("Count")
        ax.set_xlabel("Date")

        flike = self.io.BytesIO()
        fig.savefig(flike)
        result = self.b64.b64encode(flike.getvalue()).decode()
        return result















    cache = {'shares': {}}

    def get_share(self, pk):
        if pk in cache['shares']:
            return cache['shares'][pk]
        s = Share.objects.get(pk=pk)
        cache['shares'][pk] = s
        return s

    def get_share_pk(self, key):
        if not key.startswith("share_"):
            return None

        return key[6:]

    """
        Expected structure:
        {
            'forecast': {},
            'player_X': {
                'name': '',
                'pk': '',
                'share_[pk1]': 0,
                'share_[pk2]': 2,
                'share_[pk3]': 1,
            },
            'player_Y': {...}
        }
    """
    def calculate(self, input_data):
        result = 0
        return result
        