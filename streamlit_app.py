import logging
import os
from random import seed, randint
from time import sleep

import streamlit as st

from Persona import Persona
from StreamingChat import StreamingChat

AVATAR_STYLE = "pixel-art"

# This application simulates a debate between two personas using OpenAI's API.
# It implements a streaming chat interface using LangChain, OpenAI, and Streamlit.
#
# TODO:
# * Create a sample set of personas and debate topics to be able to randomize
# * Add the ability to upload PDFs about which to debate
# * Add the ability to specify the URL of a news/information page on which to debate


@st.cache_resource
def check_and_load_stsecret(name):
    if name in st.secrets and st.secrets[name] != "":
        os.environ.setdefault(name, st.secrets[name])


@st.cache_resource
def init_random():
    seed()


def init_state():
    if 'debating' not in st.session_state:
        st.session_state.debating = False
        print(f"Session State debating: {st.session_state.debating}")


def init_modes():
    global KASS_KEY_PASS
    global TEST_MODE
    global SHOW_SETTINGS
    global USE_STREAMING

    check_and_load_stsecret("OPENAI_API_KEY")
    check_and_load_stsecret("OPENAI_ORG_ID")
    check_and_load_stsecret("KASS_KEY")
    check_and_load_stsecret("KASS_KEY_PASS")

    if os.getenv("KASS_KEY_PASS") != "":
        KASS_KEY_PASS = os.getenv("KASS_KEY_PASS")

    check_and_load_stsecret("TEST_MODE")
    check_and_load_stsecret("SHOW_SETTINGS")
    check_and_load_stsecret("USE_STREAMING")

    if os.getenv("TEST_MODE") != "":
        TEST_MODE = os.getenv("TEST_MODE") == "True"
    else:
        TEST_MODE = True
    if os.getenv("SHOW_SETTINGS") != "":
        SHOW_SETTINGS = os.getenv("SHOW_SETTINGS") == "True"
    else:
        SHOW_SETTINGS = False
    if os.getenv("USE_STREAMING") != "":
        USE_STREAMING = os.getenv("USE_STREAMING") == "True"
    else:
        USE_STREAMING = False

    logging.warning(f"TEST_MODE = {TEST_MODE}")
    logging.warning(f"SHOW_SETTINGS = {SHOW_SETTINGS}")
    logging.warning(f"USE_STREAMING = {USE_STREAMING}")


def init():
    st.set_page_config(
        page_title="Master Debaters",
        page_icon="🤷‍"
    )

    init_random()
    init_state()
    init_modes()

    if "model_name" not in st.session_state:
        st.session_state.model_name = "gpt-3.5-turbo"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "response_count" not in st.session_state:
        st.session_state.response_count = 0
    if "response" not in st.session_state:
        st.session_state.response = ""

    st.session_state.chat_region = st.empty()
    st.session_state.chat_history = st.container()


def sidebar():
    with st.sidebar:
        if 'OPENAI_API_KEY' not in st.secrets:
            openapi_key = st.text_input(label="OpenAI API Key", value="", type="password")
        else:
            openapi_key = ''
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

        if SHOW_SETTINGS:
            with st.expander("Settings", expanded=False):
                st.session_state.model_name = st.selectbox("Model",
                                                           ("gpt-3.5-turbo", "gpt-3.5", 'gpt-4'))

        topic = st.text_input(label="Debate Topic:", value="the debt ceiling", placeholder="topic")

    st.session_state.debater1 = {
            'name': debater1_name,
            'id': debater1_id,
            'adjs': debater1_adjs
        }
    st.session_state.debater1["avatar"] = \
        f"https://api.dicebear.com/5.x/{AVATAR_STYLE}/svg?seed={st.session_state.debater1['name']}"
    st.session_state.debater2 = {
            'name': debater2_name,
            'id': debater2_id,
            'adjs': debater2_adjs
        }
    st.session_state.debater2["avatar"] = \
        f"https://api.dicebear.com/5.x/{AVATAR_STYLE}/svg?seed={st.session_state.debater2['name']}"
    st.session_state.topic = topic

    set_openapi_key(openapi_key)


def new_debate():
    st.session_state.messages = []

    st.session_state.debater1_chat = StreamingChat()
    st.session_state.debater2_chat = StreamingChat()

    st.session_state.debater1_persona = Persona(st.session_state.debater1['name'],
                                                st.session_state.debater1['id'],
                                                st.session_state.debater1['adjs'])
    st.session_state.debater2_persona = Persona(st.session_state.debater2['name'],
                                                st.session_state.debater2['id'],
                                                st.session_state.debater2['adjs'])

    st.session_state.debater1_response = ""
    st.session_state.debater2_response = ""


