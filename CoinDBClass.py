import requests
from currency_converter import CurrencyConverter


class CoinDB:
    def __init__(self):
        self._json = requests.get('http://api.coincap.io/v2/assets').json().get('data')
        self.coins = {coin_dict.get('symbol'): coin_dict for coin_dict in self._json}

    def refresh(self):
        self._json = requests.get('http://api.coincap.io/v2/assets').json().get('data')
        self.coins = {coin_dict.get('symbol'): coin_dict for coin_dict in self._json}

    def get_coin_data(self, symbol, some_currency_symbol=None):
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
            message = f'<a href="{coin.explorer}">{symbol_and_name}</a> <u>{price_tag}</u> \nPast 24Hrs: <u>{coin.changePercent24Hr}%</u>\n'
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

    def get_price_usd(self, symbol):
        return round(float(self.get_coin_data(symbol).get('priceUsd')), 2)

    def get_change_24hr(self, symbol):
        return round(float(self.get_coin_data(symbol).get('changePercent24Hr')), 2)

    @staticmethod
    def get_10m_notification_message(some_currency_symbol=None) -> str:
        # TODO: CREATE MESSAGE EVERY 10M
        db = CoinDB()
        messages = []
        coins = []
        for coin_dict in db.coins.values():
            coin = CoinClass(coin_dict)
            coins.append(coin)
        coins.sort(key=lambda c: abs(c.changePercent24Hr), reverse=True)
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
            messages.append(f'<a href="{coin.explorer}">{symbol_and_name}</a> <u>{price_tag}</u> \nPast 24Hrs: <u>{coin.changePercent24Hr}%</u>')
        return messages


class CoinClass:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            if k in ['priceUsd', 'changePercent24Hr', 'marketCapUsd', 'volumeUsd24Hr']:
                setattr(self, k, round(float(v), 2))
            else:
                setattr(self, k, v)

# print('\n\n'.join(CoinDB.get_10m_notification_message(some_currency_symbol='eur')))
######
# assets_request_response = requests.get('http://api.coincap.io/v2/assets')
#
# for coin_dict in assets_request_response.json().get('data'):
#     coin_name = coin_dict.get('name')
#     coin_symbol = coin_dict.get('symbol')
#     coin_price_usd = coin_dict.get('priceUsd')
#     coin_change_pct_24hr = coin_dict.get('changePercent24Hr')
#     print("#########################################################")
#     print(f"{coin_symbol} - {coin_name}")
#     print(f"Current price ${round(float(coin_price_usd), 2)}")
#     print(f"Coin change (Past 24Hrs) {round(float(coin_change_pct_24hr), 2)}%")
#     print(coin_dict)
# print(CoinDB().get_coin_data('BTC', 'usd'))