import logging
import pymongo
import copy
from country_list import countries_for_language

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
mycol = mydb["itineraries"]
mydict = {} # for biz adding, edit and remove itinerary
selected_user = "" # to store username
itineraries = []
country = ""
countries = []
countries_dict = dict(countries_for_language('en'))
for i in countries_dict.values():
    countries.append(i)
regions = ["Europe", "Asia", "North America", "South America", "Oceania", "Africa", "Antarctica"]

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

USERTYPE, REC_DESTINATION, BIZ_MAIN_MENU, CUSTOM_COUNTRY1, CUSTOM_COUNTRY2, CUSTOM_COUNTRY_BUDGET, \
CUSTOM_COUNTRY_DURATION, REC_REGION1, TOURIST_VIEW, TOURIST_SELECT, BIZ_VIEW1, BIZ_VIEW2, \
ADD_COMPANY_NAME, ADD_REGION, ADD_COUNTRY, ADD_TOUR_NAME, ADD_BUDGET, ADD_DURATION, ADD_WEBSITE, ADD_DESCRIPTION, \
NEW_ITINERARY_ADDED, BIZ_NO_ITINERARY, BIZ_EDIT1, BIZ_EDIT2, BIZ_EDIT3, BIZ_EDIT4, BIZ_REMOVE1, BIZ_REMOVE2, \
TOURIST_NO_ITINERARY, REC_SOMETHING, REC_SOMETHING_BUDGET, REC_SOMETHING_DURATION, REC_SOMETHING_BUDGET_DURATION1, \
REC_SOMETHING_BUDGET_DURATION2, CUSTOM_COUNTRY_BUDGET_DURATION1, CUSTOM_COUNTRY_BUDGET_DURATION2, REC_REGION2 = range(37)

