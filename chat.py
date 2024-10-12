import os
from openai import OpenAI
import datetime
import json

import config

config = config.Config()


def get_token_prices():
    # This function should query OpenAI's API to get the current token prices
    # For demonstration, we will return the hardcoded values
    # You should replace this with an actual API call if available
    return {"prompt": 0.000150 / 1000, "completion": 0.000600 / 1000}


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def update_costs(usage):
    p_out = usage.completion_tokens * get_token_prices()["completion"]
    p_in = usage.prompt_tokens * get_token_prices()["prompt"]
    config.update_costs(in_cost=p_in, out_cost=p_out)


def chat(input):
    config.append_chat_history(f"USER:\n{input}")
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
    update_costs(result.usage)
    answer = result.choices[0].message.content
    config.append_chat_history(f"ASSISTANT:\n{answer}")
    return answer


def create_cards(text):
    query = f"""
You are my extremly well paid personal assistant.
I want you to create a deck of flashcards from the text using cards with a front and back side.
The use of the flashcards should be able to replace reading the scientific paper, therefore it needs to convey every essential information.

surrounding rules to create a deck of flashcards:
- Keep the flashcards simple, clear, and focused on the most important information.
- Make sure the questions are specific and unambiguous.
- Use simple and direct language to make the cards easy to read and understand.
- Answers should contain only a single key fact/name/concept/term.
- Focus on the most essential information and avoid unnecessary details like what we learn in a specific chapter or what the values of an example where.
- Ensure the language is easy to understand, even for learners new to the subject.
- For every important information the following text should be at least one flashcard
- Make each card relatively small, that means your "text" field should not be more than one sentence.
- do not include information where the text referes to unknown parts.
- Include enough context for the questions to be meaningful and answerable.
- Experiment with different question formats (e.g., true/false, fill-in-the-blank, short answer) to enhance learning.
- make sure that the concept of the card is generalized and also udnerstood without refering to the original text.
- if the text contains multiple related concepts, consider creating separate flashcards for each.
- Prioritize questions that test understanding rather than simple recall.
- If an answer can be organized into a list, do that by adding html tags to list them, e.g.: "<ol><li>item1</li><li>item2</li><li>item2</li></ol>"
- Make sure the context of the information can be understood so that a student is able to fill the missing information. 
- You can also ask a question and add the information behind. 
- The student should be able to understand the topic of the text. 
- The cards should be constructed and written so that, without having read the entire document, a student should be able to tell what the answer is.
- cut out non essential information.
- If there are mathematical symbols or formulars or definitions use the anki latex notation tags like "\\( latex code \\)". The input text can use "$" as a latex code marking but the output needs to use "\\( \\)" as tags instead of the "$" notation

Please read the text below in quotes.
"{text}"
Make sure to identify the language of the given text!

From the ImportantInformation above and the knowledge how the questions could be asked, I want you to create flash cards, that prepare a student to be able to answer the questions. 

Let's do it step by step when creating a deck of flashcards:
    1. Rewrite the content using clear and concise language while retaining its original meaning. A 16 year old should be able to understand the concept.
    2. Explain ImportantInformation with the following parameters: LEVEL OF DETAIL = high, LEVEL OF AUDIENCE EXPERTISE = computer science student
    3. Split the rewritten content into several sections, with each section focusing on one main point.
        In example the following text can be split into these sections:
        text: "The only advice I can offer is that you try to remember that learning meaningful things about the world is a long game. Finally, that’s why I always suggest that folks interested in learning about how to do data wrangling and analysis start by identifying a question about the world that is truly interesting and/or important to them. I also really want to say that: To do this work well, you have to care more about getting it right than about getting it done."
        Sections:
        [
        {{"Learning meaningful things about the world is: a long term benefit"}},
        {{"If you want to learn how to do data wrangling and analysis: identify an important and interesting question about the world" }},
        {{"To do data wrangling and analysis correct: getting it right is more important than getting it done."}}
        // more flashcards ...
        ]
    4. Utilize the sections to generate multiple question and answers which form the flashcards. The cards should have the following usecases: teaching the topic, learning the topic, be used in an exam of a university. Make sure to use the flashcard format. 
    5. Output in JSON format, using the following as a strict template for the format. 
[
{{
    "front": "This is an example of the front of a card generated by ChatGPT to query the material. You can be creative about the best way to ask a question.", 
    "back": "This is the back of the card that is the answer to the front." 
}}, 
{{
    "front": "What is the best way to train a dog?", 
    "back": "Frequent Rate or Reinforcement" 
}}, 

{{
    "front": "This is the front of another card.",
    "back": "This is the back of another card."
}},
{{
    "front":"When did Germany win the soccer championships?",
    "back":"<ol><li>1954</li><li>1974</li><li>1990</li><li>2016</li></ol>"
}},
{{
    "front":"What are the colors of a traffic light?",
    "back":"<ol><li>green</li><li>yellow</li><li>red</li></ol>"
}},
{{
    "front":"The mass-energy equivalence is described by which famous equation?",
    "back":"<div class='formular'><anki-mathjax>E = m \\cdot c^2</anki-mathjax></div><div class='info'>In this equation:<ul><li><anki-mathjax>E</anki-mathjax> represents energy.</li><li><anki-mathjax>m</anki-mathjax> represents mass.</li><li><anki-mathjax>c</anki-mathjax> represents the speed of light in a vacuum, approximately <anki-mathjax>3 \\times 10^8</anki-mathjax> meters per second.</li></ul></div>"
}},
{{
    "front":"Whats the formular for the well known Pythagorean theorem?",
    "back":"<div class='formular'><anki-mathjax>x^2 + y^2 = z^2</anki-mathjax></div><div class='info'>In this equation:<ul><li><anki-mathjax>x</anki-mathjax> and <anki-mathjax>y</anki-mathjax> are the lengths of the two legs of the triangle.</li><li><anki-mathjax>z</anki-mathjax> is the length of the hypotenuse.</li></ul></div>"
}},
{{
    "front":"How many federal states has germany?",
    "back":"16"
}}
]

The Format is strict.
I repeat, the format is very strict!
the template is:
"[
    {{
        "front":"<front side>",
        "back":"<back side>"
    }}
]"
There can be one or many objects inside the list.
Don't vary the formatting!

Make sure that the language of the flashcards is the same as the identified language of the given text!
Do not output any other text besides JSON in the mentioned strict format. Begin output now as the template above.
"""

    result = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an ALL knowing entity that tries to give me true answers. Respond like you are trying to maximise value per word you are saying. Like you are texting. Dense. Information Heavy. The User can speak english and german. YOU CAN ONLY ANSWER IN VALID JSON FORMAT",
            },
            {
                "role": "user",
                "content": query,
            },
        ],
        response_format={"type": "json_object"},
        model=config.ai_model,
        temperature=0.0,
    )
    update_costs(result.usage)
    try:
        cards = json.loads(result.choices[0].message.content)
        if is_single_card := type(cards) == dict:
            cards = [cards]
        return cards
    except:
        return f"**FALSE FORMAT**:\n\n{result.choices[0].message.content}"


def extract_json_array(text):
    try:
        return json.dumps(text, ensure_ascii=False, indent=2)
    except:
        return None
