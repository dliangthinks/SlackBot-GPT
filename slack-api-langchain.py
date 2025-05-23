import os

from flask import Flask, jsonify, request
from langchain.cache import InMemoryCache
from langchain.chat_models import ChatOpenAI
from langchain.globals import set_llm_cache
from langchain.schema import HumanMessage
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier


# The following information from the environment variables:
# SLACK_BOT_TOKEN(required): The token of the slack app created above.
# SIGNING_SECRET(required): The siging secret of the slack app created above.
# OPENAI_ORGANIZATION (required): Open AI organization
# OPENAI_API_KEY(required): Open AI api key
# GPT_MODEL (optional): GPT model name (default: gpt-3.5-turbo )
# DEDICATED_CHANNELS (optional): Slack channels in which the app will also send a reply message to the channel (not in the thread)

# Read from environment variables
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SIGNING_SECRET = os.environ["SIGNING_SECRET"]
DEDICATED_CHANNELS = os.getenv("DEDICATED_CHANNELS", "").split(
    ","
)  # Also send to the channel in the dedicated channels
VERIFIER = SignatureVerifier(SIGNING_SECRET)
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-3.5-turbo")

# Client
app = Flask(__name__)
set_llm_cache(InMemoryCache())
client = WebClient(token=SLACK_BOT_TOKEN)
chat = ChatOpenAI(
    model=GPT_MODEL,
    streaming=False,
    verbose=True,
)


@app.route("/slack/events", methods=["POST"])
def slack_events():
    # Check if the request from Slack
    if not VERIFIER.is_valid_request(request.data, request.headers):
        return "Invalid request", 403

    # skip for slack retry
    if request.headers.get("x-slack-retry-num"):
        print("retry called")
        return {"statusCode": 200}

    # get event data
    data = request.get_json()
    event = data.get("event", {})

    # for url_verification event
    if data["type"] == "url_verification":
        return jsonify({"challenge": data["challenge"]})

    channel_id = event.get("channel")

    # for app_mention event
    if event.get("type") == "app_mention":
        user_id = event.get("user")
        text = event.get("text")
        print(f"{channel_id=}, {user_id=}")

        # Reply message
        try:
            response = client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name="speech_balloon",
            )
            print(response)
            answer = ask_ai(text)
            client.chat_postMessage(
                channel=channel_id,
                text=f"{answer}",
                thread_ts=event["ts"],  # Reply in thread
                reply_broadcast=channel_id in DEDICATED_CHANNELS,
            )
            response = client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name="white_check_mark",
            )
        except SlackApiError:
            response = client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name="man-bowing",
            )
            client.chat_postMessage(
                channel=channel_id,
                text="Sorry. Something's wrong.",
                thread_ts=event["ts"],  # Reply in thread
                reply_broadcast=channel_id in DEDICATED_CHANNELS,
            )

    return jsonify({"success": True})


def ask_ai(text):
    result = chat([HumanMessage(content=text)])
    return result.content


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))