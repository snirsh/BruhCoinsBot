import requests

from CoinDBClass import CoinDB
import os
import logging

from telegram import ParseMode, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CRYPTO_DAILY_UPDATED_BOT_TOKEN = os.environ['CRYPTO_DAILY_BRUH_BOT_API_TOKEN']
CRYPTO_GROUP_ID = int(os.environ['CRYTO_GROUP_CHAT_ID'])


def market_notification_evening(bot):
    try:
        message = '\n\n\n'.join(CoinDB.get_10m_notification_message())
    except requests.exceptions.HTTPError as e:
        bot.send_message(
            e.response.text,
            parse_mode=ParseMode.HTML)
        return
    bot.send_message(
        CRYPTO_GROUP_ID,
        f"{message}",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


def help_msg(update: Update, context: CallbackContext) -> None:
    message = "I just tell you whats up daily... just leave me alone! 🙄"
    context.bot.send_message(
        update.message.chat_id,
        f"{message}",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


def main() -> None:
    updater = Updater(CRYPTO_DAILY_UPDATED_BOT_TOKEN)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("help", help_msg))
    from datetime import datetime
    if datetime.utcnow().hour in [6, 7, 8]:
        market_notification_evening(dispatcher.bot)
    else:
        logger.error("WRONG TIME TO POST!")


if __name__ == '__main__':
    main()
