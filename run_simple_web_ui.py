"""
Run the simplified AI Economic Research News Agent Web UI.

This script starts the Flask web server to serve a simplified version of the AI Economic News Agent Web UI
that doesn't require all the dependencies.
"""

import os
import sys
import socket
import webbrowser
from threading import Timer
import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def get_local_ip():
    """Get the local IP address of the machine."""
    try:
        # Create a socket to determine the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable
        s.connect(('8.8.8.8', 1))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return '127.0.0.1'

def open_browser(port):
    """Open the browser after a short delay."""
    webbrowser.open(f'http://localhost:{port}')

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(os.path.join(os.path.dirname(__file__), 'src/web/static/data'), exist_ok=True)
    
    # Get the local IP address
    local_ip = get_local_ip()
    port = 5000
    
    print("\n=== AI Economic News Agent Web UI ===")
    print(f"\nLocal URL:     http://localhost:{port}")
    print(f"Network URL:   http://{local_ip}:{port}")
    print("\nPress Ctrl+C to quit the server.")
    
    # Create a flag file to prevent multiple browser windows on restart
    flag_file = os.path.join(os.path.dirname(__file__), '.browser_launched')
    
    # Only open browser if flag file doesn't exist
    if not os.path.exists(flag_file):
        # Create the flag file
        with open(flag_file, 'w') as f:
            f.write(str(datetime.datetime.now()))
        
        # Open browser automatically after a short delay
        Timer(1.5, open_browser, [port]).start()
    
    # Import and run the Flask app
    from src.web.simple_app import app
    app.run(debug=True, host='0.0.0.0', port=port)
