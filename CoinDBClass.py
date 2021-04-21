import requests


class CoinDB:
    def __init__(self):
        self._json = requests.get('http://api.coincap.io/v2/assets').json().get('data')
        self.coins = {coin_dict.get('symbol'): coin_dict for coin_dict in self._json}

    def refresh(self):
        self._json = requests.get('http://api.coincap.io/v2/assets').json().get('data')
        self.coins = {coin_dict.get('symbol'): coin_dict for coin_dict in self._json}

    def get_coin_data(self, symbol):
        # TODO: Pretty print the data:
        return self.coins[symbol]

    def get_price_usd(self, symbol):
        return round(float(self.get_coin_data(symbol).get('priceUsd')), 2)

    def get_change_24hr(self, symbol):
        return round(float(self.get_coin_data(symbol).get('changePercent24Hr')), 2)

    @staticmethod
    def get_10m_notification_message() -> str:
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
            messages.append(f"<b>Showing data for: {coin.symbol} | {coin.name}</b>\n<b>Current price</b> ${coin.priceUsd} || <b>Coin change (Past 24Hrs)</b> {coin.changePercent24Hr}%")
        return messages


class CoinClass:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            if k in ['priceUsd', 'changePercent24Hr']:
                setattr(self, k, round(float(v), 2))
            else:
                setattr(self, k, v)

print('\n\n'.join(CoinDB().get_10m_notification_message()))
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
