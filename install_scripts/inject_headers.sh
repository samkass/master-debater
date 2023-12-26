#!/bin/bash

# Path to the adsense.html file you want to modify
INDEX_HTML_PATH="/usr/local/lib/python3.11/site-packages/streamlit/static/index.html"

# Check if adsense.html exists
if [ -f "$INDEX_HTML_PATH" ]; then
    # Loop through all .html files in the headers directory
    for HEADER in headers/*.html; do
        # Ensure the file is not empty
        if [ -s "$HEADER" ]; then
            # Inject the content of the header file after the <head> tag
            sed -i "/<\/head>/i $(cat "$HEADER")" "$INDEX_HTML_PATH"
        fi
    done
else
    echo "Error: index.html not found at $INDEX_HTML_PATH"
    exit 1
fi
