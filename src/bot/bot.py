import time

from telebot import TeleBot
from telebot.apihelper import ApiException
from telebot.types import ReplyKeyboardMarkup

from constants import SPORT_FULL_NAMES_TO_SHORT
from registry import registry
from secrets import TOKEN
from singleton import Singleton
from user import User
from user_history import UserHistory
from util import get_arbitrage_bets_xlsx_filename_by_short_sport_name


class BetAssistantBot(TeleBot, metaclass=Singleton):
    _NAME = 'BetAssistantNotificationBot'
    _MESSAGE_MAX_LENGTH = 4096
    _PARSE_MODE = 'Markdown'
    _HELP_TEXT = f'''
    *What can this bot do?*

With @{_NAME} arbitrage betting becomes easy as never before.
📜 Get list of pre-scanned arbitrage bets for a sport you choose
📢 Subscribe to a sport you choose and receive all the most relevant arbitrage bets as soon as they are scanned  
    
Currently @{_NAME} supports the following kinds of sports and bookmakers:
🔘 {', '.join(list(SPORT_FULL_NAMES_TO_SHORT.keys()))}
🔘 {', '.join([scraper.get_name() for scraper in registry.keys()])}
    
Other supported commands are:  
/start - start interacting with bot  
/help - list all commands and their description  
    '''

    def __init__(self):
        super().__init__(TOKEN)
        self._init_commands()
        self.set_update_listener(self.menu_listener)

    def send_long_messages(self, chat_id, strings, reply_to, parse_mode=_PARSE_MODE):
        """
        Sends messages of arbitrary length

        :param chat_id: id of the chat to message to
        :type chat_id: str
        :param strings: messages to send
        :type strings: str
        :param reply_to: id of the message to reply to
        :type reply_to: str
        :param parse_mode: parse mode applied to all strings
        :type parse_mode: str
        """
        c = 0
        for string in strings:
            while len(string) > 0:
                length = BetAssistantBot._MESSAGE_MAX_LENGTH
                while True:
                    try:
                        self.send_message(chat_id, string[:length], parse_mode=parse_mode,
                                          reply_to_message_id=reply_to)
                        c += 1
                        break
                    except ApiException:
                        length -= 10
                string = string[length:]

                # timeout every 100 messages
                if c % 100 == 0:
                    time.sleep(300)

    def _init_commands(self):
        @self.message_handler(commands=['start', 'help'])
        def command_start_handler(message):
            """
            Handles /start and /help commands
            """
            self.send_message(message.chat.id, BetAssistantBot._HELP_TEXT, parse_mode=BetAssistantBot._PARSE_MODE)

    def menu_listener(self, messages):
        for message in messages:
            user = UserHistory.get_user(message.chat.id)
            if user is None:
                user = User(message.chat.id)
            UserHistory.add_user(user)

            action_result = user.menu.choose(message.text)
            text = user.menu.current_option.prompt
            if action_result:
                text += str(action_result)

            keyboard = ReplyKeyboardMarkup()
            keyboard.add(*user.menu.get_current_options())
            self.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode=BetAssistantBot._PARSE_MODE)
            if user.menu.current_option.filename is not None:
                try:
                    with open(user.menu.current_option.filename, 'rb') as arbitrage_bets_file:
                        self.send_document(message.chat.id, arbitrage_bets_file, reply_markup=keyboard)
                except FileNotFoundError:
                    pass

            if user.menu.current_option.is_leaf():
                user.menu.current_option = user.menu.current_option.parent
            UserHistory.update_user(user)

    def notify_subscribers(self, sport_name):
        subscribers = UserHistory.get_subscribers()
        for subscriber in subscribers:
            self.notify_subscriber(subscriber, sport_name)

    def notify_subscriber(self, subscriber, sport_name):
        keyboard = ReplyKeyboardMarkup()
        keyboard.add(*subscriber.menu.get_current_options())
        try:
            with open(get_arbitrage_bets_xlsx_filename_by_short_sport_name(sport_name), 'rb') as arbitrage_bets_file:
                self.send_document(subscriber.id, arbitrage_bets_file, reply_markup=keyboard)
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    bot = BetAssistantBot()
    bot.polling(none_stop=True)
