from django.contrib import admin

from calculator.models import Game, Player, Turn, Share, Stock, Forecast

# Register your models here.


class GameAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'pk', 'link', 'start_date')

class PlayerAdmin(admin.ModelAdmin):
    pass

class TurnAdmin(admin.ModelAdmin):
    pass

class ShareAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'cost', 'value_up', 'value_down')

class StockAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_player_name', 'get_game_link', 'get_turn_number', 'amount', 'get_share_name')
    list_filter = ('player__name', 'turn__game__link', 'turn__number', 'share__name')

    @admin.display(ordering='player__name', description='Player')
    def get_player_name(self, obj):
        return obj.player.name

    @admin.display(ordering='turn__game__link', description='Game link')
    def get_game_link(self, obj):
        return obj.turn.game.link

    @admin.display(ordering='turn__number', description='Turn')
    def get_turn_number(self, obj):
        return obj.turn.number

    @admin.display(ordering='share__name', description='Share')
    def get_share_name(self, obj):
        return obj.share.name

class ForecastAdmin(admin.ModelAdmin):
    pass


admin.site.register(Game, GameAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Turn, TurnAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(Forecast, ForecastAdmin)