import json
import os


class Config:
    CONFIG_FILE = "files/config.json"

    DEFAULT_CONFIG = {
        "ai_model": "gpt-4.1",
        "chat_mode": "chat",
        "anki_deck": [],
        "chat_history": "",
    }

    def __init__(self):
        self.initiate_config()
        self.read_keys = {}

    def initiate_config(self):
        if not os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as file:
                json.dump(self.DEFAULT_CONFIG, file, indent=2, ensure_ascii=False)

    def get(self, key=None, default=""):
        if not key in self.read_keys:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                if key is None:
                    self.read_keys = config
                    return self.read_keys
                self.read_keys[key] = config.get(key, default)
        return self.read_keys[key]

    def update(self, key, value):
        config = self.get()
        config[key] = value
        self.read_keys[key] = value
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

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
    def anki_deck(self):
        return self.get("anki_deck", [])

    @anki_deck.setter
    def anki_deck(self, value):
        self.update("anki_deck", value)

    @property
    def ai_model(self):
        return self.get("ai_model", "gpt-4.1")

    @ai_model.setter
    def ai_model(self, value):
        self.update("ai_model", value)
