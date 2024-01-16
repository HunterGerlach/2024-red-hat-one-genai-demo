import os

import streamlit as st
from langchain.llms import HuggingFaceTextGenInference
from langchain.prompts import PromptTemplate

from gui.history import ChatHistory
from gui.layout import Layout
from gui.sidebar import Sidebar, Utilities
from snowflake import SnowflakeGenerator

username = os.environ.get("REDIS_USERNAME", "default")
password = os.environ.get("REDIS_PASSWORD", "default")
host = os.environ.get("REDIS_HOST", "10.70.101.1")
redis_url = f"redis://{username}:{password}@{host}:6379"

# NOTE: This template syntax is specific to Llama2
template = """<s>[INST] <<SYS>>
You are a helpful, respectful and honest assistant.
You will be given a question you need to answer, and a context to provide you with information. You must answer the question based as much as possible on this context.
Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
<</SYS>>

Question: {question}
Context: {context} [/INST]
"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

if __name__ == '__main__':
    st.set_page_config(layout="wide", page_icon="💬", page_title="ChatPDF")
    layout, sidebar, utils = Layout(), Sidebar(), Utilities()

    layout.show_header()
    login_config = utils.load_login_details()

    if not login_config:
        layout.show_loging_details_missing()
    else:
        sidebar.show_login(login_config)
        pdf = utils.handle_upload()

        if pdf:
            sidebar.show_options()

            try:
                if 'chatbot' not in st.session_state:
                    llm = HuggingFaceTextGenInference(
                        inference_server_url=os.environ.get('INFERENCE_SERVER_URL',
                            'https://hf-text-generation-inference-server-llm'),
                        max_new_tokens=int(os.environ.get('MAX_NEW_TOKENS', '512')),
                        top_k=int(os.environ.get('TOP_K', '10')),
                        top_p=float(os.environ.get('TOP_P', '0.95')),
                        typical_p=float(os.environ.get('TYPICAL_P', '0.95')),
                        temperature=float(os.environ.get('TEMPERATURE', '0.02')),
                        repetition_penalty=float(os.environ.get('REPETITION_PENALTY', '1.01')),
                        streaming=True,
                        verbose=False
                    )

                    indexGenerator = SnowflakeGenerator(42)
                    indexName = str(next(indexGenerator))

                    chatbot = utils.setup_chatbot(pdf, llm, redis_url, indexName, "redis_schema.yaml")
                    st.session_state["chatbot"] = chatbot

                if st.session_state["ready"]:
                    history = ChatHistory()
                    history.initialize(pdf.name)

                    response_container, prompt_container = st.container(), st.container()

                    with prompt_container:
                        is_ready, user_input = layout.prompt_form()

                        if st.session_state["reset_chat"]:
                            history.reset()

                        if is_ready:
                            with st.spinner("Processing query..."):
                                output = st.session_state["chatbot"].conversational_chat(user_input, QA_CHAIN_PROMPT)

                    history.generate_messages(response_container)

            except Exception as e:
                st.error(f"{e}")
                st.stop()

    sidebar.about()