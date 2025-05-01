# AI Economic Research News Agent

A minimalist, terminal-style dashboard for tracking the most relevant AI economic news articles.

![AI Economic News Dashboard](https://i.imgur.com/example.png)

## Overview

This project provides a clean, distraction-free interface for viewing the top 5 most relevant AI economic news articles, displayed in a retro green-on-black terminal theme. The dashboard auto-refreshes hourly and shows relevance scores as percentages.

## Features

- **Terminal-Style UI**: Green text on black background for a retro console look
- **Top 5 Articles**: Shows only the most relevant AI economic news
- **Relevance Scoring**: Articles display relevance as a percentage
- **Auto-Refresh**: Content refreshes automatically every hour
- **Verified Links**: All article links are verified to work
- **Minimal Interface**: Clean, distraction-free design

## Installation

### Prerequisites

- Python 3.6 or higher
- For service management: `psutil` library

### Basic Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ai-economic-news-agent.git
cd ai-economic-news-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python final_server.py
```

4. Access the dashboard at:
```
http://localhost:8080
```

## Usage

### Running as a Service

For running the server as a background service, install the required dependency:

```bash
pip install psutil
```

Then use the service management script:

```bash
# Start as a background service
python run_as_service.py start --daemon

# Check status
python run_as_service.py status

# Stop the service
python run_as_service.py stop

# Restart the service
python run_as_service.py restart --daemon
```

### Custom Port

To run on a different port:

```bash
python final_server.py 8081
```

## Project Structure

- `final_server.py`: Production-ready server with verified article links
- `run_as_service.py`: Service management script
- `src/web/templates/index.html`: Main web UI template
- `PRODUCTION.md`: Detailed production deployment guide

## Development

### Local Development

For local development, you can use:

```bash
python final_server.py
```

### Adding New Articles

To add or update articles, modify the `SAMPLE_ARTICLES` list in `final_server.py`.

## License

MIT

## Acknowledgments

- Developed by Lucas Hendrich
- Inspired by retro terminal interfaces

## Features

- Daily automated search for economic research on AI adoption
- Content filtering and relevance scoring
- Summary generation for each article
- Export capabilities for easy content repurposing
- Email notifications with daily findings
- Web-based user interface for viewing the latest AI economic research news

## Project Structure

```
ai_econ_news_agent/
│
├── config/               # Configuration files
│   ├── settings.py       # General settings
│   └── sources.json      # News sources configuration
│
├── data/                 # Data storage
│   ├── articles/         # Stored article content
│   └── processed/        # Processed and analyzed data
│
├── src/                  # Source code
│   ├── models/           # Data models
│   ├── services/         # External services integration
│   ├── agents/           # Agent implementation
│   └── utils/            # Utility functions
│
└── tests/                # Unit and integration tests
```

## Architecture

This project implements the Model Concept Protocol (MCP) design pattern, separating:

- **Models**: Data structures and business logic
- **Concepts**: Core domain concepts and operations
- **Protocols**: Interfaces for external service interactions

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure API keys in `.env` file
4. Run the agent:
   ```
   python src/main.py
   ```

## Usage

The agent can be run in several ways:

### Command Line Interface (CLI)

The agent includes a CLI for easy operation:

```bash
# Run the full agent pipeline (find, process, export, notify)
python src/cli.py run

# Find relevant articles only
python src/cli.py find

# Find and process articles
python src/cli.py find --process

# Find, process, and export articles
python src/cli.py find --process --export

# Process articles from the past N days
python src/cli.py process --days 3

# View stored articles from the past week
python src/cli.py view

# View articles from the past N days
python src/cli.py view --days 10
```

### Web UI

The agent includes a web-based user interface for viewing the latest AI economic research news:

```bash
# Run the simplified web UI (with sample data)
python run_simple_web_ui.py

# Run the full web UI (requires all dependencies)
python run_web_ui.py
```

The web UI provides:
- A clean, sepia-themed interface that's easy on the eyes
- Display of the top 5 AI economic research articles
- Article summaries and key findings
- Economic indicators and AI adoption metrics
- Links to original sources

Access the web UI at http://localhost:5000 after starting the server.

### Scheduled Execution

The agent can be scheduled to run daily at 8:00 AM:

```bash
python src/main.py --schedule
```

### Programmatic Usage

The agent can also be used programmatically:

```python
from src.agents.news_agent import AIEconomicNewsAgent

# Initialize the agent
agent = AIEconomicNewsAgent()

# Find relevant articles
articles = agent.find_articles(limit=5)

# Process articles
processed_articles = agent.process_articles(articles)

# Get recently stored articles
recent_articles = agent.get_stored_articles(days=7)
```

## Configuration

### General Settings

Edit `config/settings.py` to customize:
- Search keywords and filters
- Number of articles to retrieve
- Output format preferences
- Notification settings

### News Sources

Edit `config/sources.json` to:
- Add new news sources
- Modify existing sources
- Adjust source quality scores
- Configure parser settings for different websites

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
# OpenAI API (for enhanced analysis)
OPENAI_API_KEY=your_openai_api_key

# Email notification settings
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SENDER_EMAIL=sender@example.com
```

## Data Export

The agent exports findings in two formats:

1. **Markdown**: Human-readable reports with article summaries and key findings
2. **JSON**: Structured data for programmatic use or integration with other systems

Exports are saved to the `data/processed/` directory.

## Extending the Agent

### Adding New News Sources

Add new sources to `config/sources.json` following this template:

```json
{
  "name": "Source Name",
  "url": "https://example.com/ai-section",
  "type": "website",
  "quality_score": 0.8,
  "focus": ["economics", "research"],
  "parser_settings": {
    "article_selector": ".article",
    "title_selector": "h2",
    "content_selector": ".article-body"
  }
}
```

### Implementing New Analysis Features

Extend the `ContentAnalyzer` class in `src/services/content_analyzer.py` to add new analysis capabilities.

## Troubleshooting

- **No articles found**: Check your keywords in `settings.py` and ensure they're not too restrictive
- **Parsing errors**: Verify the parser settings for each source in `sources.json`
- **Email notification failures**: Check your SMTP settings in the `.env` file

## License

MIT License
