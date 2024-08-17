import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import requests
import telebot
import random

from telebot import types
from source.config import Config
from source.shell.game_setup import Character

from source.shell.settings import names, classes, races

bot = telebot.TeleBot(
    token=Config.TELEGRAM_BOT_TOKEN
)

def make_markups(categories):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category_ in categories:
        button = types.KeyboardButton(category_)
        markup.add(button)

    return markup

# // TODO: make database
# Нужно для идентификации администратора
admin_id = {
    "admin_id": "uuid",
}

# // TODO: make database
# Нужно для идентификации пользователей
user_ids = {
    "user_id": "uuid",
}

BASE_URL = "http://localhost:8000/"
def post_request(endpoint, data=None):
    response = requests.post(f"{BASE_URL}{endpoint}", json=data)
    return response.json()

def get_request(endpoint):
    response = requests.get(f"{BASE_URL}{endpoint}")
    return response.json()

@bot.message_handler(commands=['game_create'])
def start(message):
    command_text = message.text.split()
    if len(command_text) != 2:
        bot.send_message(message.chat.id, "Invalid command")
        return
    
    n_players = command_text[1]
    n_AIs = command_text[2]

    game_data = {
        "n_ai": n_AIs,
        "n_players": n_players,
    }
    result = post_request("/game/create", data=game_data)
    bot.send_message(message.chat.id, result)

    for i in range(n_AIs):
        bot.send_message(message.chat.id, f"Создаём игрока AI {i+1}...")
        player_data = {
            "is_ai": True,
            "generate_auto": True,
        }
        result = post_request("/player/add", data=player_data)
        bot.send_message(message.chat.id, result)

    bot.send_message(message.chat.id, "Игроки AI созданы. Далее создание игроков вручную...")


@bot.message_handler(commands=['player_add'])
def player_add(message):
    character = Character()

    def create_character(message):
        if message.text == "Да":
            bot.send_message(message.chat.id, "Создаём игрока...")
            player_data = {
                "is_ai": False,
                "generate_auto": True,
            }
            result = post_request("/player/add", data=player_data)
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, "Процесс создания игрока вручную...")
            bot.send_message(message.chat.id, "Введите имя игрока или выбирете из случайных:", reply_markup=make_markups(random.choices(names, k=5)))
            bot.register_next_step_handler(message, name_input)

    def name_input(message):
        character.name = message.text
        bot.send_message(message.chat.id, f"Имя игрока: {message.text}", reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id, "Укажите класс игрока или выберите из случайных:", reply_markup=make_markups(random.choices(classes, k=5)))
        bot.register_next_step_handler(message, class_input)
    def class_input(message):
        character.character_class = message.text
        bot.send_message(message.chat.id, f"Класс игрока: {message.text}", reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id, "Укажите расу игрока или выберите из случайных:", reply_markup=make_markups(random.choices(races, k=5)))
        bot.register_next_step_handler(message, race_input)
    def race_input(message):
        character.race = message.text
        bot.send_message(message.chat.id, f"Раса игрока: {message.text}", reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id, "Укажите историю игрока.")
        bot.register_next_step_handler(message, backstory_input)
    def backstory_input(message):
        character.backstory = message.text
        bot.send_message(message.chat.id, f"История игрока: {message.text}")
        player_data = {
            "generate_auto": False,
            "is_ai": False,
            "name": character.name,
            "character_class": character.character_class,
            "race": character.race,
            "backstory": character.backstory,
        }
        result = post_request("/player/add", data=player_data)
        bot.send_message(message.chat.id, result)

    bot.send_message(message.chat.id, "Создание игрока. \nСоздать генеративно?", make_markups(["Да", "Нет"]))
    bot.register_next_step_handler(message, create_character)

@bot.message_handler(commands=['create_adventure'])
def create_adventure(message):
    bot.send_message(message.chat.id, "Создание приключения...")
    
    adventure_data = {
        "admin_uuid": message.from_user.id,
        "dm_intro": None,
        "create_music": False,
        "create_image": False
    }

    bot.send_message(message.chat.id, "Создать вступление DM генеративно?")


raise NotImplementedError(
    "Телеграм бот не реализован.. Однако есть возможность использовать API для создания своего бота или любого приложения."
)
bot.polling()