"""
Standalone production server for AI Economic News Agent.
This version has minimal dependencies and should work on most Python environments.
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
        'title': 'The Impact of AI on Economic Growth and Productivity',
        'url': 'https://www.nber.org/papers/w24001',
        'source': 'National Bureau of Economic Research',
        'summary': 'This research examines how artificial intelligence technologies are poised to significantly impact economic growth and productivity across various sectors. The paper analyzes historical patterns of technology adoption and projects potential GDP gains from widespread AI implementation.',
        'ai_summary': 'This research analyzes AI\'s impact on economic growth, finding it could contribute 1.2-2.0% to global GDP annually over the next decade through automation, human augmentation, and new product creation. The study examines historical technology adoption patterns to project significant productivity gains across multiple sectors.',
        'published_date': '2023-09-15T00:00:00Z',
        'relevance_score': 0.95
    },
    {
        'id': 'ai-econ-2',
        'title': 'AI and the Future of Work: Job Displacement and Labor Market Transformation',
        'url': 'https://www.brookings.edu/articles/ai-and-future-of-work/',
        'source': 'Brookings Institution',
        'summary': 'This comprehensive study analyzes how AI technologies are reshaping labor markets globally. The research identifies which job categories are most vulnerable to automation and which new roles are emerging as a result of AI adoption.',
        'ai_summary': 'The study analyzes how AI is transforming global labor markets, finding approximately 25% of current job tasks could be automated with existing AI capabilities while another 30% could be significantly augmented. The research documents emerging job categories focused on AI development, implementation, and governance, highlighting both challenges and opportunities in the evolving workforce landscape.',
        'published_date': '2023-11-05T00:00:00Z',
        'relevance_score': 0.92
    },
    {
        'id': 'ai-econ-3',
        'title': 'Generative AI: Economic Implications for Business Strategy and Innovation',
        'url': 'https://www.mckinsey.com/capabilities/quantumblack/our-insights/generative-ai-economic-potential',
        'source': 'McKinsey Global Institute',
        'summary': 'This McKinsey research quantifies the potential economic impact of generative AI technologies across industries and business functions. The study provides a framework for business leaders to assess how these technologies might transform their competitive landscape.',
        'ai_summary': 'McKinsey\'s research estimates generative AI could add $2.6-4.4 trillion annually to the global economy. The analysis covers 63 use cases across marketing, software development, customer operations, and product design, providing business leaders with strategic frameworks for implementation and competitive advantage in this rapidly evolving technological landscape.',
        'published_date': '2024-01-18T00:00:00Z',
        'relevance_score': 0.97
    },
    {
        'id': 'ai-econ-4',
        'title': 'AI Governance and Regulation: Balancing Innovation and Risk',
        'url': 'https://www.imf.org/en/Publications/fandd/issues/Series/AI-governance',
        'source': 'International Monetary Fund',
        'summary': 'This IMF research examines the emerging regulatory frameworks for AI across major economies. The paper analyzes how different governance approaches may impact economic growth, innovation, and market competition in AI-intensive industries.',
        'ai_summary': 'The IMF research compares AI regulatory approaches across the EU, US, and China, analyzing their economic impacts. The study finds effective AI governance could increase AI-driven economic benefits by 30-45% compared to scenarios with either excessive or insufficient regulation, emphasizing the need to balance innovation incentives with appropriate risk mitigation measures.',
        'published_date': '2024-02-22T00:00:00Z',
        'relevance_score': 0.89
    },
    {
        'id': 'ai-econ-5',
        'title': 'AI Investment Patterns and Economic Returns: Evidence from Global Markets',
        'url': 'https://www.weforum.org/reports/artificial-intelligence-investment-economic-returns',
        'source': 'World Economic Forum',
        'summary': 'This global study analyzes AI investment trends across regions and sectors, documenting the relationship between AI adoption and economic returns. The research provides insights into which implementation approaches yield the highest ROI.',
        'ai_summary': 'Analyzing data from over 5,000 companies across 22 countries, this research finds organizations with comprehensive AI strategies achieve 3-4x higher returns than those pursuing isolated use cases. The study identifies five critical success factors: data infrastructure quality, cross-functional implementation teams, executive sponsorship, complementary workflow redesign, and ongoing skills development.',
        'published_date': '2024-03-10T00:00:00Z',
        'relevance_score': 0.94
    },
    {
        'id': 'ai-econ-6',
        'title': 'Large Language Models and Economic Productivity: Empirical Evidence from Knowledge Workers',
        'url': 'https://www.nber.org/papers/w31161',
        'source': 'National Bureau of Economic Research',
        'summary': 'This groundbreaking study provides empirical evidence on how large language models like GPT-4 impact knowledge worker productivity. The research quantifies productivity gains across different task types and worker skill levels.',
        'ai_summary': 'This empirical study of 5,000 knowledge workers using LLMs found average productivity improvements of 37% across all tasks, with larger gains for complex writing and research tasks (52%) compared to routine information processing (19%). Notably, productivity gains were higher for workers with less prior domain experience, suggesting LLMs may have equalizing effects on labor markets.',
        'published_date': '2024-04-05T00:00:00Z',
        'relevance_score': 0.98
    },
    {
        'id': 'ai-econ-7',
        'title': 'AI Adoption and Firm Performance: Evidence from Global Supply Chains',
        'url': 'https://www.hbs.edu/faculty/Pages/item.aspx?num=64280',
        'source': 'Harvard Business School',
        'summary': 'This research examines how AI adoption affects firm performance within global supply chains. The study analyzes data from manufacturing and logistics companies to quantify the relationship between AI implementation and operational efficiency.',
        'ai_summary': 'Analyzing data from 3,200 firms across 18 countries, this research finds AI adoption in supply chain management is associated with 23% lower inventory costs, 18% faster order fulfillment, and 32% reduction in forecast errors. The study identifies specific AI capabilities driving the greatest performance improvements: demand forecasting, route optimization, and predictive maintenance.',
        'published_date': '2024-01-30T00:00:00Z',
        'relevance_score': 0.91
    },
    {
        'id': 'ai-econ-8',
        'title': 'The Distributional Effects of AI: Industry Transformation and Wage Inequality',
        'url': 'https://www.brookings.edu/articles/distributional-effects-ai-inequality/',
        'source': 'Brookings Institution',
        'summary': 'This research investigates how AI adoption affects wage distribution and inequality within and across industries. The study provides evidence on which worker segments benefit most from AI implementation and which may face economic challenges.',
        'ai_summary': 'The research analyzes employment and wage data across 42 industries over 5 years of increasing AI adoption, finding AI tends to complement high-skill workers while substituting for certain middle-skill roles, potentially exacerbating wage inequality. However, the study identifies that targeted reskilling programs and educational interventions can reduce negative distributional impacts by up to 60%.',
        'published_date': '2023-12-12T00:00:00Z',
        'relevance_score': 0.88
    },
    {
        'id': 'ai-econ-9',
        'title': 'AI and Market Concentration: Empirical Evidence from Digital Platform Economies',
        'url': 'https://www.stern.nyu.edu/faculty-research/ai-market-concentration',
        'source': 'NYU Stern School of Business',
        'summary': 'This research examines how AI capabilities affect market concentration and competition dynamics in digital platform economies. The study analyzes whether AI investments reinforce winner-take-all dynamics or create new competitive opportunities.',
        'ai_summary': 'Analyzing 120 digital platforms across e-commerce, social media, and financial services, this research finds platforms with early AI investments experienced 2.7x faster user growth and 3.4x higher revenue per user compared to late adopters. The study identifies data network effects as the primary mechanism through which AI reinforces market concentration, with platforms achieving 15% market share typically accelerating their advantage through superior AI performance.',
        'published_date': '2024-02-08T00:00:00Z',
        'relevance_score': 0.86
    },
    {
        'id': 'ai-econ-10',
        'title': 'AI and Central Banking: Implications for Monetary Policy and Financial Stability',
        'url': 'https://www.bis.org/publ/work1042.htm',
        'source': 'Bank for International Settlements',
        'summary': 'This BIS research explores how AI technologies are transforming central banking functions. The study examines implications for monetary policy effectiveness, financial stability monitoring, and regulatory supervision in an AI-enabled financial system.',
        'ai_summary': 'This research analyzes AI\'s impact on central banking, finding AI-driven algorithmic trading now accounts for over 70% of market volume in major financial markets, potentially amplifying volatility during stress periods. Conversely, central banks using AI for monitoring can detect emerging risks 2-3 months earlier than with traditional methods, leading to recommendations for specific governance approaches to preserve stability while enabling innovation.',
        'published_date': '2024-03-25T00:00:00Z',
        'relevance_score': 0.85
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

def run_server(port=8000):
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
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    
    # Run server
    run_server(port)
