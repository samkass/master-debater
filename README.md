# master-debater

## Description
This is a simple web app that allows users to define two personas, specify a debate topic, and have an AI assume the role of each persona and debate the given topic.

It is implemented with LangChain, Streamlit, and OpenAI.

## Installation
1. Clone the repository and cd into the directory
2. Install the dependencies with `pip install -r requirements.txt`
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in the OpenAI API key. (If you do not do this, it will prompt for the OpenAI Key in the sidebar.)
4. Run the app with `streamlit run streamlit_app.py`
5. Navigate to the URL provided by Streamlit

## Usage
1. Enter the personas and topic in the sidebar
2. Click the "Start Debate" button
3. Watch the debate unfold
4. Click on the "Continue Debate" button to continue the debate
5. Click on the "Conclude Debate" button to conclude the debate
