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
    logging.info(json_result)
    try:
        result = json.loads(json_result)

        if result["起名"] != "是":
            st.session_state.error = "抱歉，您的问题跟起名无关"
            return
        
        bday = result["生日"]
        cnzodiac = result["属相"]
        gender = result["性别"]
        words = result["单双名"]
        lastname = result["姓氏"]
        otherreq = result["特殊需求"]

        known = []
        unknown = []
        if gender != "":
            known.append(f"你想为{gender}取名字")
        else:
            unknown.append("宝宝的性别")

        if words != "":
            known.append(f"你想起一个{'单名' if words=='1' else '双名'}")
        else:
            unknown.append("宝宝的名字是单名还是双名")

        if lastname != "":
            known.append(f"宝宝姓{lastname}")
        else:
            unknown.append("宝宝姓什么")

        if bday != "":
            known.append(f"宝宝的生日是{bday}")
        else:
            unknown.append("宝宝的生日")

        if cnzodiac != "":
            known.append(f"宝宝属{cnzodiac}")

        if len(known) == 0:
            output = "我没有get到你起名的具体要求，建议提供以下信息：\n" + "\n".join(unknown)
        else:
            output = "请确认你起名字的要求：\n" + "\n".join(known)
            if len(unknown) > 0:
                output = output + "\n建议再补充一些信息，比如：\n" + "\n".join(unknown)

        st.session_state.agentreply = output
        json_request = {
            "gender": gender,
            "bday": bday,
            "words": words,
            "lastname": lastname,
            "cnzodiac": cnzodiac,
            "otherreq": otherreq
        }
        st.session_state.request = json.dumps(json_request)

        return
    except Exception:
        st.session_state.error = f"agent返回的内容无效：{json_result}"

def get_agent_prompt(input):
    today = datetime.date.today
    prompt = (
        "作为LLM，利用您的优势完成对输入文字的分析任务，以下是输入文字：\n"
        f"'''{input}'''"
        "\n分析的任务目标：\n"
        "1. 判断输入文字是否属于以下相关主题中的一个或多个"
        "2. 如果属于相关主题，请对内容提取核心关键字"
        "3. 如果不属于任何相关主题，请回答：问题超纲\n"
        "相关主题：\n"
        "1. 起名字\n"
        "2. 生日\n"
        "3. 生肖属相\n"
        "4. 性别\n"
        "5. 名字包含几个字\n"
        "6. 姓氏\n"
        "7. 起名的特殊要求\n"
        "其他上下文：\n"
        f"今天是{today.strftime('%Y-%m-%d')}"
        "\n请用以下的JSON格式输入，并确保回答内容可以被Python json.loads解析："
    )

    prompt = (
        prompt
        + """
{
    "起名": "输入的文字是否是关于取名字的问题",
    "生日": "如果提到了生日就输出，并且将生日格式化成标准日期格式，否则返回空字符串",
    "属相": "如果提到了属相就输出，否则返回空字符串",
    "姓氏": "要取的名字的姓是什么，如未提及则返回空字符串",
    "性别": "这个名字是男孩还是女孩，如未提及则返回空字符串",
    "单双名": "名字包含几个字，如未提及则返回空字符串",
    "特殊需求": "文字中包含的其他取名需求"
}

json'''
    """)

    logging.info(prompt)
    
    return prompt

def naming_handle(input):
    logging.info("user request: " + st.session_state.request)
    return ""

# Configure Streamlit page and state
st.set_page_config(page_title="Demo of Naming", page_icon="🤖")

if "userinput" not in st.session_state:
    st.session_state.userinput = ""
if "agentreply" not in st.session_state:
    st.session_state.agentreply = ""
if "error" not in st.session_state:
    st.session_state.error = ""
if "request" not in st.session_state:
    st.session_state.request = ""

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

if st.session_state.error:
    st.error(st.session_state.error)

user_input = st.text_input(label="输入你想问的话", placeholder="")

st.button(
    label="提问",
    type="primary",
    on_click=agent_handle,
    kwargs={ "input": user_input },
)

st.text_area(label="", value=st.session_state.agentreply, height=100)
if st.session_state.request:
    st.button(
        label="确认",
        type="primary",
        on_click=naming_handle,
        kwargs={ "input": user_input },
    )

text_spinner_placeholder = st.empty()