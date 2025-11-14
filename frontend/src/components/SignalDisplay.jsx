import React, { useMemo } from 'react'
import { format } from 'date-fns'
import './SignalDisplay.css'

const SignalDisplay = ({ signal, loading, selectedDate, binarySignals }) => {
  if (loading) {
    return (
      <div className="signal-display">
        <h2>Trading Signal</h2>
        <div className="loading-signal">Analyzing signal for {selectedDate}...</div>
      </div>
    )
  }

  if (!signal) {
    return (
      <div className="signal-display">
        <h2>Trading Signal</h2>
        <div className="no-signal">No signal available for this date</div>
      </div>
    )
  }

  // Determine the actual signal to display based on new logic
  const displaySignal = useMemo(() => {
    if (!binarySignals || !signal) {
      // Fallback to original signal if we don't have binary signals
      return signal?.signal || 'hold'
    }

    // Check for news failure: price and sentiment disagree
    const newsFailure = 
      (signal.price_direction === 'up' && signal.news_sentiment === 'bearish') ||
      (signal.price_direction === 'down' && signal.news_sentiment === 'bullish') ||
      signal.price_direction === 'neutral' ||
      signal.news_count === 0 // No news is considered a failure

    // Get binary signal states (handle null as false)
    const hasLongBinary = binarySignals.long === true
    const hasShortBinary = binarySignals.short === true

    // Logic (in priority order):
    // 1. If both long and short → BUY (default, check this first)
    if (hasLongBinary && hasShortBinary) {
      return 'buy'
    }

    // 2. If news failure AND long binary → BUY
    if (newsFailure && hasLongBinary) {
      return 'buy'
    }

    // 3. If news failure AND short binary → SELL
    if (newsFailure && hasShortBinary) {
      return 'sell'
    }

    // 4. If no news failure → HOLD
    if (!newsFailure) {
      return 'hold'
    }

    // 5. If news failure but no long AND no short → HOLD
    if (newsFailure && !hasLongBinary && !hasShortBinary) {
      return 'hold'
    }

    // Default fallback
    return 'hold'
  }, [signal, binarySignals])

  const isBuy = displaySignal === 'buy'
  const isSell = displaySignal === 'sell'
  const isHold = displaySignal === 'hold'
  const signalClass = isBuy ? 'buy-signal' : isSell ? 'sell-signal' : 'hold-signal'

  return (
    <div className="signal-display">
      <h2>Trading Signal</h2>
      <div className={`signal-card ${signalClass}`}>
        <div className="signal-action">
          <span className="signal-icon">
            {isBuy ? '📈' : isSell ? '📉' : '⏸️'}
          </span>
          <span className="signal-text">
            {displaySignal.toUpperCase()}
          </span>
        </div>
        
        <div className="signal-date">
          {format(new Date(signal.date), 'MMM dd, yyyy')}
        </div>

        <div className="signal-details">
          <div className="detail-row">
            <span className="detail-label">Price:</span>
            <span className="detail-value">${signal.price?.toFixed(2)}</span>
          </div>
          
          <div className="detail-row">
            <span className="detail-label">Previous Price:</span>
            <span className="detail-value">${signal.previous_price?.toFixed(2)}</span>
          </div>
          
          <div className="detail-row">
            <span className="detail-label">Price Change:</span>
            <span className={`detail-value ${signal.price_change >= 0 ? 'positive' : 'negative'}`}>
              {signal.price_change >= 0 ? '+' : ''}{signal.price_change?.toFixed(2)}
            </span>
          </div>
          
          <div className="detail-row">
            <span className="detail-label">Price Direction:</span>
            <span className="detail-value">{signal.price_direction}</span>
          </div>
          
          <div className="detail-row">
            <span className="detail-label">News Sentiment:</span>
            <span className={`detail-value ${signal.news_sentiment === 'bullish' ? 'positive' : 'negative'}`}>
              {signal.news_sentiment}
            </span>
          </div>
          
          <div className="detail-row">
            <span className="detail-label">Sentiment Score:</span>
            <span className="detail-value">{signal.sentiment_score?.toFixed(2)}</span>
          </div>
          
          <div className="detail-row">
            <span className="detail-label">Articles Analyzed:</span>
            <span className="detail-value">{signal.news_count || 0}</span>
          </div>
          
          {signal.news_count === 0 && (
            <div className="detail-row warning">
              <span className="detail-label">⚠️ No news found for this date</span>
            </div>
          )}
        </div>

        <div className="signal-reason">
          <strong>Reason:</strong>
          <p>
            {isHold 
              ? (() => {
                  const newsFailure = 
                    (signal.price_direction === 'up' && signal.news_sentiment === 'bearish') ||
                    (signal.price_direction === 'down' && signal.news_sentiment === 'bullish') ||
                    signal.price_direction === 'neutral' ||
                    signal.news_count === 0
                  
                  const hasLongBinary = binarySignals?.long === true
                  const hasShortBinary = binarySignals?.short === true
                  
                  if (!newsFailure) {
                    return 'Hold: No news failure (price and sentiment agree)'
                  } else if (!hasLongBinary && !hasShortBinary) {
                    return 'Hold: News failure but no long or short binary signal'
                  } else {
                    return 'Hold: Unable to determine signal'
                  }
                })()
              : isBuy
              ? 'Buy: News failure detected and long binary signal is active'
              : 'Sell: News failure detected and short binary signal is active'}
          </p>
        </div>
      </div>
    </div>
  )
}

export default SignalDisplay

