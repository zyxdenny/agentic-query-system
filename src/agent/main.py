from typing import Annotated
import os
from typing_extensions import TypedDict
import asyncio

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.system_prompt_from_data import system_prompt


class State(TypedDict):
    messages: Annotated[list, add_messages]

class Agent:
    def __init__(self, model_name="anthropic:claude-3-7-sonnet-latest"):
        self.llm = init_chat_model(model_name)
        self.mcp_client = None
        self.tools = []
        self.llm_with_tools = None
        self.graph = None


    async def initialize(self):
        await self._initialize_mcp()
        self._build_graph()

    
    async def _initialize_mcp(self):
        """Initialize MCP client and get tools"""
        try:
            self.mcp_client = MultiServerMCPClient(
                {
                    "weather": {
                        "command": "python",
                        "args": ["-m", "server.mcp_server"],
                        "transport": "stdio",
                        "env": {
                            **os.environ,
                            "PYTHONPATH": "src"
                        },
                    }
                }
            )
            
            # Get tools from MCP
            self.tools = await self.mcp_client.get_tools()
            print(f"Loaded {len(self.tools)} MCP tools: {[tool.name for tool in self.tools]}")
            
            # Bind tools to LLM
            self.llm_with_tools = self.llm.bind_tools(self.tools)
            
        except Exception as e:
            print(f"Failed to initialize MCP: {e}")
            self.tools = []
            self.llm_with_tools = self.llm


    # node functions are defined below
    async def _node_chatbot(self, state: State):
        system_message = {
            "role": "system",
            "content": system_prompt,
        }
        messages = [system_message] + [m for m in state["messages"] if m.content not in (None, "", [])]
        response = await self.llm_with_tools.ainvoke(messages)
        return {"messages": [response]}


    def _build_graph(self):
        graph_builder = StateGraph(State)
        
        if self.tools:
            tool_node = ToolNode(self.tools)
            graph_builder.add_node("tools", tool_node)
        
        graph_builder.add_node("chatbot", self._node_chatbot)
        graph_builder.add_edge(START, "chatbot")
        
        if self.tools:
            graph_builder.add_conditional_edges("chatbot", tools_condition)
            graph_builder.add_edge("tools", "chatbot")
        else:
            graph_builder.add_edge("chatbot", END)
        
        memory = InMemorySaver()
        self.graph = graph_builder.compile(checkpointer=memory)


    async def _handle_conversation(self, user_input: str, thread_id: str = "1"):
        """Handle a conversation turn, including tool calls."""
        config = {"configurable": {"thread_id": thread_id}}
        
        events = self.graph.astream(
            {"messages": [{"role": "user", "content": user_input}]},
            config,
            stream_mode="values",
        )
        
        last_message_count = 0
        async for state in events:
            messages = state.get("messages", [])
            
            # Process new messages since last iteration
            new_messages = messages[last_message_count:]
            last_message_count = len(messages)
            
            for message in new_messages:
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    # AI is making tool calls
                    print("\n🤖 Executing tools...")
                    for tool_call in message.tool_calls:
                        print(f"   📋 {tool_call['name']} - {tool_call.get('args', {})}")
                
                elif hasattr(message, 'content') and message.content:
                    # Check if this is a tool response
                    if hasattr(message, 'tool_call_id'):
                        # This is tool output
                        print("\n📤 Tool Results:")
                        content = message.content
                        if isinstance(content, str):
                            # Format tabular data nicely
                            lines = content.strip().split('\n')
                            for line in lines:
                                print(f"   {line}")
                        print("─" * 50)
                    
                    elif hasattr(message, 'type') and message.type == 'ai':
                        # This is AI response - stream it character by character
                        content = message.content
                        if isinstance(content, str):
                            print(content, end="", flush=True)

        print()


    async def run(self):
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\n> ")
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                
                await self._handle_conversation(user_input)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break

async def main():
    agent = Agent()
    await agent.initialize()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
