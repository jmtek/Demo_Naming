"""Streamlit app to generate name."""

# Import from standard library
import logging
import datetime
# import re
import json

# Import from 3rd party libraries
import streamlit as st

from langchain.llms import OpenAI
from langchain import PromptTemplate

# Configure logger
logging.basicConfig(format="\n%(asctime)s\n%(message)s", level=logging.INFO, force=True)

openai_api_key = st.secrets["OPENAI_API_KEY"]

llm_agent = OpenAI(temperature=0, openai_api_key=openai_api_key)
# The maximum number of tokens to generate in the completion. WITHOUT PROMPT!!!
llm_agent.max_tokens = 1000


llm_naming = OpenAI(temperature=.7, openai_api_key=openai_api_key)
llm_naming.max_tokens = 1000

def agent_handle(input:str):
    st.session_state.error = ""
    st.session_state.agentreply = ""

    json_result = llm_agent(get_agent_prompt(input))
    try:
        result = json.loads(json_result)

        if result["起名"] != "是":
            st.session_state.error = "抱歉，您的问题跟起名无关"
            return
        
        bday = result["生日"]
        cnzodiac = result["属相"]
        who = result["谁"]
        otherreq = result["特殊需求"]

        st.session_state.agentreply = f"谁：{who}，生日：{bday}，属相：{cnzodiac}，具体需求：{otherreq}"

        return
    except Exception:
        st.session_state.error = f"agent返回的内容无效：{json_result}"

def get_agent_prompt(input):
    today = datetime.date.today
    prompt_template = (
        "作为LLM，利用您的优势完成对输入文字的分析任务，以下是输入文字：\n\n"
        "'''{input}'''"
        "\n\n分析的任务目标：\n\n"
        "1. 判断输入文字是否属于以下相关主题中的一个或多个\n"
        "2. 如果属于相关主题，请对内容提取核心关键字\n"
        "3. 如果不属于任何相关主题，请回答：问题超纲\n"
        "\n相关主题：\n\n"
        "1. 为孩子起名\n"
        "2. 孩子的生日\n"
        "3. 生肖属相\n"
        "4. 起名的特殊要求\n"
        "\n其他上下文：\n\n"
        f"今天是{today}"
        "\n\n请用以下的JSON格式输入，并确保回答内容可以被Python json.loads解析：\n\n"
        "{\n"
        "\t'起名': '输入的文字是否是关于取名字的问题',\n"
        "\t'生日': '如果提到了生日就输出，并且将生日格式化成标准日期格式，否则留空',\n"
        "\t'属相': '如果提到了属相就输出，否则留空',\n"
        "\t'谁': '为谁起名，如果没有提到则留空',\n"
        "\t'特殊需求': '文字中包含的其他取名需求'\n"
        "}"
    )
    logging.info(prompt_template)
    prompt = PromptTemplate(
        input_variables=["input"],
        template=prompt_template,
    )
    return prompt.format(input=input)


# Configure Streamlit page and state
st.set_page_config(page_title="Demo of Naming", page_icon="🤖")

if "userinput" not in st.session_state:
    st.session_state.userinput = ""
if "agentreply" not in st.session_state:
    st.session_state.agentreply = ""
if "error" not in st.session_state:
    st.session_state.error = ""

# Force responsive layout for columns also on mobile
st.write(
    """<style>
    [data-testid="column"] {
        width: calc(50% - 1rem);
        flex: 1 1 calc(50% - 1rem);
        min-width: calc(50% - 1rem);
    }
    body {
        font-size: 13px
    }
    </style>""",
    unsafe_allow_html=True,
)

# Render Streamlit page
st.title("Naming Demo")

st.text_area(label="", value=st.session_state.agentreply, height=100)

text_spinner_placeholder = st.empty()
if st.session_state.error:
    st.error(st.session_state.error)

user_input = st.text_input(label="输入你想问的话", placeholder="")

st.button(
    label="提问",
    type="primary",
    on_click=agent_handle,
    kwargs={ "input": user_input },
)
    