# AI Economic News Agent - Production Deployment

This document provides instructions for deploying the AI Economic News Agent in a production environment.

## Production Server

The production server (`production_server.py`) is a standalone HTTP server that:

- Serves the AI Economic News dashboard with a terminal-style interface
- Provides API endpoints for fetching and refreshing articles
- Displays the top 5 most relevant AI economic news articles
- Auto-refreshes content hourly
- Requires no external dependencies (uses only Python standard library)
- Includes proper error handling and logging

## Requirements

- Python 3.6 or higher
- `psutil` library (only for service management)

## Installation

1. Install the required dependency for service management:

```bash
pip install psutil
```

2. Make sure all files are in the correct location:
   - `production_server.py`: Main server script
   - `run_as_service.py`: Service management script
   - `src/web/templates/index.html`: Web UI template

## Usage

### Starting the Production Server

To start the server in the foreground:

```bash
python production_server.py
```

To specify a custom port:

```bash
python production_server.py 8081
```

### Service Management

The `run_as_service.py` script provides commands to manage the server as a background service:

#### Start the server as a background service:

```bash
python run_as_service.py start --daemon
```

With a custom port:

```bash
python run_as_service.py start --daemon --port 8081
```

#### Stop the running service:

```bash
python run_as_service.py stop
```

#### Restart the service:

```bash
python run_as_service.py restart --daemon
```

#### Check service status:

```bash
python run_as_service.py status
```

## Accessing the Dashboard

Once the server is running, access the dashboard at:

```
http://localhost:8080
```

(Or the custom port you specified)

## Features

- **Terminal-Style UI**: Green text on black background for a retro console look
- **Top 5 Articles**: Shows only the most relevant AI economic news
- **Relevance Scoring**: Articles display relevance as a percentage
- **Auto-Refresh**: Content refreshes automatically every hour
- **Verified Links**: All article links are verified to work
- **Minimal Interface**: Clean, distraction-free design

## Logs

The production server writes logs to:
- `ai_news_server.log`: Server operation logs
- `ai_news_service.log`: Service management logs

## Troubleshooting

### Port Already in Use

If the default port (8080) is already in use:

```bash
python production_server.py 8081
```

Or let the service manager find an available port:

```bash
python run_as_service.py start --daemon
```

### Finding and Stopping a Running Instance

```bash
python run_as_service.py status
python run_as_service.py stop
```

## Security Notes

This server is intended for local or internal network use. For public-facing deployments, consider:

1. Adding authentication
2. Implementing rate limiting
3. Using HTTPS
4. Running behind a reverse proxy (Nginx, Apache)
