# -*- coding: UTF-8 -*-

from django.views.generic import TemplateView
from django.shortcuts import redirect

from calculator.models import Game, Player, Turn, Share, Stock, Forecast
from calculator.utils import PaycheckCalculator, PaycheckPlot


def flatten_dict(dictionary):
    for key in dictionary.keys():
        value = dictionary[key]
        if type(value) is list:
            value = value[0]
            dictionary[key] = value
    return dictionary


class Home(TemplateView):
    template_name = "home.html"

    def get_players(self, game):
        players = game.players.all()
        result = ""
        for player in players:
            if result != "":
                result += ", "
            result += player.name
        return result

    def get_latest_games(self):
        g = Game.objects.all()
        g = g.order_by('-start_date')
        if g.count() > 5:
            g = g[:5]

        result = []
        for el in g:
            date = el.start_date.strftime("%Y-%m-%d %H:%M:%S")
            link = el.link
            players = self.get_players(el)
            result.append([date, link, players])
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['games'] = self.get_latest_games()

        return context


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
    stock_string_start = "stock_"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = dict(self.request.POST)
        post = flatten_dict(post)
        # print(post)
        # print("- - - - - -")
        post['game'] = self.get_game(post)
        if post['game'] is None:
            context["game"] = None
            return context

        post['players'] = self.get_players(post)
        post['shares'] = self.get_shares()
        post['turn'] = self.get_turn(post)
        post['stocks'] = self.get_stocks(post)
        post['forecast'] = self.get_forecast(post)
        self.calculate_players_details(post)

        if 'finish_turn' in post and post['finish_turn'] == "true":
            self.save_and_finish(post)

        for key in post.keys():
            context[key] = post[key]
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
        pc = PaycheckCalculator()
        return pc.get_game(post['game_link'])

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
                # [player_id, player_name, player_object, player_turn_balance, player_spent_value, player_current_value]
                result.append([player.pk, player_name, player, 0, 0, 0])
        if len(result) == 0:
            pc = PaycheckCalculator()
            result = pc.initialize_players(post['game'])
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
        string_start = self.stock_string_start
        keys = list(post.keys())
        data = {}
        for key in keys:
            if str(key).startswith(string_start):
                data[key] = post[key]

        if len(data.keys()) == 0 and post['turn'][0] is not None:
            turn = post['turn'][0]
            stocks = turn.stocks.all()
            for stock in stocks:
                key = string_start + str(stock.share_id) + "_" + str(stock.player_id)
                value = stock.amount
                data[key] = value

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

    def get_forecast(self, post):
        result = {}

        # defaults
        result['main_forecast_change'] = 0
        result['secondary_forecast_change'] = 0
        result['all_forecast_change'] = 0
        result['main_forecast_share'] = -1
        result['secondary_forecast_share'] = -1

        if 'all_forecast_change' not in post:
            return result

        result['main_forecast_change'] = int(post['main_forecast_change'])
        result['secondary_forecast_change'] = int(post['secondary_forecast_change'])
        result['all_forecast_change'] = int(post['all_forecast_change'])
        result['main_forecast_share'] = int(post['main_forecast_share'])
        result['secondary_forecast_share'] = int(post['secondary_forecast_share'])

        return result

    def calculate_single_stocks_profit(self, forecast, share, stocks_amount):
        # forecast - dict
        # share - Share object
        # stocks_amount - int value
        if stocks_amount == 0:
            return 0

        profit_type = forecast["all_forecast_change"]
        share_pk = share.pk
        if share_pk == forecast["main_forecast_share"]:
            profit_type = forecast["main_forecast_change"]
        elif share_pk == forecast["secondary_forecast_share"]:
            profit_type = forecast["secondary_forecast_change"]

        single_profit = 0
        if profit_type == 3:
            single_profit = share.profit_3up
        if profit_type == 2:
            single_profit = share.profit_2up
        if profit_type == 1:
            single_profit = share.profit_1up
        if profit_type == 0:
            single_profit = share.profit_0
        if profit_type == -1:
            single_profit = share.profit_1down
        if profit_type == -2:
            single_profit = share.profit_2down
        if profit_type == -3:
            single_profit = share.profit_3down

        return single_profit*stocks_amount

    def calculate_single_stocks_spent(self, share, stocks_amount):
        # share - Share object
        # stocks_amount - int value
        if stocks_amount == 0:
            return 0

        return share.cost*stocks_amount

    def calculate_single_stocks_value(self, forecast, share, stocks_amount):
        # forecast - dict
        # share - Share object
        # stocks_amount - int value
        if stocks_amount == 0:
            return 0

        profit_type = forecast["all_forecast_change"]
        share_pk = share.pk
        if share_pk == forecast["main_forecast_share"]:
            profit_type = forecast["main_forecast_change"]
        elif share_pk == forecast["secondary_forecast_share"]:
            profit_type = forecast["secondary_forecast_change"]

        single_value = 0
        if profit_type >= 0:
            single_value = share.value_up
        if profit_type < 0:
            single_value = share.value_down

        return single_value*stocks_amount

    def calculate_players_details(self, post):
        string_start = self.stock_string_start

        forecast = post['forecast']
        players = post['players']
        shares = post['shares']

        for share in shares:
            for player in players:
                key = "stock_" + str(share.pk) + "_" + str(player[0])
                stock = 0
                if key in post:
                    stock = post[key]
                    if stock == "":
                        stock = 0
                    else:
                        stock = int(stock)

                add_profit = self.calculate_single_stocks_profit(forecast, share, stock)
                add_spent = self.calculate_single_stocks_spent(share, stock)
                add_value = self.calculate_single_stocks_value(forecast, share, stock)
                player[3] += add_profit
                player[4] += add_spent
                player[5] += add_value
        return

    def save_turn(self, post):
        new_turn = Turn()
        new_turn.game = post['game']
        new_turn.number = post['turn'][1]
        new_turn.save()
        post['turn'][0] = new_turn
        post['turn'][1] += 1
        return new_turn

    def save_one_stock(self, key, value, turn):
        if value == "" or value == "0":
            return False

        amount = int(value)

        splitted = key.split("_")
        share_id = int(splitted[1])
        player_id = int(splitted[2])

        player = Player.objects.get(pk=player_id)
        if player.game_id != turn.game_id:
            return False

        share = Share.objects.get(pk=share_id)

        stock = Stock.objects.filter(turn=turn, player=player, share=share)
        if stock.count() == 0:
            # new record
            stock = Stock()
            stock.player = player
            stock.turn = turn
            stock.share = share
            stock.amount = amount
            stock.save()
            return True

        # exsting record
        stock = stock[0]
        stock.amount= amount
        stock.save()

        return True

    def save_stocks(self, post, turn):
        string_start = self.stock_string_start
        keys = list(post.keys())

        for key in keys:
            if str(key).startswith(string_start):
                self.save_one_stock(key, post[key], turn)

        return

    def get_share(self, share_pk):
        return Share.objects.get(pk=int(share_pk))

    def save_forecast(self, post, turn):

        forecast = Forecast.objects.filter(turn=turn)
        if forecast.count() == 0:
            forecast = Forecast()
            forecast.turn = turn
        else:
            forecast = forecast[0]

        if post['main_forecast_share'] != "-1":
            forecast.main_company = self.get_share(post['main_forecast_share'])
        if post['secondary_forecast_share'] != "-1":
            forecast.secondary_company = self.get_share(post['secondary_forecast_share'])
        forecast.all_forecast = post['all_forecast_change']
        forecast.main_forecast = post['main_forecast_change']
        forecast.secondary_forecast = post['secondary_forecast_change']
        forecast.save()

        # clear data
        post['forecast']['main_forecast_change'] = 0
        post['forecast']['secondary_forecast_change'] = 0
        post['forecast']['all_forecast_change'] = 0
        post['forecast']['main_forecast_share'] = -1
        post['forecast']['secondary_forecast_share'] = -1
        return True

    def save_and_finish(self, post):
        # create new turn
        new_turn = self.save_turn(post)

        # save stocks
        self.save_stocks(post, new_turn)

        # save forecast
        self.save_forecast(post, new_turn)

        return


class GameEnd(TemplateView):
    template_name = "game_end.html"

    def extract_winner(self, time_results):
        if len(time_results) == 0:
            return "brak"
        result = ["", 0]
        last_turn = time_results[-1]
        for el in last_turn:
            if el[4] > result[1]:
                result[1] = el[4]
                result[0] = el[1]
        return "%s (%d)" % tuple(result)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pc = PaycheckCalculator()

        game_link = kwargs['link']
        context['game'] = pc.get_game(game_link)
        context['players'] = pc.get_players(context['game'])
        context['turns'] = pc.get_turns(context['game'])
        context['time_results'] = pc.get_results(context['game'])

        context['winner'] = self.extract_winner(context['time_results'])

        print(context)
        pp = PaycheckPlot()
        context['plot'] = pp.plot_values(context['time_results'])


        return context

    def post(self, request, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)
