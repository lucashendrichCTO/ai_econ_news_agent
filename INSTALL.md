# Installation Guide for AI Economic News Agent

This guide will help you set up and run the AI Economic News Agent on your system.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Basic Installation

1. Clone or download the repository:
   ```bash
   git clone https://github.com/lucashendrichCTO/ai_econ_news_agent.git
   cd ai_econ_news_agent
   ```

2. Install the basic dependencies:
   ```bash
   pip install -e .
   ```
   This will install the minimum required packages to run the simplified version of the agent.

3. For the full functionality (including NLP analysis and OpenAI integration):
   ```bash
   pip install -e ".[full]"
   ```
   Note: Some packages like spaCy might require additional steps on certain systems.

## Configuration

1. Create a `.env` file in the project root with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   
   # For email notifications (optional)
   SMTP_SERVER=smtp.example.com
   SMTP_PORT=587
   SMTP_USERNAME=your_username
   SMTP_PASSWORD=your_password
   SENDER_EMAIL=sender@example.com
   ```

2. Download required NLP models (if using the full installation):
   ```bash
   python -m spacy download en_core_web_sm
   python -m nltk.downloader punkt stopwords
   ```

## Running the Agent

### Quick Start

To run the agent with default settings:
```bash
python run_agent.py
```

### Using the CLI

The agent includes a command-line interface for more options:
```bash
python src/cli.py run
```

For more CLI options, see the README.md file.

### Web UI

To run the web UI (simplified version that works with basic installation):
```bash
python run_simple_web_ui.py
```

For the full web UI (requires full installation):
```bash
python run_web_ui.py
```

Then access the web UI at http://localhost:5000 in your browser.

## Troubleshooting

### Installation Issues

- **Compilation errors**: Some packages might require a C compiler. On Windows, you might need to install Visual C++ Build Tools.
- **spaCy models**: If you encounter errors with spaCy, try installing the models manually:
  ```bash
  python -m spacy download en_core_web_sm
  ```

### Runtime Issues

- **OpenAI API errors**: Ensure your API key is correctly set in the `.env` file.
- **No articles found**: Check your internet connection and the keywords in `config/settings.py`.
- **Email notification failures**: Verify your SMTP settings in the `.env` file.

## Support

For issues or questions, please open an issue on the GitHub repository or contact lucas.hendrich@fortegrp.com.
