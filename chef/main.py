from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.agents import create_agent
from langchain.messages import HumanMessage, AIMessage
import os 

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=1
)



system_prompt = """

"""

def main():
    os.system('uv python run app_tst.py && streamlit run app_tst.py')
    os.system('streamlit run app_tst.py')

if __name__ == "__main__":
    main()
