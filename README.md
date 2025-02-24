# Viceualize

Visualizing my vices.

## Description

## Usage

1. Place all of your `.xlsx` and `.ods` files into the `sheets/` subdirectory.

2. Run `python3 viceualize.py`

3. The Plotly window will open in your browser for your viewing. You may double click any of the `.html` files in the `assets/` subdirectory to open them manually.

### Push Smoking Tracker Statistics to Ngrok

**Steps:**

>You will need two separate terminals to run the following two commands. This setup assumes you have Ngrok installed and know what you are doing.

1. Run a Python3 HTTP server in the `assets/` subdirectory via `python -m http.server 8080`

2. Start an Ngrok HTTP tunnel to the localhost via `ngrok http http://localhost:8080 --basic-auth "user:pass"`

3. Copy the generated URL from the Ngrok `stdout` and send it to your viewer