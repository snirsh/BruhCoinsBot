import os
from enum import Enum
import requests
from shrimpy import ShrimpyApiClient
from currency_converter import CurrencyConverter
import re

COINS_WEBSITES = \
        {'BTC': 'https://blockchain.info/',
         'ETH': 'https://etherscan.io/',
         'BNB': 'https://etherscan.io/token/0xB8c77482e45F1F44dE1745F52C74426C631bDD52',
         'ADA': 'https://cardanoexplorer.com/',
         'USDT': 'https://www.omniexplorer.info/asset/31',
         'XRP': 'https://xrpcharts.ripple.com/#/graph/',
         'DOGE': 'http://dogechain.info/chain/Dogecoin',
         'USDC': 'https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
         'DOT': 'https://polkascan.io/polkadot',
         'SOL': 'https://explorer.solana.com/',
         'UNI': 'https://etherscan.io/token/0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',
         'LINK': 'https://etherscan.io/token/0x514910771af9ca656af840dff83e8264ecf986ca',
         'BCH': 'https://blockchair.com/bitcoin-cash/blocks',
         'LTC': 'http://explorer.litecoin.net/chain/Litecoin',
         'BUSD': 'https://etherscan.io/token/0x4Fabb145d64652a948d72533023f6E7A623C7C53',
         'MATIC': 'https://etherscan.io/token/0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0',
         'ETC': 'http://gastracker.io/',
         'LUNA': 'https://finder.terra.money/',
         'XLM': 'https://dashboard.stellar.org/',
         'WBTC': 'https://etherscan.io/token/0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
         'VET': 'https://explore.veforge.com/',
         'ICP': 'https://www.dfinityexplorer.org/#/',
         'THETA': 'https://etherscan.io/token/0x3883f5e181fccaF8410FA61e12b59BAd963fb645',
         'FIL': 'https://protocol.ai',
         'TRX': 'https://tronscan.org/#/',
         'DAI': 'https://etherscan.io/token/0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359',
         'AAVE': 'https://etherscan.io/token/0x80fB784B7eD66730e8b1DBd9820aFD29931aab03',
         'EOS': 'https://bloks.io/',
         'XMR': 'http://moneroblocks.info/',
         'FTT': 'https://etherscan.io/token/0x50d1c9771902476076ecfc8b2a83ad6b9355a4c9',
         'KLAY': 'https://scope.klaytn.com/blocks',
         'CAKE': 'https://bscscan.com/token/0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82',
         'GRT': 'https://etherscan.io/token/0xc944e90c64b2c07662a292be6244bdf05cda44a7',
         'NEO': 'https://neotracker.io',
         'AXS': 'https://etherscan.io/token/0xf5d669627376ebd411e34b98f19c868c8aba5ada',
         'ATOM': 'https://www.mintscan.io/',
         'CRO': 'https://etherscan.io/token/0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b',
         'MKR': 'https://etherscan.io/token/Maker',
         'BTCB': 'https://explorer.binance.org/asset/BTCB-1DE',
         'SHIB': 'https://etherscan.io/token/0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce',
         'AVAX': 'https://avascan.info/',
         'BSV': 'https://bsvexplorer.io/',
         'XTZ': 'https://tzkt.io/',
         'MIOTA': 'https://thetangle.org/',
         'ALGO': 'https://algoexplorer.io/',
         'BTT': 'https://tronscan.org/#/token/1002000',
         'LEO': 'https://etherscan.io/token/0x2af5d2ad76741191d15dfe7bf6ac92d4bd912ca3',
         'COMP': 'https://etherscan.io/token/0xc00e94cb662c3520282e6f5717214004a7f26888',
         'EGLD': 'https://explorer.elrond.com/',
         'AMP': None,
         'WAVES': 'http://wavesexplorer.com/',
         'KSM': 'https://kusama.subscan.io/',
         'HT': 'https://etherscan.io/token/0x6f259637dcd74c767781e37bc6133cd6a68aa161',
         'HBAR': 'https://hash-hash.info/',
         'DCR': 'https://mainnet.decred.org/',
         'CHZ': 'https://etherscan.io/token/0x3506424f91fd33084466f402d5d97f05f8e3b4af',
         'UST': 'https://finder.terra.money/',
         'DASH': 'https://explorer.dash.org',
         'RUNE': 'https://explorer.binance.org/asset/RUNE-B1A',
         'FEI': 'https://etherscan.io/token/0x956F47F50A910163D8BF957Cf5846D573E7f87CA',
         'HOT': 'https://etherscan.io/token/0x6c6ee5e31d828de241282b9606c8e98ea48526e2',
         'XEM': 'http://nembex.nem.ninja/',
         'TFUEL': 'https://explorer.thetatoken.org/',
         'ZEC': 'https://explorer.zcha.in/',
         'QNT': 'https://etherscan.io/token/0x4a220e6096b25eadb88358cb44068a3248254675',
         'CCXX': 'https://ccxxblocks.counos.org/',
         'HNT': 'https://explorer.helium.com/',
         'XDC': 'https://etherscan.io/token/0x41ab1b6fcbb2fa9dced81acbdec13ea6315f2bf2',
         'MANA': 'https://etherscan.io/token/decentraland',
         'SUSHI': 'https://etherscan.io/token/0x6b3595068778dd592e39a122f4f5a5cf09c90fe2',
         'NEAR': 'https://explorer.near.org/',
         'YFI': 'https://etherscan.io/token/0x0bc529c00c6401aef6d220be8c6ea1667f6ad93e',
         'SNX': 'https://etherscan.io/token/0xc011a72400e58ecd99ee497cf89e3775d4bd732f',
         'CEL': 'https://etherscan.io/token/0xaaaebe6fe48e54f431b0c390cfaf0b017d09d42d',
         'ENJ': 'https://etherscan.io/token/0xf629cbd94d3791c9250152bd8dfbdf380e2a3b9c',
         'RVN': 'https://ravencoin.network/',
         'QTUM': 'https://qtum.info/',
         'OKB': 'https://etherscan.io/token/0x75231f58b43240c9718dd58b4967c5114342a86c',
         'ZIL': 'https://etherscan.io/token/0x05f4a42e251f2d52b8ed15e9fedaacfcef1fad27',
         'TUSD': 'https://etherscan.io/token/0x8dd5fbce2f6a956c3022ba3663759011dd51e73e',
         'BAT': 'https://etherscan.io/token/Bat',
         'BTG': 'https://explorer.bitcoingold.org/insight/',
         'ONE': 'https://explorer.harmony.one',
         'TEL': 'https://etherscan.io/token/0x85e076361cc813a908ff672f9bad1541474402b2',
         'NEXO': 'https://etherscan.io/token/0xb62132e35a6c13ee1ee0f84dc5d40bad8d815206',
         'FTM': 'https://etherscan.io/token/0x4e15361fd6b4bb609fa63c81a2be19d873717870',
         'DGB': 'https://digiexplorer.info/',
         'BNT': 'https://etherscan.io/token/Bancor',
         'ONT': 'https://explorer.ont.io/',
         'SC': 'http://explore.sia.tech/',
         'SAFEMOON': 'https://www.bscscan.com/token/0x8076c74c5e3f5852037f31ff0093eeb8c8add8d3',
         'ZRX': 'https://etherscan.io/token/ZRX',
         'CELO': 'https://explorer.celo.org/blocks',
         'ICX': 'https://tracker.icon.foundation/',
         'NANO': 'https://nano.org/en/explore/',
         'MDX': 'https://hecoinfo.com/token/0x25d2e80cb6b86881fd7e07dd263fb79f4abe033c',
         'IOTX': 'https://etherscan.io/token/0x6fb3e0a217407efff7ca062d46c26e5d60a14d69',
         'CRV': 'https://etherscan.io/token/0xD533a949740bb3306d119CC777fa900bA034cd52',
         'DFI': 'http://explorer.defichain.io/',
         'ZEN': 'https://explorer.zensystem.io/'
         }

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
        if response_coincap.status_code == 200:
            _json = response_coincap.json().get('data')
            self.coins = {coin_dict.get('symbol').upper(): coin_dict for coin_dict in _json}
        else:
            self.__shrimpy_init()

    def __shrimpy_init(self) -> None:
        """
        Create the coinDB using the Shrimpy library and binance exchange.
        """
        self.TYPE = DB_SOURCE_TYPE.Shrimpy
        public_key = os.environ['SHRIMPY_PUB']
        secret_key = os.environ['SHRIMPY_SEC']

        self._shrimpy = ShrimpyApiClient(public_key, secret_key)
        supported_exchanges = self._shrimpy.get_supported_exchanges()
        self._shrimpy_ticker = self._shrimpy.get_ticker('coinbasepro')

        self.coins = {coin_dict.get('symbol').upper(): coin_dict for coin_dict in self._shrimpy_ticker}

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
                        price_tag = f"{CurrencyConverter().convert(coin.priceUsd, 'USD', currency.upper())} {custom_symbol.upper()}"
                    except ValueError:
                        price_tag = f"${coin.priceUsd}"
            except ValueError:
                price_tag = f"${coin.priceUsd}"
            message = f'<a href="{coin.explorer}">{symbol_and_name}</a> <u>{price_tag}</u> \nPast 24Hrs: <u>{round(float(coin.changePercent24Hr), 2)}%</u>\n'
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
    def get_supported_symbols() -> [str]:
        """
        Return a list with all supported coin symbols
        :return:
        """
        db = CoinDB()
        return db.coins

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
                    price_tag = f"{CurrencyConverter().convert(coin.priceUsd, 'USD', currency.upper())} {custom_symbol.upper()}"
                except ValueError:
                    price_tag = f"${coin.priceUsd}"
            if db.TYPE is DB_SOURCE_TYPE.CoinCap:
                messages.append(
                    f'<a href="{coin.explorer}">{symbol_and_name}</a> <u>{price_tag}</u> \nPast 24Hrs: <u>{round(float(coin.changePercent24Hr), 2)}%</u>')
            else:
                messages.append(
                    f'<b>{symbol_and_name}</b> <u>{price_tag}</u> \nPast 24Hrs: <u>{round(float(coin.changePercent24Hr), 2)}%</u>')
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
            if not v:
                continue
            if type(v) is int or type(v) is float or re.match(r'^-?\d+(?:\.\d+)|(?:[eE][+\-]?\d+)|(\d+)?$', v):
                setattr(self, k, float(v))
            else:
                setattr(self, k, v)
        if "explorer" not in dictionary.keys():
            if dictionary.get("symbol") and COINS_WEBSITES.get(dictionary.get("symbol")):
                setattr(self, 'explorer', COINS_WEBSITES[dictionary.get("symbol")])
            else:
                setattr(self, 'explorer', f'https://google.com/search?q={dictionary.get("symbol")}')
