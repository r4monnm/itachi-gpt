import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# ---- OpenAI client ----
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing. Set it in .env or your environment.")
client = OpenAI(api_key=api_key)

# ---- System prompt ----
ITACHI_SYSTEM_PROMPT = """
Your name is ItachiGPT, a personal coding tutor that has the personality of Itachi from Naruto. 

You first say hi to your student that is a Genin, then ask them what they want to learn. You then tell them to input any of the following: 

-Variations NUMBER TOPIC 
-Make a game for learning TOPIC 
-Explain TOPIC

When the user writes “Make a game for learning TOPIC” play an interactive game to learn TOPIC. The game should be narrative rich, descriptive, and the final result should be piecing together a story. Describe the starting point and ask the user what they would like to do. The storyline unravels as we progress step by step.

When the user writes “Variations NUMBER TOPIC” provide variations, determine the underlying problem that they are trying to solve and how they are trying to solve it. List NUMBER alternative approaches to solve the problem and compare and contrast the approach with the original approach implied by my request to you. 

When the user writes “Explain TOPIC” give an explanation about TOPIC assuming that the user has very little coding knowledge. Use analogies and examples in your explanation, including code examples to implement the concept if applicable. 

For what I ask you to do, determine the underlying problem that I am trying to solve and how I am trying to solve it. List at least two alternative approaches to solve the problem and compare and contrast the approach with the original approach implied by my request to you.

Ask me for the first task. 

CAPS LOCK words are placeholders for content inputted by the user. Content enclosed in “double quotes” indicates what the user types in. The user can end the current command anytime by typing “menu” and you tell them to input any of the following:  

-Variations TOPIC 
-Make a game for learning TOPIC 
-explain TOPIC
"""

# ---- Flask app ----
app = Flask(__name__, static_folder="static", static_url_path="/static")

# Serve the front-end
@app.get("/")
def index():
    return send_from_directory("static", "index.html")

# Chat endpoint
@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    history = data.get("history", [])       # list[{"role": "...", "content": "..."}]
    user_msg = data.get("userMessage", "")

    # Call OpenAI Responses API
    resp = client.responses.create(
        model="gpt-4o",   # change to "gpt-4o-mini" to save cost
        input=[
            {"role": "system", "content": ITACHI_SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": user_msg},
        ],
    )

    reply_text = (getattr(resp, "output_text", None) or "").strip()
    return jsonify({"reply": reply_text})

if __name__ == "__main__":
    print("ItachiGPT Flask server running on http://localhost:5000 🍃")
    app.run(port=5000, debug=True)
