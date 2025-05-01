import os
import sys
import time
import logging
import subprocess
import signal
import psutil
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("ai_news_service.log"),
        logging.StreamHandler()
    ]
)

# Default port
DEFAULT_PORT = 8080

def is_port_in_use(port):
    """Check if a port is in use"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return True
    return False

def find_available_port(start_port):
    """Find an available port starting from start_port"""
    port = start_port
    while is_port_in_use(port):
        port += 1
        if port > 65535:
            logging.error("No available ports found")
            return None
    return port

def start_server(port, daemon=False):
    """Start the AI Economic News server"""
    server_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "production_server.py")
    
    if not os.path.exists(server_script):
        logging.error(f"Server script not found: {server_script}")
        return None
    
    # Check if port is available
    if is_port_in_use(port):
        new_port = find_available_port(port)
        if new_port:
            logging.warning(f"Port {port} is in use. Using port {new_port} instead.")
            port = new_port
        else:
            logging.error(f"Port {port} is in use and no available ports found.")
            return None
    
    try:
        # Start the server process
        cmd = [sys.executable, server_script, str(port)]
        
        if daemon:
            # Start as background process
            if os.name == 'nt':  # Windows
                from subprocess import DEVNULL, CREATE_NEW_PROCESS_GROUP
                process = subprocess.Popen(
                    cmd,
                    stdout=DEVNULL,
                    stderr=DEVNULL,
                    creationflags=CREATE_NEW_PROCESS_GROUP,
                    shell=False
                )
            else:  # Unix-like
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            # Wait a moment to make sure the process started
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                logging.info(f"Server started as daemon on port {port} (PID: {process.pid})")
                
                # Write PID to file for later management
                with open("ai_news_server.pid", "w") as f:
                    f.write(str(process.pid))
                
                return process.pid
            else:
                logging.error("Server failed to start as daemon")
                return None
        else:
            # Start in foreground
            logging.info(f"Starting server on port {port}...")
            subprocess.run(cmd)
            return True
            
    except Exception as e:
        logging.error(f"Error starting server: {str(e)}")
        return None

def stop_server():
    """Stop the AI Economic News server"""
    try:
        # Check if PID file exists
        if os.path.exists("ai_news_server.pid"):
            with open("ai_news_server.pid", "r") as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            if psutil.pid_exists(pid):
                # Get process
                process = psutil.Process(pid)
                
                # Check if it's our Python server
                if "python" in process.name().lower():
                    # Kill the process
                    if os.name == 'nt':  # Windows
                        os.kill(pid, signal.CTRL_BREAK_EVENT)
                    else:  # Unix-like
                        os.kill(pid, signal.SIGTERM)
                    
                    # Wait for process to terminate
                    try:
                        process.wait(timeout=5)
                        logging.info(f"Server stopped (PID: {pid})")
                    except psutil.TimeoutExpired:
                        # Force kill if graceful shutdown fails
                        process.kill()
                        logging.info(f"Server forcefully terminated (PID: {pid})")
                    
                    # Remove PID file
                    os.remove("ai_news_server.pid")
                    return True
                else:
                    logging.error(f"Process with PID {pid} is not a Python process")
            else:
                logging.error(f"No process found with PID {pid}")
                # Remove stale PID file
                os.remove("ai_news_server.pid")
        else:
            # Try to find and kill by port
            for conn in psutil.net_connections():
                if conn.laddr.port == DEFAULT_PORT and conn.status == 'LISTEN':
                    pid = conn.pid
                    try:
                        process = psutil.Process(pid)
                        process.terminate()
                        logging.info(f"Server stopped by port (PID: {pid})")
                        return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        logging.error(f"Failed to terminate process with PID {pid}")
            
            logging.error("No running server found")
        
        return False
    except Exception as e:
        logging.error(f"Error stopping server: {str(e)}")
        return False

def status():
    """Check the status of the AI Economic News server"""
    try:
        # Check if PID file exists
        if os.path.exists("ai_news_server.pid"):
            with open("ai_news_server.pid", "r") as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            if psutil.pid_exists(pid):
                # Get process
                process = psutil.Process(pid)
                
                # Check if it's our Python server
                if "python" in process.name().lower():
                    # Get process info
                    create_time = datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S')
                    cpu_percent = process.cpu_percent(interval=0.1)
                    memory_info = process.memory_info()
                    
                    logging.info(f"Server is running (PID: {pid})")
                    logging.info(f"Started at: {create_time}")
                    logging.info(f"CPU usage: {cpu_percent}%")
                    logging.info(f"Memory usage: {memory_info.rss / (1024 * 1024):.2f} MB")
                    
                    # Try to find the port
                    for conn in process.connections():
                        if conn.status == 'LISTEN':
                            logging.info(f"Listening on port: {conn.laddr.port}")
                            break
                    
                    return True
                else:
                    logging.error(f"Process with PID {pid} is not a Python process")
            else:
                logging.error(f"No process found with PID {pid}")
                # Remove stale PID file
                os.remove("ai_news_server.pid")
        else:
            # Try to find by port
            for conn in psutil.net_connections():
                if conn.laddr.port == DEFAULT_PORT and conn.status == 'LISTEN':
                    pid = conn.pid
                    try:
                        process = psutil.Process(pid)
                        if "python" in process.name().lower():
                            logging.info(f"Server is running on port {DEFAULT_PORT} (PID: {pid})")
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            
            logging.info("Server is not running")
        
        return False
    except Exception as e:
        logging.error(f"Error checking server status: {str(e)}")
        return False

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description='AI Economic News Server Service Manager')
    
    # Command argument
    parser.add_argument('command', choices=['start', 'stop', 'restart', 'status'],
                        help='Command to execute')
    
    # Optional port argument
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
                        help=f'Port to run the server on (default: {DEFAULT_PORT})')
    
    # Daemon mode
    parser.add_argument('-d', '--daemon', action='store_true',
                        help='Run as daemon (background process)')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        start_server(args.port, args.daemon)
    elif args.command == 'stop':
        stop_server()
    elif args.command == 'restart':
        stop_server()
        time.sleep(2)  # Wait for the server to fully stop
        start_server(args.port, args.daemon)
    elif args.command == 'status':
        status()

if __name__ == "__main__":
    # Check if psutil is installed
    try:
        import psutil
    except ImportError:
        logging.error("psutil is required. Please install it with: pip install psutil")
        sys.exit(1)
        
    main()
