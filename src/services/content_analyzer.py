"""
Content analyzer service for the AI Economic Research News Agent.

This module implements the content analysis functionality to evaluate article relevance,
generate summaries, and extract key information.
"""

import re
import os
from typing import List, Dict, Any
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import spacy
from loguru import logger
import openai

from src.services.protocols import AnalysisServiceProtocol
from src.models.article import Article
from config.settings import PRIMARY_KEYWORDS, SECONDARY_KEYWORDS


# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class ContentAnalyzer(AnalysisServiceProtocol):
    """
    Content analyzer for evaluating and extracting information from articles.
    
    Implements the AnalysisServiceProtocol interface.
    """
    
    def __init__(self):
        """Initialize the content analyzer."""
        # Load NLP models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model not found, download it
            logger.info("Downloading spaCy model...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        self.stop_words = set(stopwords.words('english'))
        
        # Initialize OpenAI if API key is available
        self.use_openai = False
        if os.environ.get("OPENAI_API_KEY"):
            openai.api_key = os.environ.get("OPENAI_API_KEY")
            self.use_openai = True
            logger.info("OpenAI API initialized")
    
    def analyze_relevance(self, article: Article, keywords: List[str]) -> float:
        """
        Analyze the relevance of an article to the given keywords.
        
        Args:
            article: Article to analyze
            keywords: List of keywords to check relevance against
            
        Returns:
            Relevance score between 0 and 1
        """
        text = article.content.text.lower()
        title = article.content.title.lower()
        
        # Count keyword occurrences
        keyword_counts = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Count in title (weighted higher)
            title_count = title.count(keyword_lower) * 3
            # Count in content
            content_count = text.count(keyword_lower)
            keyword_counts[keyword] = title_count + content_count
        
        # Calculate total matches
        total_matches = sum(keyword_counts.values())
        
        # Calculate density (matches per 1000 words)
        word_count = len(text.split())
        if word_count == 0:
            return 0
        
        keyword_density = total_matches / (word_count / 1000)
        
        # Normalize to a score between 0 and 1
        # A density of 10+ keywords per 1000 words is considered highly relevant
        relevance_score = min(1.0, keyword_density / 10)
        
        return relevance_score
    
    def count_keyword_matches(self, text: str, keywords: List[str]) -> Dict[str, int]:
        """
        Count the occurrences of each keyword in the text.
        
        Args:
            text: Text to analyze
            keywords: List of keywords to count
            
        Returns:
            Dictionary mapping keywords to their occurrence counts
        """
        text_lower = text.lower()
        counts = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = text_lower.count(keyword_lower)
            
            if count > 0:
                counts[keyword] = count
        
        return counts
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """
        Generate a summary of the article text.
        
        Args:
            text: Article text to summarize
            max_length: Maximum length of the summary in words
            
        Returns:
            Summary text
        """
        if self.use_openai:
            return self._generate_summary_with_openai(text, max_length)
        else:
            return self._generate_summary_with_extractive(text, max_length)
    
    def _generate_summary_with_openai(self, text: str, max_length: int = 200) -> str:
        """Generate a summary using OpenAI."""
        try:
            # Truncate text if too long
            max_tokens = 4000
            words = text.split()
            if len(words) > max_tokens:
                text = " ".join(words[:max_tokens]) + "..."
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a specialized AI that creates concise summaries of economic research articles about AI adoption. Focus on key findings, statistics, and economic implications."},
                    {"role": "user", "content": f"Summarize this article in about {max_length} words, focusing on economic research findings related to AI adoption:\n\n{text}"}
                ],
                max_tokens=max_length * 2,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary with OpenAI: {str(e)}")
            # Fall back to extractive summarization
            return self._generate_summary_with_extractive(text, max_length)
    
    def _generate_summary_with_extractive(self, text: str, max_length: int = 200) -> str:
        """Generate a summary using extractive summarization."""
        try:
            # Tokenize the text into sentences
            sentences = sent_tokenize(text)
            
            if not sentences:
                return ""
            
            # Score sentences based on keyword matches and position
            sentence_scores = {}
            for i, sentence in enumerate(sentences):
                # Position score (earlier sentences are more important)
                position_score = 1.0 / (i + 1)
                
                # Keyword score
                keyword_score = 0
                for keyword in PRIMARY_KEYWORDS + SECONDARY_KEYWORDS:
                    if keyword.lower() in sentence.lower():
                        keyword_score += 1
                
                # Length penalty (avoid very short sentences)
                length = len(sentence.split())
                length_score = min(1.0, length / 20)
                
                # Combine scores
                sentence_scores[sentence] = (keyword_score * 0.5) + (position_score * 0.3) + (length_score * 0.2)
            
            # Sort sentences by score
            sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Select top sentences up to max_length
            selected_sentences = []
            word_count = 0
            
            for sentence, _ in sorted_sentences:
                sentence_word_count = len(sentence.split())
                if word_count + sentence_word_count <= max_length:
                    selected_sentences.append(sentence)
                    word_count += sentence_word_count
                else:
                    break
            
            # Sort selected sentences by their original order
            original_order = {sentence: i for i, sentence in enumerate(sentences)}
            selected_sentences.sort(key=lambda s: original_order.get(s, 0))
            
            # Join sentences into a summary
            summary = " ".join(selected_sentences)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating extractive summary: {str(e)}")
            
            # Return first few sentences as fallback
            first_sentences = " ".join(sentences[:3]) if sentences else ""
            return first_sentences
    
    def extract_key_findings(self, text: str) -> List[str]:
        """
        Extract key findings from the article text.
        
        Args:
            text: Article text to analyze
            
        Returns:
            List of key findings as strings
        """
        if self.use_openai:
            return self._extract_key_findings_with_openai(text)
        else:
            return self._extract_key_findings_with_nlp(text)
    
    def _extract_key_findings_with_openai(self, text: str) -> List[str]:
        """Extract key findings using OpenAI."""
        try:
            # Truncate text if too long
            max_tokens = 4000
            words = text.split()
            if len(words) > max_tokens:
                text = " ".join(words[:max_tokens]) + "..."
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a specialized AI that extracts key economic findings from research articles about AI adoption. Focus on extracting quantitative data, statistics, economic implications, and research conclusions."},
                    {"role": "user", "content": f"Extract 3-5 key economic findings from this article about AI adoption. Format each finding as a concise, standalone sentence:\n\n{text}"}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            # Parse the response
            findings_text = response.choices[0].message.content.strip()
            
            # Split into individual findings
            findings = []
            for line in findings_text.split('\n'):
                # Remove numbering and bullet points
                clean_line = re.sub(r'^[\d\-\*\•\.\s]+', '', line).strip()
                if clean_line and len(clean_line) > 20:  # Minimum length to be a finding
                    findings.append(clean_line)
            
            return findings
            
        except Exception as e:
            logger.error(f"Error extracting key findings with OpenAI: {str(e)}")
            # Fall back to NLP method
            return self._extract_key_findings_with_nlp(text)
    
    def _extract_key_findings_with_nlp(self, text: str) -> List[str]:
        """Extract key findings using NLP techniques."""
        findings = []
        
        try:
            # Process the text with spaCy
            doc = self.nlp(text)
            
            # Look for sentences with economic indicators and AI terms
            economic_terms = [
                "percent", "growth", "increase", "decrease", "billion", "million",
                "economy", "economic", "GDP", "productivity", "revenue", "cost",
                "profit", "investment", "market", "industry", "sector", "forecast",
                "estimate", "projection", "study", "research", "analysis", "report"
            ]
            
            ai_terms = [
                "AI", "artificial intelligence", "machine learning", "ML", "automation",
                "algorithm", "neural network", "deep learning", "NLP", "computer vision"
            ]
            
            # Extract sentences that contain both economic and AI terms
            for sent in doc.sents:
                sent_text = sent.text.strip()
                sent_lower = sent_text.lower()
                
                # Check if sentence contains economic terms and AI terms
                has_economic = any(term in sent_lower for term in economic_terms)
                has_ai = any(term in sent_lower for term in ai_terms)
                
                # Check if sentence contains numbers (likely to have statistics)
                has_numbers = any(token.like_num for token in sent)
                
                # Check if sentence is a reasonable length
                good_length = 10 <= len(sent_text.split()) <= 40
                
                if (has_economic and has_ai and good_length) or (has_economic and has_ai and has_numbers):
                    findings.append(sent_text)
            
            # Limit to top 5 findings
            return findings[:5]
            
        except Exception as e:
            logger.error(f"Error extracting key findings with NLP: {str(e)}")
            return []
    
    def extract_economic_indicators(self, text: str) -> List[Dict[str, str]]:
        """
        Extract economic indicators from the article text.
        
        Args:
            text: Article text to analyze
            
        Returns:
            List of dictionaries containing economic indicators
        """
        indicators = []
        
        try:
            # Process the text with spaCy
            doc = self.nlp(text)
            
            # Define patterns for economic indicators
            gdp_pattern = r'(?:GDP|gross domestic product)(?:\s+growth)?\s+(?:of|at|by)?\s+([-+]?\d+(?:\.\d+)?%?)'
            growth_pattern = r'(?:economic|economy|market|industry|sector)\s+growth\s+(?:of|at|by)?\s+([-+]?\d+(?:\.\d+)?%?)'
            investment_pattern = r'(?:investment|funding|capital|spending)\s+(?:of|at|by)?\s+(\$?\d+(?:\.\d+)?\s+(?:billion|million|trillion))'
            productivity_pattern = r'productivity\s+(?:gain|increase|growth)\s+(?:of|at|by)?\s+([-+]?\d+(?:\.\d+)?%?)'
            roi_pattern = r'(?:ROI|return on investment)\s+(?:of|at|by)?\s+([-+]?\d+(?:\.\d+)?%?)'
            
            # Search for patterns in the text
            gdp_matches = re.findall(gdp_pattern, text, re.IGNORECASE)
            growth_matches = re.findall(growth_pattern, text, re.IGNORECASE)
            investment_matches = re.findall(investment_pattern, text, re.IGNORECASE)
            productivity_matches = re.findall(productivity_pattern, text, re.IGNORECASE)
            roi_matches = re.findall(roi_pattern, text, re.IGNORECASE)
            
            # Add GDP indicators
            for match in gdp_matches:
                indicators.append({
                    "name": "GDP Growth",
                    "value": match,
                    "description": self._find_context_for_match(text, match)
                })
            
            # Add economic growth indicators
            for match in growth_matches:
                indicators.append({
                    "name": "Economic Growth",
                    "value": match,
                    "description": self._find_context_for_match(text, match)
                })
            
            # Add investment indicators
            for match in investment_matches:
                indicators.append({
                    "name": "Investment",
                    "value": match,
                    "description": self._find_context_for_match(text, match)
                })
            
            # Add productivity indicators
            for match in productivity_matches:
                indicators.append({
                    "name": "Productivity Gain",
                    "value": match,
                    "description": self._find_context_for_match(text, match)
                })
            
            # Add ROI indicators
            for match in roi_matches:
                indicators.append({
                    "name": "Return on Investment",
                    "value": match,
                    "description": self._find_context_for_match(text, match)
                })
            
            # Extract sentences with monetary values and percentages
            for sent in doc.sents:
                sent_text = sent.text.strip()
                
                # Look for sentences with money and percentages that aren't already captured
                has_money = any(token.like_num and "$" in sent_text for token in sent)
                has_percent = any(token.like_num and "%" in sent_text for token in sent)
                
                if (has_money or has_percent) and "economic" in sent_text.lower():
                    # Extract the value
                    money_match = re.search(r'\$\d+(?:\.\d+)?\s+(?:billion|million|trillion)', sent_text)
                    percent_match = re.search(r'[-+]?\d+(?:\.\d+)?%', sent_text)
                    
                    if money_match and not any(money_match.group() in ind.get("value", "") for ind in indicators):
                        indicators.append({
                            "name": "Economic Value",
                            "value": money_match.group(),
                            "description": sent_text
                        })
                    
                    if percent_match and not any(percent_match.group() in ind.get("value", "") for ind in indicators):
                        indicators.append({
                            "name": "Economic Percentage",
                            "value": percent_match.group(),
                            "description": sent_text
                        })
            
            # Remove duplicates and limit to top 10
            unique_indicators = []
            seen_values = set()
            
            for indicator in indicators:
                value = indicator.get("value", "")
                if value and value not in seen_values:
                    seen_values.add(value)
                    unique_indicators.append(indicator)
            
            return unique_indicators[:10]
            
        except Exception as e:
            logger.error(f"Error extracting economic indicators: {str(e)}")
            return []
    
    def extract_ai_adoption_metrics(self, text: str) -> List[Dict[str, str]]:
        """
        Extract AI adoption metrics from the article text.
        
        Args:
            text: Article text to analyze
            
        Returns:
            List of dictionaries containing AI adoption metrics
        """
        metrics = []
        
        try:
            # Process the text with spaCy
            doc = self.nlp(text)
            
            # Define patterns for AI adoption metrics
            adoption_pattern = r'(?:AI|artificial intelligence|machine learning)\s+adoption\s+(?:rate|level)?\s+(?:of|at|by)?\s+([-+]?\d+(?:\.\d+)?%?)'
            implementation_pattern = r'(?:implemented|deployed|using|adopted)\s+(?:AI|artificial intelligence|machine learning).*?(\d+(?:\.\d+)?%?)\s+(?:of|in)'
            investment_pattern = r'(?:investment|spending)\s+(?:in|on)\s+(?:AI|artificial intelligence|machine learning).*?(\$?\d+(?:\.\d+)?\s+(?:billion|million|trillion))'
            efficiency_pattern = r'(?:efficiency|productivity)\s+(?:gain|increase|improvement).*?(?:AI|artificial intelligence|machine learning).*?([-+]?\d+(?:\.\d+)?%?)'
            cost_pattern = r'(?:cost|expense)\s+(?:reduction|saving|decrease).*?(?:AI|artificial intelligence|machine learning).*?([-+]?\d+(?:\.\d+)?%?)'
            
            # Search for patterns in the text
            adoption_matches = re.findall(adoption_pattern, text, re.IGNORECASE)
            implementation_matches = re.findall(implementation_pattern, text, re.IGNORECASE)
            investment_matches = re.findall(investment_pattern, text, re.IGNORECASE)
            efficiency_matches = re.findall(efficiency_pattern, text, re.IGNORECASE)
            cost_matches = re.findall(cost_pattern, text, re.IGNORECASE)
            
            # Add adoption rate metrics
            for match in adoption_matches:
                metrics.append({
                    "name": "AI Adoption Rate",
                    "value": match,
                    "description": self._find_context_for_match(text, match)
                })
            
            # Add implementation metrics
            for match in implementation_matches:
                metrics.append({
                    "name": "AI Implementation",
                    "value": match,
                    "description": self._find_context_for_match(text, match)
                })
            
            # Add investment metrics
            for match in investment_matches:
                metrics.append({
                    "name": "AI Investment",
                    "value": match,
                    "description": self._find_context_for_match(text, match)
                })
            
            # Add efficiency metrics
            for match in efficiency_matches:
                metrics.append({
                    "name": "AI Efficiency Gain",
                    "value": match,
                    "description": self._find_context_for_match(text, match)
                })
            
            # Add cost reduction metrics
            for match in cost_matches:
                metrics.append({
                    "name": "AI Cost Reduction",
                    "value": match,
                    "description": self._find_context_for_match(text, match)
                })
            
            # Extract sentences with AI terms and numerical values
            for sent in doc.sents:
                sent_text = sent.text.strip()
                sent_lower = sent_text.lower()
                
                # Check if sentence contains AI terms
                has_ai = any(term in sent_lower for term in ["ai", "artificial intelligence", "machine learning", "automation"])
                
                # Check if sentence contains numerical values
                has_numbers = any(token.like_num for token in sent)
                
                if has_ai and has_numbers and not any(match in sent_text for match in 
                                                     adoption_matches + implementation_matches + 
                                                     investment_matches + efficiency_matches + cost_matches):
                    # Extract the value
                    num_match = re.search(r'[-+]?\d+(?:\.\d+)?%?|\$\d+(?:\.\d+)?\s+(?:billion|million|trillion)', sent_text)
                    
                    if num_match and not any(num_match.group() in metric.get("value", "") for metric in metrics):
                        # Determine the type of metric
                        if "cost" in sent_lower or "saving" in sent_lower or "expense" in sent_lower:
                            metric_name = "AI Cost Impact"
                        elif "efficiency" in sent_lower or "productivity" in sent_lower:
                            metric_name = "AI Efficiency Impact"
                        elif "investment" in sent_lower or "spending" in sent_lower:
                            metric_name = "AI Investment"
                        elif "adoption" in sent_lower or "implement" in sent_lower or "deploy" in sent_lower:
                            metric_name = "AI Adoption Metric"
                        else:
                            metric_name = "AI Impact Metric"
                        
                        metrics.append({
                            "name": metric_name,
                            "value": num_match.group(),
                            "description": sent_text
                        })
            
            # Remove duplicates and limit to top 10
            unique_metrics = []
            seen_values = set()
            
            for metric in metrics:
                value = metric.get("value", "")
                if value and value not in seen_values:
                    seen_values.add(value)
                    unique_metrics.append(metric)
            
            return unique_metrics[:10]
            
        except Exception as e:
            logger.error(f"Error extracting AI adoption metrics: {str(e)}")
            return []
    
    def _find_context_for_match(self, text: str, match: str) -> str:
        """
        Find the surrounding context for a matched pattern.
        
        Args:
            text: Full text to search in
            match: The matched pattern to find context for
            
        Returns:
            A sentence or fragment containing the match
        """
        try:
            # Find the sentence containing the match
            sentences = sent_tokenize(text)
            
            for sentence in sentences:
                if match in sentence:
                    # If sentence is too long, extract a window around the match
                    if len(sentence) > 200:
                        match_pos = sentence.find(match)
                        start = max(0, match_pos - 100)
                        end = min(len(sentence), match_pos + len(match) + 100)
                        return sentence[start:end] + "..."
                    return sentence
            
            # If not found in any sentence, return empty string
            return ""
            
        except Exception as e:
            logger.debug(f"Error finding context: {str(e)}")
            return ""
