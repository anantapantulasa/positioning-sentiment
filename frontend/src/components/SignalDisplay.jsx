import React from 'react'
import { format } from 'date-fns'
import './SignalDisplay.css'

const SignalDisplay = ({ signal, loading, selectedDate }) => {
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

  const isBuy = signal.signal === 'buy'
  const isSell = signal.signal === 'sell'
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
            {signal.signal.toUpperCase()}
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
          <p>{signal.reason}</p>
        </div>
      </div>
    </div>
  )
}

export default SignalDisplay

