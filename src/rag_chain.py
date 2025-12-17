"""
Minimal RAG chain using LangChain RetrievalQA with a FAISS-backed retriever.
"""
from typing import List, Dict, Any
import logging
import os

from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

logger = logging.getLogger(__name__)


class RAGChain:
    def __init__(self, openai_api_key: str, retriever=None):
        os.environ["OPENAI_API_KEY"] = openai_api_key
        self.llm = OpenAI(temperature=0)
        self.prompt = PromptTemplate(input_variables=["context", "question"], template="Context:\n{context}\n\nQuestion:\n{question}")
        self.retriever = retriever

    def answer(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        try:
            if self.retriever is None:
                raise ValueError("Retriever not provided")
            chain = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=self.retriever, return_source_documents=True)
            result = chain({"query": question})
            answer = result.get("result")
            docs = result.get("source_documents", [])
            sources = [{"page_content": d.page_content[:300], "metadata": d.metadata} for d in docs]
            return {"answer": answer, "sources": sources}
        except Exception:
            logger.exception("RAG chain failed")
            raise