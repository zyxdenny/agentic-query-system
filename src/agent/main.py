from typing import Annotated
import requests

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from agent.system_prompt_from_data import system_prompt


llm = init_chat_model(
    "anthropic:claude-3-7-sonnet-latest",
)

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)


def chatbot(state: State):
    system_message = {
        "role": "system", 
        "content": system_prompt
    }
    messages = [system_message] + state["messages"]
    # messages = llm.invoke(messages)
    full_content = ""
    for chunk in llm.stream(messages):
        if hasattr(chunk, 'content') and chunk.content:
            print(chunk.content, end="", flush=True)
            full_content += chunk.content

    print()

    response = AIMessage(content=full_content)
    return {"messages": [response]}

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
memory = InMemorySaver()
graph = graph_builder.compile(memory)


def handle_conversation(user_input: str, thread_id: str = "1"):
    """Handle a conversation turn, including interruptions."""
    config = {"configurable": {"thread_id": thread_id}}
    
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    )

    for event in events:
        pass

def main():
    print("I am your expert analyst for camera feed systems.\n"
          "With access to feed data, encoder/decoder parameters, and their schemas, I can answer questions, explain configurations, and help troubleshoot encoding and decoding processes.\n"
          "What do you want to ask me?"
    )
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            handle_conversation(user_input)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
