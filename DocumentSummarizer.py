# from langchain.chains.llm import LLMChain
# from langchain.prompts import PromptTemplate
# from langchain.chains.combine_documents.stuff import StuffDocumentsChain
#
# class DocumentSummarizer:
#
#     __init__(self, model_name="gpt-3.5-turbo-16k", temperature=0.9):
#
#
# # Define prompt
# prompt_template = """Write a concise summary of the following:
# "{text}"
# CONCISE SUMMARY:"""
# prompt = PromptTemplate.from_template(prompt_template)
#
# # Define LLM chain
# llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
# llm_chain = LLMChain(llm=llm, prompt=prompt)
#
# # Define StuffDocumentsChain
# stuff_chain = StuffDocumentsChain(
#     llm_chain=llm_chain, document_variable_name="text"
# )
#
# docs = loader.load()
# print(stuff_chain.run(docs))