# -*- coding: UTF-8 -*-

from calculator.models import Share

class PaycheckCalculator(object):

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
        