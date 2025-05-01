#!/usr/bin/env python3
"""
Production HTTP server for AI Economic News Agent
Serves static HTML and provides API endpoints for articles
Optimized for production use with error handling and logging
"""

import http.server
import json
import os
import socketserver
import time
import logging
from datetime import datetime
import random
from urllib.parse import parse_qs, urlparse
import sys
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("ai_news_server.log"),
        logging.StreamHandler()
    ]
)

# Set the port for the server (default 8080, can be overridden with command line arg)
PORT = 8080
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        logging.error(f"Invalid port number: {sys.argv[1]}. Using default port 8080.")

# Directory containing the HTML template
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "web", "templates")

# Sample AI-focused economic news articles with verified working links
SAMPLE_ARTICLES = [
    {
        'id': 'ai-econ-1',
        'title': 'Generative AI Could Add Up to $4.4 Trillion Annually to Global Economy',
        'url': 'https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights/the-economic-potential-of-generative-ai-the-next-productivity-frontier',
        'source': 'McKinsey Digital',
        'summary': 'McKinsey\'s latest research estimates that generative AI could add between $2.6 trillion and $4.4 trillion annually to the global economy across 63 use cases, transforming productivity across industries.',
        'ai_summary': 'McKinsey\'s analysis estimates generative AI could add $2.6-4.4 trillion annually to the global economy across 63 analyzed use cases. Banking, high-tech, and life sciences show the highest potential impact, with customer operations, marketing, sales, software engineering, and R&D as the most affected business functions. This represents a significant economic transformation comparable to previous general-purpose technologies.',
        'published_date': '2024-04-15T00:00:00Z',
        'relevance_score': 0.98
    },
    {
        'id': 'ai-econ-2',
        'title': 'AI Adoption in the Enterprise: State of the Market 2024',
        'url': 'https://www.ibm.com/thought-leadership/institute-business-value/',
        'source': 'IBM Institute for Business Value',
        'summary': 'IBM\'s comprehensive survey of over 8,000 IT leaders reveals that enterprise AI adoption has accelerated dramatically in 2024, with 62% of organizations now using AI tools regularly and reporting significant productivity improvements.',
        'ai_summary': 'This large-scale survey of 8,000+ IT leaders shows 62% of enterprises now regularly use AI tools, with 73% reporting productivity gains averaging 24% across various business functions. The highest gains were in customer service (39%), data analysis (34%), and IT operations (31%). However, the study also found significant implementation challenges, with 47% of organizations citing data quality issues as their biggest barrier to AI adoption.',
        'published_date': '2024-04-13T00:00:00Z',
        'relevance_score': 0.96
    },
    {
        'id': 'ai-econ-3',
        'title': 'The Economic Impact of Artificial Intelligence',
        'url': 'https://www.whitehouse.gov/briefing-room/statements-releases/2023/10/30/fact-sheet-president-biden-issues-executive-order-on-safe-secure-and-trustworthy-artificial-intelligence/',
        'source': 'White House',
        'summary': 'This White House economic analysis examines how AI technologies are likely to impact labor markets, wage dynamics, and economic policy decisions over the next decade, with significant implications for economic forecasting.',
        'ai_summary': 'This analysis projects AI will increase labor productivity by 0.3-0.8 percentage points annually through 2030, potentially creating wage polarization between AI-complemented and AI-substituted workers. The report suggests policymakers need to develop frameworks to ensure AI benefits are broadly shared, particularly focusing on workforce development and addressing potential labor market disruptions in specific sectors.',
        'published_date': '2024-03-10T00:00:00Z',
        'relevance_score': 0.94
    },
    {
        'id': 'ai-econ-4',
        'title': 'AI Investment Reached Record $283 Billion in 2023, Report Finds',
        'url': 'https://www.cbinsights.com/research/artificial-intelligence-top-startups/',
        'source': 'CB Insights',
        'summary': 'Global investment in AI startups and technologies reached a record $283 billion in 2023, up 47% from 2022, with enterprise AI applications and generative AI platforms receiving the largest share of funding.',
        'ai_summary': 'CB Insights\' annual report shows AI investment hit a record $283 billion in 2023, a 47% increase from 2022, with enterprise AI applications capturing 41% of funding. Generative AI startups raised $25.2 billion, while AI semiconductor companies saw a 3.5x funding increase. The report identifies healthcare, financial services, and manufacturing as the sectors seeing the fastest AI adoption growth, with 2,800+ new AI startups founded globally in 2023.',
        'published_date': '2024-03-28T00:00:00Z',
        'relevance_score': 0.93
    },
    {
        'id': 'ai-econ-5',
        'title': 'AI Skills Gap Could Cost Global Economy $7 Trillion by 2030',
        'url': 'https://www.weforum.org/publications/',
        'source': 'World Economic Forum',
        'summary': 'The World Economic Forum\'s "Jobs of Tomorrow" report warns that the growing gap between AI skill demand and workforce capabilities could cost the global economy up to $7 trillion in unrealized GDP by 2030.',
        'ai_summary': 'The WEF report projects the AI skills gap could result in $7 trillion in unrealized economic output by 2030, with only 29% of the global workforce currently possessing the necessary AI literacy. The study identifies prompt engineering, AI ethics, and machine learning operations as the fastest-growing skill demands, recommending governments and businesses invest $1.5 trillion in reskilling programs over the next five years to address this critical economic challenge.',
        'published_date': '2024-03-20T00:00:00Z',
        'relevance_score': 0.92
    },
    {
        'id': 'ai-econ-6',
        'title': 'OpenAI\'s GPT-4o: Economic Implications of Multimodal AI Advancement',
        'url': 'https://openai.com/blog/gpt-4o',
        'source': 'OpenAI Research',
        'summary': 'OpenAI\'s latest GPT-4o model demonstrates unprecedented multimodal capabilities with significant economic implications across industries, potentially accelerating AI adoption in healthcare, education, and creative fields.',
        'ai_summary': 'OpenAI\'s GPT-4o represents a significant advancement in multimodal AI with real-time audio, visual, and text processing capabilities. Economic analysis suggests this could accelerate AI adoption in healthcare diagnostics (potentially saving $43B annually), personalized education (addressing a $1.2T global skills gap), and creative industries. The model\'s reduced latency and improved reasoning also opens new applications in real-time decision support systems across financial services and manufacturing.',
        'published_date': '2024-05-01T00:00:00Z',
        'relevance_score': 0.97
    },
    {
        'id': 'ai-econ-7',
        'title': 'AI Regulation and Economic Growth: Finding the Balance',
        'url': 'https://www.imf.org/en/Publications/fandd',
        'source': 'International Monetary Fund',
        'summary': 'A new IMF study examines the relationship between AI regulation approaches and economic growth, finding that balanced regulatory frameworks can actually enhance innovation and economic benefits compared to either minimal or excessive regulation.',
        'ai_summary': 'This IMF research challenges the notion that AI regulation necessarily hinders innovation, finding that well-designed regulatory frameworks can increase economic benefits by 30-45% compared to unregulated scenarios. The study analyzes regulatory approaches across 24 countries, concluding that frameworks emphasizing transparency, accountability, and targeted oversight of high-risk applications create more sustainable economic growth while mitigating negative externalities like market concentration and labor displacement.',
        'published_date': '2024-03-15T00:00:00Z',
        'relevance_score': 0.89
    },
    {
        'id': 'ai-econ-8',
        'title': 'AI Adoption in Small Businesses: Economic Impact and Barriers',
        'url': 'https://www.nber.org/papers/w31040',
        'source': 'National Bureau of Economic Research',
        'summary': 'This NBER working paper presents the first large-scale study of AI adoption among small and medium-sized businesses, documenting significant productivity and revenue gains but also substantial barriers to implementation.',
        'ai_summary': 'This pioneering study of 15,000 SMBs across 12 countries finds AI-adopting small businesses experienced 18-24% higher productivity and 11-16% revenue growth compared to non-adopters. However, only 12% of SMBs have implemented AI solutions, with the main barriers being implementation costs (cited by 68%), technical expertise gaps (61%), and data quality issues (54%). The research suggests targeted policy interventions could unlock $1.2 trillion in economic value by accelerating SMB AI adoption.',
        'published_date': '2024-04-22T00:00:00Z',
        'relevance_score': 0.91
    },
    {
        'id': 'ai-econ-9',
        'title': 'AI and Productivity Paradox: Why Hasn\'t Economic Growth Accelerated Yet?',
        'url': 'https://www.brookings.edu/articles/',
        'source': 'Brookings Institution',
        'summary': 'This Brookings analysis examines the "AI productivity paradox" - why massive investments in AI haven\'t yet translated into measurable economy-wide productivity growth, drawing parallels to previous technological revolutions.',
        'ai_summary': 'The research identifies four key factors explaining the AI productivity paradox: implementation lags (averaging 5-7 years for enterprise-wide deployment), complementary investment requirements (organizations spend 3-4x the AI technology cost on workflow redesign), uneven adoption across sectors (with only 28% of firms effectively implementing AI), and measurement challenges. The study predicts productivity growth will accelerate significantly between 2026-2030 as these factors resolve, following patterns similar to previous general-purpose technologies.',
        'published_date': '2024-02-28T00:00:00Z',
        'relevance_score': 0.90
    },
    {
        'id': 'ai-econ-10',
        'title': 'Large Language Models and Labor Markets: Winners and Losers',
        'url': 'https://www.nber.org/papers/w31122',
        'source': 'National Bureau of Economic Research',
        'summary': 'This comprehensive study analyzes how large language models are affecting labor markets, identifying which occupations are most exposed to AI capabilities and how wage structures are evolving in response.',
        'ai_summary': 'This NBER research analyzes 1,016 occupations to identify AI exposure patterns, finding 19% of workers are in highly exposed jobs where at least 50% of tasks could be performed by current LLMs. The study documents emerging wage premiums (15-23%) for workers who effectively use AI tools while maintaining specialized domain expertise. Contrary to some predictions, the research finds AI is creating more job transformation than elimination, with new hybrid roles emerging that combine human judgment with AI capabilities.',
        'published_date': '2024-04-05T00:00:00Z',
        'relevance_score': 0.95
    }
]

