import logging
import pymongo
import copy

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
mycol = mydb["itineraries"]
mydict = {} # for biz adding, edit and remove itinerary
selected_user = "" # to store username
itineraries = []
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

USERTYPE, REC_DESTINATION1, BIZ_MAIN_MENU, CUSTOM_COUNTRY, REC_REGION, \
REC_DESTINATION2, TOURIST_VIEW_ITINERARY, TOURIST_SELECT_ITINERARY, BIZ_VIEW1, BIZ_VIEW2, ADD_COMPANY_NAME, ADD_REGION, \
ADD_COUNTRY, ADD_TOUR_NAME, ADD_BUDGET, ADD_DURATION, ADD_DESCRIPTION, NEW_ITINERARY_ADDED, NO_ITINERARY, \
BIZ_EDIT1, BIZ_EDIT2, BIZ_EDIT3, BIZ_EDIT4, BIZ_REMOVE1, BIZ_REMOVE2 = range(25)

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
        return BIZ_MAIN_MENU

def rec_destination1(update: Update, _: CallbackContext) -> int:
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

def biz_main_menu(update: Update, _: CallbackContext) -> int:
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
                return BIZ_VIEW1

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

def no_itinerary(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)
    mydict["Username"] = user.username
    update.message.reply_text("Please tell me the name of the company you belong to.")
    return ADD_COMPANY_NAME

