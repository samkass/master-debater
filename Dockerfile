FROM python:3.11-slim

WORKDIR /app

# Copy just the requirements (do this early to avoid rebuilding the image when requirements don't change)
COPY requirements.txt ./
RUN mkdir ./.streamlit/

# Create the secrets file
RUN sh -c 'touch ./.streamlit/secrets.toml'

# Install dependencies
RUN pip3 install -r requirements.txt --no-cache-dir

# Copy your application source and headers
COPY . ./

# Copy your header injection script
COPY install_scripts/inject_headers.sh /usr/local/bin/inject_headers.sh
RUN chmod +x /usr/local/bin/inject_headers.sh

# Run the header injection script
RUN /usr/local/bin/inject_headers.sh

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]
