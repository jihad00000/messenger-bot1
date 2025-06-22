from flask import Flask, request
import requests
import json
import random
import subprocess
import os

app = Flask(__name__)  # Fixed: use __name__, not name

PAGE_ACCESS_TOKEN = "EAAJ2bWlNlpwBO2vNZCu9ZAD1jbQnV8ytpEjXhUctfS6BDm2pyctGOBgEXPzztXHJuiETY0GRcI6SqXnlxCvXjUMPqf8WHNTRLRtaft4DLKg9GwZB3lyYTnFRSph4zcWqKuteMGKZCHczFGJ2S92lhZCe0PIlJAvUzdQ2bDZC0uEDEIbLZBjROScWc95BDj9hpGWr5GltJg3XwZDZD"
VERIFY_TOKEN = "zihadai0099.01"

@app.route("/webhook", methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Unauthorized", 403

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                if messaging_event.get("message") and messaging_event["message"].get("text"):
                    message_text = messaging_event["message"]["text"]
                    handle_command(sender_id, message_text.strip())
    return "ok", 200

def handle_command(sender_id, text):
    text_lower = text.lower()
    if text_lower.startswith("~quiz") and "bn" not in text_lower:
        send_quiz(sender_id, lang="en")
    elif "~quiz(bn)" in text_lower or "~qz(bn)" in text_lower:
        send_quiz(sender_id, lang="bn")
    elif "~mathquiz" in text_lower or "~mathqz" in text_lower:
        send_quiz(sender_id, lang="math")
    elif text_lower.startswith("~play"):
        send_message(sender_id, "🎵 Audio playback feature coming soon!")
    elif any(link in text_lower for link in ["facebook.com", "instagram.com", "youtu"]):
        download_video(sender_id, text)
    else:
        send_message(sender_id, "❓ Unknown command. Try ~quiz, ~mathquiz, or send a link.")

def send_message(recipient_id, text):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    response = requests.post(
        f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}",
        headers=headers,
        data=json.dumps(payload)
    )
    print(f"Sent message to {recipient_id}: {text}")
    print(f"Response: {response.status_code}, {response.text}")

def send_quiz(sender_id, lang="en"):
    quizzes = {
        "en": [
            {"q": "What is the capital of France?", "a": "Paris"},
            {"q": "What is 2 + 2?", "a": "4"}
        ],
        "bn": [
            {"q": "বাংলাদেশের রাজধানী কী?", "a": "ঢাকা"},
            {"q": "৩ + ৫ = ?", "a": "৮"}
        ],
        "math": [
            {"q": "Solve: 12 * 8", "a": "96"},
            {"q": "What is the square root of 49?", "a": "7"}
        ]
    }
    quiz_list = quizzes.get(lang, quizzes["en"])
    quiz = random.choice(quiz_list)
    send_message(sender_id, f"❓ {quiz['q']}\n👉 Answer: {quiz['a']}")

def download_video(sender_id, url):
    send_message(sender_id, "⏬ Downloading video...")
    try:
        filename = "video.mp4"
        cmd = ["yt-dlp", "-f", "mp4", "-o", filename, url]
        subprocess.run(cmd, check=True)
        send_message(sender_id, "✅ Video downloaded successfully! (File sending feature coming soon)")
    except Exception as e:
        print(f"Error downloading video: {e}")
        send_message(sender_id, "❌ Failed to download video. Please check the link.")

if __name__ == '__main__':  # Fixed: use __name__ == '__main__'
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

