from PyPDF2 import PdfReader
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter


class EmbeddingsException(Exception):
    pass


class DocumentSummarizer:

    def __init__(self, pdf):
        self.pdf = pdf

    def to_embeddings(self):
        chunks = self.pdf_to_text(self.pdf)
        embeddings = self.doc_context_to_embeddings(chunks)
        return embeddings

    @staticmethod
    def pdf_to_text(pdf):
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    @staticmethod
    def doc_context_to_embeddings(doc_context):
        print("Splitting PDF into chunks and create embeddings")
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(doc_context)
        try:
            embeddings = OpenAIEmbeddings()
            knowledge_base = FAISS.from_texts(chunks, embeddings)
            print("Created embeddings")
        except Exception as e:
            print("Error creating embeddings: "+repr(e))
            raise EmbeddingsException("Error creating embeddings: "+repr(e))
        return knowledge_base
