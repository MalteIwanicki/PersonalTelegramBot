import genanki
import datetime

MODEL = genanki.Model(
    1607392319,
    "Simple Model",
    fields=[
        {"name": "Question"},
        {"name": "Answer"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{Question}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}',
        },
    ],
)


def generate_deck(deck):
    notes = [
        genanki.Note(model=MODEL, fields=[card["front"], card["back"]]) for card in deck
    ]
    new_deck = genanki.Deck(2059400110, "New Cards")
    [new_deck.add_note(note) for note in notes]
    prefix = datetime.datetime.now().strftime("%Y%m%dT%H%M")
    filename = f"{prefix}_deck.apkg"
    genanki.Package(new_deck).write_to_file(filename)
    return filename
