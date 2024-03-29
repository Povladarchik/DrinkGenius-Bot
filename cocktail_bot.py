import os
import phrases
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from cocktail_class import Cocktail
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Telegram bot
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
bot = TeleBot(TELEGRAM_API_TOKEN, parse_mode='HTML')


# Command Handlers
@bot.message_handler(commands=['start'])
def start_command_handler(message):
    bot.reply_to(message, phrases.start_message)


@bot.message_handler(commands=['help'])
def help_command_handler(message):
    bot.reply_to(message, phrases.help_message)


@bot.message_handler(commands=['recipe'])
def recipe_command_handler(message):
    handle_command_with_cocktail_info(message, send_cocktail_info)


@bot.message_handler(commands=['similar'])
def similar_command_handler(message):
    handle_command_with_cocktail_info(message, send_similar_cocktails)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    send_cocktail_info(call.message, call.data)


# Helper Functions
def handle_command_with_cocktail_info(message, func_send):
    command_parts = message.text.split()
    cocktail_name = ' '.join(command_parts[1:]) if len(command_parts) > 1 else None

    if cocktail_name:
        func_send(message, cocktail_name)
    else:
        bot.reply_to(message, phrases.incorrect_input_message)


def send_cocktail_info(message, cocktail_name):
    cocktail = Cocktail(cocktail_name)

    image = cocktail.get_image()
    ingredients = f'<b>Ingredients:</b>\n{cocktail.get_ingredients()}'
    steps = f'<b>Recipe:\n</b>{cocktail.get_recipe()}'
    text = f'{ingredients}\n\n{steps}'

    bot.send_photo(message.chat.id, image, f'<b>{cocktail.name}</b>')
    bot.send_message(message.chat.id, text)


def send_similar_cocktails(message, cocktail_name):
    cocktail = Cocktail(cocktail_name)

    markup = InlineKeyboardMarkup(row_width=1)
    similar_cocktails = cocktail.recommend_similar_cocktails()
    options = [InlineKeyboardButton(name, callback_data=name) for name in similar_cocktails]
    markup.add(*options)

    text = f'Similar cocktails to <b>{cocktail.name}</b>'
    bot.send_message(message.chat.id, text, reply_markup=markup)


if __name__ == "__main__":
    print('Bot is running!')
    bot.infinity_polling()
