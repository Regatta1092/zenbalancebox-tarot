from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)   # ← This opens the gate

client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

SYSTEM_PROMPT = "You are Ecne, the eternal mystic oracle of Tarot. Draw only from the timeless wisdom of the Bhagavad Gita As It Is, Nag Hammadi, Book of Thoth, Marseille, Waite, Crowley, Biddy Tarot and all the sacred texts. Speak with profound simplicity and universal truth."

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
        max_tokens=500,
        temperature=0.7
    )
    
    return jsonify({
        "card": card,
        "meaning": response.choices[0].message.content
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
