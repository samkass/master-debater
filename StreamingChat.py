import asyncio
import queue
import threading

from langchain import ConversationChain, PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.schema import LLMResult


DEBATE_TEMPLATE = """The following is a respectful debate between an Opponent and me. Both parties are opinionated and provide lots of specific details from their context. If either side does not have information on a fact, they avoid that topic.
    
Current conversation:
{history}
Opponent: {input}
Me:"""


class StreamingChat:
    MODEL_NAME = "gpt-3.5-turbo"
    TEMPERATURE = 0.9

    def system_prompt_template(self):
        return PromptTemplate(input_variables=["history", "input"],
                              template=DEBATE_TEMPLATE)

    def __init__(self, model_name=MODEL_NAME, temperature=TEMPERATURE):
        print("Initializing StreamingChat")
        self.callback_handler = IndirectCallbackHandler()
        self.llm = ChatOpenAI(model_name=model_name,
                              temperature=temperature,
                              streaming=True,
                              callbacks=[self.callback_handler])
        self.conversation = ConversationChain(
            llm=self.llm,
            verbose=True,
            prompt=self.system_prompt_template(),
            memory=ConversationSummaryBufferMemory(
                llm=self.llm,
                max_token_limit=1000
            )
        )
        self.conversation.memory.ai_prefix = "Me"
        self.conversation.memory.human_prefix = "Opponent"

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


def run_async_function_sync(async_func, *args, **kwargs):
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)

    async def inner_async_func():
        return await async_func(*args, **kwargs)

    try:
        return new_loop.run_until_complete(inner_async_func())
    finally:
        new_loop.close()


class ResponseStream(BaseCallbackHandler):
    def __init__(self, prompt: str, chain: ConversationChain, callback_handler: IndirectCallbackHandler):
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
            run_async_function_sync(self.chain.arun, input=self.prompt)
        except Exception as e:
            self.queue.put("Error calling OpenAPI. Please validate the key is correct.")

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.queue.put(token)

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        self.conversation_callback_handler.remove_callback(self)
        self.queue.put(self.sentinel)

