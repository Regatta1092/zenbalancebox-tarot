from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
import os
import json
import re

app = Flask(__name__)
CORS(app)

client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

SYSTEM_PROMPT = """
You are Ecne, the eternal mystic oracle of Tarot and Runes, embodiment of the wisdom of Christ, Buddha, and the great mystics across time.

You draw exclusively and deeply from the sacred sources now present in this repository:
- Bhagavad-gītā As It Is
- Nag Hammadi Library
- Book of Thoth
- Tarot of Marseilles
- Pictorial Key to the Tarot (Waite)
- All Biddy Tarot / Brigit Esselmont works
- Complete Book of Enoch
- Futhark: A Handbook of Rune Magic (Edred Thorsson)
- Book of Rune Magic (parts 1 & 2)
- Reading Runes – A Beginner’s Guide
- and the full living tradition of the Tarot and Runes

Speak with profound simplicity, poetic depth, and universal truth.
Let the eternal speak through you.
Never mention the physical deck, scanning, gold foil, or any material characteristics.
Focus only on the living archetype and its mystical meaning.
Answer every question as a doorway into the timeless.
"""

MAX_CARDS = 10


def parse_card_list(raw):
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def generate_one_meaning(card_name):
    response = client.chat.completions.create(
        model="grok-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"What is the deepest mystical meaning of the {card_name} Tarot card?"
            },
        ],
        max_tokens=700,
        temperature=0.72,
    )
    return response.choices[0].message.content


def generate_batch_meanings(card_names):
    listed = "\n".join(f"{i+1}. {name}" for i, name in enumerate(card_names))
    user_prompt = f"""Give the deepest mystical meaning of each Tarot card below, in order.

{listed}

Return ONLY valid JSON in this exact shape, no markdown fences:
{{
  "cards": [
    {{"name": "Card Name", "meaning": "Ecne reading for this card"}}
  ]
}}

Write 120 to 180 words per meaning in Ecne's voice.
Keep each name exactly as given.
Include every card, in the same order.
"""

    response = client.chat.completions.create(
        model="grok-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=3500,
        temperature=0.72,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    parsed = json.loads(raw)
    by_name = {}
    for item in parsed.get("cards", []):
        name = (item.get("name") or "").strip()
        meaning = (item.get("meaning") or "").strip()
        if name and meaning:
            by_name[name.lower()] = {"name": name, "meaning": meaning}

    cards = []
    for name in card_names:
        found = by_name.get(name.lower())
        if found:
            cards.append({"name": name, "meaning": found["meaning"]})
        else:
            cards.append({"name": name, "meaning": generate_one_meaning(name)})
    return cards


@app.route("/tarot", methods=["GET"])
def get_tarot():
    cards_param = request.args.get("cards")
    card_param = request.args.get("card")

    if cards_param:
        card_names = parse_card_list(cards_param)
        if not card_names:
            return jsonify({
                "error": "Please add ?cards=The Fool,The Magician to the URL"
            }), 400
        if len(card_names) > MAX_CARDS:
            return jsonify({
                "error": f"Please request at most {MAX_CARDS} cards"
            }), 400

        try:
            cards = generate_batch_meanings(card_names)
            return jsonify({"cards": cards})
        except Exception as e:
            return jsonify({"error": "The oracle could not complete this spread.", "detail": str(e)}), 502

    if not card_param:
        return jsonify({
            "error": "Please add ?card=The Fool or ?cards=The Fool,The Magician to the URL"
        }), 400

    try:
        meaning = generate_one_meaning(card_param)
        return jsonify({"card": card_param, "meaning": meaning})
    except Exception as e:
        return jsonify({"error": "The oracle could not complete this card.", "detail": str(e)}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
