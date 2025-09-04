from graph import graph
from speech_to_text import speech_to_text
from langfuse.callback import CallbackHandler
from dotenv import load_dotenv
import os
load_dotenv()

# Langfuse setup
langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
langfuse_host = os.getenv("LANGFUSE_HOST")

langfuse_handler = CallbackHandler(
    secret_key=langfuse_secret_key,
    public_key=langfuse_public_key,
    host=langfuse_host
)

# add new thread id to config a new user
config = {"configurable": {"thread_id": "1000"}, "callbacks": [langfuse_handler]}

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}, config=config):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
            # print(event.values())

def main():
    # Allow users to choose between typing and speaking
    input_method = input("Choose input method (type/voice): ").lower()
    while True:
        try:
            if input_method == "voice":
                user_input = speech_to_text()
                # Check if speech recognition returned anything
                if not user_input:
                    print("No speech detected. Please try again.")
                    continue
                print("User: " + user_input)
            else:
                user_input = input("User: ")
            
            if user_input.lower() in ["quit", "exit", "q", "goodbye", "bye"]:
                print("Goodbye!")
                break
            
            # Only proceed if we have non-empty input
            if user_input.strip():
                stream_graph_updates(user_input)
            else:
                print("I didn't receive any input. Please try again.")
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            user_input = "Who are you? Give a brief introduction"
            print("User: " + user_input)
            stream_graph_updates(user_input)
            break

if __name__ == "__main__":
    main()