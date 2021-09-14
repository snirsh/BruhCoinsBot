from CoinDBClass import CoinDB, COINS_WEBSITES
import os
import logging
import time
import requests
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

"""
Secrets, Tokens, etc.
"""
API_TOKEN_TELEGRAM = os.environ['API_TOKEN_TELEGRAM']
CRYPTO_GROUP_ID = int(os.environ['CRYTO_GROUP_CHAT_ID'])


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def show_one_coin(update: Update, context: CallbackContext) -> None:
    """
    If the group is correct, the bot will show one coin.
    This is the function called when using 'supwith' comand followed by some coin symbol (DOGE)
    and optionally a currency symbol (AUD).
    """
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
            except (IndexError, ValueError):
                update.message.reply_text(cdb.get_coin_data(coin_symbol.upper()), parse_mode=ParseMode.HTML)
                return
        except (IndexError, ValueError):
            update.message.reply_text('F**k you doing? just tell me the symbol')
        except (KeyError):
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
                          "\n\n<b>WHY USD IF ITS THE DEFAULT?! U CRAZY FAHK 🤦🏻‍</b>"
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
    message = "Waddap fhaka I'm here to update you on 💰 changes.\n\n<a>/supwith</a> CoinSymbol - will return the " \
              "current coin's USD price.\n<a>/updateme</a> {currency_symbol} - will send back all the coins that had a +-10% change (or " \
              "more), over the past 24 Hours.\n\n\nSee ya! "
    context.bot.send_message(
        update.message.chat_id,
        f"{message}",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

def get_supported_coins(update: Update, context: CallbackContext) -> None:
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

def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(API_TOKEN_TELEGRAM)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("supwith", show_one_coin))
    dispatcher.add_handler(CommandHandler("supwithallthose", show_multiple_coins))
    dispatcher.add_handler(CommandHandler("updateme", market_notification))
    dispatcher.add_handler(CommandHandler("whatchaknow", get_supported_coins))
    dispatcher.add_handler(CommandHandler("help", help_msg))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
