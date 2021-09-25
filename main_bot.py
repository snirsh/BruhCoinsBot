from bot_handlers import *

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

"""
Secrets, Tokens, etc.
"""
API_TOKEN_TELEGRAM = os.environ['API_TOKEN_TELEGRAM']


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
