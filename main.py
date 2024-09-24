import os
from functools import wraps

import json
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import chat
from generate_anki_deck import generate_deck

with open("deck.json", "r", encoding="utf-8") as f:
    deck = json.load(f)

token = os.environ.get("TELEGRAM_API_TOKEN")
bot = telebot.TeleBot(token)

OWNER_ID = 1310360635
def authorized_only(f):
    @wraps(f)
    def decorated_function(message, *args, **kwargs):
        if message.from_user.id != OWNER_ID:
            bot.send_message(message.chat.id, "you are not authorized.")
            return
        return f(message, *args, **kwargs)
    return decorated_function

commands = {
    "/help": "help",
    "/costs": "Shows the costs of the OpenAI API",
    "/ask": "sends a message to chatgpt",
    "/anki": "Creates Anki Cards from the input text",
    "/exportAnki": "exports the current anki Deck to an .apkg file and clears it",
}


@bot.message_handler(commands=["help"])
def send_help(message):
    help_text = "Here are the available commands:\n\n"
    for command, description in commands.items():
        help_text += f"{command} - {description}\n"
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=["costs"])
@authorized_only
def get_costs(message):
    with open("costs.json", "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    result = f'*Total:* {round(data["total"],2)}€\n*In:* {round(data["in"],2)}€\n*Out:* {round(data["out"],2)}€'
    bot.send_message(message.chat.id, result, parse_mode="Markdown")


@bot.message_handler(commands=["ask"])
@authorized_only
def chat_response(message):
    text = message.text.replace("/ask ", "")
    result = chat.ask(text)
    bot.send_message(message.chat.id, result, parse_mode="Markdown")


@bot.message_handler(commands=["exportAnki"])
@authorized_only
def chat_response(message):
    global deck
    file = generate_deck(deck)
    with open(file, "rb") as file:
        bot.send_document(message.chat.id, file)
    deck = []
    with open("deck.json", "w", encoding="utf-8") as f:
        json.dump(deck, f, indent=4)
    os.remove(file)


@bot.message_handler(commands=["anki"])
@authorized_only
def chat_response(message):
    text = message.text.replace("/anki ", "")
    cards = chat.create_cards(text)
    if type(cards) == str:  # not valid json format
        bot.send_message(message.chat.id, cards, parse_mode="Markdown")
        return None
    for card in cards:
        markup = InlineKeyboardMarkup(row_width=2)

        sent_message = bot.send_message(
            message.chat.id,
            json.dumps(card),  # json format
            parse_mode="Markdown",
            reply_markup=markup,
        )
        delete_button = InlineKeyboardButton(
            "❌", callback_data=f"delete_{sent_message.message_id}"
        )
        add_button = InlineKeyboardButton(
            "➕", callback_data=f"add_{sent_message.message_id}"
        )
        markup.add(delete_button, add_button)
        bot.edit_message_reply_markup(
            chat_id=sent_message.chat.id,
            message_id=sent_message.message_id,
            reply_markup=markup,
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def delete_card(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def add_card(call):
    card_text = call.message.text
    deck.append(json.loads(card_text))
    with open("deck.json", "w", encoding="utf-8") as f:
        json.dump(deck, f, indent=4)
    bot.answer_callback_query(
        call.id, f"Card added to deck!\nDeck contains  {len(deck)} cards."
    )
    bot.delete_message(call.message.chat.id, call.message.message_id)


if __name__ == "__main__":
    bot.infinity_polling()
