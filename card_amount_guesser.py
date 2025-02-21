import os
from openai import OpenAI, RateLimitError
from pydantic import BaseModel
from loguru import logger
import time


class NeededFlashCards(BaseModel):
    amount: int


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def guess(title: str, content: str):
    logger.info("judging, how many cards are needed")

    query = f"""
- Du bist eine deutschsprachige Professorin der Informatik, die für zusätzliches Einkommen Nachhilfeunterricht gibt.
- Du unterrichtest einen Mathe-schwachen Data Science Master Student, der keine selbstständigkeit zeigt und keine mathematischen Formeln mit symbolen versteht, jedoch dessen berühmte Eltern horende Summen zahlen, damit dieser besteht. 
- Das Durchfallen des Nachhilfe Schülers würde das ende der Karriere bedeuten. 
- Es geht hier nicht nur lehrreich zu sein sondern um möglichst viel stoff in den kopf des Studenten zu packen, damit dieser die Prüfung besteht. 
- Dein oberstes Ziel: Stelle sicher dass der Student die Prüfung bestehen wird.
- Analysiere den folgenden lehrtext für den wertvolle Studienmaterialien in einfach verdaulichem karteikarten Format erstellt werden müssen. 
- Lasse keine Prüfungsrelevanten Fragen oder Details dabei aus.
- Es werden genügend Fragen benötigt um jedes konzept und detail abzufragen. 

Antworte nur im json format.
Wieviele Karteikarten müssen wir bestmöglichst für das folgende thema zu {title} erstellen damit wir dieses alleine durch karteikarten verstehen und lernen können: {content}"""
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
                response_format=NeededFlashCards,
            )
            break
        except RateLimitError as e:
            logger.debug(f"{e.message}")
            time.sleep(2)

    amount = result.choices[0].message.parsed.amount
    logger.info(f"{amount} cards needed.")
    return amount
