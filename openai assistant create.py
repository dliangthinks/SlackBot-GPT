import os
from openai import OpenAI
import time

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Initialize the OpenAI client
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    print("API Key not found.")
    exit()

# Create an assistant
assistant = client.beta.assistants.create(
    name="RAG Assistant",
    instructions="You are a helpful assistant that uses the provided document for information.",
    model="gpt-4o",
    tools=[{"type": "file_search"}],  # no more "retrieval"
)

# Create a vector store called "Precious Knowledge"
vector_store = client.beta.vector_stores.create(name="Precious Knowledge")

# Ready the files for upload to OpenAI
file_ids = ["file-r5QHOKap0dvZL9g1UY3C6jVJ"]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_ids
)

# You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)

# To make the files accessible to your assistant, update the assistant’s tool_resources with the new vector_store id.
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# Create a thread
thread = client.beta.threads.create()

print("Hello! I'm your RAG Assistant. You can ask me questions about the document you provided.")
print("Type 'exit' to end the conversation.")

while True:
    # Get user input
    user_input = input("You: ")
    
    if user_input.lower() == 'exit':
        break

    # Add the user's message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please use the provided document to answer the user's question.",
    )

    # Wait for the run to complete
    while run.status not in ["completed", "failed"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    if run.status == "failed":
        print("Assistant: Sorry, I encountered an error while processing your request.")
        continue

    # Retrieve and print the assistant's response
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    assistant_messages = [msg for msg in messages if msg.role == "assistant"]
    if assistant_messages:
        latest_response = assistant_messages[-1].content  # Adjusted to fetch the correct message content
        print("Assistant:", latest_response)
    else:
        print("Assistant: I'm sorry, I couldn't generate a response.")

# Clean up
client.beta.assistants.delete(assistant.id)

print("Thank you for chatting! Goodbye.")