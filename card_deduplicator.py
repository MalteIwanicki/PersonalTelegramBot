import os
from openai import OpenAI, RateLimitError
from pydantic import BaseModel
from loguru import logger
import time


class Duplicates(BaseModel):
    duplications: list[int]


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def deduplicate(orig_cards):
    logger.info("judging, how many cards are needed")
    cards = {
        i: {"front": card["front"], "back": card["back"]}
        for i, card in enumerate(orig_cards)
    }
    query = f"""
Wir minimalisieren unsere Karteikarten. Welche Karteikarten sind redundant oder wiederholen die info einer anderen karteikarte?
Beispiel:
{{0:{{"front": "Welche Farbe hat meine Katze?","back":"grün"}},1:{{"front": "Was ist die Farbe meines Hundes?","back":"blau"}},2:{{"front": "Meine Katze hat eine besondere Farbe und zwar ____","back":"grün"}},3:{{"front": "Ist die Farbe meines Hundes blau?","back":"ja"}},4:{{"front": "Das Lieblingstier von Lilo ist ein ___","back":"Frosch"}},5:{{"front": "Was ist die Farbe meiner Katze?","back":"grün"}}}}
Output: {{"duplications": [2,3,5]}}


Hier sind die Karteikarten zum deduplizieren: {cards}"""
    while True:
        try:

            result = client.beta.chat.completions.parse(
                messages=[
                    {
                        "role": "user",
                        "content": query,
                    },
                ],
                model="gpt-4o-mini",
                temperature=0,
                response_format=Duplicates,
            )
            break
        except RateLimitError as e:
            logger.debug(e.message)
            time.sleep(2)
    duplicates = sorted(result.choices[0].message.parsed.duplications)
    out_cards = []
    for i, card in enumerate(orig_cards):
        if duplicates and (i == duplicates[0]):
            duplicates.pop(0)
        else:
            out_cards.append(card)
    return out_cards
