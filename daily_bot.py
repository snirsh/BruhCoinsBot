from bot_handlers import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CRYPTO_DAILY_UPDATED_BOT_TOKEN = os.environ['CRYPTO_DAILY_BRUH_BOT_API_TOKEN']
if not os.environ.get("DEV"):
    CRYPTO_GROUP_ID = int(os.environ['CRYTO_GROUP_CHAT_ID'])
else:
    CRYPTO_GROUP_ID = int(os.environ['DEV_GROUP'])


def daily_market_notification(bot):
    try:
        message = '\n\n'.join(CoinDB.get_10m_notification_message())
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


def daily_help_msg(update: Update, context: CallbackContext) -> None:
    message = "I just tell you whats up daily... just leave me alone! 🙄"
    logger.info(update.message.chat_id)
    context.bot.send_message(
        update.message.chat_id,
        f"{message}",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


def daily_check_coin(update: Update, context: CallbackContext) -> None:
    coins = CoinDB().get_supported_symbols()
    message = '\n'.join(
        [f'{k} - <a href="{COINS_WEBSITES.get(k) if COINS_WEBSITES.get(k) else ""}">{v.get("name")}</a>' for (k, v) in
         coins.items()])
    if not os.environ.get("DEV"):
        return
    logger.info("Checking coin")
    logger.info(update.message)
    context.bot.send_message(
        update.message.chat_id,
        f""
        f'{message}',
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


def main() -> None:
    updater = Updater(CRYPTO_DAILY_UPDATED_BOT_TOKEN)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("help", daily_help_msg))
    from datetime import datetime
    if os.environ.get('DEV'):
        dispatcher.add_handler(CommandHandler("checkcoin", daily_check_coin))
        daily_market_notification(dispatcher.bot)
        updater.start_polling()
        updater.idle()
    else:
        if datetime.utcnow().hour in [6, 7, 8]:
            daily_market_notification(dispatcher.bot)
        else:
            logger.error("WRONG TIME TO POST!")


if __name__ == '__main__':
    main()
