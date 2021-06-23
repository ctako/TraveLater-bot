import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

USERTYPE, DESTINATION1, REGION, DESTINATION2, ITINERARY = range(5)

def start(update: Update, _: CallbackContext) -> int:
    reply_keyboard = [["Tourist", "Business Owner"]]

    update.message.reply_text(
        "Welcome to TraveLater! Are you a tourist or a business owner?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return USERTYPE

def usertype(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("%s", update.message.text)
    reply_keyboard = [["Yes", "No"]]

    update.message.reply_text(
        "Hello traveller! Do you have any specific holiday destinations in mind?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return DESTINATION1

def destination1(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("%s", update.message.text)
    reply_keyboard = [["Africa"], ["Asia"], ["Australia"], ["Europe"], ["North America"],
                      ["South America"],["Recommend something for me"]]

    update.message.reply_text(
        "No worries! Do you have a region that you want to visit?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return REGION

def region(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("%s", update.message.text)
    reply_keyboard = [["Bali", "Egypt", "Japan", "San Francisco", "Switzerland"]]

    update.message.reply_text(
        "Here are some trending holiday destinations among our users!",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return DESTINATION2

def destination2(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("%s", update.message.text)
    reply_keyboard = [["Select this itinerary", "Find out more", "Show me another itinerary"]]

    update.message.reply_text(
        "Here is the most popular itinerary among our users that have visited the country:"
        "\n"
        "\nBest of Switzerland"
        "\nExperience all of Switzerland as you visit places from farms to the urban city!",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return ITINERARY

def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main() -> None:
    updater = Updater("1812880044:AAF2Yjx5HopPKZu35TM5xO_dx096qJJUB8w")

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERTYPE: [MessageHandler(Filters.regex("^(Tourist|Business Owner)$"), usertype)],
            DESTINATION1: [MessageHandler(Filters.regex("^(Yes|No)$"),
                                          destination1)],
            REGION: [MessageHandler(Filters.regex("^(Africa|Asia|Australia|Europe|North America|"
                                                        "South America|Recommend something for me)$"),
                                    region)],
            DESTINATION2: [MessageHandler(Filters.regex("^(Bali|Egypt|Japan|San Francisco|Switzerland)$"),
                                          destination2)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()

