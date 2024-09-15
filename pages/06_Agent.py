import openai
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create an Assistant
def create_assistant(name, description, model, tools, file_ids):
    try:
        assistant = openai.Assistant.create(
            name=name,
            description=description,
            model=model,
            tools=tools,
            file_ids=file_ids
        )
        return assistant
    except AttributeError as e:
        print(f"Error creating assistant: {e}")
        return None

# Create an Assistant with given parameters
assistant = create_assistant(
    name="Personal Tutor",
    description="You are a personal tutor. Answer questions and provide information.",
    model="gpt-4-1106-preview",
    tools=[{"type": "retrieval"}],
    file_ids=[]  # Add file IDs if you have any
)

if assistant:
    assistant_id = assistant.get('id')  # Retrieve the Assistant ID

    # Example usage for further operations
    def create_thread(assistant_id, message_content):
        try:
            thread = openai.Thread.create(
                assistant_id=assistant_id,
                messages=[
                    {"role": "user", "content": message_content}
                ]
            )
            return thread
        except AttributeError as e:
            print(f"Error creating thread: {e}")
            return None

    def run_thread(thread_id, assistant_id):
        try:
            run = openai.Run.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            return run
        except AttributeError as e:
            print(f"Error running thread: {e}")
            return None

    def get_run_status(run_id, thread_id):
        try:
            run = openai.Run.retrieve(
                run_id=run_id,
                thread_id=thread_id
            )
            return run
        except AttributeError as e:
            print(f"Error retrieving run status: {e}")
            return None

    def get_messages(thread_id):
        try:
            messages = openai.ThreadMessages.list(thread_id=thread_id)
            messages = list(messages)
            messages.reverse()
            for message in messages:
                print(f"{message.role}: {message.content.get('text', '')}")
        except AttributeError as e:
            print(f"Error retrieving messages: {e}")

    # Use the assistant
    if assistant:
        thread = create_thread(assistant_id, "Search for information about quantum physics on Wikipedia")
        if thread:
            run = run_thread(thread.id, assistant_id)
            if run:
                run_status = get_run_status(run.id, thread.id)
                if run_status:
                    print(f"Run Status: {run_status.get('status', 'unknown')}")
                    get_messages(thread.id)
