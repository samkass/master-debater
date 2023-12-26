import logging
import os

import streamlit as st

from ChatTestIterator import ChatTestIterator
from DocumentSummarizer import DocumentSummarizer, EmbeddingsException
from ParleyPossibilities import PARLEY_DEBATE_TOPIC_LIST, PARLEY_DEBATE_PERSONA_LIST
from Persona import Persona
from DebateRandomizer import DebateRandomizer
from StreamingChat import StreamingChat
from StreamingChatWithEmbeddings import StreamingChatWithEmbeddings


# This application simulates a debate between two personas using OpenAI's API.
# It implements a streaming chat interface using LangChain, OpenAI, and Streamlit.


@st.cache_resource
def check_and_load_stsecret(name):
    if name in st.secrets and st.secrets[name] != "":
        os.environ.setdefault(name, st.secrets[name])


def init_state():
    if 'debating' not in st.session_state:
        st.session_state.debating = False
        print(f"Session State debating: {st.session_state.debating}")


def init_modes():
    # Load keys from secrets and put into env variables
    check_and_load_stsecret("OPENAI_API_KEY")
    check_and_load_stsecret("OPENAI_ORG_ID")
    check_and_load_stsecret("KASS_KEY")
    check_and_load_stsecret("KASS_KEY_PASS")
    check_and_load_stsecret("CITI_KEY")
    check_and_load_stsecret("CITI_KEY_PASS")

    # Load settings from secrets and put into env variables
    check_and_load_stsecret("TEST_MODE")
    check_and_load_stsecret("SHOW_SETTINGS")
    check_and_load_stsecret("USE_STREAMING")
    check_and_load_stsecret("VERBOSE_LOGGING")
    check_and_load_stsecret("ALLOW_DOCS")

    # Also put settings into session state
    if os.getenv("TEST_MODE") != "":
        test_mode = os.getenv("TEST_MODE") == "True"
    else:
        test_mode = True
    if os.getenv("SHOW_SETTINGS") != "":
        show_settings = os.getenv("SHOW_SETTINGS") == "True"
    else:
        show_settings = False
    if os.getenv("USE_STREAMING") != "":
        use_streaming = os.getenv("USE_STREAMING") == "True"
    else:
        use_streaming = False
    if os.getenv("VERBOSE_LOGGING") != "":
        verbose_logging = os.getenv("VERBOSE_LOGGING") == "True"
    else:
        verbose_logging = False
    if os.getenv("ALLOW_DOCS") != "":
        allow_docs = os.getenv("ALLOW_DOCS") == "True"
    else:
        allow_docs = False

    st.session_state.settings = {
        "test_mode": test_mode,
        "show_settings": show_settings,
        "use_streaming": use_streaming,
        "verbose_logging": verbose_logging,
        "allow_docs": allow_docs
    }

    logging.getLogger().setLevel(logging.DEBUG if verbose_logging else logging.INFO)
    logging.info(f"TEST_MODE = {st.session_state.settings['test_mode']}")
    logging.info(f"SHOW_SETTINGS = {st.session_state.settings['show_settings']}")
    logging.info(f"USE_STREAMING = {st.session_state.settings['use_streaming']}")
    logging.info(f"VERBOSE_LOGGING = {st.session_state.settings['verbose_logging']}")


def init_debaters():
    if 'randomizer' not in st.session_state:
        params = st.experimental_get_query_params()
        if params is not None and 'parleyMode' in params and params['parleyMode'][0] == 'true':
            st.session_state.randomizer = DebateRandomizer(topics=PARLEY_DEBATE_TOPIC_LIST,
                                                           personas=PARLEY_DEBATE_PERSONA_LIST)
        else:
            st.session_state.randomizer = DebateRandomizer()
    if 'dropdown_mode' not in st.session_state:
        params = st.experimental_get_query_params()
        st.session_state.dropdown_mode = \
            params is not None and 'parleyMode' in params and params['parleyMode'][0] == 'true'
    if 'debater1_name' not in st.session_state or 'debater2_name' not in st.session_state:
        randomize_debaters()
    if 'topic' not in st.session_state:
        st.session_state.topic = st.session_state.randomizer.get_topic()


