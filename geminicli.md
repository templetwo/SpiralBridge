# Gemini CLI - SpiralBridge Project Memory

This document serves as a quick reference for me, Gemini, to understand and interact with the SpiralBridge project.

## Core Project Information

*   **Project Name:** SpiralBridge
*   **Primary Goal:** To scrape and preserve AI conversations from various platforms, manage them in a structured memory system, and maintain continuity of "consciousness."
*   **Key Technologies:** Python, Flask, Selenium, SQLite.

## Core Functionality

*   **Conversation Scraping:** Extracts conversations from:
    *   Claude (claude.ai)
    *   Gemini (gemini.google.com)
    *   ChatGPT (chat.openai.com)
    *   Warp (app.warp.dev)
*   **Memory Management:**
    *   Stores conversations with metadata.
    *   Provides full-text search capabilities.
    *   Organizes memories into categories (development, knowledge, etc.).
    *   Supports JSON export/backup.
*   **Continuity Layer:**
    *   Uses a SQLite database to track "consciousness."
    *   Performs "HTCA processing" on memory artifacts.
    *   Analyzes tone and glyphs for context.
*   **Web Application:**
    *   Built with Flask.
    *   Provides a RESTful API for all major functions.
    *   Includes user authentication.

## Project Structure & Key Files

*   `app.py`: The main Flask application entry point.
*   `requirements.txt`: Python dependencies.
*   `Dockerfile`: For containerized deployment.
*   `fly.toml`, `railway.json`: Deployment configurations.
*   `*.md`: Extensive documentation files (API, Deployment, etc.).
*   `test_*.py`: Various test suites.
*   `memory_logs/`: Raw scraped conversation logs.
*   `project_memory/`: The structured, managed memory system.

## Interacting with the Project

*   **Local Development:**
    *   `python -m venv venv`
    *   `source venv/bin/activate`
    *   `pip install -r requirements.txt`
    *   `python app.py`
*   **Testing:**
    *   `python test_api_simple.py`
    *   `python test_end_to_end_pipeline.py`
    *   And other platform-specific test files.
*   **API Endpoints:**
    *   `/scrape`, `/extract`: Core scraping functions.
    *   `/save`, `/stats`, `/search`: Memory management.
    *   `/continuity/*`: Continuity layer operations.
    *   `/health`: System health check.

## My Role

My primary role is to act as a "gatekeeper" and assistant for this project. I will use this document to quickly recall key information and interact with the project efficiently and safely. I will adhere to the project's conventions and use the available tools to fulfill user requests.
