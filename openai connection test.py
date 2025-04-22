import os
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


if not(OPENAI_API_KEY):
    print("API Key not found.")

from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, world!"}
  ]
)

print(response.choices[0].message.content)
