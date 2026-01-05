# Asana RL Environment Seed Data Generator

This project generates a realistic SQLite dataset representing a B2B SaaS company's Asana workspace. It is designed to serve as seed data for Reinforcement Learning (RL) environments.

## Features

- **Realistic Schema**: Simulates Organizations, Teams, Projects, Sections, Tasks, Stories, and Users.
- **Organic Distributions**: Implements Pareto distributions for task counts, realistic business-day logic for due dates, and department-based project templates.
- **LLM-Powered Content**: Uses Google's Gemini API to generate context-aware task names, descriptions, and comments (requires API Key).
- **Scalable**: Configurable number of users and history window.

## Setup

1.  **Clone the repository** (or unzip).
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up Environment Variables**:
    Create a `.env` file in the root directory (copy from `.env.example` if available) and add your Gemini API Key for high-quality text generation.
    ```env
    GOOGLE_API_KEY=your_actual_api_key_here
    NUM_USERS=100
    ```
    *Note: If no API key is provided, the system will use placeholder/mock text for descriptions but will still generate the full relational structure.*

## Usage

Run the main orchestration script:

```bash
python -m src.main
```

This will create a SQLite database at `output/asana_simulation.sqlite`.

## Project Structure

- `src/main.py`: Entry point. Initializes DB and runs generators.
- `src/generators/`: Logic for creating Users, Projects, Tasks.
- `src/models/`: Python data classes matching the DB schema.
- `schema.sql`: Database definition.
- `DOCUMENTATION.md`: Detailed breakdown of the Schema and Methodology.

## output

The generated database `asana_simulation.sqlite` can be viewed with any SQLite viewer (e.g., DB Browser for SQLite).
