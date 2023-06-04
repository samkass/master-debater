import os
from random import choice, seed, random, randint
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from langchain import OpenAI
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.schema import ChatMessage
from streamlit_chat import message

from Persona import Persona

TEST_MODE = True

idle_messages = [
    "Thinking...",
    "Go Away! 'Bating!",
    "Hmmm...",
    "I've read Wikipedia, so I'm somewhat of an expert...",
    "Well, actually..."
]
seed()


@st.cache_resource
def generate_llm(model_name="gpt-3.5-turbo", is_chat=True, temperature=0.9):
    if is_chat:
        llm = ChatOpenAI(model_name=model_name, temperature=temperature)
    else:
        llm = OpenAI(model_name=model_name, temperature=temperature)
    return llm


def check_and_load_stsecret(name):
    if name in st.secrets and st.secrets[name] != "":
        os.environ.setdefault(name, st.secrets[name])


def init():
    load_dotenv()
    check_and_load_stsecret("OPENAI_API_KEY")
    check_and_load_stsecret("OPENAI_ORG_ID")
    check_and_load_stsecret("TEST_MODE")

    if os.getenv("TEST_MODE") != "":
        global TEST_MODE
        TEST_MODE = os.getenv("TEST_MODE")

    st.set_page_config(
        page_title="Master Debaters",
        page_icon="🤷‍"
    )
    if "model_name" not in st.session_state:
        st.session_state.model_name = "gpt-3.5-turbo"
    if "model_type" not in st.session_state:
        st.session_state.model_type = "Chat"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "response_count" not in st.session_state:
        st.session_state.response_count = 0
    if "response" not in st.session_state:
        st.session_state.response = ""

    st.session_state.chat_region = st.container()


def run_chain_with_cb(chain, query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        print(cb)

    return result


def reset_messages():
    st.session_state.messages = []


def new_debate(topic):
    reset_messages()
    st.session_state.debating = True
    st.session_state.debate_id = randint(10000000, 100000000)

    llm = generate_llm(st.session_state.model_name, st.session_state.model_type == "Chat")
    st.session_state.debater1_conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=650
        )
    )
    st.session_state.debater2_conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=650
        )
    )

    st.session_state.debater = st.session_state.debater1
    st.session_state.conversation = st.session_state.debater1_conversation
    st.session_state.response_count = 0

    generate_next_argument(topic, "Open")
    generate_next_argument(topic, "Open")


def increment_debate():
    if st.session_state.debater == st.session_state.debater1:
        st.session_state.debater = st.session_state.debater2
        st.session_state.conversation = st.session_state.debater2_conversation
    else:
        st.session_state.debater = st.session_state.debater1
        st.session_state.conversation = st.session_state.debater1_conversation

    st.session_state.response_count += 1


def generate_next_argument(topic, phase):
    new_response = ""
    if TEST_MODE:
        with st.spinner(choice(idle_messages)):
            new_response = f"Random {phase} message number {random()} at {datetime.now()}"
    else:
        with st.spinner(choice(idle_messages)):
            if phase == "Open":
                new_response = run_chain_with_cb(st.session_state.conversation,
                                                 st.session_state.debater.opening_prompt(topic,
                                                                                         st.session_state.response))
            elif phase == "Continue":
                new_response = run_chain_with_cb(st.session_state.conversation,
                                                 st.session_state.debater.response_prompt(st.session_state.response))
            elif phase == "Conclude":
                new_response = run_chain_with_cb(st.session_state.conversation,
                                                 st.session_state.debater.conclusion_prompt(st.session_state.response))

    st.session_state.messages.append(ChatMessage(content=new_response, role=st.session_state.debater.name))

    st.session_state.response = new_response
    with st.session_state.chat_region:
        message(message=st.session_state.response,
                is_user=(st.session_state.debater.name != st.session_state.debater2.name),
                avatar_style="pixel-art",
                seed=st.session_state.debater.name,
                key=f"{st.session_state.debater.name}-{st.session_state.response_count}-{st.session_state.debate_id}")
    increment_debate()
    # TODO: Switch to streaming interface


def print_debate():
    with st.session_state.chat_region:
        for i, msg in enumerate(st.session_state.messages):
            message(message=msg.content,
                    is_user=(msg.role == st.session_state.debater1.name),
                    avatar_style="pixel-art",
                    seed=msg.role,
                    key=f"{msg.role}-{i}-{st.session_state.debate_id}")


def continue_debate(topic):
    if st.session_state.response_count > 0 and st.session_state.debating:
        col1, col2 = st.columns(2)
        continue_debate_button = col1.button("Continue Debate", type="primary")
        conclude_debate_button = col2.button("Conclude Debate", type="primary")

        if continue_debate_button:
            generate_next_argument(topic, "Continue")
        if conclude_debate_button:
            st.session_state.debating = False
            generate_next_argument(topic, "Conclude")
            generate_next_argument(topic, "Conclude")
            st.experimental_rerun()


def main():
    init()

    with st.sidebar:
        with st.expander("Debater", expanded=True):
            debater1_name = st.text_input(label="Name", value="Bo", placeholder="Name")
            debater1_id = st.text_input(label="Identity", value="a Conservative", placeholder="Short Description")
            debater1_adjs = st.text_input(label="Adjectives",
                                          placeholder="Comma-separated words",
                                          value="ideological, serious, conservative, religious, Christian, pro-life")

        with st.expander("Opponent", expanded=True):
            debater2_name = st.text_input(label="Name", value="Luke", placeholder="Name")
            debater2_id = st.text_input(label="Identity", value="a Progressive", placeholder="Short Description")
            debater2_adjs = st.text_input(label="Adjectives",
                                          placeholder="Comma-separated words",
                                          value="pragmatic, empathetic, liberal, nonreligious, anti-gun, pro-choice")

        with st.expander("Settings", expanded=False):
            st.session_state.model_name = st.selectbox("Model",
                                                       ("gpt-3.5-turbo",
                                                        "text-davinci-003"))
            st.session_state.model_type = st.radio("Type",
                                                   ("Chat", "Text"))

        topic = st.text_input(label="Debate Topic:", value="the debt ceiling", placeholder="topic")

        new_debate_button = st.button("New Debate!", type="primary")

    with st.session_state.chat_region:
        st.text(body='''
        Welcome to Master Debaters! If you are curious and want to find satisfaction alone 
        in the privacy of your own room, try our 'baters on your favorite topic. Enjoy!
        ''')

    if new_debate_button:
        if (debater1_name == "" or
                debater2_name == "" or
                debater1_id == "" or
                debater2_id == "" or
                debater1_adjs == "" or
                debater2_adjs == "" or
                topic == ""):
            message(message="Please fill in the debate details!!", avatar_style="bottts")

        else:
            st.session_state.debater1 = Persona(debater1_name, debater1_id, debater1_adjs)
            st.session_state.debater2 = Persona(debater2_name, debater2_id, debater2_adjs)

            reset_messages()
            new_debate(topic)
    else:
        print_debate()

    continue_debate(topic)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
