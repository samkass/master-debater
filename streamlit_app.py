import logging
import os
from random import seed, randint

import streamlit as st
from langchain.memory import ConversationSummaryBufferMemory

from Persona import Persona
from StreamingChat import StreamingChat

AVATAR_STYLE = "pixel-art"


@st.cache_resource
def check_and_load_stsecret(name):
    if name in st.secrets and st.secrets[name] != "":
        os.environ.setdefault(name, st.secrets[name])


@st.cache_resource
def init_random():
    seed()


def init_state():
    if 'state' not in st.session_state:
        st.session_state.state = 'SETUP'


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

    st.session_state.chat_region = st.container()


def sidebar():
    with st.sidebar:
        openapi_key = st.text_input(label="OpenAI API Key", value="", type="password")
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

        new_debate_button = st.button("New Debate!", type="primary")

    return {
        'openapi_key': openapi_key,
        'debater1': {
            'name': debater1_name,
            'id': debater1_id,
            'adjs': debater1_adjs
        },
        'debater2': {
            'name': debater2_name,
            'id': debater2_id,
            'adjs': debater2_adjs
        },
        'topic': topic,
        'new_debate_button': new_debate_button,
    }


def print_debate():
    if st.session_state.state == 'DEBATING':
        with st.session_state.chat_region:
            for i, msg in enumerate(st.session_state.messages):
                with st.chat_message(msg["role"], avatar=msg["avatar"]):
                    st.markdown(msg["content"])


def new_debate(topic):
    st.session_state.messages = []
    st.session_state.state = 'DEBATING'

    st.session_state.debater1_chat = StreamingChat()
    st.session_state.debater2_chat = StreamingChat()

    st.session_state.debater1_response = ""
    st.session_state.debater2_response = ""


def generate_response_pair(topic, phase):
    st.session_state.debate_id = randint(10000000, 100000000)

    st.session_state.debater1_response = ""
    with st.session_state.chat_region:
        with st.chat_message("user", avatar=st.session_state.debater1["avatar"]):
            message_placeholder = st.empty()
            full_response = ""
            for response in st.session_state.debater1_chat.\
                    response(st.session_state.debater1_persona.prompt_for_phase(phase,
                                                                                topic,
                                                                                st.session_state.debater2_response)):
                full_response += response
                message_placeholder.markdown(full_response + " ")
            message_placeholder.markdown(full_response)
            st.session_state.debater1_response = full_response

    st.session_state.messages.append({"role": st.session_state.debater1["name"],
                                      "avatar": st.session_state.debater1["avatar"],
                                      "content": st.session_state.debater1_response})

    with st.session_state.chat_region:
        with st.chat_message("user", avatar=st.session_state.debater2["avatar"]):
            message_placeholder = st.empty()
            full_response = ""
            for response in st.session_state.debater2_chat.\
                    response(st.session_state.debater2_persona.prompt_for_phase(phase,
                                                                                topic,
                                                                                st.session_state.debater2_response)):
                full_response += response
                message_placeholder.markdown(full_response + " ")
            message_placeholder.markdown(full_response)

            st.session_state.messages.append({"role": st.session_state.debater2["name"],
                                              "avatar": st.session_state.debater2["avatar"],
                                              "content": full_response})
    st.session_state.response_count += 2


def continue_debate(topic):
    if st.session_state.response_count > 0 and st.session_state.state != 'DONE':
        col1, col2 = st.columns(2)
        continue_debate_button = col1.button("Continue Debate",
                                             type="primary")
        conclude_debate_button = col2.button("Conclude Debate",
                                             type="primary")

        if continue_debate_button:
            generate_response_pair(topic, "response")
        if conclude_debate_button:
            st.session_state.state = 'DONE'
            generate_response_pair(topic, "conclusion")


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
        if key == KASS_KEY_PASS and os.getenv("OPENAI_API_KEY") is not None:
            os.environ["OPENAI_API_KEY"] = os.getenv("KASS_KEY")
        else:
            os.environ["OPENAI_API_KEY"] = key


def main():
    init()

    # Get debater information from sidebar
    sidebar_values = sidebar()
    openapi_key = sidebar_values['openapi_key']
    st.session_state.debater1 = sidebar_values['debater1']
    st.session_state.debater1["avatar"] = \
        f"https://api.dicebear.com/5.x/{AVATAR_STYLE}/svg?seed={st.session_state.debater1['name']}"
    st.session_state.debater2 = sidebar_values['debater2']
    st.session_state.debater2["avatar"] = \
        f"https://api.dicebear.com/5.x/{AVATAR_STYLE}/svg?seed={st.session_state.debater2['name']}"
    st.session_state.topic = sidebar_values['topic']
    st.session_state.new_debate_button = sidebar_values['new_debate_button']

    with st.session_state.chat_region:
        st.text(body='''
        Welcome to Master Debaters! They will debate on the topic of your choice. Enjoy!
        ''')

    set_openapi_key(openapi_key)

    print_debate()

    if st.session_state.new_debate_button:
        if not is_debate_info_complete():
            with st.chat_message("assistant"):
                st.markdown("Please fill in the debate details!!")
        else:
            st.session_state.debater1_persona = Persona(st.session_state.debater1['name'],
                                                           st.session_state.debater1['id'],
                                                           st.session_state.debater1['adjs'])
            st.session_state.debater2_persona = Persona(st.session_state.debater2['name'],
                                                           st.session_state.debater2['id'],
                                                           st.session_state.debater2['adjs'])

            st.session_state.state = 'DEBATING'
            new_debate(st.session_state.topic)
            generate_response_pair(st.session_state.topic, "opening")

    continue_debate(st.session_state.topic)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
