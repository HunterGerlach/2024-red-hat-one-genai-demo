import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import tempfile

from chatbot import Chatbot
from embedding import DocEmbedding


class Sidebar:
    MODEL_OPTIONS = ["Llama-2-7b", "Mistral-7B"]
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.0
    TEMPERATURE_STEP = 0.01

    @staticmethod
    def show_logo():
        st.sidebar.image("./rhone.png", width=200)

    @staticmethod
    def about():
        about = st.sidebar.expander("About 🤖")
        sections = [
            "#### ChatPDF is an advanced AI chatbot equipped with conversational memory capabilities, "
            "specifically crafted to facilitate intuitive discussions and interactions with users regarding their PDF "
            "data."
        ]
        for section in sections:
            about.write(section)

    @staticmethod
    def show_login(config):
        # Initialize the authentication_status key in st.session_state
        if 'authentication_status' not in st.session_state:
            st.session_state['authentication_status'] = None

        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config['preauthorized']
        )
        name, authentication_status, username = authenticator.login('Login', 'sidebar')

        # Initialize session state variables
        if 'authentication_status' not in st.session_state:
            st.session_state['authentication_status'] = None
        if 'name' not in st.session_state:
            st.session_state['name'] = None

        # Rest of your authentication logic...

        # Use session state variables for control flow
        if st.session_state["authentication_status"]:
            authenticator.logout('Logout', 'sidebar')
            st.write(f'Welcome *{st.session_state["name"]}*')
        elif not st.session_state["authentication_status"]:
            st.error('Username/password is incorrect')
        elif st.session_state["authentication_status"] is None:
            st.warning('Please enter your username and password')

    def model_selector(self):
        model = st.selectbox(label="Model", options=self.MODEL_OPTIONS)
        st.session_state["model"] = model

    @staticmethod
    def reset_chat_button():
        if st.button("Reset chat"):
            st.session_state["reset_chat"] = True
        st.session_state.setdefault("reset_chat", False)

    def temperature_slider(self):
        temperature = st.slider(
            label="Temperature",
            min_value=self.TEMPERATURE_MIN_VALUE,
            max_value=self.TEMPERATURE_MAX_VALUE,
            value=self.TEMPERATURE_DEFAULT_VALUE,
            step=self.TEMPERATURE_STEP,
        )
        st.session_state["temperature"] = temperature

    def show_options(self):
        with st.sidebar.expander("🛠️ Tools", expanded=True):
            self.reset_chat_button()
            self.model_selector()
            # self.temperature_slider()
            st.session_state.setdefault("model", self.MODEL_OPTIONS[0])
            # st.session_state.setdefault("temperature", self.TEMPERATURE_DEFAULT_VALUE)


class Utilities:
    @staticmethod
    def load_login_details():
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
        return config

    @staticmethod
    def handle_upload():
        """
        Handles the file upload and displays the uploaded file
        """
        uploaded_file = st.sidebar.file_uploader("upload", type="pdf", label_visibility="collapsed")
        if uploaded_file is not None:
            pass
        else:
            st.sidebar.info(
                "Upload your PDF file to get started", icon="👆"
            )
            st.session_state["reset_chat"] = True
        return uploaded_file

    @staticmethod
    def setup_chatbot(uploaded_file, llm, redis_url, index_name, schema):
        """
        Sets up the chatbot with the uploaded file, model, and temperature
        """
        embeds = DocEmbedding()
        with st.spinner("Processing..."):
            uploaded_file.seek(0)
            file = uploaded_file.read()

            embeds.create_doc_embedding(file, redis_url, index_name)

            retriever = embeds.get_doc_retriever(redis_url, index_name, schema)
            chatbot = Chatbot(retriever, llm)
            print(f"new chatbot is created with {index_name} {schema}.")
        st.session_state["ready"] = True
        return chatbot