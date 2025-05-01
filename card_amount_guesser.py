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


def guess(content: str):
    logger.info("judging, how many cards are needed")

    query = f"""Ich möchte, dass du als professioneller Anki-Kartenersteller agierst, der in der Lage ist, Anki-Karten aus dem von mir bereitgestellten Text zu erstellen.

Bei der Formulierung des Karteninhalts hältst du dich an zwei Prinzipien: Erstens das Minimal-Informations-Prinzip: Das zu lernende Material muss so einfach wie möglich formuliert werden. Einfachheit bedeutet jedoch nicht, dass Informationen verloren gehen oder schwierige Teile ausgelassen werden. Zweitens die Optimierung der Formulierung: Die Formulierung der Inhalte muss so optimiert werden, dass in kürzester Zeit die richtige Assoziation im Gehirn ausgelöst wird. Dies reduziert Fehlerquoten, erhöht die Präzision, verkürzt die Reaktionszeit und verbessert die Konzentration.

Bevor du die Karten erstellst, überprüfst du zunächst den bereitgestellten Inhalt sorgfältig, um festzustellen, wie viele Karten notwendig sind, damit alle relevanten Informationen erhalten bleiben. Du stellst sicher, dass kein Wissen verloren geht und dass jede Karte eine sinnvolle, vollständige Lerneinheit darstellt.

Antworte nur im json format.
Wieviele Karteikarten müssen wir bestmöglichst für den folgenden text erstellen damit wir dieses alleine durch karteikarten verstehen und lernen können ohne dabei sich zu wiederholen: {content}"""
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
