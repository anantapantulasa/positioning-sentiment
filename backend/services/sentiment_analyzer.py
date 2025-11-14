import os
from typing import List, Dict
from groq import Groq

class SentimentAnalyzer:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        # Use the cheapest model (llama-3.1-8b-instant)
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
    
    async def analyze_sentiment(self, articles: List[Dict]) -> Dict:
        """
        Analyze sentiment of news articles using Groq API.
        Returns: {'sentiment': 'bullish' or 'bearish', 'score': float}
        """
        if not articles:
            return {'sentiment': 'neutral', 'score': 0.0}
        
        # Combine article titles and summaries
        text_content = "\n".join([
            f"{article.get('title', '')} {article.get('summary', '')}"
            for article in articles[:10]  # Limit to 10 articles for API call
        ])
        
        prompt = f"""Analyze the sentiment of the following gold commodity news articles. 
Determine if the overall sentiment is bullish (positive for gold prices going up) or bearish (negative for gold prices going down).

News articles:
{text_content}

Respond with ONLY a JSON object in this exact format:
{{"sentiment": "bullish" or "bearish", "score": a number between -1 and 1 where -1 is very bearish and 1 is very bullish}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial sentiment analyst. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            sentiment = result.get('sentiment', 'neutral').lower()
            score = float(result.get('score', 0.0))
            
            # Normalize sentiment
            if sentiment not in ['bullish', 'bearish']:
                sentiment = 'bullish' if score > 0 else 'bearish' if score < 0 else 'neutral'
            
            return {
                'sentiment': sentiment,
                'score': score
            }
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            # Fallback: simple keyword-based sentiment
            return self._fallback_sentiment(articles)
    
    def _fallback_sentiment(self, articles: List[Dict]) -> Dict:
        """Fallback sentiment analysis using keyword matching"""
        bullish_keywords = ['up', 'rise', 'gain', 'surge', 'rally', 'increase', 'higher', 'positive', 'strong', 'boost']
        bearish_keywords = ['down', 'fall', 'drop', 'decline', 'lower', 'negative', 'weak', 'crash', 'plunge', 'loss']
        
        bullish_count = 0
        bearish_count = 0
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            bullish_count += sum(1 for keyword in bullish_keywords if keyword in text)
            bearish_count += sum(1 for keyword in bearish_keywords if keyword in text)
        
        if bullish_count > bearish_count:
            return {'sentiment': 'bullish', 'score': min(1.0, bullish_count / 10.0)}
        elif bearish_count > bullish_count:
            return {'sentiment': 'bearish', 'score': max(-1.0, -bearish_count / 10.0)}
        else:
            return {'sentiment': 'neutral', 'score': 0.0}

