# SlackBot-GPT

This project implements a Slack bot that integrates with OpenAI's GPT models to respond to user mentions.

## Core Functionality (`main.py`)

-   **Framework:** Uses Flask as the web server and Slack Bolt for Python to handle Slack events.
-   **Trigger:** Listens for `@app_mention` events in Slack channels where the bot is present.
-   **Processing:**
    -   Extracts the user's message from the event payload.
    -   Sends the message as a prompt to the OpenAI Chat Completions API (`gpt-3.5-turbo` model).
    -   Includes a system prompt identifying the bot as a helpful assistant from the "Stanford Technology Training team".
-   **Response:** Posts the generated response from OpenAI back to the originating Slack channel as a reply in the thread.
-   **Dependencies:** `Flask`, `openai`, `slack_bolt`, `slack_sdk`, `gunicorn`.

## Other Components

-   **`cinethinker.py`:** A command-line interface script to interact directly with a specific, pre-existing OpenAI Assistant (using the Assistants API). This is separate from the main Slack bot functionality.
-   **`slack-api-langchain`:** An alternative implementation of the Slack event handler, also using Flask. This version utilizes LangChain (`ChatOpenAI`) for interacting with the GPT model and includes features like reaction emojis and optional broadcasting of replies to dedicated channels.

## Setup

1.  **Environment Variables:** The application requires the following environment variables to be set:
    *   `OPENAI_API_KEY`: Your OpenAI API key.
    *   `SLACK_BOT_TOKEN`: Your Slack bot token.
    *   `SLACK_SIGNING_SECRET`: Your Slack app's signing secret.
    *   `PORT` (Optional): The port for the Flask server (defaults to 3000 in `main.py` or 8080 in `slack-api-langchain`).
    *   The `slack-api-langchain` script also uses `OPENAI_ORGANIZATION` (required), `GPT_MODEL` (optional), and `DEDICATED_CHANNELS` (optional).

2.  **Dependencies:** Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Running:**
    *   To run the main Slack bot (`main.py`):
        ```bash
        gunicorn main:flask_app
        # or for development:
        # python main.py
        ```
    *   To run the terminal chat (`cinethinker.py`):
        ```bash
        python cinethinker.py
        ```
    *   Ensure your Slack App is configured to send events to the correct `/slack/events` endpoint of your running Flask application.

## Note

