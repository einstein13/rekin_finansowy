# -*- coding: UTF-8 -*-

from django.views.generic import TemplateView
from django.shortcuts import redirect

from calculator.models import Game, Player, Turn, Share, Stock, Forecast


def flatten_dict(dictionary):
    for key in dictionary.keys():
        value = dictionary[key]
        if type(value) is list:
            value = value[0]
            dictionary[key] = value
    return dictionary


class Home(TemplateView):
    template_name = "home.html"


class StartGame(TemplateView):
    template_name = "start.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        players_number = self.request.POST['players']
        players_number = int(players_number)

        context['players_number'] = players_number
        context['range'] = list(range(1, players_number+1))

        game = Game()
        game.save()
        context['game_link'] = game.link

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)


class TurnCalculator(TemplateView):
    template_name = "turn.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = dict(self.request.POST)
        post = flatten_dict(post)
        post['game'] = self.get_game(post)
        if post['game'] is None:
            context["game"] = None
            return context

        post['players'] = self.get_players(post)
        post['shares'] = self.get_shares()
        post['turn'] = self.get_turn(post)
        post['stocks'] = self.get_stocks(post)

        print(post)
        context = context | post
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data()
        if context["game"] is None:
            return redirect("home")
        return self.render_to_response(context)

    def get(self, request, **kwargs):
        request.__setattr__("POST", kwargs)
        context = self.get_context_data()
        if context["game"] is None:
            return redirect("home")
        return self.render_to_response(context)        

    def get_game(self, post):
        if 'game_link' not in post:
            return None
        link = post['game_link']
        g = Game.objects.filter(link=link)
        if g.count() == 0:
            return None
        return g[0]

    def single_player(self, player_name, player_order, game):
        p = Player.objects.filter(game=game, name=player_name)
        if p.count() == 0:
            p = Player()
            p.name = player_name
            p.game = game
            p.order = player_order
            p.save()
            return p
        return p[0]

    def get_players(self, post):
        keys = list(post.keys())
        keys.sort()
        result = []
        for key in keys:
            if key.startswith('player_'):
                player_id = key[7:]
                player_id = int(player_id)
                player_name = post[key]
                player = self.single_player(player_name, player_id, post['game'])
                # [player_id, player_name, player_object, player_turn_balance, player_wallet_value]
                result.append([player_id, player_name, player, 0, 0])
        if len(result) == 0:
            game = post['game']
            players = game.players.all()
            for player in players:
                result.append([player.pk, player.name, 0, 0])
        return result

    def get_shares(self):
        s = Share.objects.all()
        result = []
        for el in s:
            result.append(el)
        return result

    def get_turn(self, post):
        game = post['game']
        if not "turn" in post or post['turn'] == "0":
            # try to find turn based on game
            turn = game.turns.all()
            if turn.count() == 0:
                # brand new game
                return [None, 0]
            # restored game
            turn = turn.latest('pk')
            return [turn, turn.number+1]

        turn = Turn.objects.filter(game=post['game'], number=int(post['turn'])-1)
        if turn.count() == 0:
            # error - return latest turn
            turn = game.turns.all()
            turn = turn.latest('pk')
            return [turn, turn.number+1]
        # there is a turn
        turn = turn[0]
        return [turn, turn.number+1]

    def get_stocks(self, post):
        string_start = "stock_"
        keys = list(post.keys())
        data = {}
        for key in keys:
            if str(key).startswith(string_start):
                data[key] = post[key]

        if len(data.keys()) == 0:
            # no stocks data
            pass

        shares = post['shares']
        players = post['players']
        result = []
        for share in shares:
            line = [share, []]
            for player in players:
                new_key = string_start + str(share.pk) + "_" + str(player[2].pk)
                if new_key in data and data[new_key] != "":
                    line[1].append([player[2].pk, int(data[new_key])])
                else:
                    line[1].append([player[2].pk, 0])
            result.append(line)

        return result

class GameEnd(TemplateView):
    template_name = "game_end.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)
