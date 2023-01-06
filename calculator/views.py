# -*- coding: UTF-8 -*-

from django.views.generic import TemplateView

from calculator.models import Game, Player, Turn, Share, Stock, Forecast


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
        print(post)

        post['game'] = self.get_game(post)

        return context

    def get_game(self, post):
        link = post['game_link']
        g = Game.objects.filter(link=link)
        return g

    def get_players(self, post):
        keys = post.keys()
        keys.sort()
        result = []
        for key in keys:
            if key.startswith('player_'):
                player_id = post[key][7:]
                player_id = int(player_id)
                result.append(player_id)
        return result

    def post(self, request, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)


class GameEnd(TemplateView):
    template_name = "game_end.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)