def init():
    st.set_page_config(
        page_title="Master-Debaters",
        page_icon="🤷‍",
        menu_items={
            "About": '''Master Debater  
https://master-debater.streamlit.app  
Copyright 2023 Sam Kass. All Rights Reserved.'''
        }
    )

    init_state()
    init_modes()
    init_debaters()

    if "model_name" not in st.session_state:
        st.session_state.model_name = "gpt-3.5-turbo"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "response" not in st.session_state:
        st.session_state.response = ""
    if "embeddings" not in st.session_state:
        st.session_state.embeddings = None


def generate_dropdowns():
    st.session_state.persona_name_list = st.session_state.randomizer.get_persona_name_list()
    st.session_state.persona_displayname_list = st.session_state.randomizer.get_persona_displayname_list()


def set_debater1_from_persona(persona):
    st.session_state.debater1_name = persona.name
    st.session_state.debater1_identity = persona.identity
    st.session_state.debater1_adjectives = persona.adjectives


def set_debater2_from_persona(persona):
    st.session_state.debater2_name = persona.name
    st.session_state.debater2_identity = persona.identity
    st.session_state.debater2_adjectives = persona.adjectives


def randomize_debaters():
    debater1 = st.session_state.randomizer.create_random_persona()
    debater2 = st.session_state.randomizer.create_random_persona()
    while debater2.name == debater1.name:
        debater2 = st.session_state.randomizer.create_random_persona()

    set_debater1_from_persona(debater1)
    set_debater2_from_persona(debater2)


def process_pdf():
    print("Processing PDF.")
    if st.session_state.pdf is not None:
        with st.spinner("Processing PDF."):
            try:
                st.session_state.embeddings = DocumentSummarizer(st.session_state.pdf).to_embeddings()
                st.session_state.messages.append({"role": "assistant",
                                                  "avatar": "🤖",
                                                  "content": f'''
                PDF {st.session_state.pdf.name} processed successfully. Debaters will draw on it for context.
                '''})
            except EmbeddingsException as e:
                st.session_state.messages.append({"role": "assistant",
                                                  "avatar": "🤖",
                                                  "content": '''
                                          Error creating embeddings. Are you sure your OpenAI API key is correct?
                                          Please check your key, then remove and re-add the PDF.'''})
    else:
        st.session_state.embeddings = None


def sidebar():
    with st.sidebar:
        if 'OPENAI_API_KEY' not in st.secrets:
            openapi_key = st.text_input(label="OpenAI API Key",
                                        value="",
                                        type="password",
                                        help="Not stored to disk or logged")
            st.divider()
        else:
            openapi_key = ''

        if st.session_state.dropdown_mode:
            generate_dropdowns()

        with st.container():
            col1, col2 = st.columns(2)
            col1.markdown("Enter debate info or ")
            randomize = col2.button("Randomize", disabled=st.session_state.debating)
            if randomize:
                randomize_debaters()
                st.session_state.topic = st.session_state.randomizer.get_topic()
                if st.session_state.dropdown_mode:
                    st.session_state.debater1_displayname = \
                        st.session_state.persona_displayname_list[
                            st.session_state.persona_name_list.index(st.session_state.debater1_name)
                        ]
                    st.session_state.debater2_displayname = \
                        st.session_state.persona_displayname_list[
                            st.session_state.persona_name_list.index(st.session_state.debater2_name)
                        ]

        st.text_input(label="Debate Topic",
                      key="topic",
                      placeholder="topic",
                      disabled=st.session_state.debating)

        with st.expander("Debater", expanded=True):
            if st.session_state.dropdown_mode:
                st.selectbox(
                    label="Debater Name",
                    key="debater1_displayname",
                    options=st.session_state.persona_displayname_list,
                    placeholder="Name",
                    disabled=st.session_state.debating,
                    help="Name of the first debater")
                debater1_name_index = \
                    st.session_state.persona_displayname_list.index(st.session_state.debater1_displayname)
                debater1_name = st.session_state.persona_name_list[debater1_name_index]
                set_debater1_from_persona(st.session_state.randomizer.get_persona_object(name=debater1_name))
            else:
                st.text_input(label="Debater Name",
                              key="debater1_name",
                              placeholder="Name",
                              disabled=st.session_state.debating,
                              help="Can be a real person or completely fictional")
            st.text_input(label="Debater Identity",
                          key="debater1_identity",
                          placeholder="Short Description",
                          disabled=st.session_state.debating,
                          help=f"A couple words, for example, 'a football player'")
            st.text_input(label="Debater Adjectives",
                          key="debater1_adjectives",
                          placeholder="Comma-separated words",
                          disabled=st.session_state.debating,
                          help="A couple of adjectives, for example, 'smart, funny, charming'"
                          )

        with st.expander("Opponent", expanded=True):
            if st.session_state.dropdown_mode:
                st.selectbox(
                    label="Debater Name",
                    key="debater2_displayname",
                    options=st.session_state.persona_displayname_list,
                    placeholder="Name",
                    disabled=st.session_state.debating,
                    help="Name of the opponent debater")
                debater2_name_index = \
                    st.session_state.persona_displayname_list.index(st.session_state.debater2_displayname)
                debater2_name = st.session_state.persona_name_list[debater2_name_index]
                set_debater2_from_persona(st.session_state.randomizer.get_persona_object(name=debater2_name))
            else:
                st.text_input(label="Opponent Name",
                              key="debater2_name",
                              placeholder="Name",
                              disabled=st.session_state.debating,
                              help="Can be a real person or completely fictional")
            st.text_input(label="Opponent Identity",
                          key="debater2_identity",
                          placeholder="Short Description",
                          disabled=st.session_state.debating,
                          help=f"A couple words, for example, 'a cheerleader'")
            st.text_input(label="Opponent Adjectives",
                          key="debater2_adjectives",
                          placeholder="Comma-separated words",
                          disabled=st.session_state.debating,
                          help="A couple of adjectives, for example, 'smart, funny, charming'")

            if st.session_state.settings["show_settings"]:
                with st.expander("Settings", expanded=False):
                    st.session_state.model_name = st.selectbox("Model",
                                                               ("gpt-3.5-turbo-16k", "gpt-3.5-turbo", "gpt-3.5", 'gpt-4'))
        if st.session_state.settings["allow_docs"]:
            st.file_uploader("PDF Document (optional)",
                             type="pdf",
                             on_change=process_pdf,
                             key="pdf",
                             disabled=st.session_state.debating,
                             help="Will be used to provide additional or up-to-date context to debaters.")

    set_openapi_key(openapi_key)


def new_debate():
    st.session_state.messages = []

    if st.session_state.embeddings is None:
        st.session_state.debater1_chat = StreamingChat(verbose=st.session_state.settings['verbose_logging'])
        st.session_state.debater2_chat = StreamingChat(verbose=st.session_state.settings['verbose_logging'])
    else:
        st.session_state.debater1_chat = \
            StreamingChatWithEmbeddings(embeddings=st.session_state.embeddings,
                                        verbose=st.session_state.settings['verbose_logging'])
        st.session_state.debater2_chat = \
            StreamingChatWithEmbeddings(embeddings=st.session_state.embeddings,
                                        verbose=st.session_state.settings['verbose_logging'])

    st.session_state.debater1_response = ""
    st.session_state.debater2_response = ""


def print_debate():
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar=msg["avatar"]):
            st.markdown(msg["content"])


