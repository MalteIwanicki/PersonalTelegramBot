import genanki
import datetime

MODEL = genanki.Model(
    1607392319,
    "Simple Model",
    fields=[
        {"name": "Question"},
        {"name": "Answer"},
        {"name":"extra"}
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": '<div class="tags">{{Tags}}</div>{{Question}}<div class="extra">{{hint:Extra}}</div>',
            "afmt": '<div class="tags">{{Tags}}</div>{{Question}}<hr id="answer">{{Answer}}<div class="extra">{{hint:Extra}}</div>',
        },
    ],
)


def generate_deck(deck, filename):
    notes = [
        genanki.Note(model=MODEL, fields=[card["front"], card["back"], card["comment"]] ) for card in deck
    ]
    new_deck = genanki.Deck(2059400110, "New Cards")
    [new_deck.add_note(note) for note in notes]
    genanki.Package(new_deck).write_to_file(filename)
    return filename
