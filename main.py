import API_KEY as key
import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Welcome to TraveLater! Are you a tourist or a business owner?\n/1 For Tourists \n/2 For Business Owners")

def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Type /start to get started and we will take care of the rest!')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def tourist_step_1(update, context):
    """The /1 command"""
    update.message.reply_text("Hello traveller! Do you have any specific holiday destinations in mind?\n/1 Yes\n/2 No")

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(key.API_KEY)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("1", tourist_step_1))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()