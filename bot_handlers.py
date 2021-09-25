import logging
import requests
import os
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from CoinDBClass import CoinDB, COINS_WEBSITES

CRYPTO_GROUP_ID = int(os.environ['CRYTO_GROUP_CHAT_ID'])

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def show_one_coin(update: Update, context: CallbackContext) -> None:
    """
    If the group is correct, the bot will show one coin.
    This is the function called when using 'supwith' comand followed by some coin symbol (DOGE)
    and optionally a currency symbol (AUD).
    """
    logger.info(f"Showing one coin: {context.args}")
    chat_id = update.message.chat_id
    if chat_id == CRYPTO_GROUP_ID:
        update.message.reply_text("WRONG GROUP BRUH")
        return
    else:
        # Create CoinDB and parse the message
        try:
            cdb = CoinDB()
        except requests.exceptions.HTTPError as e:
            update.message.reply_text(
                e.response.text,
                parse_mode=ParseMode.HTML)
            return
        try:
            coin_symbol = context.args[0]
            try:
                converting_coin_symbol = context.args[1]
                update.message.reply_text(
                    cdb.get_coin_data(coin_symbol.upper(), some_currency_symbol=converting_coin_symbol),
                    parse_mode=ParseMode.HTML)
                return
            except (IndexError, ValueError) as E:
                logger.error(E)
                update.message.reply_text(cdb.get_coin_data(coin_symbol.upper()), parse_mode=ParseMode.HTML)
                return
        except (IndexError, ValueError) as E:
            logger.error(E)
            update.message.reply_text('F**k you doing? just tell me the symbol')
        except (KeyError) as E:
            logger.error(E)
            update.message.reply_text('I dont know this coin man...')


def show_multiple_coins(update: Update, context: CallbackContext) -> None:
    """
    Basically, this function does what the previous one does but for multiple coins ('supwithallthose' command).
    """
    chat_id = update.message.chat_id
    if chat_id == CRYPTO_GROUP_ID:
        update.message.reply_text("WRONG GROUP BRUH")
        return
    else:
        try:
            cdb = CoinDB()
        except requests.exceptions.HTTPError as e:
            update.message.reply_text(
                e.response.text,
                parse_mode=ParseMode.HTML)
            return
        try:
            coin_symbols = context.args[0].split(',')
            for symbol in coin_symbols:
                if not cdb.you_know_this(symbol.upper()):
                    continue
                try:
                    converting_coin_symbol = context.args[1]
                    update.message.reply_text(
                        cdb.get_coin_data(symbol.upper(), some_currency_symbol=converting_coin_symbol),
                        parse_mode=ParseMode.HTML)
                except (IndexError, ValueError):
                    update.message.reply_text(cdb.get_coin_data(symbol.upper()), parse_mode=ParseMode.HTML)
        except (IndexError, ValueError):
            update.message.reply_text(f"something went wrong with this")


def market_notification(update: Update, context: CallbackContext) -> None:
    """
    Creates a message including the top/worst performers in the past 24 hrs. ('updateme' command).
    """
    try:
        currency_symbol = context.args[0].lower()
        if currency_symbol and currency_symbol != 'usd' and currency_symbol != 'aud':
            try:
                message = '\n\n'.join(CoinDB.get_10m_notification_message(currency_symbol.upper()))
            except requests.exceptions.HTTPError as e:
                update.message.reply_text(
                    e.response.text,
                    parse_mode=ParseMode.HTML)
                return
        elif currency_symbol == 'aud':
            try:
                message = '\n\n'.join(CoinDB.get_10m_notification_message(currency_symbol.upper())) + \
                          "\n\n<b>You mean 🪃?</b>"
            except requests.exceptions.HTTPError as e:
                update.message.reply_text(
                    e.response.text,
                    parse_mode=ParseMode.HTML)
                return
        else:
            try:
                message = '\n\n'.join(CoinDB.get_10m_notification_message()) + \
                          "\n\n<b>WHY USD IF ITS THE DEFAULT?! 🤦🏻‍</b>"
            except requests.exceptions.HTTPError as e:
                update.message.reply_text(
                    e.response.text,
                    parse_mode=ParseMode.HTML)
                return
    except (IndexError, ValueError):
        try:
            message = '\n\n'.join(CoinDB.get_10m_notification_message())
        except requests.exceptions.HTTPError as e:
            update.message.reply_text(
                e.response.text,
                parse_mode=ParseMode.HTML)
            return
    context.bot.send_message(
        update.message.chat_id,
        f"{message}",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


def help_msg(update: Update, context: CallbackContext) -> None:
    """
    creates a string for the 'helpme' command.
    """
    message = "Waddap fhaka I'm here to update you on 💰 changes.\n\n" \
              "<a>/supwith</a> CoinSymbol - will return the current coin's USD price.\n" \
              "<a>/updateme</a> {currency_symbol} - will send back all the coins that had a +-10% change (or more), over the past 24 Hours.\n" \
              "<a>/supwithallthose</a> - followed by comma separated {COIN_SYMBOLS} and an optional {FIAT_CURRENCY} will return the list of coin's USD Price and info (or converted).\n" \
              "<a>/updateme</a> - followed by an optional {FIAT_CURRENCY}, will send back all the coins that had a +-10% change (or more), over the past 24 Hours(or converted).\n" \
              "<a>/whatchaknow</a> - get a list of supported coins\n" \
              "<a>/help</a> - displays some data and commands" \
              "\n\n\nSee ya!"
    context.bot.send_message(
        update.message.chat_id,
        f"{message}",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


def get_supported_coins(update: Update, context: CallbackContext) -> None:
    logger.info("Getting supported coins")
    message = "Those are all the coins I'm familiar with:\n"
    coins = CoinDB().get_supported_symbols()
    message += '\n'.join(
        [f'{k} - <a href="{COINS_WEBSITES.get(k) if COINS_WEBSITES.get(k) else ""}">{v.get("name")}</a>' for (k, v)
         in coins.items()])
    context.bot.send_message(
        update.message.chat_id,
        message,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )
