# testing working on July 9th
# this little program will allow you to chat in the terminal 
# with a specific assistant already created under my account
# this assistant already has a document uploaded and vector store created
# replace assiastant_id with your own assistant id
# in the next step I will try to see if there is a need to create an assistant on the fly and upload document



import os
from openai import OpenAI
from openai.types.beta import Thread
from typing_extensions import override
from openai import AssistantEventHandler

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Assistant ID
assistant_id = "asst_zdYFRWZ5geak53NIfxBwX6FD"

class EventHandler(AssistantEventHandler):    
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)
          
    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)
          
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)
    
    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

def retrieve_assistant(assistant_id: str):
    """Retrieve an existing assistant"""
    return client.beta.assistants.retrieve(assistant_id)

def create_thread() -> Thread:
    """Create a new thread"""
    return client.beta.threads.create()

def add_message_to_thread(thread_id: str, content: str):
    """Add a message to the thread"""
    return client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )

def stream_run(thread_id: str, assistant_id: str, instructions: str):
    """Stream the run using the EventHandler"""
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=instructions,
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

def main():
    # Retrieve the assistant
    assistant = retrieve_assistant(assistant_id)
    print(f"Retrieved assistant: {assistant.name}")

    # Create a new thread
    thread = create_thread()
    print(f"Created thread: {thread.id}")

    # Instructions for the assistant
    instructions = "Please address the user as Dear Learner, and preface everything you said with According to Dr. Liang"

    print("You can start your conversation now. Type 'exit' to end the conversation.")

    while True:
        # Get user input
        user_input = input("\nYou > ")
        
        if user_input.lower() == 'exit':
            print("Nice chat, see you next time!")
            break

        # Add the user's message to the thread
        add_message_to_thread(thread.id, user_input)

        # Stream the run
        stream_run(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions=instructions
        )

if __name__ == "__main__":
    main()