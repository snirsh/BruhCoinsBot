from CoinDBClass import CoinDB
import os
import logging
import time

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

API_TOKEN_TELEGRAM = os.environ['API_TOKEN_TELEGRAM']
CRYPTO_GROUP_ID = int(os.environ['CRYTO_GROUP_CHAT_ID'])


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')


def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    if chat_id != CRYPTO_GROUP_ID:
        update.message.reply_text("WRONG GROUP BRUH")
        return
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

        text = 'Timer successfully set!'
        if job_removed:
            text += ' Old one was removed.'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)


def show_market(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if chat_id == CRYPTO_GROUP_ID:
        update.message.reply_text("WRONG GROUP BRUH")
        return
    else:
        cdb = CoinDB()
        try:
            coin_symbol = context.args[0]
            update.message.reply_text(cdb.get_coin_data(coin_symbol.upper()))
        except (IndexError, ValueError):
            update.message.reply_text('Fuck you doing? just tell me the symbol')
        except (KeyError):
            update.message.reply_text('I dont know this coin man...')


def market_notification_10m(bot):
    while True:
        message = '\n\n\n'.join(CoinDB.get_10m_notification_message())
        bot.send_message(
            CRYPTO_GROUP_ID,
            f"{message}",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        time.sleep(86400)


def market_notification(update: Update, context: CallbackContext) -> None:
    try:
        if context.args[0].lower() == 'boomerangs':
            message = '\n\n'.join(CoinDB.get_10m_notification_message(True))
        else:
            message = '\n\n'.join(CoinDB.get_10m_notification_message())
    except (IndexError, ValueError):
        message = '\n\n'.join(CoinDB.get_10m_notification_message())
    context.bot.send_message(
        update.message.chat_id,
        f"{message}",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


def help_msg(update: Update, context: CallbackContext) -> None:
    message = "Waddap fhaka I'm here to update you on 💰 changes.\n\n<a>/supwith</a> CoinSymbol - will return the " \
              "current coin's USD price.\n<a>/updateme</a> - will send back all the coins that had a +-10% change (or "\
              "more), over the past 24 Hours.\n\n\nSee ya! "
    context.bot.send_message(
        update.message.chat_id,
        f"{message}",
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
    dispatcher.add_handler(CommandHandler("supwith", show_market))
    dispatcher.add_handler(CommandHandler("UPDATEME", market_notification))
    dispatcher.add_handler(CommandHandler("help", help_msg))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()

    market_notification_10m(dispatcher.bot)
    ###### EXAMPLES ######
    # dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(CommandHandler("help", start))
    # dispatcher.add_handler(CommandHandler("set", set_timer))
    # dispatcher.add_handler(CommandHandler("unset", unset))


if __name__ == '__main__':
    main()
