import logging
import pymongo
import copy

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
mycol = mydb["itineraries"]
mydict = {} # for biz adding itinerary
edit_field = [] # for biz edit and remove itinerary
selected_user = "" # to store username
itineraries= []
country = ""

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

USERTYPE, REC_DESTINATION1, BIZ_OPTIONS1, CUSTOM_COUNTRY, REC_REGION, \
REC_DESTINATION2, TOURIST_VIEW_ITINERARY, TOURIST_SELECT_ITINERARY, CUSTOM_COUNTRY, BIZ_VIEW, ADD_COMPANY_NAME, ADD_REGION, \
ADD_COUNTRY, ADD_TOUR_NAME, ADD_DESCRIPTION, NEW_ITINERARY_ADDED, NO_ITINERARY, \
BIZ_EDIT1, BIZ_EDIT2, BIZ_EDIT3, BIZ_REMOVE1, BIZ_REMOVE2 = range(22)

def start(update: Update, _: CallbackContext) -> int:
    reply_keyboard = [["Tourist"], ["Business Owner"]]

    update.message.reply_text(
        "Hello, I am TraveLaterBot! I can recommend you tours for places that you might be interested in if you are a "
        "tourist, or help you advertise your tours if you are business owner. Are you a tourist or a business owner?"
        "\n \n"
        "You can select the /done button or type \"/done\" anytime you wish to terminate the conversation",
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
                          ["Edit an itinerary", "Remove an itinerary"], ["/done"]]
        update.message.reply_text(
            "Hello business owner! What would you like to do today?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return BIZ_OPTIONS1

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

def biz_options1(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    myquery = {"Username": user.username}
    text = update.message.text
    logger.info("%s", text)

    if text == "View my itineraries" or text == "Edit an itinerary" or text == "Remove an itinerary":
        results = mycol.find(myquery)
        results_lst = []
        for result in results:
            results_lst.append(result)

        if len(results_lst) == 0:
            reply_keyboard = [["Add an itinerary", "/done"]]

            update.message.reply_text(
                "Currently, you do not have any itineraries saved with us. Would you like to add one?",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
            )
            return NO_ITINERARY

        else:
            table = []
            row = []
            for result in results_lst:
                tour_name = result.get("Tour name")
                if len(row) < 2:
                    row.append(tour_name)
                else:
                    dup_row = copy.deepcopy(row)
                    table.append(dup_row)
                    row.clear()
                    row.append(tour_name)
            table.append(row)

            reply_keyboard = table

            if text == "View my itineraries":
                update.message.reply_text(
                    "Which itinerary would you like to view?",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
                )
                return BIZ_VIEW

            elif text == "Edit an itinerary":
                update.message.reply_text(
                    "Which itinerary would you like to edit?",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
                )
                return BIZ_EDIT1

            elif text == "Remove an itinerary":
                update.message.reply_text(
                    "Which itinerary would you like to remove?",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
                )
                return BIZ_REMOVE1

    elif text == "Add an itinerary":
        mydict["Username"] = user.username
        update.message.reply_text("Please tell me the name of the company you belong to.")
        return ADD_COMPANY_NAME

def biz_view(update: Update, _: CallbackContext) -> int:
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
                      ["Edit an itinerary", "Remove an itinerary"], ["/done"]]
    update.message.reply_text(
        f"Here is the information we have saved on {text}. \n \n"
        f"{s} \n"
        f"What else would you like to do?", parse_mode= 'Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return BIZ_OPTIONS1

def biz_edit1(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)
    edit_field.append(text) # name of tour added to list
    s = ""
    selected_itinerary = mycol.find_one({"$and": [{"Username": user.username}, {"Tour name": text}]})

    for key in selected_itinerary:
        if key == "Username" or key == "_id":
            continue
        else:
            s += "*" + key + ":* " + selected_itinerary.get(key) + "\n"
    reply_keyboard = [["Company", "Region"], ["Country", "Tour name"], ["Description"]]
    update.message.reply_text(
        f"Here is the information we have saved on {text}. \n \n"
        f"{s} \n"
        f"Which field would you like to edit?", parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return BIZ_EDIT2

def biz_edit2(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    edit_field.append(text) # field to be edited added to list
    update.message.reply_text(f"You would like to edit the {text} field? Sure thing! Just send me the new information "
                              f"to be saved under that field.")
    return BIZ_EDIT3

def biz_edit3(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)
    mycol.update_one({"$and": [{"Username": user.username}, {"Tour name": edit_field[0]}]},
                     {"$set": {edit_field[1]: text}})
    s = ""
    if edit_field[1] == "Tour name":
        edited_itinerary = mycol.find_one({"$and": [{"Username": user.username}, {"Tour name": text}]})
    else:
        edited_itinerary = mycol.find_one({"$and": [{"Username": user.username}, {"Tour name": edit_field[0]}]})

    for key in edited_itinerary:
        if key == "Username" or key == "_id":
            continue
        else:
            s += "*" + key + ":* " + edited_itinerary.get(key) + "\n"

    reply_keyboard = [["View my itineraries", "Add an itinerary"],
                      ["Edit an itinerary", "Remove an itinerary"], ["/done"]]
    update.message.reply_text(
        f"Here is the updated {edit_field[0]}. \n \n"
        f"{s} \n"
        f"What else would you like to do?", parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    edit_field.clear()
    return BIZ_OPTIONS1

def biz_remove1(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)
    s = ""
    selected_itinerary = mycol.find_one({"$and": [{"Username": user.username}, {"Tour name": text}]})
    edit_field.append(selected_itinerary.get("_id"))

    for key in selected_itinerary:
        if key == "Username" or key == "_id":
            continue
        else:
            s += "*" + key + ":* " + selected_itinerary.get(key) + "\n"
    reply_keyboard = [["Yes", "No"]]
    update.message.reply_text(
        f"Here is the information we have saved on {text}. \n \n"
        f"{s} \n"
        f"Are you sure you want to remove it?", parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return BIZ_REMOVE2

def biz_remove2(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    reply_keyboard = [["View my itineraries", "Add an itinerary"],
                      ["Edit an itinerary", "Remove an itinerary"], ["/done"]]
    if text == "Yes":
        mycol.delete_one({"_id": edit_field[0]})
        update.message.reply_text("That tour has successfully been removed. What else would you like to do?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    else:
        update.message.reply_text("What else would you like to do?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    edit_field.clear()
    return BIZ_OPTIONS1

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
                      ["Edit an itinerary", "Remove an itinerary"], ["/done"]]
    update.message.reply_text(
        "And you're done! Here's what you sent me. \n \n"
        f"{s} \n"
        f"What else would you like to do?", parse_mode= 'Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    mycol.insert_one(mydict)
    mydict.clear()
    return BIZ_OPTIONS1

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
        myquery = {"Region": text}
        results = mycol.find(myquery)
        results_lst = []
        for result in results:
            results_lst.append(result)

        table = []
        row = []
        for result in results_lst:
            country = result.get("Country")
            if len(row) < 2:
                row.append(country)
            else:
                dup_row = copy.deepcopy(row)
                table.append(dup_row)
                row.clear()
                row.append(country)
        table.append(row)
        reply_keyboard = table
        update.message.reply_text(
            f"Here are some popular destinations for {text}. You can select them to find out more!",
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return REC_DESTINATION2

def destination2(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    #reply_keyboard = [["Select this itinerary"], ["Find out more"], ["Show me another itinerary"]]

    myquery = {"Country": text}
    results = mycol.find(myquery)
    results_lst = []
    for result in results:
        results_lst.append(result)

    table = []
    row = []
    for result in results_lst:
        tour_name = result.get("Tour name")
        if len(row) < 2:
            row.append(tour_name)
        else:
            dup_row = copy.deepcopy(row)
            table.append(dup_row)
            row.clear()
            row.append(tour_name)
    table.append(row)
    reply_keyboard = table
    global country
    country = text
    global itineraries
    itineraries = table
    update.message.reply_text(
        f"Here are some itineraries for {text}:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return TOURIST_VIEW_ITINERARY

def tourist_view(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    myquery = {"Tour name": text}
    results = mycol.find(myquery)
    results_lst = []
    for result in results:
        results_lst.append(result)

    for i in results_lst:
        description = i.get("Description")
        global selected_user
        selected_user = i.get("Username")
        company = i.get("Company")

    reply_keyboard = [["Select this itinerary"], ["Go back"]]
    update.message.reply_text(
        f"Company: {company}\n{text}:\n{description}",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return TOURIST_SELECT_ITINERARY

def tourist_select(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    if text == "Select this itinerary":
        update.message.reply_text(
            f"Here is the Telegram handle for the person-in-charge. Please contact him for more details!\n@{selected_user}",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    else:
        global country
        global itineraries
        reply_keyboard = itineraries
        update.message.reply_text(
            f"Here are some itineraries for {country}:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )

        return TOURIST_VIEW_ITINERARY

def custom_country(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    myquery = {"Country": text}
    results = mycol.find(myquery)
    results_lst = []
    for result in results:
        results_lst.append(result)

    table = []
    row = []
    for result in results_lst:
        tour_name = result.get("Tour name")
        if len(row) < 2:
            row.append(tour_name)
        else:
            dup_row = copy.deepcopy(row)
            table.append(dup_row)
            row.clear()
            row.append(tour_name)
    table.append(row)
    reply_keyboard = table
    global country
    country = text
    global itineraries
    itineraries = table
    update.message.reply_text(
        f"Here are some itineraries for {text}:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return TOURIST_VIEW_ITINERARY

def done(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s ended the conversation.", user.first_name)
    update.message.reply_text(
        "Goodbye! I hope I managed to assist you and that we can talk again some day.",
        reply_markup=ReplyKeyboardRemove()
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
                                                        "South America|Recommend something for me)$"), region)],
            REC_DESTINATION2: [MessageHandler(Filters.text & ~Filters.command,
                                              destination2)],
            TOURIST_SELECT_ITINERARY: [MessageHandler(Filters.regex("^(Select this itinerary|Go back)$"), tourist_select)],
            TOURIST_VIEW_ITINERARY: [MessageHandler(Filters.text & ~Filters.command, tourist_view)],
            CUSTOM_COUNTRY: [MessageHandler(Filters.text & ~Filters.command, custom_country)],
            BIZ_OPTIONS1: [MessageHandler(Filters.regex("^(View my itineraries|Add an itinerary|Edit an itinerary|"
                                                             "Remove an itinerary)$"), biz_options1)],
            BIZ_VIEW: [MessageHandler(Filters.text & ~Filters.command, biz_view)],
            BIZ_EDIT1: [MessageHandler(Filters.text & ~Filters.command, biz_edit1)],
            BIZ_EDIT2: [MessageHandler(Filters.regex("^(Company|Region|Country|Tour name|Description)$"), biz_edit2)],
            BIZ_EDIT3: [MessageHandler(Filters.text & ~Filters.command,biz_edit3)],
            BIZ_REMOVE1: [MessageHandler(Filters.text & ~Filters.command, biz_remove1)],
            BIZ_REMOVE2: [MessageHandler(Filters.regex("^(Yes|No)$"), biz_remove2)],
            ADD_COMPANY_NAME: [MessageHandler(Filters.text & ~Filters.command,add_company_name)],
            ADD_REGION: [MessageHandler(Filters.text & ~Filters.command, add_region)],
            ADD_COUNTRY: [MessageHandler(Filters.text & ~Filters.command, add_country)],
            ADD_TOUR_NAME: [MessageHandler(Filters.text & ~Filters.command, add_tour_name)],
            ADD_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, add_description)],
        },
        fallbacks=[CommandHandler("done", done)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()

