# Agent Query System

## About
This is an AI query agent for camera feeds, encoder and decoder. Raw data files are in [./camera-raw-data](./camera-raw-data).

## Usage
You need to have an [Anthropic API key](https://docs.anthropic.com/en/docs/get-started) and set it as an environment variable.

Set up a virtual enviroment and install required packages.
```bash
python3 -m venv .env
pip install -r requirements.txt
```

Run the agent with
```bash
./start_agent
```

To exit the program, use either `Ctrl+d` or enter a prompt to ask for exit.

# Queries
The agent will translate human language to SQL queries, and use MCP to query the database. 
Some examples are in [./test_questions.txt](./test_questions.txt).

# Demo
Please watch the demo.
[Demo](https://youtu.be/gtsSLyOyyvY)
