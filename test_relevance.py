"""
Test script to check the relevance scores in the web UI.
"""

import os
import json
import requests
from datetime import datetime

# Check if cache file exists and what it contains
def check_cache():
    cache_path = os.path.join('src', 'web', 'static', 'data', 'latest_articles.json')
    
    if os.path.exists(cache_path):
        print(f"Cache file exists at: {cache_path}")
        print(f"Last modified: {datetime.fromtimestamp(os.path.getmtime(cache_path))}")
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                
            print(f"Number of articles in cache: {len(data)}")
            
            # Print relevance scores
            print("\nRelevance scores in cache:")
            for i, article in enumerate(data):
                title = article.get('title', 'Unknown Title')
                relevance = article.get('relevance_score', 'N/A')
                print(f"{i+1}. {title[:40]}... - Relevance: {relevance}")
                
            return data
        except Exception as e:
            print(f"Error reading cache: {str(e)}")
            return None
    else:
        print(f"Cache file does not exist at: {cache_path}")
        return None

# Test direct API call
def test_api_call():
    try:
        print("\nTesting direct API call to /api/articles...")
        response = requests.get('http://localhost:5000/api/articles?cache=false&t=' + str(datetime.now().timestamp()))
        
        if response.status_code == 200:
            data = response.json()
            print(f"API returned {len(data)} articles")
            
            # Print relevance scores
            print("\nRelevance scores from API:")
            for i, article in enumerate(data):
                title = article.get('title', 'Unknown Title')
                relevance = article.get('relevance_score', 'N/A')
                print(f"{i+1}. {title[:40]}... - Relevance: {relevance}")
                
            return data
        else:
            print(f"API call failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error making API call: {str(e)}")
        return None

# Test refresh endpoint
def test_refresh():
    try:
        print("\nTesting refresh endpoint...")
        response = requests.get('http://localhost:5000/api/refresh')
        
        if response.status_code == 200:
            data = response.json()
            print(f"Refresh status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            print(f"Count: {data.get('count')}")
            
            # Now get the articles
            response = requests.get('http://localhost:5000/api/articles?cache=false&t=' + str(datetime.now().timestamp()))
            
            if response.status_code == 200:
                articles = response.json()
                print(f"After refresh, API returned {len(articles)} articles")
                
                # Print relevance scores
                print("\nRelevance scores after refresh:")
                for i, article in enumerate(articles):
                    title = article.get('title', 'Unknown Title')
                    relevance = article.get('relevance_score', 'N/A')
                    print(f"{i+1}. {title[:40]}... - Relevance: {relevance}")
                    
                return articles
        else:
            print(f"Refresh call failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error making refresh call: {str(e)}")
        return None

# Check the HTML template
def check_template():
    template_path = os.path.join('src', 'web', 'templates', 'index.html')
    
    if os.path.exists(template_path):
        print(f"\nTemplate file exists at: {template_path}")
        
        try:
            with open(template_path, 'r') as f:
                content = f.read()
                
            # Look for relevance score formatting
            relevance_lines = [line.strip() for line in content.split('\n') if 'relevance' in line.lower() and 'score' in line.lower()]
            
            print("\nRelevance score formatting in template:")
            for line in relevance_lines:
                print(line)
                
        except Exception as e:
            print(f"Error reading template: {str(e)}")
    else:
        print(f"Template file does not exist at: {template_path}")

if __name__ == "__main__":
    print("=== Testing Relevance Scores ===\n")
    
    # Check cache
    cache_data = check_cache()
    
    # Test API call
    api_data = test_api_call()
    
    # Test refresh
    refresh_data = test_refresh()
    
    # Check template
    check_template()
    
    print("\n=== Test Complete ===")
