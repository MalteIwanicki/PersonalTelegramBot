import os
from openai import OpenAI, RateLimitError
from pydantic import BaseModel
from loguru import logger
import time


class Topic(BaseModel):
    title: str
    start: int
    end: int


class Topics(BaseModel):
    topics: list[Topic]


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def split(text: str, max_len=8000):
    logger.info("Split text into topics")

    query = f"""Deine Aufgabe besteht darin den kompletten Text in Kapitel zu unterteilen. Text der nicht zugeordnet werden kann muss in ein "other" kapitel. Benenne dabei jeweils den Kapitel Titel und die Zeichen, die dazu gehören. Hier ein Beispiel:
Eingabetext:
"Meine Katze liebt Kaugummi. Bäume wachsen langsam. So das wars, dankeschön"
Antwort:
{{"topics":[
{{"title":"1. Meine Katze","start":0,"end":27}},
{{"title":"2. Bäume","start":27,"end":51}},
{{"title":"3. other","start":51, "end":73}}
]
}}
Antworte nur im json format.
Die end position ist exclusiv, wie in python.
Bei Fachwörtern füge den englischen fachbegriff in Klammern hinzu.
Hier ist der zu bearbeitende Text der von zeichen 0 bis {len(text)-1} in mindestens {len(text)//max_len} kapitel unterteilt werden muss: {text}"""
    try:
        while True:
            result = client.beta.chat.completions.parse(
                messages=[
                    {
                        "role": "user",
                        "content": query,
                    },
                ],
                model="gpt-4o-mini",
                temperature=0,
                response_format=Topics,
            )
            break
    except RateLimitError as e:
        logger.debug(e.message)
        time.sleep(2)
    logger.debug(f"{result}")
    results = result.choices[0].message.parsed
    logger.info(f"{len(results.topics)} topics found.")
    topics = {topic.title: text[topic.start : topic.end] for topic in results.topics}
    output = {}
    for title, content in topics.items():
        if len(content) <= max_len:
            output[title] = content
        elif len(content) < 5:
            continue
        else:
            subs = split(content)
            id, title = title.split(" ", 1)
            for subtitle, subcontent in subs.items():
                subid, subtitle = subtitle.split(" ", 1)
                output[f"{id}{subid} {title} - {subtitle}"] = subcontent
    return output
