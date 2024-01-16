import streamlit as st
import os
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import ChatPromptTemplate


class Chatbot:

    def __init__(self, rds_retriever, llm):
        self.rds_retriever = rds_retriever
        self.llm = llm

    def conversational_chat(self, query, condense_question_prompt):
        """
        Starts a conversational chat with a model via Langchain
        """
        # Prompt
        template = """<s>[INST] <<SYS>>
        You are a helpful, respectful and honest assistant named HatBot answering questions about OpenShift Data Science, aka RHODS.
        You will be given a question you need to answer, and a context to provide you with information. You must answer the question based as much as possible on this context.
        Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

        If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
        <</SYS>>

        Question: {question}
        Context: {context} [/INST]
        """
        # QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
        #
        # qa_chain = RetrievalQA.from_chain_type(
        #     llm=self.llm,
        #     chain_type='stuff',
        #     retriever=self.rds_retriever,
        #     verbose=True,
        #     chain_type_kwargs={
        #         "verbose": True,
        #         "prompt": QA_CHAIN_PROMPT,
        #         "memory": st.session_state["history"],
        #     },
        #     return_source_documents=True
        # )
        #
        # result = qa_chain({"query": query}, return_only_outputs=True)

        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            memory=st.session_state["history"],
            retriever=self.rds_retriever
        )
        result = chain({"question": query}, return_only_outputs=True)

        return result["answer"]