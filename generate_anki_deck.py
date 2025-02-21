import genanki
import datetime

MODEL = genanki.Model(
    1607392319,
    "Simple Model",
    fields=[{"name": "Question"}, {"name": "Answer"}, {"name": "Extra"}],
    templates=[
        {
            "name": "Card 1",
            "qfmt": '<div class="tags">{{Tags}}</div>{{Question}}<div class="extra">{{hint:Extra}}</div>',
            "afmt": '<div class="tags">{{Tags}}</div>{{Question}}<hr id="answer">{{Answer}}<div class="extra">{{hint:Extra}}</div>',
        },
    ],
    css="""body {
    background-color: #2B2B2B;
    color: #FFFFFF;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 18px;
    padding: 20px;
    border: 2px solid #00C58E;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
    margin: 20px;
}

hr#answer {
    border: none;
    border-top: 1px solid #FFFFFF;
    margin: 20px 0;
}

.extra, .tags-container {
    display: none;
}

.extra{
    display: block;
    background-color: #2B2B2B;
    color: #00C58E;
    padding: 10px;
    margin-top: 20px;
    border-radius: 10px;
 display: block;

font-size:0.7em;
opacity:0.5;
}


.tags {
    display: block;
opacity:0.3;
font-size:0.5em;
padding-bottom:0.8em;
}
""",
)


def generate_deck(deck, filename):
    notes = [
        genanki.Note(model=MODEL, fields=[card["front"], card["back"], card["comment"]])
        for card in deck
    ]
    new_deck = genanki.Deck(2059400110, "New Cards")
    [new_deck.add_note(note) for note in notes]
    genanki.Package(new_deck).write_to_file(filename)
    return filename
