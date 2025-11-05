import { useState } from 'react'
import type { Dataset, Filters } from '../types/api'
import './FilterPanel.css'

interface FilterPanelProps {
  dataset: Dataset | null
  filters: Filters
  onFilterChange: (filters: Filters) => void
}

const FilterPanel = ({ dataset, filters, onFilterChange }: FilterPanelProps) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(false)
  const [localFilters, setLocalFilters] = useState<Filters>({
    min_price: '',
    max_price: '',
    booking_status: [],
    arrival_year: '',
    arrival_month: '',
    market_segment: [],
    hotel: [],
    country: [],
  })

  const handleInputChange = (field: keyof Filters, value: string | string[]) => {
    setLocalFilters(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleApplyFilters = () => {
    // Convert empty strings to null and filter out empty arrays
    const cleanFilters: Filters = {}
    Object.keys(localFilters).forEach(key => {
      const typedKey = key as keyof Filters
      const value = localFilters[typedKey]
      if (value !== '' && value !== null && value !== undefined) {
        if (Array.isArray(value) && value.length > 0) {
          cleanFilters[typedKey] = value as any
        } else if (!Array.isArray(value)) {
          cleanFilters[typedKey] = value as any
        }
      }
    })
    onFilterChange(cleanFilters)
  }

  const handleClearFilters = () => {
    setLocalFilters({
      min_price: '',
      max_price: '',
      booking_status: [],
      arrival_year: '',
      arrival_month: '',
      market_segment: [],
      hotel: [],
      country: [],
    })
    onFilterChange({})
  }

  const handleCheckboxChange = (field: keyof Filters, value: string) => {
    setLocalFilters(prev => {
      const currentValues = (prev[field] as string[]) || []
      const newValues = currentValues.includes(value)
        ? currentValues.filter(v => v !== value)
        : [...currentValues, value]
      return {
        ...prev,
        [field]: newValues
      }
    })
  }

  const activeFilterCount = Object.values(filters).filter(v => 
    v !== null && v !== undefined && v !== '' && (!Array.isArray(v) || v.length > 0)
  ).length

  return (
    <div className="filter-panel">
      <div className="filter-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h3>
          🔍 Filters 
          {activeFilterCount > 0 && (
            <span className="filter-badge">{activeFilterCount} active</span>
          )}
        </h3>
        <button className="toggle-btn">
          {isExpanded ? '▲ Collapse' : '▼ Expand'}
        </button>
      </div>

      {isExpanded && (
        <div className="filter-content">
          <div className="filter-grid">
            {/* Price Filters */}
            <div className="filter-group">
              <label>Price Range</label>
              <div className="range-inputs">
                <input
                  type="number"
                  placeholder="Min Price"
                  value={localFilters.min_price}
                  onChange={(e) => handleInputChange('min_price', e.target.value)}
                  min="0"
                  step="10"
                />
                <span>to</span>
                <input
                  type="number"
                  placeholder="Max Price"
                  value={localFilters.max_price}
                  onChange={(e) => handleInputChange('max_price', e.target.value)}
                  min="0"
                  step="10"
                />
              </div>
            </div>

            {/* Booking Status */}
            <div className="filter-group">
              <label>Booking Status</label>
              <div className="checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={localFilters.booking_status?.includes('Not_Canceled') || 
                             localFilters.booking_status?.includes('false') || false}
                    onChange={() => {
                      handleCheckboxChange('booking_status', 'Not_Canceled')
                      handleCheckboxChange('booking_status', 'false')
                    }}
                  />
                  Not Canceled
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={localFilters.booking_status?.includes('Canceled') ||
                             localFilters.booking_status?.includes('true') || false}
                    onChange={() => {
                      handleCheckboxChange('booking_status', 'Canceled')
                      handleCheckboxChange('booking_status', 'true')
                    }}
                  />
                  Canceled
                </label>
              </div>
            </div>

            {/* Arrival Year */}
            <div className="filter-group">
              <label>Arrival Year</label>
              <select
                value={localFilters.arrival_year}
                onChange={(e) => handleInputChange('arrival_year', e.target.value)}
              >
                <option value="">All Years</option>
                <option value="2015">2015</option>
                <option value="2016">2016</option>
                <option value="2017">2017</option>
                <option value="2018">2018</option>
                <option value="2019">2019</option>
              </select>
            </div>

            {/* Arrival Month */}
            <div className="filter-group">
              <label>Arrival Month</label>
              <select
                value={localFilters.arrival_month}
                onChange={(e) => handleInputChange('arrival_month', e.target.value)}
              >
                <option value="">All Months</option>
                {Array.from({ length: 12 }, (_, i) => i + 1).map(month => (
                  <option key={month} value={month.toString()}>
                    {new Date(2000, month - 1).toLocaleString('default', { month: 'long' })}
                  </option>
                ))}
              </select>
            </div>

            {/* Market Segment */}
            <div className="filter-group">
              <label>Market Segment</label>
              <div className="checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={localFilters.market_segment?.includes('Online') || false}
                    onChange={() => handleCheckboxChange('market_segment', 'Online')}
                  />
                  Online
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={localFilters.market_segment?.includes('Offline') || false}
                    onChange={() => handleCheckboxChange('market_segment', 'Offline')}
                  />
                  Offline
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={localFilters.market_segment?.includes('Online TA') || false}
                    onChange={() => handleCheckboxChange('market_segment', 'Online TA')}
                  />
                  Online TA (Travel Agents)
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={localFilters.market_segment?.includes('Online TO') || false}
                    onChange={() => handleCheckboxChange('market_segment', 'Online TO')}
                  />
                  Online TO (Tour Operators)
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={localFilters.market_segment?.includes('Corporate') || false}
                    onChange={() => handleCheckboxChange('market_segment', 'Corporate')}
                  />
                  Corporate
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={localFilters.market_segment?.includes('Aviation') || false}
                    onChange={() => handleCheckboxChange('market_segment', 'Aviation')}
                  />
                  Aviation
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={localFilters.market_segment?.includes('Complementary') || false}
                    onChange={() => handleCheckboxChange('market_segment', 'Complementary')}
                  />
                  Complementary
                </label>
              </div>
            </div>
          </div>

          <div className="filter-actions">
            <button className="apply-btn" onClick={handleApplyFilters}>
              ✓ Apply Filters
            </button>
            <button className="clear-btn" onClick={handleClearFilters}>
              ✕ Clear All
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default FilterPanel

