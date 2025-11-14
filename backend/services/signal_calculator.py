from typing import Dict

class SignalCalculator:
    """
    Calculates trading signals based on price direction and news sentiment.
    
    Logic:
    - Price up + News bullish = Bullish (BUY)
    - Price down + News bearish = Bearish (SELL)
    - Price up + News bearish = Reversal (BUY - price going up despite bearish news)
    - Price down + News bullish = Reversal (SELL - price going down despite bullish news)
    """
    
    def calculate_signal(self, price_direction: str, news_sentiment: str) -> Dict:
        """
        Calculate trading signal based on price direction and news sentiment.
        
        Args:
            price_direction: 'up', 'down', or 'neutral'
            news_sentiment: 'bullish' or 'bearish'
        
        Returns:
            Dict with 'action' ('buy' or 'sell') and 'reason'
        """
        price_direction = price_direction.lower()
        news_sentiment = news_sentiment.lower()
        
        # Agreement cases
        if price_direction == 'up' and news_sentiment == 'bullish':
            return {
                'action': 'buy',
                'reason': 'Price increased and news sentiment is bullish - strong bullish signal'
            }
        
        if price_direction == 'down' and news_sentiment == 'bearish':
            return {
                'action': 'sell',
                'reason': 'Price decreased and news sentiment is bearish - strong bearish signal'
            }
        
        # Disagreement cases (reversals)
        if price_direction == 'up' and news_sentiment == 'bearish':
            return {
                'action': 'buy',
                'reason': 'Reversal signal: Price increased despite bearish news - potential bullish reversal'
            }
        
        if price_direction == 'down' and news_sentiment == 'bullish':
            return {
                'action': 'sell',
                'reason': 'Reversal signal: Price decreased despite bullish news - potential bearish reversal'
            }
        
        # Neutral cases
        if price_direction == 'neutral':
            if news_sentiment == 'bullish':
                return {
                    'action': 'buy',
                    'reason': 'Neutral price but bullish news sentiment'
                }
            elif news_sentiment == 'bearish':
                return {
                    'action': 'sell',
                    'reason': 'Neutral price but bearish news sentiment'
                }
        
        # Default fallback
        return {
            'action': 'hold',
            'reason': 'Insufficient data to determine signal'
        }

