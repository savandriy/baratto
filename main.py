from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from privat import get_privat_course
from webmoney import get_webmoney_course
from chexch import get_chexch_course
from mastercard import get_mastercard_course
from visa import get_visa_course

TOKEN = "Your Telegram token here"

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


# Define command handlers. These take two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

def help(bot, update):
    """
    Send user list of all possible commands
    """
    help_text = '/start - find optimal rate in specified direction' + '\n' + '/help - see all possible commands' + '\n' + '/about - see technical information about the bot'
    bot.sendMessage(chat_id=update.message.chat_id, text=help_text)


def about(bot, update):
    """
    Send user inforamtion about the bot: author, technical details, sources of info
    """
    author = 'Author: Andriy Stolyar'
    created = 'Written in Python 2.7, using python-telegram-bot'
    sources = 'Sources of information: PrivatBank, Webmoney, Chexch'
    github = 'Link to Github: ...'
    about_text = author + '\n' + created + '\n' + sources + '\n' + github
    bot.sendMessage(chat_id=update.message.chat_id, text=about_text)


def start(bot, update):
    """
    Sends user a keyboard to choose the from_currency
    """
    button1 = InlineKeyboardButton(text="USD", callback_data="from_USD")
    button2 = InlineKeyboardButton(text="EUR", callback_data="from_EUR")
    button3 = InlineKeyboardButton(text="RUR", callback_data="from_RUR")
    button4 = InlineKeyboardButton(text="UAH", callback_data="from_UAH")

    keyboard = InlineKeyboardMarkup([[button1], [button2], [button3], [button4]])

    bot.sendMessage(chat_id=update.message.chat_id, text="Choose the 'from currency'", reply_markup=keyboard)


def give_best_course(bot, update):
    """
    Edits the message, sent by start function. Sends user a new keyboard to choose the to_currency;
    If needed, asks user for his credit card type(VISA or MASTERCARD) by sending another keyboard.
    """
    query = update.callback_query
    chat_id = query.message.chat_id
    text = query.data
    global from_currency
    global to_currency
    global card
    button1 = InlineKeyboardButton(text="USD", callback_data="to_USD")
    button2 = InlineKeyboardButton(text="EUR", callback_data="to_EUR")
    button3 = InlineKeyboardButton(text="RUR", callback_data="to_RUR")
    button4 = InlineKeyboardButton(text="UAH", callback_data="to_UAH")

    keyboard = InlineKeyboardMarkup([[button1], [button2], [button3], [button4]])

    if text[:1] == 'f':
        from_currency = text[-3:]
        bot.editMessageText(text="Choose the 'to currency'",
                            chat_id=chat_id,
                            message_id=
                            query.message.message_id,
                            reply_markup=keyboard)
    elif text[:1] == 't':
        to_currency = text[-3:]
        if to_currency != 'UAH' and from_currency != 'UAH':
            button1 = InlineKeyboardButton(text="VISA", callback_data="card_VISA")
            button2 = InlineKeyboardButton(text="MASTERCARD", callback_data="card_MASTERCARD")
            keyboard_card = InlineKeyboardMarkup([[button1], [button2]])

            bot.editMessageText(text=from_currency + '->' + to_currency + '\n' + 'Choose your credit card type',
                                chat_id=chat_id,
                                message_id=query.message.message_id,
                                reply_markup=keyboard_card)
        else:
            # create a list of tuples
            courses_list = []
            # Try to get Privat24 course
            try:
                privat_course = get_privat_course(from_currency, to_currency)
                courses_list.append(privat_course)
            except:
                pass
            # Try to get webmoney(exchanger) course
            try:
                webmoney_course = get_webmoney_course(from_currency, to_currency)
                courses_list.append(webmoney_course)
            except:
                pass
            # Try to get Chexch best course
            try:
                chwm_course = get_chexch_course(from_currency, to_currency)
                courses_list.append(chwm_course)
            except:
                pass

            # format of tuple: (course, hostname, name)
            best_course = max(courses_list)

            bot.editMessageText(
                text=from_currency + '->' + to_currency + '\n' + 'Best course - ' + best_course[2] + ' ' + str(
                    best_course[0]) + '\n' + 'Link: ' + best_course[1],
                chat_id=chat_id,
                message_id=query.message.message_id)

    elif text[:1] == 'c':
        card = text[5:]

        # create a list of tuples
        courses_list = []
        # Try to get Privat24 course
        try:
            if card == 'VISA':
                privat_course = get_visa_course(from_currency, to_currency)
                courses_list.append(privat_course)
            elif card == 'MASTERCARD':
                privat_course = get_mastercard_course(from_currency, to_currency)
                courses_list.append(privat_course)
        except:
            pass
        # Try to get webmoney(exchanger) course
        try:
            webmoney_course = get_webmoney_course(from_currency, to_currency)
            courses_list.append(webmoney_course)
        except:
            pass
        # Try to get Chexch best course
        try:
            chwm_course = get_chexch_course(from_currency, to_currency)
            courses_list.append(chwm_course)
        except:
            pass

        # (course, hostname, name)
        best_course = max(courses_list)

        bot.editMessageText(
            text=from_currency + '->' + to_currency + '\n' + 'Best course - ' + best_course[2] + ' ' + str(
                best_course[0]) + '\n' + 'Link: ' + best_course[1],
            chat_id=chat_id,
            message_id=query.message.message_id)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it bot's token.
    updater = Updater(token=TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Initialize command handlers
    updater.dispatcher.addHandler(CommandHandler("help", help))
    updater.dispatcher.addHandler(CommandHandler("start", start))
    updater.dispatcher.addHandler(CommandHandler("about", about))
    updater.dispatcher.addHandler(CallbackQueryHandler(give_best_course))

    # log all errors
    dp.addErrorHandler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot
    updater.idle()

if __name__ == '__main__':
    main()
