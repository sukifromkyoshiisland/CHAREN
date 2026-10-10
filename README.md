# CHAREN — AI-Powered Specialty Tea Discovery Platform

## Project Overview

CHAREN is a specialty tea discovery and education platform designed to make tea culture more accessible, with a particular focus on Chinese tea traditions.

The project combines educational content with an AI-powered Tea Sommelier, developed as a smart sales assistant prototype.

This repository contains the initial Python development environment, application architecture, and working prototype prepared for the training programme.

## Project Objectives

- Introduce users to specialty teas, their origins, processing methods, and brewing techniques.
- Help visitors explore teas according to their preferences.
- Develop an AI-powered assistant that can answer tea-related questions and support product discovery.
- Establish a foundation for future integrations with tea sellers and product information pages.

## Technology Stack

- **Python:** Backend programming language
- **Flask:** Web application framework
- **HTML/CSS:** Web interface
- **Groq API:** AI model integration
- **SQLite:** Local database
- **Git & GitHub:** Version control and project repository

## Application Architecture

The project follows a modular Flask application structure.

```text
CHAREN/
├── app/
│   ├── services/
│   │   └── ai_service.py
│   ├── templates/
│   │   ├── index.html
│   │   └── dashboard.html
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   └── routes.py
├── config.py
├── hello.py
├── requirements.txt
├── run.py
└── .gitignore
```

### Main Components

**Web Interface:** Provides the visitor-facing homepage and an initial management dashboard.

**Application Routes:** Handles incoming requests and connects the web interface to backend functionality.

**AI Service:** Contains the integration layer for the planned AI-powered tea assistant.

**Database:** Provides a foundation for storing visitor enquiries and related information.

**Configuration:** Loads environment variables and keeps API credentials separate from source code.

## Local Development

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install the project dependencies:

```bash
pip install -r requirements.txt
```

4. Configure the required environment variables in a local `.env` file.
5. Start the Flask application:

```bash
python run.py
```

The application can then be accessed locally at:

`http://127.0.0.1:5000`

## Environment Smoke Test

A separate `hello.py` script is included to verify that the Python and Flask development environment is functioning correctly.

Run:

```bash
python hello.py
```

Expected browser response:

`Ortam calisiyor!`

The smoke test has been successfully executed in the local development environment.

## Current Project Status

**Initial environment setup and architecture prototype completed.**

The repository includes the foundational application structure, a working local Flask environment, initial web pages, and a development smoke test.

The AI assistant, enquiry management workflow, and further product features remain subject to continued development and testing.

## Security

API credentials are stored locally through environment variables. The `.env` file, virtual environment, and local SQLite database are excluded from Git version control.

## Future Development

- Expand the AI Tea Sommelier's conversational capabilities.
- Improve tea discovery and recommendation flows.
- Develop visitor enquiry tracking and management features.
- Add detailed tea information pages and educational resources.
- Prepare the application for deployment and further testing.
