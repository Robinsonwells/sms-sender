# Bulk SMS Sender

A Python Flask web application for sending bulk SMS messages using the Twilio API.

## Overview

This app provides a simple web interface for sending SMS messages to multiple recipients via Twilio's API. Users can upload a CSV file of phone numbers or provide a URL to a CSV file.

## Project Structure

- `app.py` - Main Flask application
- `settings.py` - Configuration (reads from environment variables)
- `tools.py` - Helper functions (Twilio API calls, CSV parsing, validation)
- `templates/` - Jinja2 HTML templates
- `static/` - CSS, JS, and image assets
- `requirements.txt` - Python dependencies
- `gunicorn_config.py` - Gunicorn configuration (not used directly in workflow)

## Running the Application

The app runs via Gunicorn on port 5000:

```
gunicorn --timeout 120 --worker-tmp-dir /dev/shm --bind 0.0.0.0:5000 app:app
```

## Environment Variables

- `SECRET_KEY` - Flask secret key for sessions
- `TWILIO_SID` - Twilio Account SID (optional, can be entered in UI)
- `TWILIO_TOKEN` - Twilio Auth Token (optional, can be entered in UI)
- `CSV_URL` - Default CSV URL (optional)

## Tech Stack

- Python 3.12
- Flask 3.1.3
- Gunicorn 25.1.0
- Twilio SDK 9.10.2
- Vanilla JS + CSS frontend
