# Smart Log Analyzer & Anomaly Detector

## Overview
A lightweight, full-stack log analysis tool that ingests server logs, detects anomalies using custom rule-based logic, and leverages AI to generate plain-English root cause explanations for flagged entries. 

## Tech Stack
* **Backend:** Python, FastAPI
* **Database:** SQLite (via SQLAlchemy)
* **Frontend:** Vanilla HTML, JavaScript, Tailwind CSS (via CDN)
* **AI Integration:** Google Gemini API (`gemini-3.6-flash`)

## Setup Instructions
1. Ensure Python 3.8+ is installed.
2. Clone or extract the project directory and open your terminal.
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows