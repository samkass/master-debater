import logging
import os

import streamlit as st
import streamlit.components.v1 as components

from ChatTestIterator import ChatTestIterator
from DocumentSummarizer import DocumentSummarizer, EmbeddingsException
from ParleyPossibilities import PARLEY_DEBATE_TOPIC_LIST, PARLEY_DEBATE_PERSONA_LIST
from Persona import Persona
from DebateRandomizer import DebateRandomizer
from StreamingChat import StreamingChat
from StreamingChatWithEmbeddings import StreamingChatWithEmbeddings

# Define adsense component for use in sidebar
adsense_component = components.declare_component(
    "adsense_component",
    path="./adsense_component"
)

# This application simulates a debate between two personas using OpenAI's API.
# It implements a streaming chat interface using LangChain, OpenAI, and Streamlit.


# If there is a secrets file, load the secret and put it into an env variable
@st.cache_resource
def check_and_load_stsecret(name):
    try:
        if name in st.secrets and st.secrets[name] != "":
            os.environ.setdefault(name, st.secrets[name])
    except OSError as e:
        logging.error(f"Secrets file missing or unloadable for {name}")


@st.cache_resource
def getenv_bool(name, default):
    return os.getenv(name, default).strip('"') == "True"


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
    check_and_load_stsecret("SHOW_ADS")

    # Also put settings into session state
    test_mode = getenv_bool("TEST_MODE", "True")
    show_settings = getenv_bool("SHOW_SETTINGS", "False")
    use_streaming = getenv_bool("USE_STREAMING", "True")
    verbose_logging = getenv_bool("VERBOSE_LOGGING", "False")
    allow_docs = getenv_bool("ALLOW_DOCS", "False")
    show_ads = getenv_bool("SHOW_ADS", "False")

    st.session_state.settings = {
        "test_mode": test_mode,
        "show_settings": show_settings,
        "use_streaming": use_streaming,
        "verbose_logging": verbose_logging,
        "allow_docs": allow_docs,
        "show_ads": show_ads
    }

    logging.getLogger().setLevel(logging.DEBUG if verbose_logging else logging.INFO)
    logging.info(f"TEST_MODE = {st.session_state.settings['test_mode']}")
    logging.info(f"SHOW_SETTINGS = {st.session_state.settings['show_settings']}")
    logging.info(f"USE_STREAMING = {st.session_state.settings['use_streaming']}")
    logging.info(f"VERBOSE_LOGGING = {st.session_state.settings['verbose_logging']}")
    logging.info(f"ALLOW_DOCS = {st.session_state.settings['allow_docs']}")
    logging.info(f"SHOW_ADS = {st.session_state.settings['show_ads']}")
    logging.info(f"{st.session_state.settings}")


def init_debaters():
    params = st.query_params
    parley_mode = params is not None \
                  and 'parleyMode' in params \
                  and params['parleyMode'] == 'true'
    if 'randomizer' not in st.session_state:
        if parley_mode:
            st.session_state.randomizer = DebateRandomizer(topics=PARLEY_DEBATE_TOPIC_LIST,
                                                           personas=PARLEY_DEBATE_PERSONA_LIST)
        else:
            st.session_state.randomizer = DebateRandomizer()
    if 'debater1_name' not in st.session_state or 'debater2_name' not in st.session_state:
        randomize_debaters()
    if 'dropdown_mode' not in st.session_state:
        st.session_state.dropdown_mode = parley_mode
    if 'topic' not in st.session_state:
        st.session_state.topic = st.session_state.randomizer.get_topic()


def init():
    st.set_page_config(
        page_title="Master-Debaters",
        page_icon=":shrug:",
        menu_items={
            "About": '''Master Debaters  
https://chat.master-debaters.com 
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
        if not os.getenv("OPENAI_API_KEY"):
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
                st.session_state.debater1_displayname = \
                    st.session_state.persona_displayname_list[
                        st.session_state.persona_name_list.index(st.session_state.debater1_name)
                    ]
                debater1_name_index = \
                    st.session_state.persona_displayname_list.index(st.session_state.debater1_displayname)
                st.selectbox(
                    label="Debater Name",
                    key="debater1_displayname",
                    options=st.session_state.persona_displayname_list,
                    placeholder="Name",
                    disabled=st.session_state.debating,
                    help="Name of the first debater")
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
                st.session_state.debater2_displayname = \
                    st.session_state.persona_displayname_list[
                        st.session_state.persona_name_list.index(st.session_state.debater2_name)
                    ]
                debater2_name_index = \
                    st.session_state.persona_displayname_list.index(st.session_state.debater2_displayname)
                st.selectbox(
                    label="Debater Name",
                    key="debater2_displayname",
                    options=st.session_state.persona_displayname_list,
                    placeholder="Name",
                    disabled=st.session_state.debating,
                    help="Name of the opponent debater")
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

        if st.session_state.settings["show_ads"]:
            # html_file = open("./adsense.html", 'r', encoding='utf-8')
            # source_code = html_file.read()
            # print(source_code)
            # components.html(source_code, height=400)
            adsense_component(key="adsense_component", height=400)

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


def print_instructions():
    with st.container(border=True):
        st.text(body='''
            Master Debaters will debate on the topic of your choice, taking the
            personas as described in the sidebar. They will attempt to use the context 
            of the PDF document, if provided. The first debater will take a position
            on the topic, and the opponent will be required to take the opposite side.
            
            If a persona is that of a well-known figure, it will attempt to imitate 
            the style of speech of that figure. The text produced should not be construed 
            as the actual opinion of the figure. Also, the avatars are randomly generated 
            from the name, and do not represent the actual figure.
            
            Finally, please understand that this is automatically generated text and can 
            contain factual errors. All that being said, Enjoy!
            ''')


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

                instructions_area = st.empty()

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

    if len(st.session_state.messages) == 0:
        with instructions_area:
            print_instructions()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
