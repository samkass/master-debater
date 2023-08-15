import logging
import os
from random import seed, randint
from time import sleep

import streamlit as st

from Persona import Persona, create_random_persona
from Possibilities import DebateRandomizer
from StreamingChat import StreamingChat

# This application simulates a debate between two personas using OpenAI's API.
# It implements a streaming chat interface using LangChain, OpenAI, and Streamlit.
#
# TODO:
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


def init_debaters():
    if 'debater1' not in st.session_state:
        st.session_state.debater1 = create_random_persona()
    if 'debater2' not in st.session_state:
        st.session_state.debater2 = create_random_persona()
    if 'topic' not in st.session_state:
        st.session_state.topic = DebateRandomizer.get_topic()


def init():
    st.set_page_config(
        page_title="Master-Debaters",
        page_icon="🤷‍"
    )

    init_random()
    init_state()
    init_modes()
    init_debaters()

    if "model_name" not in st.session_state:
        st.session_state.model_name = "gpt-3.5-turbo"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "response" not in st.session_state:
        st.session_state.response = ""

    st.session_state.chat_region = st.empty()
    st.session_state.chat_history = st.container()


def sidebar():
    with st.sidebar:
        randomize = st.button("Randomize", disabled=st.session_state.debating)
        if randomize:
            st.session_state.debater1 = create_random_persona()
            st.session_state.debater2 = create_random_persona()
            st.session_state.topic = DebateRandomizer.get_topic()

        if 'OPENAI_API_KEY' not in st.secrets:
            openapi_key = st.text_input(label="OpenAI API Key", value="", type="password")
        else:
            openapi_key = ''

        topic = st.text_input(label="Debate Topic:",
                              value=st.session_state.topic,
                              placeholder="topic",
                              disabled=st.session_state.debating)

        with st.expander("Debater", expanded=True):
            debater1_name = st.text_input(label="Name",
                                          value=st.session_state.debater1.name,
                                          placeholder="Name",
                                          key=f"{randint(0, 100000)}",
                                          disabled=st.session_state.debating)
            debater1_id = st.text_input(label="Identity",
                                        value=st.session_state.debater1.identity,
                                        placeholder="Short Description",
                                        key=f"{randint(0, 100000)}",
                                        disabled=st.session_state.debating)
            debater1_adjs = st.text_input(label="Adjectives",
                                          value=st.session_state.debater1.adjectives,
                                          placeholder="Comma-separated words",
                                          key=f"{randint(0, 100000)}",
                                          disabled=st.session_state.debating)

        with st.expander("Opponent", expanded=True):
            debater2_name = st.text_input(label="Name",
                                          value=st.session_state.debater2.name,
                                          placeholder="Name",
                                          key=f"{randint(0, 100000)}",
                                          disabled=st.session_state.debating)
            debater2_id = st.text_input(label="Identity",
                                        value=st.session_state.debater2.identity,
                                        placeholder="Short Description",
                                        key=f"{randint(0, 100000)}",
                                        disabled=st.session_state.debating)
            debater2_adjs = st.text_input(label="Adjectives",
                                          value=st.session_state.debater2.adjectives,
                                          placeholder="Comma-separated words",
                                          key=f"{randint(0, 100000)}",
                                          disabled=st.session_state.debating)

        if SHOW_SETTINGS:
            with st.expander("Settings", expanded=False):
                st.session_state.model_name = st.selectbox("Model",
                                                           ("gpt-3.5-turbo", "gpt-3.5", 'gpt-4'))

    st.session_state.debater1 = Persona(debater1_name, debater1_id, debater1_adjs)
    st.session_state.debater2 = Persona(debater2_name, debater2_id, debater2_adjs)
    st.session_state.topic = topic

    set_openapi_key(openapi_key)


def new_debate():
    st.session_state.messages = []

    st.session_state.debater1_chat = StreamingChat()
    st.session_state.debater2_chat = StreamingChat()

    st.session_state.debater1_response = ""
    st.session_state.debater2_response = ""


def print_debate():
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar=msg["avatar"]):
            st.markdown(msg["content"])


def chat_response_generator(topic, phase, chat, persona, opponent_response):
    if TEST_MODE:
        chat_response = ChatTestIterator()
    else:
        chat_response = chat.response(persona.prompt_for_phase(phase,
                                                               topic,
                                                               opponent_response))
    return chat_response


def generate_response(topic, phase, chat, persona, opponent_response):
    with st.chat_message("user", avatar=persona.avatar):
        message_placeholder = st.empty()
        full_response = ""
        chat_responses = chat_response_generator(topic, phase, chat, persona, opponent_response)
        for response in chat_responses:
            full_response += response
            message_placeholder.markdown(full_response + " ")
        message_placeholder.markdown(full_response)
    return full_response


def generate_response_pair(topic, phase):
    st.session_state.debater1_response = generate_response(topic,
                                                           phase,
                                                           st.session_state.debater1_chat,
                                                           st.session_state.debater1,
                                                           st.session_state.debater2_response)
    st.session_state.messages.append({"role": st.session_state.debater1.name,
                                      "avatar": st.session_state.debater1.avatar,
                                      "content": st.session_state.debater1_response})

    st.session_state.debater2_response = generate_response(topic,
                                                           phase,
                                                           st.session_state.debater2_chat,
                                                           st.session_state.debater2,
                                                           st.session_state.debater1_response)
    st.session_state.messages.append({"role": st.session_state.debater2.name,
                                      "avatar": st.session_state.debater2.avatar,
                                      "content": st.session_state.debater2_response})


def is_debate_info_complete():
    return (st.session_state.debater1.name != "" and
            st.session_state.debater2.name != "" and
            st.session_state.debater1.identity != "" and
            st.session_state.debater2.identity != "" and
            st.session_state.debater1.adjectives != "" and
            st.session_state.debater2.adjectives != "" and
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
                new_chat = col1.button("New Debate", disabled=st.session_state.debating)
                continue_chat = col2.button("Continue Debate", disabled=not st.session_state.debating)
                conclude_chat = col3.button("Conclude Debate", disabled=not st.session_state.debating)

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
            generate_response_pair(st.session_state.topic, "response")
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