def chat_response_generator(topic, phase, chat, persona, opponent_response):
    if st.session_state.settings['test_mode']:
        chat_response = ChatTestIterator()
    else:
        chat_response = chat.response(persona.prompt_for_phase(phase,
                                                               topic,
                                                               opponent_response))
    return chat_response


def generate_response(phase, topic, chat, persona, opponent_response):
    with st.chat_message("user", avatar=persona.avatar):
        message_placeholder = st.empty()
        full_response = ""
        chat_responses = chat_response_generator(topic, phase, chat, persona, opponent_response)
        for response in chat_responses:
            full_response += response
            message_placeholder.markdown(full_response + " ")
        message_placeholder.markdown(full_response)
    return full_response


def generate_response_pair(phase):
    debater1_persona = Persona(name=st.session_state.debater1_name,
                               identity=st.session_state.debater1_identity,
                               adjectives=st.session_state.debater1_adjectives)
    st.session_state.debater1_response = generate_response(phase,
                                                           st.session_state.topic,
                                                           st.session_state.debater1_chat,
                                                           debater1_persona,
                                                           st.session_state.debater2_response)
    st.session_state.messages.append({"role": debater1_persona.name,
                                      "avatar": debater1_persona.avatar,
                                      "content": st.session_state.debater1_response})

    debater2_persona = Persona(name=st.session_state.debater2_name,
                               identity=st.session_state.debater2_identity,
                               adjectives=st.session_state.debater2_adjectives)
    st.session_state.debater2_response = generate_response(phase,
                                                           st.session_state.topic,
                                                           st.session_state.debater2_chat,
                                                           debater2_persona,
                                                           st.session_state.debater1_response)
    st.session_state.messages.append({"role": debater2_persona.name,
                                      "avatar": debater2_persona.avatar,
                                      "content": st.session_state.debater2_response})


def is_debate_info_complete():
    return (st.session_state.debater1_name != "" and
            st.session_state.debater2_name != "" and
            st.session_state.debater1_identity != "" and
            st.session_state.debater2_identity != "" and
            st.session_state.debater1_adjectives != "" and
            st.session_state.debater2_adjectives != "" and
            st.session_state.topic != "")


def set_openapi_key(key):
    if key != '':
        if os.getenv("KASS_KEY_PASS") is not None and \
                key == os.getenv("KASS_KEY_PASS") and \
                os.getenv("KASS_KEY") is not None:
            os.environ["OPENAI_API_KEY"] = os.getenv("KASS_KEY")
        elif os.getenv("CITI_KEY_PASS") is not None and \
                key == os.getenv("CITI_KEY_PASS") and \
                os.getenv("CITI_KEY") is not None:
            os.environ["OPENAI_API_KEY"] = os.getenv("CITI_KEY")
        else:
            os.environ["OPENAI_API_KEY"] = key


def main():
    init()

    st.text(body='''
        Welcome to Master Debaters! They will debate on the topic of your choice. Enjoy!
        ''')

    # Get debater information from sidebar
    sidebar()

    chat_area = st.empty()
    appendix = st.empty()

    with chat_area.container():
        print_debate()
        with appendix.container():
            with st.container():
                col1, col2, col3 = st.columns(3)
                new_chat = col1.button("New Debate", key="NewDebateButton", disabled=st.session_state.debating)
                continue_chat = col2.button("Continue Debate", key="ContinueDebateButton", disabled=not st.session_state.debating)
                conclude_chat = col3.button("Conclude Debate", key="ConcludeDebateButton", disabled=not st.session_state.debating)

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
                generate_response_pair("opening")
            st.session_state.debating = True
            st.rerun()

    if continue_chat:
        with appendix.container():
            generate_response_pair("response")
        st.rerun()

    if conclude_chat:
        with appendix.container():
            generate_response_pair("conclusion")
        st.session_state.debating = False
        st.rerun()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
