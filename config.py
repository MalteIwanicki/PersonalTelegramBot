import json
import os


class Config:
    CONFIG_FILE = "config.json"

    DEFAULT_CONFIG = {
        "ai_model": "gpt-4o",
        "chat_mode": "chat",
        "costs": {"total": 0, "in": 0, "out": 0},
        "anki_deck": [],
        "chat_history": "",
        "temp_card_content": "",
    }

    def __init__(self):
        self.initiate_config()

    def initiate_config(self):
        if not os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as file:
                json.dump(self.DEFAULT_CONFIG, file, indent=4)

    def get(self, key=None, default=""):
        with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            if key is None:
                return config
            return config.get(key, default)

    def update(self, key, value):
        config = self.get()
        config[key] = value
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

    @property
    def chat_history(self):
        return self.get("chat_history", "")

    @chat_history.setter
    def chat_history(self, value):
        self.update("chat_history", value)

    def append_chat_history(self, text):
        value = self.chat_history + "\n" + text
        self.update("chat_history", value)

    @property
    def chat_mode(self):
        return self.get("chat_mode", "chat")

    @chat_mode.setter
    def chat_mode(self, value):
        self.update("chat_mode", value)

    @property
    def costs(self):
        return self.get("costs")

    def update_costs(self, in_cost=0, out_cost=0):
        costs = self.get("costs")
        costs["in"] += in_cost
        costs["out"] += out_cost
        costs["total"] += in_cost + out_cost
        self.update("costs", costs)

    @property
    def anki_deck(self):
        return self.get("anki_deck", [])

    @anki_deck.setter
    def anki_deck(self, value):
        self.update("anki_deck", value)

    @property
    def ai_model(self):
        return self.get("ai_model", "gpt-4o")

    @ai_model.setter
    def ai_model(self, value):
        self.update("ai_model", value)

    @property
    def temp_card_content(self):
        return self.get("temp_card_content", "")

    @temp_card_content.setter
    def temp_card_content(self, value):
        self.update("temp_card_content", value)
