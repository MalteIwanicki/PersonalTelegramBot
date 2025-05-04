import os
from openai import OpenAI, RateLimitError
import datetime
import json
from pydantic import BaseModel
from loguru import logger
import config
import card_amount_guesser
import time

config = config.Config()


class AnkiCard(BaseModel):
    front: str
    back: str


class AnkiDeck(BaseModel):
    ankicards: list[AnkiCard]


def get_token_prices():
    # This function should query OpenAI's API to get the current token prices
    # For demonstration, we will return the hardcoded values
    # You should replace this with an actual API call if available
    return {"prompt": 3 / 1_000_000, "completion": 12 / 1_000_000}


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def chat(text_input):
    config.append_chat_history(f"USER:\n{text_input}")
    result = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an ALL knowing entity that tries to give me true answers. Respond like you are trying to maximise value per word you are saying. Like you are texting. Dense. Information Heavy. The User can speak english and german",
            },
            {
                "role": "user",
                "content": config.chat_history,
            },
        ],
        model=config.ai_model,
        temperature=0.0,
    )
    answer = result.choices[0].message.content
    config.append_chat_history(f"ASSISTANT:\n{answer}")
    return answer


def create_cards(content, ai_model=config.ai_model):
    needed_cards = card_amount_guesser.guess(content)
    query = f"""**Ich möchte, dass du als professioneller Anki-Kartenersteller agierst**, der aus dem von mir bereitgestellten Text optimal strukturierte Anki-Karten erstellt.

### Vorgehen:
1. **Prüfung der Inhalte**: Analysiere den bereitgestellten Text aus dem {needed_cards} Karten erstellt werden sollen. Jede Karte muss dazu beitragen, dass das gesamte Thema verständlich bleibt, ohne Redundanzen.
2. **Optimierung der Fragen**: Formuliere Fragen so, dass sie das Konzept bestmöglich vermitteln und Wiederholungen minimiert werden.
3. **Formatierung & Struktur**:
   - Verwende das **Minimal-Informations-Prinzip**, um jede Karte so einfach wie möglich zu halten.
   - Nutze **optimierte Formulierungen**, um das Abrufen von Wissen so effizient wie möglich zu gestalten.
   - **Antworten in Listen**, wenn passend, mit `<ol><li>Item</li></ol>`-Tags für eine bessere Darstellung.
   - **Fachbegriffe zusätzlich in Englisch**, in runden Klammern.
   - **Formeln** mit '\\(latex code\\)' in Anki-Notation.
   - **Kontext** bereitstellen, damit jede Karte auch unabhängig sinnvoll ist.

### Format:
Antworte **ausschließlich im JSON-Format** mit folgender Struktur:

'''json
{{
  "ankicards": [
    {{
      "front": "Hier steht die Frage, möglichst präzise formuliert.",
      "back": "Hier steht die Antwort mit minimalem, aber vollständigem Inhalt."
    }},
    {{
      "front": "Welche Farben hat eine Ampel?",
      "back": "<ol><li>Grün</li><li>Gelb</li><li>Rot</li></ol>"
    }},
    {{
      "front": "Welche Formel beschreibt die Äquivalenz von Masse und Energie?",
      "back": "\\(E = m \\cdot c^2\\)"
    }}
  ]
}}
'''

### Ziel:
- Mindestens '{needed_cards}' Karten erzeugen.
- **Keine Duplikate, keine unnötigen Wiederholungen**.
- **Verschiedene Frageformate**, z. B. Frage/Antwort, Lückentext, Wahr/Falsch.
- **Verallgemeinertes Wissen**, nicht nur direkte Wiedergabe aus dem Text.

---

Hier ist der Vorlesungstext, den du in Karten umwandeln sollst:

'''
{content}
'''

**Erstelle jetzt mindestens '{needed_cards}' perfekt formulierte Anki-Karten!**

"""
    temperature = 0
    while True:
        try:
            result = client.beta.chat.completions.parse(
                messages=[
                    {
                        "role": "user",
                        "content": query,
                    },
                ],
                model=ai_model,
                temperature=temperature,
                response_format=AnkiDeck,
            )
            break
        except RateLimitError as e:
            logger.debug(e.message)
            time.sleep(2)
        except Exception as e:
            logger.debug(e.message)
            break
    logger.debug(f"{result}")
    cards = [card.model_dump() for card in result.choices[0].message.parsed.ankicards]
    return cards


def extract_json_array(text):
    try:
        return json.dumps(text, ensure_ascii=False, indent=2)
    except:
        return None
