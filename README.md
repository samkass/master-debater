# master-debater

## Description
This is a simple web app that allows users to define two personas, specify a debate topic, and have an AI assume the role of each persona and debate the given topic.

It is implemented with LangChain, Streamlit, and OpenAI's GPT API.

It is available online at https://master-debater.streamlit.app

To built and run it yourself, follow the instructions below.

## Installation
1. Clone the repository and cd into the directory
2. Install the dependencies with `pip install -r requirements.txt`
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in the OpenAI API key. (If you do not do this, it will prompt for the OpenAI Key in the sidebar when run.)
4. Run the app with `streamlit run streamlit_app.py`
5. Navigate to the URL provided by Streamlit

## Usage
1. Enter the OpenAI API key in the sidebar (if not supplied in secrets.toml file)
2. Enter the personas and topic in the sidebar
3. Click the "Start Debate" button
4. Watch the debate unfold
5. Click on the "Continue Debate" button to continue the debate
6. Click on the "Conclude Debate" button to conclude the debate

## Settings in secret.toml
1. TEST_MODE: Instead of calling OpenAPI, will generate a stream of numbers to simulate a response. Useful for testing without incurring costs from OpenAI.
2. SHOW_SETTINGS: Show a settings sidebar that allows you to change the LLM model. May offer additional settings in the future.
3. USE_STREAMING: A flag to indicate whether the OpenAI engine should use streaming or wait for the full reply. Currently ignored, as in the last rewrite I only implemented streaming.
