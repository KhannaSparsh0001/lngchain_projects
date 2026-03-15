from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage, AIMessage
#from dotenv import load_dotenv, set_key
import streamlit as st
from streamlit_mic_recorder import mic_recorder
import base64
from utils import web_search, mem
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv, dotenv_values #, set_key
import json
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

#AGENT DEFINITIONS

config = json.loads(dotenv_values(".env").get("CONFIG", "{}"))

system_prompt = """
You are a chef, the user will provide an image of his refrigerator or alternatively share the list of items he/she has, you job is to actually fcking show recipe suggestions and help the user with the recipe he/she likes to be made from the items.

Guidelines:
You have to ensure that the sole purpose of this app is to help with recipes, every other request should be denied immidiately.
The user may provide input via the audio.
You have been provided with two tools, one is mem and the other being web_search
    mem: whenever u feel like something is critical to store in memory, use this tool. For ex: storing the items the user has for future context, food prefernces.
    web_search: this is service that allows u to search the web, use this when ur knowldege base aint able to satisfy user requirement. 
Assume that the user has the necessary spices such as salt, pepper etc. 
The user might occasionally upload images of the food mid process, your job in such case is to guide him/her.

You are operating as per the following workflow:
user provides info bout list of items 
            |
you process them and generate a list of recipes 
            |
user selects one 
            |
you guide the user on how to make one and answer the relevant queries to that recipe

any deviation from the above defines workflow such as asking what's the price of gold today?, shud lead to denial of request processing.
"""

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=.35,
)

agent = create_react_agent(
    model=model,
    checkpointer=InMemorySaver(),
    prompt=system_prompt, 
    tools=[mem, web_search]
)



#"""INTERFACE DEFINITION"""

st.set_page_config(page_title="CHEF")
st.header('CHEF', text_alignment='center')


# ------------------------
# STATE INIT
# ------------------------
if "trigger" not in st.session_state:
    st.session_state.trigger = False

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

if "image_data" not in st.session_state:
    st.session_state.image_data = None


# ------------------------
# MAIN FORM (Enter submits automatically)
# ------------------------
with st.form("main_form", clear_on_submit=False):

    text_input = st.text_input("Prompt")

    uploaded_file = st.file_uploader(
        "Upload image",
        type=["png", "jpg", "jpeg"]
    )

    audio = mic_recorder(
    start_prompt="🎤",
    stop_prompt="⏹",
    just_once=True
    )

    submit_text = st.form_submit_button("Submit")

    if submit_text:
        st.session_state.trigger = True

    if audio:
        st.session_state.audio_data = audio["bytes"]
        st.session_state.trigger = True
    
    if uploaded_file:
        st.session_state.image_data = uploaded_file.read()


# ------------------------
# CENTRAL TRIGGER
# ------------------------
if st.session_state.trigger:

 #   st.write("### Processing...")

#    payload = []

    if text_input:
        #payload.append({"type": "text", "text": text_input})
        ques=HumanMessage(content=[
            {"type":"text", "text":text_input}
        ])
        response = agent.invoke(
            {"messages":[ques]},
            config=config
        )
        st.write(response['messages'][-1])

#    if st.session_state.image_data:
 #       img_b64 = base64.b64encode(
  #          st.session_state.image_data
   #     ).decode("utf-8")
#
 #       img_ques = HumanMessage(content=[
  #          {"type":"image", "base64":img_b64, "mime_type":"png/jpeg/jpg"},
   #         {"type":"text", "text":"recipes for the indegrients uploaded....., based upon the food preferences if any"}
    #    ])

     #   response = agent.invoke(
      #      {"messages":[img_ques]},
       #     config=config
        #)
        #st.write(response['messages'][-1])

if uploaded_file:

    img_bytes = uploaded_file.read()
    img_b64 = base64.b64encode(st.session_state.image_data).decode()

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Give recipes from this fridge"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_b64}"
                }
            }
        ]
    )

    response = agent.invoke(
        {"messages":[message]},
        config=config
    ) 

    st.write(response['messages'][-1])

    if st.session_state.audio_data:
        st.audio(st.session_state.audio_data)
       # st.write(type(st.session_state.audio_data))
#`       generate  byte based data
#         
        audio_question = HumanMessage(content=[
            {"type": "audio", "base64": aud_b64, "mime_type": "audio/wav"}
        ])
        response = agent.invoke(
            {"messages":[audio_question]},
            config=config
        )
    st.write(response['messages'][-1], "content")
    st.session_state.trigger = False

"""
    response = agent.invoke(
        {"messages":[img_ques,audio_question,ques]}
    )
"""
#    st.write("Payload ready:")
     #st.write(payload)

    # Reset trigger (important)
#    st.session_state.trigger = False