def print_debate():
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar=msg["avatar"]):
            st.markdown(msg["content"])


def generate_response_pair(topic, phase):
    with st.chat_message("user", avatar=st.session_state.debater1["avatar"]):
        message_placeholder = st.empty()
        full_response = ""
        if TEST_MODE:
            chat_response_generator = ChatTestIterator()
        else:
            chat = st.session_state.debater1_chat
            persona = st.session_state.debater1_persona
            chat_response_generator = chat.response(persona.prompt_for_phase(phase,
                                                                             topic,
                                                                             st.session_state.debater2_response))
        for response in chat_response_generator:
            full_response += response
            message_placeholder.markdown(full_response + " ")
        message_placeholder.markdown(full_response)
        st.session_state.debater1_response = full_response

    st.session_state.messages.append({"role": st.session_state.debater1["name"],
                                      "avatar": st.session_state.debater1["avatar"],
                                      "content": st.session_state.debater1_response})

    with st.chat_message("user", avatar=st.session_state.debater2["avatar"]):
        message_placeholder = st.empty()
        full_response = ""
        if TEST_MODE:
            chat_response_generator = ChatTestIterator()
        else:
            chat = st.session_state.debater2_chat
            persona = st.session_state.debater2_persona
            chat_response_generator = chat.response(persona.prompt_for_phase(phase,
                                                                             topic,
                                                                             st.session_state.debater1_response))
        for response in chat_response_generator:
            full_response += response
            message_placeholder.markdown(full_response + " ")
        message_placeholder.markdown(full_response)
        st.session_state.debater2_response = full_response

    st.session_state.messages.append({"role": st.session_state.debater2["name"],
                                      "avatar": st.session_state.debater2["avatar"],
                                      "content": full_response})

    st.session_state.response_count += 2


def is_debate_info_complete():
    return (st.session_state.debater1['name'] != "" and
            st.session_state.debater2['name'] != "" and
            st.session_state.debater1['id'] != "" and
            st.session_state.debater2['id'] != "" and
            st.session_state.debater1['adjs'] != "" and
            st.session_state.debater2['adjs'] != "" and
            st.session_state.topic != "")


def set_openapi_key(key):
    if key != '':
        if key == KASS_KEY_PASS and os.getenv("KASS_KEY") is not None:
            os.environ["OPENAI_API_KEY"] = os.getenv("KASS_KEY")
        else:
            os.environ["OPENAI_API_KEY"] = key


def main():
    init()

    # Get debater information from sidebar
    sidebar()

    st.text(body='''
        Welcome to Master Debaters! They will debate on the topic of your choice. Enjoy!
        ''')
    chat_area = st.empty()
    appendix = st.empty()

    with chat_area.container():
        print_debate()
        with appendix.container():
            with st.container():
                col1, col2, col3 = st.columns(3)
                new_chat = col1.button("New Chat", disabled=st.session_state.debating)
                continue_chat = col2.button("Continue Chat", disabled=not st.session_state.debating)
                conclude_chat = col3.button("Conclude Chat", disabled=not st.session_state.debating)

    if new_chat:
        if not is_debate_info_complete():
            with st.chat_message("assistant"):
                st.markdown("Please fill in the debate details!!")
        elif not os.getenv("OPENAI_API_KEY"):
            with st.chat_message("assistant"):
                st.markdown("Please set your OpenAI API key.")
        else:
            new_debate()
            chat_area.empty()
            with appendix.container():
                generate_response_pair(st.session_state.topic, "opening")
            st.session_state.debating = True
            st.experimental_rerun()

    if continue_chat:
        with appendix.container():
            generate_response_pair(st.session_state.topic, "responding")
        st.experimental_rerun()

    if conclude_chat:
        with appendix.container():
            generate_response_pair(st.session_state.topic, "conclusion")
        st.session_state.debating = False
        st.experimental_rerun()


# Return a string of random numbers to simulate a streaming chat service
class ChatTestIterator:
    def __init__(self, count=10):
        self.count = count

    def __iter__(self):
        # pause 0.5 seconds and yield a new random number.
        for i in range(self.count):
            sleep(0.2)
            yield f"{randint(0, 100)} "


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
