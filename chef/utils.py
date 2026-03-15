from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage, AIMessage
from tavily import TavilyClient
from langgraph.graph import StateGraph
from dotenv import load_dotenv#, set_key
from typing import Dict, Any
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

    

def mem_build_check(func):

    @wraps(func)
    def check(func):
        if graph.checkpointer == None:
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

        return func
    return check 



@tool("mem",  description='This serves as the memory for the agents to store critical info which can be used later on.')
@mem_build_check
def mem(text: str):
    #graph.invoke(
     #   input=context, 
      #  config={"configurable": config}
    #)

    graph.invoke(
        {"messages": [HumanMessage(content=text)]},
        config=config
    )


