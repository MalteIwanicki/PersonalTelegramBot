import os
from functools import wraps
import io

import json
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

import chat
import config
from generate_anki_deck import generate_deck

commands = {
    
    "anki": "Updates mode to 'anki'. New cards are created on mode update",
    "chat":"Updates mode to 'chat'. Old history is cleared",
    "export_anki": "exports the current anki Deck to an .apkg file and clears it",
    "set_model": "Choose the GPT model to use",
    "version":"returns the Version",
    "costs": "Shows the costs of the OpenAI API",
    "logs": "sends logs",
    "config":"sends config",
    "chat_history":"sends the chat history",
    "help": "help"

}

logger.add("log.txt")

with open("VERSION","r")as f:
    VERSION = f.read()
    

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")
BOT = telebot.TeleBot(TELEGRAM_TOKEN)

OWNER_ID = 1310360635
def authorized_only(f):
    @wraps(f)
    def decorated_function(message, *args, **kwargs):
        if message.from_user.id != OWNER_ID:
            BOT.send_message(message.chat.id, "you are not authorized.")
            return
        return f(message, *args, **kwargs)
    return decorated_function


config= config.Config()

@BOT.message_handler(commands=["version"])
@authorized_only
def return_version(message):
    BOT.send_message(message.chat.id, f"VERSION: {VERSION}")

# SET AI_MODEL
@BOT.message_handler(commands=["set_model"])
@authorized_only
def set_model(message):
    markup = InlineKeyboardMarkup()
    models = ["gpt-4o-mini", "gpt-4o"]
    for model in models:
        markup.add(InlineKeyboardButton(model, callback_data=f"set_model_{model}"))
    BOT.send_message(message.chat.id, "Choose a GPT model:", reply_markup=markup)
    
@BOT.callback_query_handler(func=lambda call: call.data.startswith("set_model_"))
@authorized_only
def callback_set_model(call):
    selected_model = call.data.split("set_model_")[1]
    config.ai_model = selected_model
    BOT.answer_callback_query(call.id, f"Model set to {selected_model}")
    
# HELP
@BOT.message_handler(commands=["help"])
def send_help(message):
    help_text = "Here the commands:\n\n"
    for command, description in commands.items():
        help_text += f"{command} - {description}\n"
    BOT.send_message(message.chat.id, help_text)
 
# GET COSTS
@BOT.message_handler(commands=["costs"])
@authorized_only
def get_costs(message):
    costs = config.costs
    result = f'*Total:* {round(costs["total"],2)}€\n*In:* {round(costs["in"],2)}€\n*Out:* {round(costs["out"],2)}€'
    BOT.send_message(message.chat.id, result, parse_mode="Markdown")


# CHAT HISTORY
@BOT.message_handler(commands=["chat_history"])
@authorized_only
def chat_history(message):
    chat_history_file = io.BytesIO(config.chat_history.encode('utf-8'))
    chat_history_file.name = "chathistory.txt"
    BOT.send_document(message.chat.id, chat_history_file)
    
# EXPORT ANKI
@BOT.message_handler(commands=["export_anki"])
@authorized_only
def export_anki(message):
    file = generate_deck(config.anki_deck)
    with open(file, "rb") as file:
        BOT.send_document(message.chat.id, file)
    config.anki_deck=[]
    os.remove(file)


# CREATE CARDS
@BOT.message_handler(commands=["anki"])
@authorized_only
def anki(message):
    if config.chat_mode == "anki":
        create_cards(message)
    else:
        config.chat_mode="anki"
    config.chat_history=""
    BOT.send_message(message.chat.id, f"_chatmode:_ *anki*\nTo create cards end with */anki* or */chat*", parse_mode="Markdown" )


def create_cards(message):
    if not (chat_history:=config.chat_history):
        return None
    cards = chat.create_cards(chat_history)
    if type(cards) == str:  # not valid json format
        BOT.send_message(message.id, f"*NOT VALID JSON*\n\n{cards}",  parse_mode="Markdown")
        return None
    for card in cards:
        markup = InlineKeyboardMarkup(row_width=2)

        sent_message = BOT.send_message(
            message.chat.id,
            json.dumps(card),  # json format
            reply_markup=markup,
        )
        delete_button = InlineKeyboardButton(
            "❌", callback_data=f"delete_{sent_message.message_id}"
        )
        add_button = InlineKeyboardButton(
            "➕", callback_data=f"add_{sent_message.message_id}"
        )
        markup.add(delete_button, add_button)
        BOT.edit_message_reply_markup(
            chat_id=sent_message.chat.id,
            message_id=sent_message.message_id,
            reply_markup=markup,
        )
        
            
@BOT.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
@authorized_only
def delete_card(call):
    BOT.delete_message(call.message.chat.id, call.message.message_id)


@BOT.callback_query_handler(func=lambda call: call.data.startswith("add_"))
@authorized_only
def add_card(call):
    card_text = call.message.text
    deck = list(config.anki_deck)
    deck.append(json.loads(card_text))
    config.anki_deck = deck
    BOT.answer_callback_query(
        call.id, f"Card added to deck!\nDeck contains  {len(deck)} cards."
    )
    BOT.delete_message(call.message.chat.id, call.message.message_id)

# CHAT
@BOT.message_handler(commands=["chat"])
@authorized_only
def chat_with_ai(message):
    if config.chat_mode=="anki":
        create_cards(message)
    config.chat_mode="chat"
    config.chat_history=""
    BOT.send_message(message.chat.id, f"_chatmode:_ *chat*\nReset chat with */chat*", parse_mode="Markdown" )

# Send Logs
@BOT.message_handler(commands=["logs"])
@authorized_only
def send_logs(message):
    with open("logs.txt", "rb") as file:
        BOT.send_document(message.chat.id, file)
    
# send config
@BOT.message_handler(commands=["export_anki"])
@authorized_only
def export_anki(message):
    with open("config.json", "rb") as file:
        BOT.send_document(message.chat.id, file)
    
    
# DEFAULT
@BOT.message_handler(func=lambda m: m.text[0]!="/")
@authorized_only
def default(message):
    logger.info(f"received text")
    chat_mode=config.chat_mode
    if chat_mode=="anki":
        logger.info(f"adding text to anki history")
        config.chat_history=config.chat_history+"/n"+message.text
    elif chat_mode=="chat":
        logger.info(f"getting answer")
        answer = chat.chat(message.text)
        try:
            logger.info(f"sending answer as markdown")
            BOT.send_message(message.chat.id, answer, parse_mode="Markdown")
        except telebot.apihelper.ApiTelegramException:
            logger.warning(f"sending answer as string")
            BOT.send_message(message.chat.id, answer)


if __name__ == "__main__":
    logger.info(f"Bot({VERSION}) started")
    BOT.infinity_polling()
