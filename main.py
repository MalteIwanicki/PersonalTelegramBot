import os
from functools import wraps

import json
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import chat
from generate_anki_deck import generate_deck

with open("config.json", "r", encoding="utf-8") as f:
    conf = json.load(f)
deck = conf["deck"]

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
    "blank": "chats with chatgpt",
    "clear": "clears chathistory",
    "help": "help",
    "costs": "Shows the costs of the OpenAI API",
    "anki": "Creates Anki Cards from the input text",
    "export_anki": "exports the current anki Deck to an .apkg file and clears it",
    "set_model": "Choose the GPT model to use",
    "chat_history":"the current chat history"
}

@bot.message_handler(commands=["set_model"])
@authorized_only
def set_model(message):
    markup = InlineKeyboardMarkup()
    models = ["gpt-4o-mini", "gpt-4o"]
    for model in models:
        markup.add(InlineKeyboardButton(model, callback_data=f"set_model_{model}"))
    bot.send_message(message.chat.id, "Choose a GPT model:", reply_markup=markup)
    
@bot.callback_query_handler(func=lambda call: call.data.startswith("set_model_"))
@authorized_only
def callback_set_model(call):
    selected_model = call.data.split("set_model_")[1]
    with open("config.json","r") as f:
        conf = json.load(f)
    conf["model"] = selected_model
    with open("config.json","w") as f:
        json.dump(conf, f, indent=4)
    bot.answer_callback_query(call.id, f"Model set to {selected_model}")
    

@bot.message_handler(commands=["help"])
def send_help(message):
    help_text = "Here are the available commands:\n\n"
    for command, description in commands.items():
        help_text += f"{command} - {description}\n"
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=["clear"])
@authorized_only
def clear(message):
    chat.clear_chathistory()
    bot.send_message(message.chat.id, f"🧹 chat cleared 🧽")

 
@bot.message_handler(commands=["costs"])
@authorized_only
def get_costs(message):
    with open("config.json", encoding="utf-8") as json_file:
        conf = json.load(json_file)
    costs = conf["costs"]
    result = f'*Total:* {round(costs["total"],2)}€\n*In:* {round(costs["in"],2)}€\n*Out:* {round(costs["out"],2)}€'
    bot.send_message(message.chat.id, result, parse_mode="Markdown")

@bot.message_handler(commands=["chat_history"])
@authorized_only
def chat_history(message):
    with open("chathistory.txt", "rb") as file:
        bot.send_document(message.chat.id, file)

@bot.message_handler(commands=["export_anki"])
@authorized_only
def export_anki(message):
    global deck
    file = generate_deck(deck)
    with open(file, "rb") as file:
        bot.send_document(message.chat.id, file)
    deck = []
    with open("conf.json", "r", encoding="utf-8") as f:
        conf = json.load(f)
    conf["deck"]=deck
    with open("conf.json", "w", encoding="utf-8") as f:
        json.dump(conf, f, indent=4)
    os.remove(file)


@bot.message_handler(commands=["anki"])
@authorized_only
def create_anki_cards(message):
    text = message.text.replace("/anki ", "")
    cards = chat.create_cards(text)
    if type(cards) == str:  # not valid json format
        bot.send_message(message.chat.id, f"# **NOT VALID JSON**\n\n{cards}", )
        return None
    for card in cards:
        markup = InlineKeyboardMarkup(row_width=2)

        sent_message = bot.send_message(
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
        bot.edit_message_reply_markup(
            chat_id=sent_message.chat.id,
            message_id=sent_message.message_id,
            reply_markup=markup,
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
@authorized_only
def delete_card(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
@authorized_only
def add_card(call):
    card_text = call.message.text
    deck.append(json.loads(card_text))
    with open("config.json","r", encoding="utf-8") as f:
        conf = json.load(f)
    conf["deck"]=deck
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(conf, f, indent=4)
    bot.answer_callback_query(
        call.id, f"Card added to deck!\nDeck contains  {len(deck)} cards."
    )
    bot.delete_message(call.message.chat.id, call.message.message_id)



@bot.message_handler(func=lambda m: m.text[0]!="/")
@authorized_only
def chat_response(message):
    answer = chat.chat(message.text)
    try:
        bot.send_message(message.chat.id, answer, parse_mode="Markdown")
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(message.chat.id, answer)


if __name__ == "__main__":
    bot.infinity_polling()
