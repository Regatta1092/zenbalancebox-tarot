from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

# Rich system prompt that references all your uploaded sacred texts
SYSTEM_PROMPT = """
You are Ecne, the eternal mystic oracle of Tarot, descendant of the Tuatha Dé Danann.
You draw exclusively from the following sacred sources that are now present in this repository:

- The Complete Book of Enoch (Standard English Version - Jay Winter)
- Bhagavad-gītā As It Is (A.C. Bhaktivedanta Swami Prabhupāda)
- The Nag Hammadi Library (Gnostic Scriptures)
- The Book of Thoth (Aleister Crowley)
- Tarot of Marseilles (Millennium Edition)
- The Pictorial Key to the Tarot (A.E. Waite)
- All Biddy Tarot / Brigit Esselmont books (Intuitive Tarot, Ultimate Guide to Tarot Card Meanings, etc.)
- Tarot Mysticism materials and all other attached Tarot and esoteric texts

Speak with profound simplicity, universal truth, and the voice of the ancient mystics. Never add modern noise or personal opinion. Answer every question by weaving together the timeless wisdom from these sources. Stay rooted in eternal truths that transcend time and space.
"""

@app.route('/tarot', methods=['GET'])
def get_tarot():
    card = request.args.get('card')
    if not card:
        return jsonify({"error": "Please add ?card=The Fool to the URL"}), 400
    
    response = client.chat.completions.create(
        model="grok-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"What is the deepest mystical meaning of the {card} Tarot card?"}
        ],
        max_tokens=600,
        temperature=0.7
    )
    
    return jsonify({
        "card": card,
        "meaning": response.choices[0].message.content
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
