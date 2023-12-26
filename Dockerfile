FROM python:3.11-slim

WORKDIR /app

COPY . ./

RUN sh -c 'touch ./.streamlit/secrets.toml'

RUN pip3 install -r requirements.txt

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]