def biz_view1(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)
    s = ""
    selected_itinerary = mycol.find_one({"$and": [{"Username": user.username}, {"Tour name": text}]})
    for key in selected_itinerary:
        if key == "Username" or key == "_id":
            continue
        else:
            s += "*" + key + ":* " + str(selected_itinerary.get(key)) + "\n"

    reply_keyboard = [["View other itineraries", "Back to main menu"]]
    update.message.reply_text(
        f"Here is the information we have saved on {text}. \n \n"
        f"{s} \n"
        f"What else would you like to do?", parse_mode= 'Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return BIZ_VIEW2

def biz_view2(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)

    if text == "View other itineraries":
        myquery = {"Username": user.username}
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
        update.message.reply_text(
            "Which itinerary would you like to view?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return BIZ_VIEW1

    elif text == "Back to main menu":
        reply_keyboard = [["View my itineraries", "Add an itinerary"],
                          ["Edit an itinerary", "Remove an itinerary"], ["/done"]]
        update.message.reply_text(
            "What else would you like to do?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return BIZ_MAIN_MENU

def biz_edit1(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)
    mydict["Tour name"] = text
    s = ""
    selected_itinerary = mycol.find_one({"$and": [{"Username": user.username}, {"Tour name": text}]})

    for key in selected_itinerary:
        if key == "Username" or key == "_id":
            continue
        else:
            s += "*" + key + ":* " + str(selected_itinerary.get(key)) + "\n"
    reply_keyboard = [["Company", "Region"], ["Country", "Tour name"], ["Budget per pax (in USD)", "Duration (in days)"]
        , ["Description"]]
    update.message.reply_text(
        f"Here is the information we have saved on {text}. \n \n"
        f"{s} \n"
        f"Which field would you like to edit?", parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return BIZ_EDIT2

def biz_edit2(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Field"] = text
    update.message.reply_text(f"You would like to edit the *{text}* field? Sure thing! Just send me the new information "
                              f"to be saved under that field. If you are editing the budget or duration field, please "
                              f"only include the numerical values for those fields.", parse_mode="Markdown")
    return BIZ_EDIT3

def biz_edit3(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)
    if mydict.get("Field") == "Budget per pax (in USD)" or mydict.get("Field") == "Duration (in days)":
        text = int(text)
    mycol.update_one({"$and": [{"Username": user.username}, {"Tour name": mydict.get("Tour name")}]},
                     {"$set": {mydict.get("Field"): text}})

    if mydict.get("Field") == "Tour name":
        edited_itinerary = mycol.find_one({"$and": [{"Username": user.username}, {"Tour name": text}]})
        mydict["Tour name"] = text
    else:
        edited_itinerary = mycol.find_one({"$and": [{"Username": user.username}, {"Tour name": mydict.get("Tour name")}]})

    s = ""
    for key in edited_itinerary:
        if key == "Username" or key == "_id":
            continue
        else:
            s += "*" + key + ":* " + str(edited_itinerary.get(key)) + "\n"

    reply_keyboard = [["Edit another field for this tour", "Edit another tour"], ["Back to main menu", "/done"]]
    update.message.reply_text(
        f"Here is the updated {mydict.get('Tour name')}. \n \n"
        f"{s} \n"
        f"What else would you like to do?", parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return BIZ_EDIT4

def biz_edit4(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)

    if text == "Edit another tour":
        myquery = {"Username": user.username}
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
        update.message.reply_text(
            "Which itinerary would you like to edit?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return BIZ_EDIT1

    elif text == "Edit another field for this tour":
        reply_keyboard = [["Company", "Region"], ["Country", "Tour name"],
                          ["Budget per pax (in USD)", "Duration (in days)"], ["Description"]]
        update.message.reply_text("Which field would you like to edit?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
                                  )
        return BIZ_EDIT2

    elif text == "Back to main menu":
        reply_keyboard = [["View my itineraries", "Add an itinerary"],
                          ["Edit an itinerary", "Remove an itinerary"], ["/done"]]
        update.message.reply_text("What else would you like to do?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
                                  )
        mydict.clear()
        return BIZ_MAIN_MENU

def biz_remove1(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)
    s = ""
    selected_itinerary = mycol.find_one({"$and": [{"Username": user.username}, {"Tour name": text}]})
    mydict["_id"] = selected_itinerary.get("_id")

    for key in selected_itinerary:
        if key == "Username" or key == "_id":
            continue
        else:
            s += "*" + key + ":* " + str(selected_itinerary.get(key)) + "\n"
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
        mycol.delete_one({"_id": mydict.get("_id")})
        update.message.reply_text("That tour has successfully been removed. What else would you like to do?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    else:
        update.message.reply_text("What else would you like to do?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    mydict.clear()
    return BIZ_MAIN_MENU

def add_company_name(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Company"] = text
    update.message.reply_text(f"Your company name is {text}. Next, please tell me the region your tour will be held in "
                              f"(eg. Asia, Europe etc).")
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
    update.message.reply_text(f"The name of your tour is {text}. Next, please give me an estimate on the budget of your"
                              f" tour per pax in USD.")
    return ADD_BUDGET

def add_budget(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Budget per pax (in USD)"] = int(text)
    update.message.reply_text(f"The estimated budget of your tour per pax is USD{text}. Next, please give me the "
                              f"duration of your tour in days.")
    return ADD_DURATION

def add_duration(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Duration (in days)"] = int(text)
    update.message.reply_text(f"The duration of your tour will be {text} days. Lastly, please give me a description of "
                              f"your tour. We suggest including information such as places that the tourists will be "
                              f"visiting, how many hours are allocated for tourists to visit each place, meals that"
                              f"the tourists will be having etc.")
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
            s += "*" + key + ":* " + str(mydict.get(key)) + "\n"

    reply_keyboard = [["View my itineraries", "Add an itinerary"],
                      ["Edit an itinerary", "Remove an itinerary"], ["/done"]]
    update.message.reply_text(
        "And you're done! Here's what you sent me. \n \n"
        f"{s} \n"
        f"What else would you like to do?", parse_mode= 'Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    mycol.insert_one(mydict)
    mydict.clear()
    return BIZ_MAIN_MENU

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
            if country in row:
                continue

            elif len(row) < 2:
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

def rec_destination2(update: Update, _: CallbackContext) -> int:
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
        f"*Company:* {company}\n*{text}:*\n{description}", parse_mode= "Markdown",
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
                                              rec_destination1)],
            REC_REGION: [MessageHandler(Filters.regex("^(Africa|Asia|Australia|Europe|North America|"
                                                        "South America|Recommend something for me)$"), region)],
            REC_DESTINATION2: [MessageHandler(Filters.text & ~Filters.command,
                                              rec_destination2)],
            TOURIST_SELECT_ITINERARY: [MessageHandler(Filters.regex("^(Select this itinerary|Go back)$"), tourist_select)],
            TOURIST_VIEW_ITINERARY: [MessageHandler(Filters.text & ~Filters.command, tourist_view)],
            CUSTOM_COUNTRY: [MessageHandler(Filters.text & ~Filters.command, custom_country)],
            NO_ITINERARY: [MessageHandler(Filters.regex("^(Add an itinerary)$"), no_itinerary)],
            BIZ_MAIN_MENU: [MessageHandler(Filters.regex("^(View my itineraries|Add an itinerary|Edit an itinerary|"
                                                        "Remove an itinerary)$"), biz_main_menu)],
            BIZ_VIEW1: [MessageHandler(Filters.text & ~Filters.command, biz_view1)],
            BIZ_VIEW2: [MessageHandler(Filters.regex("^(View other itineraries|Back to main menu)$"), biz_view2)],
            BIZ_EDIT1: [MessageHandler(Filters.text & ~Filters.command, biz_edit1)],
            BIZ_EDIT2: [MessageHandler(Filters.regex("^(Company|Region|Country|Tour name|Budget per pax \(in USD\)|"
                                                     "Duration \(in days\)|Description)$"), biz_edit2)],
            BIZ_EDIT3: [MessageHandler(Filters.text & ~Filters.command, biz_edit3)],
            BIZ_EDIT4: [MessageHandler(Filters.regex("^(Edit another field for this tour|Edit another tour|"
                                                     "Back to main menu)$"), biz_edit4)],
            BIZ_REMOVE1: [MessageHandler(Filters.text & ~Filters.command, biz_remove1)],
            BIZ_REMOVE2: [MessageHandler(Filters.regex("^(Yes|No)$"), biz_remove2)],
            ADD_COMPANY_NAME: [MessageHandler(Filters.text & ~Filters.command,add_company_name)],
            ADD_REGION: [MessageHandler(Filters.text & ~Filters.command, add_region)],
            ADD_COUNTRY: [MessageHandler(Filters.text & ~Filters.command, add_country)],
            ADD_TOUR_NAME: [MessageHandler(Filters.text & ~Filters.command, add_tour_name)],
            ADD_BUDGET: [MessageHandler(Filters.text & ~Filters.command, add_budget)],
            ADD_DURATION: [MessageHandler(Filters.text & ~Filters.command, add_duration)],
            ADD_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, add_description)],
        },
        fallbacks=[CommandHandler("done", done)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()

