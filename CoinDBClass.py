import os
from enum import Enum
import requests
from shrimpy import ShrimpyApiClient
from currency_converter import CurrencyConverter
import re


class DB_SOURCE_TYPE(Enum):
    CoinCap = 0
    Shrimpy = 1


class CoinDB:
    TYPE: DB_SOURCE_TYPE = DB_SOURCE_TYPE.CoinCap

    def __init__(self):
        """
        create the coinDB using Coincap API.
        """
        response_coincap = requests.get('http://api.coincap.io/v2/assets')
        if response_coincap.status_code is 200:
            _json = response_coincap.json().get('data')
            self.coins = {coin_dict.get('symbol'): coin_dict for coin_dict in _json}
        else:
            self.__shrimpy_init()

    def __shrimpy_init(self):
        self.TYPE = DB_SOURCE_TYPE.Shrimpy
        public_key = os.environ['SHRIMPY_PUB']
        secret_key = os.environ['SHRIMPY_SEC']

        self._shrimpy = ShrimpyApiClient(public_key, secret_key)
        self._shrimpy_ticker = self._shrimpy.get_ticker('binance')

        self.coins = {coin_dict.get('symbol'): coin_dict for coin_dict in self._shrimpy_ticker}

    def get_coin_data(self, symbol, some_currency_symbol=None) -> str:
        """
        This function creates the CoinClass structure and parses the data to be representable.
        :param symbol: BTC, ETH, XRP, DOGE(TO THE MOON) etc.
        :param some_currency_symbol: USD, ILS, etc.
        :return: A string containing a rich text representation of the data.
        """
        try:
            coin = CoinClass(self.coins[symbol])
            if coin.symbol == coin.name:
                symbol_and_name = f"{coin.name}"
            else:
                symbol_and_name = f"{coin.symbol} | {coin.name}"
            price_tag = f"${coin.priceUsd}"
            try:
                if some_currency_symbol and some_currency_symbol.lower() != 'usd':
                    currency = some_currency_symbol
                    custom_symbol = some_currency_symbol
                    if some_currency_symbol.lower() == "boomerangs":
                        currency = "AUD"
                        custom_symbol = "🪃"
                    try:
                        price_tag = f"{round(CurrencyConverter().convert(coin.priceUsd, 'USD', currency.upper()), 2)} {custom_symbol.upper()}"
                    except ValueError:
                        price_tag = f"${coin.priceUsd}"
            except ValueError:
                price_tag = f"${coin.priceUsd}"
            if self.TYPE is DB_SOURCE_TYPE.CoinCap:
                message = f'<a href="{coin.explorer}">{symbol_and_name}</a> <u>{price_tag}</u> \nPast 24Hrs: <u>{coin.changePercent24Hr}%</u>\n'
            else:
                message = f'<b>{symbol_and_name}</b> <u>{price_tag}</u> \nPast 24Hrs: <u>{coin.percentChange24hUsd}%</u>\n'
            if self.TYPE is DB_SOURCE_TYPE.CoinCap:
                if some_currency_symbol:
                    try:
                        message += f"<b>Market Cap:</b> <u>{'{:,.2f}'.format(round(CurrencyConverter().convert(coin.marketCapUsd, currency.upper()), 2))} {custom_symbol.upper()}</u> | <b>24Hr Volume:</b> <u>{'{:,.2f}'.format(round(CurrencyConverter().convert(coin.volumeUsd24Hr, currency.upper()), 2))} {custom_symbol.upper()}</u>"
                    except ValueError:
                        message += f"<b>Market Cap:</b> <u>${'{:,.2f}'.format(coin.marketCapUsd)}</u> | <b>24Hr Volume:</b> <u>${'{:,.2f}'.format(coin.volumeUsd24Hr)}</u>"
                else:
                    message += f"<b>Market Cap:</b> <u>${'{:,.2f}'.format(coin.marketCapUsd)}</u> | <b>24Hr Volume:</b> <u>${'{:,.2f}'.format(coin.volumeUsd24Hr)}</u>"
            return message
        except KeyError:
            raise KeyError

    """
    Getters:
    get_price_usd
    get_change_24hr
    you_know_this: do you know this coin or nah
    """

    def get_price_usd(self, symbol) -> float:
        return round(float(self.get_coin_data(symbol).get('priceUsd')), 2)

    def get_change_24hr(self, symbol) -> float:
        return round(float(self.get_coin_data(symbol).get('changePercent24Hr')), 2)

    def you_know_this(self, coin_symbol) -> bool:
        """
        :param coin_symbol: BTC, ETH, DOGE, etc.
        :return: BOOL: checks if the coin symbol is in our coin dict keys.
        """
        return coin_symbol.upper() in self.coins.keys()

    """
    Static methods:
    get_10m_notification_message: A notification with the best/worst performers
    """

    @staticmethod
    def get_10m_notification_message(some_currency_symbol=None) -> str:
        """
        This method creates a nice string that includes the notification message that we want
        :param some_currency_symbol: i.e USD, EU, AUD, ILS, etc.
        :return: A string representation of the Telegram response message that we want to show the client
        """
        db = CoinDB()
        messages = []
        coins = []
        for coin_dict in db.coins.values():
            coin = CoinClass(coin_dict)
            coins.append(coin)
        coins.sort(key=lambda c: c.changePercent24Hr, reverse=True)
        coins = list(filter(lambda c: abs(c.changePercent24Hr) > 10, coins))
        for coin in coins:
            if coin.symbol == coin.name:
                symbol_and_name = f"{coin.name}"
            else:
                symbol_and_name = f"{coin.symbol} | {coin.name}"
            price_tag = f"${coin.priceUsd}"
            if some_currency_symbol:
                currency = some_currency_symbol
                custom_symbol = some_currency_symbol
                if some_currency_symbol.lower() == "boomerangs":
                    currency = "AUD"
                    custom_symbol = "🪃"
                elif some_currency_symbol.lower() == 'usd':
                    custom_symbol = "$"
                try:
                    price_tag = f"{round(CurrencyConverter().convert(coin.priceUsd, 'USD', currency.upper()), 2)} {custom_symbol.upper()}"
                except ValueError:
                    price_tag = f"${coin.priceUsd}"
            if db.TYPE is DB_SOURCE_TYPE.CoinCap:
                messages.append(
                    f'<a href="{coin.explorer}">{symbol_and_name}</a> <u>{price_tag}</u> \nPast 24Hrs: <u>{coin.changePercent24Hr}%</u>')
            else:
                messages.append(
                    f'<b>{symbol_and_name}</b> <u>{price_tag}</u> \nPast 24Hrs: <u>{coin.changePercent24Hr}%</u>')
        return messages


class CoinClass:
    """
    A Class that is generated from the JSON that we've received in the above class.
    Very straight forward using dictionary and key value pairs.
    """

    def __init__(self, dictionary):
        for k, v in dictionary.items():
            if k == "percentChange24hUsd":
                k = "changePercent24Hr"
            if type(v) is int or type(v) is float or re.match(r'^-?\d+(?:\.\d+)?$', v):
                setattr(self, k, round(float(v), 2))
            else:
                setattr(self, k, v)
