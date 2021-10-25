import json
import math
import os
from binance import Client
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Message


API_KEY = os.environ.get('API_KEY', False)
SECRET_KEY = os.environ.get('SECRET_KEY', False)
PASSWORD = os.environ.get('PASSWORD', False)

SIDE_BUY = 'buy'
SIDE_SELL = 'sell'


def round_down(number: float, decimals: int = 2):
    num = float(number)
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.floor(num)

    factor = 10 ** decimals
    return math.floor(num * factor) / factor


def get_symbol_from_pair(pair):
    if 'USDT' in pair:
        pair = pair.replace('USDT', '')
    return pair


@csrf_exempt
def message_create(request):
    message = json.loads(request.body.decode('utf-8'))

    if message['password'] != PASSWORD:
        return JsonResponse({'error': 'wrong password'})

    action = Message.objects.create(
        ticker=message['ticker'],
        action=message['action'],
        message=json.dumps(message)
    )

    trade = Trade(action)
    result = trade.execute()

    action.result = json.dumps(result)
    action.result_at = timezone.now()
    action.save()

    return JsonResponse(message, safe=False)


class Trade():
    amount = 100

    def __init__(self, action):
        self.ticker = action.ticker

        if action.action == 'sell':
            self.side = SIDE_SELL
        else:
            self.side = SIDE_BUY

        self.client = Client(API_KEY, SECRET_KEY)

    def get_account_balance(self):
        return Decimal(self.client.get_asset_balance('USDT').get('free'))

    def get_amount(self):
        balance = self.get_account_balance()
        if balance < Decimal(100):
            return balance
        else:
            return self.amount

    def execute(self):
        if self.side == SIDE_BUY:
            return self.buy(self.ticker)
        if self.side == SIDE_SELL:
            return self.sell(self.ticker)

    def buy(self, pair):
        order = self.client.order_market_buy(
            symbol=pair,
            quoteOrderQty=self.get_amount()
        )
        return order

    def sell(self, pair):
        asset_balance = self.client.get_asset_balance(get_symbol_from_pair(pair)).get('free')

        tick = None
        amount = None
        info = self.client.get_symbol_info(pair)
        for filt in info['filters']:
            if filt['filterType'] == 'LOT_SIZE':
                tick = filt['stepSize']
                break

        if tick.startswith("0"):
            amount = round_down(asset_balance, tick.find("1") - 1)
        elif tick.startswith("1"):
            amount = round_down(asset_balance, 0)

            order = self.client.order_market.sell(
                symbol=pair,
                quantity=amount
            )
            return order