def start(update: Update, _: CallbackContext) -> int:
    reply_keyboard = [["Tourist", "Business Owner"]]

    update.message.reply_text(
        "Hello, I am TraveLaterBot! I can recommend you tours for places that you might be interested in if you are a "
        "tourist, or help you advertise your tours if you are business owner. Are you a tourist or a business owner?"
        "\n \n"
        "You can select the /done button or type \"/done\" anytime you wish to terminate the conversation",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return USERTYPE

def usertype(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)

    if text == "Tourist":
        reply_keyboard = [["Yes", "No"]]
        update.message.reply_text(
            "Welcome traveller! Do you have a specific country that you wish to visit?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return REC_DESTINATION

    else:
        reply_keyboard = [["View my itineraries", "Add an itinerary"],
                          ["Edit an itinerary", "Remove an itinerary"], ["/done"]]
        update.message.reply_text(
            "Hello business owner! What would you like to do today?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return BIZ_MAIN_MENU

def rec_destination1(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)

    if text == "Yes":
        update.message.reply_text("Great! Where would you like to go?")
        return CUSTOM_COUNTRY1

    else:
        reply_keyboard = [["Africa", "Antarctica"], ["Asia", "Europe"], ["North America",
                          "South America"], ["Oceania", "Recommend something for me"]]

        update.message.reply_text(
            "No worries! Do you have a region that you want to visit? If you don't, you can select the \"*Recommend "
            "something for me*\" button so that we can guide you in choosing your next holiday destination.", parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return REC_REGION1

def biz_main_menu(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    myquery = {"Username": user.username}
    text = update.message.text
    logger.info("%s", text)

    if text == "View my itineraries" or text == "Edit an itinerary" or text == "Remove an itinerary":
        results_lst = cursor_to_list(myquery)

        if len(results_lst) == 0:
            reply_keyboard = [["Add an itinerary", "/done"]]

            update.message.reply_text(
                "Currently, you do not have any itineraries saved with us. Would you like to add one?",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
            )
            return BIZ_NO_ITINERARY

        else:
            reply_keyboard = list_to_keyboard(results_lst)

            if text == "View my itineraries":
                update.message.reply_text(
                    "Which itinerary would you like to view?",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
                )
                return BIZ_VIEW1

            elif text == "Edit an itinerary":
                update.message.reply_text(
                    "Which itinerary would you like to edit?",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
                )
                return BIZ_EDIT1

            elif text == "Remove an itinerary":
                update.message.reply_text(
                    "Which itinerary would you like to remove?",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
                )
                return BIZ_REMOVE1

    elif text == "Add an itinerary":
        mydict["Username"] = user.username
        update.message.reply_text("Please tell me the name of the company you belong to.")
        return ADD_COMPANY_NAME

def biz_no_itinerary(update: Update, _: CallbackContext) -> int:
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
    selected_itinerary = mycol.find_one({"$and": [{"Username": user.username}, {"Tour name": text}]})
    output = show_itinerary_details(selected_itinerary)

    reply_keyboard = [["View other itineraries", "Back to main menu"]]
    update.message.reply_text(
        f"Here is the information we have saved on {text}. \n \n"
        f"{output} \n"
        f"What else would you like to do?", parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return BIZ_VIEW2

def biz_view2(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)

    if text == "View other itineraries":
        myquery = {"Username": user.username}
        results_lst = cursor_to_list(myquery)
        reply_keyboard = list_to_keyboard(results_lst)
        update.message.reply_text(
            "Which itinerary would you like to view?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return BIZ_VIEW1

    elif text == "Back to main menu":
        reply_keyboard = [["View my itineraries", "Add an itinerary"],
                          ["Edit an itinerary", "Remove an itinerary"], ["/done"]]
        update.message.reply_text(
            "What else would you like to do?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return BIZ_MAIN_MENU

def biz_edit1(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)
    mydict["Tour name"] = text
    selected_itinerary = mycol.find_one({"$and": [{"Username": user.username}, {"Tour name": text}]})
    output = show_itinerary_details(selected_itinerary)
    reply_keyboard = [["Company", "Region"], ["Country", "Tour name"], ["Budget per pax (in USD)", "Duration (in days)"],
                      ["Website", "Description"]]
    update.message.reply_text(
        f"Here is the information we have saved on {text}. \n \n"
        f"{output} \n"
        f"Which field would you like to edit?", parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
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

    output = show_itinerary_details(edited_itinerary)
    reply_keyboard = [["Edit another field for this tour", "Edit another tour"], ["Back to main menu", "/done"]]
    update.message.reply_text(
        f"Here is the updated {mydict.get('Tour name')}. \n \n"
        f"{output} \n"
        f"What else would you like to do?", parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return BIZ_EDIT4

def biz_edit4(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)

    if text == "Edit another tour":
        myquery = {"Username": user.username}
        results_lst = cursor_to_list(myquery)
        reply_keyboard = list_to_keyboard(results_lst)
        update.message.reply_text(
            "Which itinerary would you like to edit?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return BIZ_EDIT1

    elif text == "Edit another field for this tour":
        reply_keyboard = [["Company", "Region"], ["Country", "Tour name"],
                          ["Budget per pax (in USD)", "Duration (in days)"], ["Website", "Description"]]
        update.message.reply_text("Which field would you like to edit?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True),)
        return BIZ_EDIT2

    elif text == "Back to main menu":
        reply_keyboard = [["View my itineraries", "Add an itinerary"],
                          ["Edit an itinerary", "Remove an itinerary"], ["/done"]]
        update.message.reply_text("What else would you like to do?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True),)
        mydict.clear()
        return BIZ_MAIN_MENU

def biz_remove1(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("%s", text)
    selected_itinerary = mycol.find_one({"$and": [{"Username": user.username}, {"Tour name": text}]})
    mydict["_id"] = selected_itinerary.get("_id")
    output = show_itinerary_details(selected_itinerary)
    reply_keyboard = [["Yes", "No"]]
    update.message.reply_text(
        f"Here is the information we have saved on {text}. \n \n"
        f"{output} \n"
        f"Are you sure you want to remove it?", parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return BIZ_REMOVE2

def biz_remove2(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    reply_keyboard = [["View my itineraries", "Add an itinerary"],
                      ["Edit an itinerary", "Remove an itinerary"], ["/done"]]
    if text == "Yes":
        mycol.delete_one({"_id": mydict.get("_id")})
        update.message.reply_text("That tour has successfully been removed. What else would you like to do?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
    else:
        update.message.reply_text("What else would you like to do?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
    mydict.clear()
    return BIZ_MAIN_MENU

def add_company_name(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Company"] = text
    update.message.reply_text(f"Your company name is *{text}*. Next, please tell me the region your tour will be held in "
                              f"(eg. Asia, Europe etc).", parse_mode="Markdown")
    return ADD_REGION

def add_region(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    if text in regions:
        mydict["Region"] = text
        update.message.reply_text(f"Your tour will be held in *{text}*. Next, please tell me which country your tour will be "
                                f"held in.", parse_mode="Markdown")
        return ADD_COUNTRY
    else:
        update.message.reply_text(f"Please enter a valid region (i.e. Africa, Antarctica, Asia, Europe, North America, South America, Oceania).", parse_mode="Markdown")
        return ADD_REGION

def add_country(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    if text in countries:
        mydict["Country"] = text
        update.message.reply_text(f"Your tour will be held in *{text}*. Next, please tell me the name of your tour.",
                                  parse_mode="Markdown")
        return ADD_TOUR_NAME
    else:
        update.message.reply_text(f"Please enter a valid country.", parse_mode="Markdown")
        return ADD_COUNTRY

def add_tour_name(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Tour name"] = text
    update.message.reply_text(f"The name of your tour is *{text}*. Next, please give me an estimate on the budget of your"
                              f" tour per pax in USD.", parse_mode="Markdown")
    return ADD_BUDGET

def add_budget(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Budget per pax (in USD)"] = int(text)
    update.message.reply_text(f"The estimated budget of your tour per pax is *USD{text}*. Next, please give me the "
                              f"duration of your tour in days.", parse_mode="Markdown")
    return ADD_DURATION

def add_duration(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Duration (in days)"] = int(text)
    update.message.reply_text(f"The duration of your tour will be *{text}* days. Next, please give me the link to "
                              f"the website where this tour can be found.", parse_mode="Markdown")
    return ADD_WEBSITE

def add_website(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Website"] = text
    update.message.reply_text(
        f"This it the link to your website: \n{text} \n\nLastly, please give me a description of "
        f"your tour. We suggest including information such as places that the tourists will be "
        f"visiting, how many hours are allocated for tourists to visit each place, meals that "
        f"the tourists will be having etc.", parse_mode="Markdown")
    return ADD_DESCRIPTION

def add_description(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    mydict["Description"] = text
    output = show_itinerary_details(mydict)

    reply_keyboard = [["View my itineraries", "Add an itinerary"],
                      ["Edit an itinerary", "Remove an itinerary"], ["/done"]]
    update.message.reply_text(
        "And you're done! Here's what you sent me. \n \n"
        f"{output} \n"
        f"What else would you like to do?", parse_mode= 'Markdown',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    mycol.insert_one(mydict)
    mydict.clear()
    return BIZ_MAIN_MENU

def rec_region1(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)

    if text == "Recommend something for me":
        reply_keyboard = [["Budget", "Duration"], ["Budget and Duration", "Popularity"]]
        update.message.reply_text(
            "How would you like to search for itineraries? You can choose to search for them based on a specified budget "
            "only, a specified duration only, popularity among our users or a combination of both a specified budget "
            "and duration.",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True, resize_keyboard=True))
        return REC_SOMETHING

    else:
        global mydict
        mydict["Region"] = text
        results_lst = cursor_to_list(mydict)
        if len(results_lst) == 0:
            reply_keyboard = [["Africa", "Antarctica"], ["Asia", "Europe"], ["North America", "South America"],
                              ["Oceania", "Recommend something for me"]]
            update.message.reply_text(
                f"Unfortunately,we do not have any itineraries for the *{text}*. You can try selecting another region or "
                f"we could recommend something for you. Which region would you like to visit?", parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
            )
            return REC_REGION1

        else:
            reply_keyboard = [["View all results", "View by countries"], ["View by popular countries"]]
            update.message.reply_text(
                f"We found *{len(results_lst)}* itineraries for the region *{text}*. You can choose to view all of them, "
                f"view itineraries by popular countries or view itineraries by their respective countries. What "
                f"would you like to do?", parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
            )
            return REC_REGION2

def rec_region2(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    results_lst = cursor_to_list(mydict)

    if text == "View all results":
        reply_keyboard = list_to_keyboard(results_lst)
        global itineraries
        itineraries = reply_keyboard
        update.message.reply_text(
            f"Here are all the itineraries for the region *{mydict.get('Region')}*. You can select them to find out "
            f"more.", parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                              resize_keyboard=True)
        )
        mydict.clear()
        return TOURIST_VIEW

    elif text == "View by countries":
        lst = []
        for doc in results_lst:
            country = doc.get("Country")
            if country not in lst:
                lst.append(country)
        table = []
        row = []
        sorting = []
        for result in lst:
            sorting.append(result)

        sorting.sort()
        for tour_name in sorting:
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
            f"Here are the countries that we have itineraries for under the region *{mydict.get('Region')}*. You can "
            f"select a country to view the itineraries that we have for that country.", parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return CUSTOM_COUNTRY1

    elif text == "View by popular countries":
        newdict = {}
        myquery = {"Region": mydict.get("Region")}
        for doc in mycol.find(myquery):
            if doc.get("Country") not in newdict:
                newdict[doc.get("Country")] = 0
        for doc in mycol.find(myquery):
            value = newdict.get(doc.get("Country"))
            newdict[doc.get("Country")] = value + 1
        sorteddict = dict(sorted(newdict.items(), key=lambda item: item[1], reverse=True))
        top4 = []
        for country in sorteddict.keys():
            while len(top4) < 4 and country not in top4:
                top4.append(country)
        top4.sort()
        table = []
        row = []
        for tour_name in top4:
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
            f"Here are the popular countries under the region *{mydict.get('Region')}*. You can "
            f"select a country to view the itineraries that we have for that country.", parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return CUSTOM_COUNTRY1

def tourist_view(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    myquery = {"Tour name": text}
    result = mycol.find_one(myquery)
    global selected_user
    selected_user = result.get("Username")
    output = show_itinerary_details(result)
    reply_keyboard = [["Select this itinerary", "Go back"]]
    update.message.reply_text(
        f"Here are the details on {text}:\n\n"
        f"{output}", parse_mode= "Markdown",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return TOURIST_SELECT

def tourist_select(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    if text == "Select this itinerary":
        update.message.reply_text(
            f"Here is the Telegram handle for the person-in-charge. You can contact him/her for more details!\n@{selected_user}",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    else:
        global country
        global itineraries
        reply_keyboard = itineraries
        update.message.reply_text(
            f"Here are the itineraries that you might be interested in. You can select them to find out more.",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return TOURIST_VIEW

def custom_country1(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    global mydict
    mydict["Country"] = text
    results_lst = cursor_to_list(mydict)
    if len(results_lst) == 0:
        reply_keyboard = [["Search for another country", "Guide me"]]
        update.message.reply_text(
            f"Unfortunately we do not have any tours posted for *{text}*. Would you like to search for tours "
            f"for another country, or would you like us to guide you in choosing a country to visit?",
            parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                    resize_keyboard=True),
        )
        return TOURIST_NO_ITINERARY

    else:
        reply_keyboard = [["View all results", "Filter by budget"], ["Filter by duration",
                          "Filter by budget and duration"]]
        update.message.reply_text(
            f"We found *{len(results_lst)}* itineraries for *{text}*. You can choose to view all of them or filter the "
            f"results. You can choose to filter by a specified budget, duration or both budget and duration. What "
            f"would you like to do?",
            parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return CUSTOM_COUNTRY2

def custom_country2(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)

    if text == "View all results":
        results_lst = cursor_to_list(mydict)
        reply_keyboard = list_to_keyboard(results_lst)
        global country
        country = text
        global itineraries
        itineraries = reply_keyboard
        update.message.reply_text(
            f"Here are all the itineraries for *{mydict.get('Country')}*:", parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        mydict.clear()
        return TOURIST_VIEW

    elif text == "Filter by budget":
        update.message.reply_text("Please state your maximum budget per pax in USD. We will search for tours that are "
                                  "within your budget.")
        return CUSTOM_COUNTRY_BUDGET

    elif text == "Filter by duration":
        update.message.reply_text("Please state your desired duration of stay. We will search for tours that are "
                                  "within the specified duration.")
        return CUSTOM_COUNTRY_DURATION

    elif text == "Filter by budget and duration":
        update.message.reply_text("Please state your maximum budget per pax in USD. We will search for tours that are "
                                  "within your budget.")
        return CUSTOM_COUNTRY_BUDGET_DURATION1

def custom_country_budget(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    text = int(text)
    results = mycol.find({"$and": [{"Country": mydict.get("Country")}, {"Budget per pax (in USD)": {"$lte": text}}]})
    results_lst = []
    for result in results:
        results_lst.append(result)

    if len(results_lst) == 0:
        reply_keyboard = [["View all results", "Filter by budget"], ["Filter by duration",
                                                                     "Filter by budget and duration"]]
        update.message.reply_text("Unfortunately, we could not find any tours that fit within your budget. You can "
                                  "instead increase your budget or choose one of the other options offered. What would "
                                  "you like to do?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return CUSTOM_COUNTRY2

    else:
        reply_keyboard = list_to_keyboard(results_lst)
        global itineraries
        itineraries = reply_keyboard
        update.message.reply_text(
            "Here are the tours that fit within your budget. You can select them to find out more.",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        mydict.clear()
        return TOURIST_VIEW

def custom_country_duration(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    text = int(text)
    results = mycol.find({"$and": [{"Country": mydict.get("Country")}, {"Duration (in days)": {"$lte": text}}]})
    results_lst = []
    for result in results:
        results_lst.append(result)

    if len(results_lst) == 0:
        reply_keyboard = [["View all results", "Filter by budget"], ["Filter by duration",
                                                                     "Filter by budget and duration"]]
        update.message.reply_text("Unfortunately, we could not find any tours that fit within your budget. You can "
                                  "instead increase your budget or choose one of the other options offered. What would "
                                  "you like to do?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return CUSTOM_COUNTRY2

    else:
        reply_keyboard = list_to_keyboard(results_lst)
        global itineraries
        itineraries = reply_keyboard
        update.message.reply_text(
            "Here are the tours that fit within your duration of stay. You can select them to find out more.",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        mydict.clear()
        return TOURIST_VIEW

def custom_country_budget_duration1(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    global mydict
    mydict["Budget"] = int(text)
    update.message.reply_text(f"Your budget is *USD{text}*. Please state your desired duration of stay. We will search"
                              f" for tours that are within the specified duration", parse_mode="Markdown")
    return CUSTOM_COUNTRY_BUDGET_DURATION2

def custom_country_budget_duration2(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    text = int(text)
    results = mycol.find(
        {"$and": [{"Country": mydict.get("Country")}, {"Budget per pax (in USD)": {"$lte": mydict.get("Budget")}},
                  {"Duration (in days)": {"$lte": text}}]})
    results_lst = []
    for result in results:
        results_lst.append(result)

    if len(results_lst) == 0:
        reply_keyboard = [["View all results", "Filter by budget"], ["Filter by duration",
                                                                     "Filter by budget and duration"]]
        update.message.reply_text("Unfortunately, we could not find any tours that fit within your budget or duration of stay. You can "
                                  "instead increase your budget or choose one of the other options offered. What would "
                                  "you like to do?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return CUSTOM_COUNTRY2

    else:
        reply_keyboard = list_to_keyboard(results_lst)
        global itineraries
        itineraries = reply_keyboard
        update.message.reply_text(
            "Here are the tours that fit within your budget and duration of stay. You can select them to find out more.",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        mydict.clear()
        return TOURIST_VIEW

def tourist_no_itinerary(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)

    if text == "Search for another country":
        update.message.reply_text("Where would you like to go?")
        return CUSTOM_COUNTRY1

    elif text == "Guide me":
        reply_keyboard = [["Africa", "Asia"], ["Australia", "Europe"], ["North America", "South America"],
                          ["Recommend something for me"]]
        update.message.reply_text(
            "Sure thing! Do you have a region that you want to visit?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return REC_REGION1

def rec_something(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)

    if text == "Popularity":
        newdict = {}
        for doc in mycol.find():
            if doc.get("Country") not in newdict:
                newdict[doc.get("Country")] = 0
        for doc in mycol.find():
            value = newdict.get(doc.get("Country"))
            newdict[doc.get("Country")] = value + 1
        sorteddict = dict(sorted(newdict.items(), key=lambda item: item[1], reverse=True))
        top4 = []
        for country in sorteddict.keys():
            while len(top4) < 4 and country not in top4:
                top4.append(country)
        top4.sort()
        table = []
        row = []
        for tour_name in top4:
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
            "Here are some trending holiday destinations among our users. You can select them to find out more.",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return CUSTOM_COUNTRY1

    elif text == "Budget":
        update.message.reply_text("Please state your maximum budget per pax in USD. We will search for tours that are "
                                  "within your budget.")
        return REC_SOMETHING_BUDGET

    elif text == "Duration":
        update.message.reply_text("Please state your desired duration of stay. We will search for tours that are "
                                  "within the specified duration.")
        return REC_SOMETHING_DURATION

    elif text == "Budget and Duration":
        update.message.reply_text("Please state your maximum budget per pax in USD. We will search for tours that are "
                                  "within your budget.")
        return REC_SOMETHING_BUDGET_DURATION1

def rec_something_budget(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    text = int(text)
    myquery = {"Budget per pax (in USD)": {"$lte": text}}
    results_lst = cursor_to_list(myquery)

    if len(results_lst) == 0:
        reply_keyboard = [["Budget", "Duration"], ["Budget and Duration", "Popularity"]]
        update.message.reply_text("Unfortunately, we could not find any tours that fit within your budget. You can "
                                  "instead increase your budget or choose one of the other options offered. How would "
                                  "you like to search for itineraries?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return REC_SOMETHING

    else:
        reply_keyboard = list_to_keyboard(results_lst)
        global itineraries
        itineraries = reply_keyboard
        update.message.reply_text(
            "Here are the tours that fit within your budget. You can select them to find out more.",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return TOURIST_VIEW

def rec_something_duration(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    text = int(text)
    myquery = {"Duration (in days)": {"$lte": text}}
    results_lst = cursor_to_list(myquery)

    if len(results_lst) == 0:
        reply_keyboard = [["Budget", "Duration"], ["Budget and Duration", "Popularity"]]
        update.message.reply_text("Unfortunately, we could not find any tours that fit within your specified duration. "
                                  "You can instead increase the duration or choose one of the other options offered. "
                                  "How would you like to search for itineraries?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return REC_SOMETHING

    else:
        reply_keyboard = list_to_keyboard(results_lst)
        global itineraries
        itineraries = reply_keyboard
        update.message.reply_text(
            "Here are the tours that fit within your duration. You can select them to find out more.",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return TOURIST_VIEW

def rec_something_budget_duration1(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    global mydict
    mydict["Budget"] = int(text)
    update.message.reply_text(f"Your budget is *USD{text}*. Please state your desired duration of stay. We will search"
                              f" for tours that are within the specified duration", parse_mode="Markdown")
    return REC_SOMETHING_BUDGET_DURATION2

def rec_something_budget_duration2(update: Update, _: CallbackContext) -> int:
    text = update.message.text
    logger.info("%s", text)
    global mydict
    results = mycol.find({"$and": [{"Budget per pax (in USD)": {"$lte": mydict.get("Budget")}},
                         {"Duration (in days)": {"$lte": int(text)}}]})
    mydict.clear()
    results_lst = []
    for result in results:
        results_lst.append(result)

    if len(results_lst) == 0:
        reply_keyboard = [["Budget", "Duration"], ["Budget and Duration", "Popularity"]]
        update.message.reply_text("Unfortunately, we could not find any tours that fit within your specified budget and "
                                  "duration. You can instead increase the budget and/or duration or choose one of the "
                                  "other options offered. How would you like to search for itineraries?",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                   resize_keyboard=True))
        return REC_SOMETHING

    else:
        reply_keyboard = list_to_keyboard(results_lst)
        global itineraries
        itineraries = reply_keyboard
        update.message.reply_text(
            "Here are the tours that fit within your budget and duration. You can select them to find out more.",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return TOURIST_VIEW

def done(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s ended the conversation.", user.first_name)
    update.message.reply_text(
        "Goodbye! I hope I managed to assist you and that we can talk again some day.",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def cursor_to_list(query):
    results = mycol.find(query)
    results_lst = []
    for result in results:
        results_lst.append(result)
    return results_lst

def list_to_keyboard(lst):
    table = []
    row = []
    sorting = []
    for result in lst:
        tour_name = result.get("Tour name")
        sorting.append(tour_name)

    sorting.sort()
    for tour_name in sorting:
        if len(row) < 2:
            row.append(tour_name)
        else:
            dup_row = copy.deepcopy(row)
            table.append(dup_row)
            row.clear()
            row.append(tour_name)
    table.append(row)
    return table

def show_itinerary_details(itinerary):
    output = ""
    for key in itinerary:
        if key == "Username" or key == "_id":
            continue
        else:
            output += "*" + key + ":* " + str(itinerary.get(key)) + "\n"
    return output

def main() -> None:
    updater = Updater("1819142055:AAFEWaUSAn7RZGFQ8qBMFXVqvAlqfspOn2A")

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERTYPE: [MessageHandler(Filters.regex("^(Tourist|Business Owner)$"), usertype)],
            REC_DESTINATION: [MessageHandler(Filters.regex("^(Yes|No)$"),
                                             rec_destination1)],
            REC_REGION1: [MessageHandler(Filters.regex("^(Africa|Asia|Australia|Antarctica|Europe|North America|"
                                                        "South America|Oceania|Recommend something for me)$"), rec_region1)],
            REC_REGION2: [MessageHandler(Filters.regex("^(View all results|View by countries|"
                                                       "View by popular countries)$"), rec_region2)],
            REC_SOMETHING: [MessageHandler(Filters.regex("^(Budget|Duration|Popularity|Budget and Duration)$"),
                                           rec_something)],
            REC_SOMETHING_BUDGET: [MessageHandler(Filters.text & ~Filters.command, rec_something_budget)],
            REC_SOMETHING_DURATION: [MessageHandler(Filters.text & ~Filters.command, rec_something_duration)],
            REC_SOMETHING_BUDGET_DURATION1: [MessageHandler(Filters.text & ~Filters.command,
                                                            rec_something_budget_duration1)],
            REC_SOMETHING_BUDGET_DURATION2: [MessageHandler(Filters.text & ~Filters.command,
                                                            rec_something_budget_duration2)],
            TOURIST_SELECT: [MessageHandler(Filters.regex("^(Select this itinerary|Go back)$"), tourist_select)],
            TOURIST_VIEW: [MessageHandler(Filters.text & ~Filters.command, tourist_view)],
            CUSTOM_COUNTRY1: [MessageHandler(Filters.text & ~Filters.command, custom_country1)],
            CUSTOM_COUNTRY2: [MessageHandler(Filters.regex("^(View all results|Filter by budget|Filter by duration|"
                                                           "Filter by budget and duration)$"), custom_country2)],
            CUSTOM_COUNTRY_BUDGET: [MessageHandler(Filters.text & ~Filters.command, custom_country_budget)],
            CUSTOM_COUNTRY_DURATION: [MessageHandler(Filters.text & ~Filters.command, custom_country_duration)],
            CUSTOM_COUNTRY_BUDGET_DURATION1: [MessageHandler(Filters.text & ~Filters.command, custom_country_budget_duration1)],
            CUSTOM_COUNTRY_BUDGET_DURATION2: [MessageHandler(Filters.text & ~Filters.command, custom_country_budget_duration2)],
            TOURIST_NO_ITINERARY: [MessageHandler(Filters.regex("^(Search for another country|Guide me)$"), tourist_no_itinerary)],
            BIZ_NO_ITINERARY: [MessageHandler(Filters.regex("^(Add an itinerary)$"), biz_no_itinerary)],
            BIZ_MAIN_MENU: [MessageHandler(Filters.regex("^(View my itineraries|Add an itinerary|Edit an itinerary|"
                                                        "Remove an itinerary)$"), biz_main_menu)],
            BIZ_VIEW1: [MessageHandler(Filters.text & ~Filters.command, biz_view1)],
            BIZ_VIEW2: [MessageHandler(Filters.regex("^(View other itineraries|Back to main menu)$"), biz_view2)],
            BIZ_EDIT1: [MessageHandler(Filters.text & ~Filters.command, biz_edit1)],
            BIZ_EDIT2: [MessageHandler(Filters.regex("^(Company|Region|Country|Tour name|Budget per pax \(in USD\)|"
                                                     "Duration \(in days\)|Website|Description)$"), biz_edit2)],
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
            ADD_WEBSITE: [MessageHandler(Filters.text & ~Filters.command, add_website)],
            ADD_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, add_description)],
        },
        fallbacks=[CommandHandler("done", done)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()

