import os

import streamlit as st
from langchain.llms import HuggingFaceTextGenInference
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate

from gui.history import ChatHistory
from gui.layout import Layout
from gui.sidebar import Sidebar, Utilities
from snowflake import SnowflakeGenerator

if __name__ == '__main__':
    st.set_page_config(layout="wide", page_icon="💬", page_title="ChatPDF")
    layout, sidebar, utils = Layout(), Sidebar(), Utilities()

    configs = utils.load_config_details()
    
    username = configs["redis"]["username"]
    password = configs["redis"]["password"]
    host = configs["redis"]["host"]
    port = configs["redis"]["port"]
    redis_url = f"redis://{username}:{password}@{host}:{port}"

    inference_server_url= configs["inference_server"]["url"]


    layout.show_header()
    if not configs:
        layout.show_loging_details_missing()
    else:
        
        sidebar.show_logo(configs)
        sidebar.show_login(configs)
        pdf = utils.handle_upload()

        if pdf:
            sidebar.show_options()

            try:
                if 'chatbot' not in st.session_state:
                    # llm = HuggingFaceTextGenInference(
                    #     inference_server_url=os.environ.get('INFERENCE_SERVER_URL'),
                    #     max_new_tokens=int(os.environ.get('MAX_NEW_TOKENS', '512')),
                    #     top_k=int(os.environ.get('TOP_K', '10')),
                    #     top_p=float(os.environ.get('TOP_P', '0.95')),
                    #     typical_p=float(os.environ.get('TYPICAL_P', '0.95')),
                    #     temperature=float(os.environ.get('TEMPERATURE', '0.9')),
                    #     repetition_penalty=float(os.environ.get('REPETITION_PENALTY', '1.01')),
                    #     streaming=False,
                    #     verbose=False
                    # )
                    
                    llm = Ollama(model="mistral")

                    indexGenerator = SnowflakeGenerator(42)
                    index_name = str(next(indexGenerator))
                    print("Index Name: " + index_name)
                    
                    chatbot = utils.setup_chatbot(pdf, llm, redis_url, index_name, "redis_schema.yaml")
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
                                output = st.session_state["chatbot"].conversational_chat(user_input)

                    history.generate_messages(response_container)

            except Exception as e:
                st.error(f"{e}")
                st.stop()

    sidebar.about()
