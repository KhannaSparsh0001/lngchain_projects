from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from tavily import TavilyClient
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv#, set_key
from typing import Dict, Any, Annotated,List,  TypedDict
from langgraph.graph.message import add_messages
#from typing_extensions import 
from functools import wraps
from pathlib import Path

env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)

global tavily_client
tavily_client = TavilyClient()

@tool
def web_search(query: str) -> Dict[str, Any]:

    """Search the web for information"""
    return tavily_client.search(query)

    
# --- 2. STATEGRAPH DEFINITION (The "Backpack" Schema) ---
# As per your docs: 'state_schema' defines how nodes communicate.
class State(TypedDict):
    # 'add_messages' is the reducer that prevents overwriting
    messages: Annotated[List[BaseMessage], add_messages]

# Initialize the Builder
builder = StateGraph(State)

# Add a basic node so the graph is valid for compilation
def process_mem_node(state: State):
    # Simply passes the state through; you can add logic here later
    return {"messages": state["messages"]}

builder.add_node("mem_node", process_mem_node)
builder.add_edge(START, "mem_node")
builder.add_edge("mem_node", END)


def mem_build_check(func):

    @wraps(func)
    def check(*args, **kwargs):
        global graph, config
        
        if 'graph' not in globals() or graph.checkpointer is None:

            checkpointer= InMemorySaver()
            graph = builder.compile(
                checkpointer=checkpointer
                )

            #saving config object in .env 
            config = {
                    "configurable": {
                        "thread_id": "1"
                        }
                    }
            set_key('.env','CONFIG',config)
        else:
            load_dotenv()

        return func(*args, **kwargs)
    return check 



@tool("mem")
@mem_build_check
def mem(text: str):
    #graph.invoke(
     #   input=context, 
      #  config={"configurable": config}
    #)

    """This serves as the memory for the agents to store critical info which can be used later on."""

    graph.invoke(
        {"messages": [HumanMessage(content=text)]},
        config=config
    )


