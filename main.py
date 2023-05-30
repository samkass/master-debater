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


@st.cache_resource
def generate_llm(model_name="gpt-3.5-turbo", is_chat=True, temperature=0.9):
    if is_chat:
        llm = ChatOpenAI(model_name=model_name, temperature=temperature)
    else:
        llm = OpenAI(model_name=model_name, temperature=temperature)
    return llm


def init():
    load_dotenv()

    st.set_page_config(
        page_title="Master Debaters",
        page_icon="🤷‍"
    )
    st.session_state.model_name = "gpt-3.5-turbo"
    st.session_state.model_type = "Chat"


def run_chain_with_cb(chain, query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        print(cb)

    return result


def generate_debate(debater1, debater2, topic):
    if "messages" not in st.session_state:
        st.session_state.messages = []

    llm = generate_llm(st.session_state.model_name, st.session_state.model_type == "Chat")
    debater1_conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=650
        )
    )
    debater2_conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=650
        )
    )
    with st.spinner("Thinking..."):
        response = run_chain_with_cb(debater1_conversation, debater1.opening_prompt(topic))
#    st.session_state.messages.append(DebateMessage(message=response, name=debater1.name))
    st.session_state.messages.append(ChatMessage(content=response, role=debater1.name))
    message(message=response, is_user=False, avatar_style="pixel-art", seed=debater1.name)

    with st.spinner("Thinking..."):
        response = run_chain_with_cb(debater2_conversation, debater2.opening_prompt(topic, response))
    st.session_state.messages.append(ChatMessage(content=response, role=debater2.name))
    message(message=response, is_user=True, avatar_style="pixel-art", seed=debater2.name)

    # print(debater2_response)
    # debater1_response = run_chain_with_cb(debater1_conversation, debater1.response_prompt(debater2_response))
    # print(debater1_response)
    # debater2_response = run_chain_with_cb(debater2_conversation, debater2.response_prompt(debater1_response))
    # print(debater2_response)
    # debater1_response = run_chain_with_cb(debater1_conversation, debater1.conclusion_prompt())
    # print(debater1_response)
    # debater2_response = run_chain_with_cb(debater2_conversation, debater2.conclusion_prompt())
    # print(debater2_response)


def main():
    init()

    with st.sidebar:
        with st.expander("Debater", expanded=True):
            debater1_name = st.text_input(label="Name", value="Bo", placeholder="Name")
            debater1_id = st.text_input(label="Identity", value="a Conservative", placeholder="Short Description")
            debater1_adjs = st.text_input(label="Adjectives",
                                          placeholder="Comma-separated words",
                                          value="ideological, serious, religious, Christian, pro-life")

        with st.expander("Opponent", expanded=True):
            debater2_name = st.text_input(label="Name", value="Luke", placeholder="Name")
            debater2_id = st.text_input(label="Identity", value="a Progressive", placeholder="Short Description")
            debater2_adjs = st.text_input(label="Adjectives",
                                          placeholder="Comma-separated words",
                                          value="empathetic, pragmatic, liberal, atheist, anti-gun, pro-choice")

        with st.expander("Settings", expanded=False):
            st.session_state.model_name = st.selectbox("Model",
                                                       ("gpt-3.5-turbo",
                                                        "text-davinci-003"))
            st.session_state.model_type = st.radio("Type",
                                                   ("Chat", "Text"))

        topic = st.text_input(label="Debate Topic:", value="the debt ceiling", placeholder="topic")

        debate_button = st.button("Debate!", type="primary")

    if debate_button:
        if debater1_name == "" or debater2_name == "" or debater1_id == "" or debater2_id == "" or debater1_adjs == "" or debater2_adjs == "":
            message(message="Please fill in the debater details!!", avatar_style="bottts")

        else:
            debater1 = Persona(debater1_name, debater1_id, debater1_adjs)
            debater2 = Persona(debater2_name, debater2_id, debater2_adjs)

            generate_debate(debater1, debater2, topic)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
