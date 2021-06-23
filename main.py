import logging
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
mycol = mydb["itineraries"]
mydict = {}

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

USERTYPE, REC_DESTINATION1, BUSINESS_OPTIONS1, CUSTOM_COUNTRY, REC_REGION, \
REC_DESTINATION2, TOURIST_VIEW_ITINERARY, BUSINESS_VIEW_ITINERARY, ADD_COMPANY_NAME, ADD_REGION, \
ADD_COUNTRY, ADD_TOUR_NAME, ADD_DESCRIPTION, NEW_ITINERARY_ADDED, SHOW_ITINERARY = range(15)

def start(update: Update, _: CallbackContext) -> int:
    reply_keyboard = [["Tourist"], ["Business Owner"]]

    update.message.reply_text(
        "Hello, I am TraveLaterBot! I can recommend you tours for places that you might be interested in if you are a"
        "tourist, or help you advertise your tours if you are business owner. Are you a tourist or a business owner?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return USERTYPE

def usertype(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)

    if text == "Tourist":
        reply_keyboard = [["Yes"], ["No"]]
        update.message.reply_text(
            "Welcome traveller! Do you have any specific holiday destinations in mind?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return REC_DESTINATION1

    else:
        reply_keyboard = [["View my itineraries", "Add an itinerary"],
                          ["Edit an itinerary", "Remove an itinerary"]]
        update.message.reply_text(
            "Hello business owner! What would you like to do today?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return BUSINESS_OPTIONS1

def destination1(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)

    if text == "Yes":
        update.message.reply_text("Great! Where would you like to go?")
        return CUSTOM_COUNTRY

    else:
        reply_keyboard = [["Africa", "Asia"], ["Australia", "Europe"], ["North America",
                          "South America"], ["Recommend something for me"]]

        update.message.reply_text(
            "No worries! Do you have a region that you want to visit?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return REC_REGION

def business_options1(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    myquery = {"Username": user.username}
    text = update.message.text
    logger.info("%s", text)

    if text == "View my itineraries":
        results = mycol.find(myquery)
        results_lst = []
        for result in results:
            results_lst.append(result)

        if len(results_lst) == 0:
            reply_keyboard = [["View my itineraries", "Add an itinerary"],
                              ["Edit an itinerary", "Remove an itinerary"]]

            update.message.reply_text(
                "Currently, you do not have any itineraries saved with us. What would you like to do?",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
            )
            return BUSINESS_OPTIONS1

        else:
            outer_lst = []
            inner_lst = []
            for result in results_lst:
                tour_name = result.get("Tour name")
                if len(inner_lst) < 2:
                    inner_lst.append(tour_name)
                else:
                    outer_lst.append(inner_lst)
                    inner_lst.clear()
                    inner_lst.append(tour_name)
            outer_lst.append(inner_lst)

            reply_keyboard = outer_lst

            update.message.reply_text(
                "Which itinerary would you like to view?",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
            )
            return BUSINESS_VIEW_ITINERARY

    elif text == "Add an itinerary":
        mydict["Username"] = user.username
        update.message.reply_text("Please tell me the name of the company you belong to.")
        return ADD_COMPANY_NAME


def business_view_itinerary(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)
    s = ""
    selected_itinerary = mycol.find_one({"$and": [{"Username": user.username}, {"Tour name": text}]})
    for key in selected_itinerary:
        if key == "Username" or key == "_id":
            continue
        else:
            s += "*" + key + ":* " + selected_itinerary.get(key) + "\n"

    reply_keyboard = [["View my itineraries", "Add an itinerary"],
                      ["Edit an itinerary", "Remove an itinerary"]]
    update.message.reply_text(
        f"Here is the information we have saved on {text}. \n \n"
        f"{s} \n \n"
        f"What else would you like to do?", parse_mode= 'Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return BUSINESS_OPTIONS1

def add_company_name(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Company"] = text
    update.message.reply_text(f"Your company name is {text}. Next, please tell me the region your tour will be held in.")
    return ADD_REGION

def add_region(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Region"] = text
    update.message.reply_text(f"Your tour will be held in {text}. Next, please tell me which country your tour will be "
                              f"held in.")
    return ADD_COUNTRY

def add_country(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Country"] = text
    update.message.reply_text(f"Your tour will be held in {text}. Next, please tell me the name of your tour.")
    return ADD_TOUR_NAME

def add_tour_name(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Tour name"] = text
    update.message.reply_text(f"The name of your tour is {text}. Lastly, please give me a description of your tour.")
    return ADD_DESCRIPTION

def add_description(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Description"] = text
    s = ""
    for key in mydict:
        if key == "Username":
            continue
        else:
            s += "*" + key + ":* " + mydict.get(key) + "\n"

    reply_keyboard = [["View my itineraries", "Add an itinerary"],
                      ["Edit an itinerary", "Remove an itinerary"]]
    update.message.reply_text(
        "And you're done! Here's what you sent me. \n \n"
        f"{s} \n \n"
        f"What else would you like to do?", parse_mode= 'Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    mycol.insert_one(mydict)
    mydict.clear()
    return BUSINESS_OPTIONS1

def region(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)

    if text == "Recommend something for me":
        reply_keyboard = [["Bali", "Egypt"], ["Japan", "San Francisco"], ["Switzerland"]]

        update.message.reply_text(
            "Here are some trending holiday destinations among our users!",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return REC_DESTINATION2

    else:
        update.message.reply_text(
            f"Here are some popular destinations for {text}. You can select them to find out more!"
        )
        return REC_DESTINATION2

def destination2(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    reply_keyboard = [["Select this itinerary"], ["Find out more"], ["Show me another itinerary"]]

    update.message.reply_text(
        f"Here is the most popular itinerary among our users that have visited the {text}:"
        "\n"
        f"\nBest of {text}"
        f"\nExperience all of {text} as you visit places from farms to the urban city!",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return TOURIST_VIEW_ITINERARY

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
            REC_DESTINATION1: [MessageHandler(Filters.regex("^(Yes|No)$"),
                                              destination1)],
            REC_REGION: [MessageHandler(Filters.regex("^(Africa|Asia|Australia|Europe|North America|"
                                                        "South America|Recommend something for me)$"),
                                        region)],
            REC_DESTINATION2: [MessageHandler(Filters.regex("^(Bali|Egypt|Japan|San Francisco|Switzerland)$"),
                                              destination2)],
            BUSINESS_OPTIONS1: [MessageHandler(Filters.regex("^(View my itineraries|Add an itinerary|Edit an itinerary|"
                                                             "Remove an itinerary)$"), business_options1)],
            BUSINESS_VIEW_ITINERARY: [MessageHandler(Filters.text & ~Filters.command, business_view_itinerary)],
            ADD_COMPANY_NAME: [MessageHandler(Filters.text & ~Filters.command, add_company_name)],
            ADD_REGION: [MessageHandler(Filters.text & ~Filters.command, add_region)],
            ADD_COUNTRY: [MessageHandler(Filters.text & ~Filters.command, add_country)],
            ADD_TOUR_NAME: [MessageHandler(Filters.text & ~Filters.command, add_tour_name)],
            ADD_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, add_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()

