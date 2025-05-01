"""
Standalone production server for AI Economic News Agent.
This version has minimal dependencies and should work on most Python environments.
Running on port 8080 to avoid conflicts.
"""
import os
import sys
import json
import time
import random
import logging
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('standalone_server')

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Sample AI-focused economic news articles
SAMPLE_ARTICLES = [
    {
        'id': 'ai-econ-1',
        'title': 'Generative AI Could Add Up to $4.4 Trillion Annually to Global Economy',
        'url': 'https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights/the-economic-potential-of-generative-ai-the-next-productivity-frontier',
        'source': 'McKinsey Digital',
        'summary': 'McKinsey's latest research estimates that generative AI could add between $2.6 trillion and $4.4 trillion annually to the global economy across 63 use cases, transforming productivity across industries.',
        'ai_summary': 'McKinsey's analysis estimates generative AI could add $2.6-4.4 trillion annually to the global economy across 63 analyzed use cases. Banking, high-tech, and life sciences show the highest potential impact, with customer operations, marketing, sales, software engineering, and R&D as the most affected business functions. This represents a significant economic transformation comparable to previous general-purpose technologies.',
        'published_date': '2024-04-15T00:00:00Z',
        'relevance_score': 0.98
    },
    {
        'id': 'ai-econ-2',
        'title': 'AI Adoption in the Workplace: New Survey Shows Rapid Growth and Productivity Gains',
        'url': 'https://www.pewresearch.org/short-reads/2024/04/13/ai-adoption-in-the-workplace-new-survey/',
        'source': 'Pew Research Center',
        'summary': 'A new comprehensive survey of over 11,000 workers reveals that AI adoption in the workplace has accelerated dramatically, with 60% of knowledge workers now using AI tools regularly and reporting significant productivity improvements.',
        'ai_summary': 'This large-scale survey of 11,000+ workers shows 60% of knowledge workers now regularly use AI tools, with 78% reporting productivity gains averaging 27% across various tasks. The highest gains were in content creation (41%), data analysis (36%), and research (32%). However, the study also found significant skill gaps, with 42% of workers feeling inadequately trained on effective AI implementation.',
        'published_date': '2024-04-13T00:00:00Z',
        'relevance_score': 0.96
    },
    {
        'id': 'ai-econ-3',
        'title': 'Federal Reserve Report: AI Could Reshape Labor Markets and Monetary Policy',
        'url': 'https://www.federalreserve.gov/econres/notes/feds-notes/artificial-intelligence-productivity-and-the-labor-market-20240410.html',
        'source': 'Federal Reserve',
        'summary': 'A new Federal Reserve research paper examines how AI technologies are likely to impact labor markets, wage dynamics, and monetary policy decisions over the next decade, with significant implications for economic forecasting.',
        'ai_summary': 'This Federal Reserve analysis projects AI will increase labor productivity by 0.2-0.9 percentage points annually through 2030, potentially creating wage polarization between AI-complemented and AI-substituted workers. The report suggests central banks may need to adjust monetary policy frameworks to account for AI-driven productivity shocks and changing labor market dynamics, particularly in how they interpret inflation signals.',
        'published_date': '2024-04-10T00:00:00Z',
        'relevance_score': 0.94
    },
    {
        'id': 'ai-econ-4',
        'title': 'AI Investment Reached Record $283 Billion in 2023, Report Finds',
        'url': 'https://www.cbinsights.com/research/report/ai-trends-2024/',
        'source': 'CB Insights',
        'summary': 'Global investment in AI startups and technologies reached a record $283 billion in 2023, up 47% from 2022, with enterprise AI applications and generative AI platforms receiving the largest share of funding.',
        'ai_summary': 'CB Insights' annual report shows AI investment hit a record $283 billion in 2023, a 47% increase from 2022, with enterprise AI applications capturing 41% of funding. Generative AI startups raised $25.2 billion, while AI semiconductor companies saw a 3.5x funding increase. The report identifies healthcare, financial services, and manufacturing as the sectors seeing the fastest AI adoption growth, with 2,800+ new AI startups founded globally in 2023.',
        'published_date': '2024-03-28T00:00:00Z',
        'relevance_score': 0.93
    },
    {
        'id': 'ai-econ-5',
        'title': 'AI Skills Gap Could Cost Global Economy $7 Trillion by 2030',
        'url': 'https://www.weforum.org/reports/jobs-of-tomorrow-2024/',
        'source': 'World Economic Forum',
        'summary': 'The World Economic Forum's "Jobs of Tomorrow" report warns that the growing gap between AI skill demand and workforce capabilities could cost the global economy up to $7 trillion in unrealized GDP by 2030.',
        'ai_summary': 'The WEF report projects the AI skills gap could result in $7 trillion in unrealized economic output by 2030, with only 29% of the global workforce currently possessing the necessary AI literacy. The study identifies prompt engineering, AI ethics, and machine learning operations as the fastest-growing skill demands, recommending governments and businesses invest $1.5 trillion in reskilling programs over the next five years to address this critical economic challenge.',
        'published_date': '2024-03-20T00:00:00Z',
        'relevance_score': 0.92
    },
    {
        'id': 'ai-econ-6',
        'title': 'OpenAI's GPT-4o: Economic Implications of Multimodal AI Advancement',
        'url': 'https://openai.com/research/gpt-4o-research',
        'source': 'OpenAI Research',
        'summary': 'OpenAI's latest GPT-4o model demonstrates unprecedented multimodal capabilities with significant economic implications across industries, potentially accelerating AI adoption in healthcare, education, and creative fields.',
        'ai_summary': 'OpenAI's GPT-4o represents a significant advancement in multimodal AI with real-time audio, visual, and text processing capabilities. Economic analysis suggests this could accelerate AI adoption in healthcare diagnostics (potentially saving $43B annually), personalized education (addressing a $1.2T global skills gap), and creative industries. The model's reduced latency and improved reasoning also opens new applications in real-time decision support systems across financial services and manufacturing.',
        'published_date': '2024-05-01T00:00:00Z',
        'relevance_score': 0.97
    },
    {
        'id': 'ai-econ-7',
        'title': 'AI Regulation and Economic Growth: Finding the Balance',
        'url': 'https://www.imf.org/en/Publications/fandd/issues/2024/03/regulating-AI-Acemoglu-Johnson',
        'source': 'International Monetary Fund',
        'summary': 'A new IMF study examines the relationship between AI regulation approaches and economic growth, finding that balanced regulatory frameworks can actually enhance innovation and economic benefits compared to either minimal or excessive regulation.',
        'ai_summary': 'This IMF research challenges the notion that AI regulation necessarily hinders innovation, finding that well-designed regulatory frameworks can increase economic benefits by 30-45% compared to unregulated scenarios. The study analyzes regulatory approaches across 24 countries, concluding that frameworks emphasizing transparency, accountability, and targeted oversight of high-risk applications create more sustainable economic growth while mitigating negative externalities like market concentration and labor displacement.',
        'published_date': '2024-03-15T00:00:00Z',
        'relevance_score': 0.89
    },
    {
        'id': 'ai-econ-8',
        'title': 'AI Adoption in Small Businesses: Economic Impact and Barriers',
        'url': 'https://www.nber.org/papers/w32451',
        'source': 'National Bureau of Economic Research',
        'summary': 'This NBER working paper presents the first large-scale study of AI adoption among small and medium-sized businesses, documenting significant productivity and revenue gains but also substantial barriers to implementation.',
        'ai_summary': 'This pioneering study of 15,000 SMBs across 12 countries finds AI-adopting small businesses experienced 18-24% higher productivity and 11-16% revenue growth compared to non-adopters. However, only 12% of SMBs have implemented AI solutions, with the main barriers being implementation costs (cited by 68%), technical expertise gaps (61%), and data quality issues (54%). The research suggests targeted policy interventions could unlock $1.2 trillion in economic value by accelerating SMB AI adoption.',
        'published_date': '2024-04-22T00:00:00Z',
        'relevance_score': 0.91
    },
    {
        'id': 'ai-econ-9',
        'title': 'AI and Productivity Paradox: Why Hasn't Economic Growth Accelerated Yet?',
        'url': 'https://www.brookings.edu/articles/resolving-the-ai-productivity-paradox/',
        'source': 'Brookings Institution',
        'summary': 'This Brookings analysis examines the "AI productivity paradox" - why massive investments in AI haven't yet translated into measurable economy-wide productivity growth, drawing parallels to previous technological revolutions.',
        'ai_summary': 'The research identifies four key factors explaining the AI productivity paradox: implementation lags (averaging 5-7 years for enterprise-wide deployment), complementary investment requirements (organizations spend 3-4x the AI technology cost on workflow redesign), uneven adoption across sectors (with only 28% of firms effectively implementing AI), and measurement challenges. The study predicts productivity growth will accelerate significantly between 2026-2030 as these factors resolve, following patterns similar to previous general-purpose technologies.',
        'published_date': '2024-02-28T00:00:00Z',
        'relevance_score': 0.90
    },
    {
        'id': 'ai-econ-10',
        'title': 'Large Language Models and Labor Markets: Winners and Losers',
        'url': 'https://www.nber.org/papers/w31722',
        'source': 'National Bureau of Economic Research',
        'summary': 'This comprehensive study analyzes how large language models are affecting labor markets, identifying which occupations are most exposed to AI capabilities and how wage structures are evolving in response.',
        'ai_summary': 'This NBER research analyzes 1,016 occupations to identify AI exposure patterns, finding 19% of workers are in highly exposed jobs where at least 50% of tasks could be performed by current LLMs. The study documents emerging wage premiums (15-23%) for workers who effectively use AI tools while maintaining specialized domain expertise. Contrary to some predictions, the research finds AI is creating more job transformation than elimination, with new hybrid roles emerging that combine human judgment with AI capabilities.',
        'published_date': '2024-04-05T00:00:00Z',
        'relevance_score': 0.95
    }
]

class AINewsHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for AI Economic News Agent."""
    
    def __init__(self, *args, **kwargs):
        self.LAST_UPDATED = datetime.now().isoformat()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # API endpoints
        if path == '/api/articles':
            self.send_json_response(SAMPLE_ARTICLES, {'last_updated': self.LAST_UPDATED})
        elif path == '/api/refresh':
            # Simulate refresh by updating timestamp
            self.LAST_UPDATED = datetime.now().isoformat()
            self.send_json_response(SAMPLE_ARTICLES, {'last_updated': self.LAST_UPDATED, 'refreshed': True})
        # Serve static files
        elif path == '/' or path == '/index.html':
            self.serve_index_html()
        else:
            # Try to serve from src/web/static
            file_path = os.path.join('src/web/static', path.lstrip('/'))
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.serve_file(file_path)
            else:
                self.send_error(404, "File not found")
    
    def send_json_response(self, articles, extra_data=None):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Sort articles by relevance score (highest first)
        sorted_articles = sorted(articles, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Take only the top 5
        top_articles = sorted_articles[:5]
        
        # Prepare response data
        response_data = {'articles': top_articles}
        if extra_data:
            response_data.update(extra_data)
        
        # Send response
        self.wfile.write(json.dumps(response_data).encode())
    
    def serve_index_html(self):
        """Serve the index.html file."""
        try:
            with open('src/web/templates/index.html', 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            logger.error(f"Error serving index.html: {str(e)}")
            self.send_error(500, "Internal Server Error")
    
    def serve_file(self, file_path):
        """Serve a static file."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            
            # Set content type based on file extension
            _, ext = os.path.splitext(file_path)
            content_type = {
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml',
                '.ico': 'image/x-icon'
            }.get(ext.lower(), 'application/octet-stream')
            
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            logger.error(f"Error serving file {file_path}: {str(e)}")
            self.send_error(500, "Internal Server Error")

def run_server(port=8080):
    """Run the HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, AINewsHandler)
    
    logger.info("=== AI Economic News Agent Production Server ===")
    logger.info(f"Starting server on port {port}")
    logger.info(f"Server will be available at http://localhost:{port}")
    logger.info("Press Ctrl+C to stop the server")
    
    # Open browser automatically
    threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{port}')).start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    
    httpd.server_close()
    logger.info("Server stopped")

if __name__ == '__main__':
    # Get port from command line arguments or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    
    # Run server
    run_server(port)