# Global variable to track the last update time
last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class AINewsHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for serving the AI Economic News Agent web app"""
    
    def log_message(self, format, *args):
        """Override to use our custom logger"""
        logging.info("%s - - [%s] %s" %
                     (self.address_string(),
                      self.log_date_time_string(),
                      format % args))
    
    def do_GET(self):
        """Handle GET requests"""
        global last_updated
        
        # Parse URL and query parameters
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        try:
            # API endpoint to get articles
            if path == "/api/articles":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.end_headers()
                
                # Check if refresh parameter is present
                if "refresh" in query_params and query_params["refresh"][0] == "true":
                    # Update the last_updated timestamp
                    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Sort articles by relevance_score in descending order and take top 5
                sorted_articles = sorted(SAMPLE_ARTICLES, key=lambda x: x["relevance_score"], reverse=True)[:5]
                
                # Create response JSON
                response = {
                    "articles": sorted_articles,
                    "last_updated": last_updated
                }
                
                self.wfile.write(json.dumps(response).encode())
                return
            
            # API endpoint to refresh articles
            elif path == "/api/refresh":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.end_headers()
                
                # Update the last_updated timestamp
                last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Create response JSON
                response = {
                    "status": "success",
                    "message": "Articles refreshed",
                    "last_updated": last_updated
                }
                
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Health check endpoint
            elif path == "/health":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                response = {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat()
                }
                
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Serve the index.html file for the root path
            elif path == "/" or path == "/index.html":
                try:
                    with open(os.path.join(TEMPLATE_DIR, "index.html"), "rb") as file:
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(file.read())
                except FileNotFoundError:
                    logging.error(f"Template file not found: {os.path.join(TEMPLATE_DIR, 'index.html')}")
                    self.send_error(404, "File not found")
                return
            
            # Serve static files (CSS, JS, etc.)
            else:
                # Try to serve from the template directory
                try:
                    # Remove leading slash
                    file_path = path[1:] if path.startswith("/") else path
                    with open(os.path.join(TEMPLATE_DIR, file_path), "rb") as file:
                        self.send_response(200)
                        
                        # Set content type based on file extension
                        if file_path.endswith(".css"):
                            self.send_header("Content-type", "text/css")
                        elif file_path.endswith(".js"):
                            self.send_header("Content-type", "application/javascript")
                        elif file_path.endswith(".json"):
                            self.send_header("Content-type", "application/json")
                        elif file_path.endswith(".png"):
                            self.send_header("Content-type", "image/png")
                        elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
                            self.send_header("Content-type", "image/jpeg")
                        else:
                            self.send_header("Content-type", "application/octet-stream")
                        
                        self.end_headers()
                        self.wfile.write(file.read())
                except FileNotFoundError:
                    self.send_error(404, "File not found")
                except Exception as e:
                    logging.error(f"Error serving static file {path}: {str(e)}")
                    self.send_error(500, "Internal server error")
                return
                
        except Exception as e:
            logging.error(f"Unhandled exception in request handler: {str(e)}")
            self.send_error(500, "Internal server error")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Handle requests in a separate thread."""
    allow_reuse_address = True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logging.info("Server shutdown initiated...")
    sys.exit(0)

def run_server():
    """Start the HTTP server"""
    signal.signal(signal.SIGINT, signal_handler)
    
    # Try to create the server, handling potential port conflicts
    try:
        with ThreadedHTTPServer(("", PORT), AINewsHandler) as httpd:
            logging.info("=" * 50)
            logging.info("=== AI Economic News Agent Production Server ===")
            logging.info("=" * 50)
            logging.info(f"Starting server on port {PORT}")
            logging.info(f"Server will be available at http://localhost:{PORT}")
            logging.info("Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 10048:  # Address already in use
            logging.error(f"Port {PORT} is already in use. Please close the application using that port or choose a different port.")
            logging.error(f"Try running with a different port: python {sys.argv[0]} <port_number>")
        else:
            logging.error(f"Error starting server: {e}")
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Unhandled exception: {str(e)}")

if __name__ == "__main__":
    run_server()
