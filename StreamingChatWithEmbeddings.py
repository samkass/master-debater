import queue
import threading

from langchain import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import LLMResult

DEBATE_TEMPLATE = """The following is a respectful debate between an Opponent and Me. 
Both parties are opinionated and provide lots of specific details from their context. 
If either side does not have information on a fact, they avoid that topic.

Current conversation:
{chat_history}
Opponent: {question}
Me:"""


class StreamingChatWithEmbeddings:
    MODEL_NAME = "gpt-3.5-turbo-16k"
    TEMPERATURE = 0.9

    @staticmethod
    def system_prompt_template():
        return PromptTemplate(input_variables=["history", "input", "doc_chat_context"],
                              template=DEBATE_TEMPLATE)

    def __init__(self, embeddings, model_name=MODEL_NAME, temperature=TEMPERATURE):
        print("Initializing StreamingChat")

        prompt_template = PromptTemplate.from_template(DEBATE_TEMPLATE)

        self.callback_handler = IndirectCallbackHandler()
        llm = ChatOpenAI(model_name=model_name,
                         temperature=temperature,
                         streaming=True,
                         callbacks=[self.callback_handler])

        self.conversation = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=embeddings.as_retriever(),
            condense_question_prompt=prompt_template,
            memory=ConversationBufferMemory(  # Use ConversationSummaryBufferMemory?
                llm=llm,
                max_token_limit=1000,
                ai_prefix="Me",
                human_prefix="Opponent",
                memory_key="chat_history",
                return_messages=True
            )
        )

    def response(self, prompt):
        stream = ResponseStream(prompt, self.conversation, self.callback_handler)
        return stream


class IndirectCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.callbacks = []

    def add_callback(self, callback: BaseCallbackHandler):
        self.callbacks.append(callback)

    def remove_callback(self, callback: BaseCallbackHandler):
        self.callbacks.remove(callback)

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        for callback in self.callbacks:
            callback.on_llm_new_token(token, **kwargs)

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        for callback in self.callbacks:
            callback.on_llm_end(response, **kwargs)


class ResponseStream(BaseCallbackHandler):
    def __init__(self, prompt: str, chain: Chain, callback_handler: IndirectCallbackHandler):
        self.prompt = prompt
        self.chain = chain
        self.conversation_callback_handler = callback_handler
        self.conversation_callback_handler.add_callback(self)

        self.queue = queue.Queue()
        self.sentinel = object()

    def __iter__(self):
        thread = threading.Thread(target=self.run_chain)
        thread.start()
        while True:
            chunk = self.queue.get()
            if chunk == self.sentinel:
                thread.join()
                return
            yield chunk

    def run_chain(self):
        try:
            self.chain.run({"question": self.prompt})
        except Exception as e:
            self.queue.put("Error calling OpenAPI. Please validate the key is correct.")

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.queue.put(token)

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        self.conversation_callback_handler.remove_callback(self)
        self.queue.put(self.sentinel)

