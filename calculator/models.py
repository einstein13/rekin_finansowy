# -*- coding: UTF-8 -*-

from random import choices

from django.db import models

# Create your models here.

class Game(models.Model):

    link = models.CharField(max_length=15, blank=True, null=True, unique=True)
    start_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.link is None:
            self.link = self.generate_link()
        return super().save(args, kwargs)

    def generate_shortcut(self):
        keys = "abcdefghijkmnopqrstuvwxyz"
        keys += "ABCDEFGHJKLMNPQRSTUVWXYZ"
        keys += "123456789"
        generated = choices(keys, k=7)
        generated = "".join(generated)
        return generated

    def generate_link(self):
        new_shortcut = None
        while new_shortcut is None:
            new_shortcut = self.generate_shortcut()
            g = Game.objects.filter(link=new_shortcut)
            count = g.count()
            if count != 0:
                new_shortcut = None
        return new_shortcut


class Player(models.Model):

    name = models.CharField(max_length=31)
    order = models.IntegerField(default=1)
    game = models.ForeignKey('Game', on_delete=models.CASCADE,
            related_name='players')


class Turn(models.Model):

    number = models.IntegerField(default=1)
    game = models.ForeignKey('Game', on_delete=models.CASCADE,
            related_name='turns')


class Share(models.Model):

    name = models.CharField(max_length=31)
    cost = models.IntegerField()

    divident = models.IntegerField()
    value_up = models.IntegerField()
    value_down = models.IntegerField()

    profit_3up = models.IntegerField()
    profit_2up = models.IntegerField()
    profit_1up = models.IntegerField()
    profit_0 = models.IntegerField()
    profit_1down = models.IntegerField()
    profit_2down = models.IntegerField()
    profit_3down = models.IntegerField()


class Stock(models.Model):

    player = models.ForeignKey('Player', on_delete=models.CASCADE,
            related_name='stocks')
    turn = models.ForeignKey('Turn', on_delete=models.CASCADE,
            related_name='stocks')
    share = models.ForeignKey('Share', on_delete=models.CASCADE,
            related_name='stocks')
    amount = models.IntegerField(default=0)


class Forecast(models.Model):

    turn = models.ForeignKey('Turn', on_delete=models.CASCADE,
            related_name='forecasts')
    all_company = models.ForeignKey('Share', on_delete=models.CASCADE,
            related_name='forecast0')
    main_company = models.ForeignKey('Share', on_delete=models.CASCADE,
            related_name='forecast1')
    secondary_company = models.ForeignKey('Share', on_delete=models.CASCADE,
            related_name='forecast2')
    all_forecast = models.IntegerField(default=0)
    main_forecast = models.IntegerField(default=0)
    secondary_forecast = models.IntegerField(default=0)
