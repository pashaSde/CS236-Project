import type { StatsResponse } from '../types/api'
import './StatsPanel.css'

interface StatsPanelProps {
  stats: StatsResponse
}

const StatsPanel = ({ stats }: StatsPanelProps) => {
  if (!stats || !stats.statistics) return null

  const { statistics } = stats

  return (
    <div className="stats-panel">
      <h3>Dataset Statistics</h3>
      
      <div className="stats-grid">
        {/* Total Records */}
        <div className="stat-card">
          <div className="stat-content">
            <div className="stat-label">Total Records</div>
            <div className="stat-value">{stats.total_records.toLocaleString()}</div>
          </div>
        </div>

        {/* Average Price */}
        <div className="stat-card">
          <div className="stat-content">
            <div className="stat-label">Average Price</div>
            <div className="stat-value">
              ${statistics.price_statistics?.average?.toFixed(2) || 'N/A'}
            </div>
            {statistics.price_statistics?.minimum !== null && statistics.price_statistics?.minimum !== undefined &&
             statistics.price_statistics?.maximum !== null && statistics.price_statistics?.maximum !== undefined && (
              <div className="stat-subtitle">
                ${statistics.price_statistics.minimum.toFixed(2)} - ${statistics.price_statistics.maximum.toFixed(2)}
              </div>
            )}
          </div>
        </div>

        {/* Cancellation Rate */}
        <div className="stat-card">
          <div className="stat-content">
            <div className="stat-label">Cancellation Rate</div>
            <div className="stat-value">
              {statistics.cancellation_statistics?.cancellation_rate?.toFixed(1)}%
            </div>
            <div className="stat-subtitle">
              {statistics.cancellation_statistics?.canceled?.toLocaleString()} canceled / 
              {statistics.cancellation_statistics?.not_canceled?.toLocaleString()} confirmed
            </div>
          </div>
        </div>

        {/* Average Lead Time */}
        <div className="stat-card">
          <div className="stat-content">
            <div className="stat-label">Avg Lead Time</div>
            <div className="stat-value">
              {statistics.booking_statistics?.avg_lead_time?.toFixed(0) || 'N/A'} days
            </div>
          </div>
        </div>

        {/* Unique Hotels */}
        {(statistics.unique_hotels || 0) > 0 && (
          <div className="stat-card">
            <div className="stat-content">
              <div className="stat-label">Hotels</div>
              <div className="stat-value">{statistics.unique_hotels}</div>
            </div>
          </div>
        )}

        {/* Unique Countries */}
        {(statistics.unique_countries || 0) > 0 && (
          <div className="stat-card">
            <div className="stat-content">
              <div className="stat-label">Countries</div>
              <div className="stat-value">{statistics.unique_countries}</div>
            </div>
          </div>
        )}

        {/* Average Stay */}
        <div className="stat-card">
          <div className="stat-content">
            <div className="stat-label">Avg Stay</div>
            <div className="stat-value">
              {(
                (statistics.booking_statistics?.avg_weekend_nights || 0) +
                (statistics.booking_statistics?.avg_week_nights || 0)
              ).toFixed(1)} nights
            </div>
            <div className="stat-subtitle">
              {statistics.booking_statistics?.avg_weekend_nights?.toFixed(1)} weekend + 
              {statistics.booking_statistics?.avg_week_nights?.toFixed(1)} weekday
            </div>
          </div>
        </div>

        {/* Market Segments */}
        {(statistics.unique_market_segments || 0) > 0 && (
          <div className="stat-card">
            <div className="stat-content">
              <div className="stat-label">Market Segments</div>
              <div className="stat-value">{statistics.unique_market_segments}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default StatsPanel
