"""
Testing and demo commands
"""
from CoinDBClass import CoinDB
import requests


def demo_db_repr():
    print('\n\n'.join(CoinDB.get_10m_notification_message(some_currency_symbol='eur')))
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

