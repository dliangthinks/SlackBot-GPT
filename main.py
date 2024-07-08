import os
from openai import OpenAI
from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
# Event API & Web API
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
openai_client = OpenAI(api_key=OPENAI_API_KEY)
slack_client = WebClient(SLACK_BOT_TOKEN)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)
@app.event("app_mention")
def handle_message_events(body, logger):
    prompt = str(body["event"]["text"]).split(">")[1]
    
    chat_completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant named working as part of the Stanford Technology Training team"},
            {"role": "user", "content": prompt}
        ]
    )
    response_text = chat_completion.choices[0].message.content

    response = slack_client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=response_text)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
