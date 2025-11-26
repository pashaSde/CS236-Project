import React, { useState } from 'react'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
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
    arrival_date_from: '',
    arrival_date_to: '',
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

  const handleNumberKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Allow: backspace, delete, tab, escape, enter, decimal point
    // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+Z (common shortcuts)
    // Allow: Arrow keys, Home, End
    if (
      ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', '.', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(e.key) ||
      (e.ctrlKey && ['a', 'c', 'v', 'x', 'z'].includes(e.key.toLowerCase())) ||
      (e.metaKey && ['a', 'c', 'v', 'x', 'z'].includes(e.key.toLowerCase()))
    ) {
      return
    }
    // Allow numbers 0-9
    if (e.key >= '0' && e.key <= '9') {
      return
    }
    // Prevent everything else (including letters, special chars)
    e.preventDefault()
  }

  const handleNumberInput = (e: React.ChangeEvent<HTMLInputElement>, field: keyof Filters) => {
    const value = e.target.value
    // Only allow numbers and decimal point, remove any other characters
    const numericValue = value.replace(/[^0-9.]/g, '')
    // Prevent multiple decimal points
    const parts = numericValue.split('.')
    const sanitizedValue = parts.length > 2 ? parts[0] + '.' + parts.slice(1).join('') : numericValue
    handleInputChange(field, sanitizedValue)
  }

  const handleDatePickerKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Allow: backspace, delete, tab, escape, enter
    // Allow: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+Z (common shortcuts)
    // Allow: Arrow keys, Home, End
    if (
      ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(e.key) ||
      (e.ctrlKey && ['a', 'c', 'v', 'x', 'z'].includes(e.key.toLowerCase())) ||
      (e.metaKey && ['a', 'c', 'v', 'x', 'z'].includes(e.key.toLowerCase()))
    ) {
      return
    }
    // Allow numbers 0-9
    if (e.key >= '0' && e.key <= '9') {
      return
    }
    // Allow space, dash, slash for date formatting
    if ([' ', '-', '/'].includes(e.key)) {
      return
    }
    // Prevent everything else (including letters)
    e.preventDefault()
  }

  // Custom input component for DatePicker to prevent alphabetic input
  const DatePickerInput = React.forwardRef<HTMLInputElement, any>(({ value, onClick, onChange, placeholder }, ref) => {
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      // Only allow numbers, spaces, dashes, and slashes
      const sanitized = e.target.value.replace(/[^0-9\s\-/]/g, '')
      if (onChange) {
        onChange({ target: { value: sanitized } })
      }
    }

    return (
      <input
        ref={ref}
        type="text"
        value={value}
        onClick={onClick}
        onChange={handleInputChange}
        onKeyDown={handleDatePickerKeyDown}
        placeholder={placeholder}
        className="date-picker-input"
        readOnly={false}
      />
    )
  })

  DatePickerInput.displayName = 'DatePickerInput'

  const handleApplyFilters = () => {
    // Convert empty strings to null and filter out empty arrays
    const cleanFilters: Filters = {}
    const allMarketSegments = ['Online', 'Offline', 'Online TA', 'Online TO', 'Corporate', 'Aviation', 'Complementary']
    
    Object.keys(localFilters).forEach(key => {
      const typedKey = key as keyof Filters
      const value = localFilters[typedKey]
      
      // Special handling for market_segment: if all or none selected, don't filter
      if (typedKey === 'market_segment' && Array.isArray(value)) {
        const selectedCount = value.length
        // If all segments selected or none selected, don't apply filter (show all)
        if (selectedCount === 0 || selectedCount === allMarketSegments.length) {
          // Don't add to cleanFilters - means show all
          return
        }
        // Otherwise, apply the filter with selected segments
        cleanFilters[typedKey] = value as any
        return
      }
      
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
      arrival_date_from: '',
      arrival_date_to: '',
      market_segment: [],
      hotel: [],
      country: [],
    })
    onFilterChange({})
  }

  const handleCheckboxChange = (field: keyof Filters, value: string) => {
    setLocalFilters(prev => {
      const currentValues = (prev[field] as string[]) || []
      
      // Special handling for market_segment "Select All"
      if (field === 'market_segment' && value === 'All') {
        const allMarketSegments = ['Online', 'Offline', 'Online TA', 'Online TO', 'Corporate', 'Aviation', 'Complementary']
        const allSelected = currentValues.length === allMarketSegments.length
        // If all selected, deselect all. Otherwise, select all
        return {
          ...prev,
          [field]: allSelected ? [] : allMarketSegments
        }
      }
      
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
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '8px' }}>
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          Filters 
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
            {/* Row 1: Price Range | Booking Status */}
            {/* Price Filters */}
            <div className="filter-group">
              <label>Price Range</label>
              <div className="range-inputs">
                <input
                  type="text"
                  inputMode="numeric"
                  placeholder="Min Price"
                  value={localFilters.min_price}
                  onChange={(e) => handleNumberInput(e, 'min_price')}
                  onKeyDown={handleNumberKeyDown}
                  min="0"
                />
                <span>to</span>
                <input
                  type="text"
                  inputMode="numeric"
                  placeholder="Max Price"
                  value={localFilters.max_price}
                  onChange={(e) => handleNumberInput(e, 'max_price')}
                  onKeyDown={handleNumberKeyDown}
                  min="0"
                />
              </div>
            </div>

            {/* Booking Status */}
            <div className="filter-group">
              <label>Booking Status</label>
              <div className="checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="radio"
                    name="booking_status"
                    checked={!localFilters.booking_status || localFilters.booking_status.length === 0}
                    onChange={() => {
                      handleInputChange('booking_status', [])
                    }}
                  />
                  All
                </label>
                <label className="checkbox-label">
                  <input
                    type="radio"
                    name="booking_status"
                    checked={localFilters.booking_status?.includes('Canceled') || false}
                    onChange={() => {
                      handleInputChange('booking_status', ['Canceled'])
                    }}
                  />
                  Canceled
                </label>
                <label className="checkbox-label">
                  <input
                    type="radio"
                    name="booking_status"
                    checked={localFilters.booking_status?.includes('Not_Canceled') || false}
                    onChange={() => {
                      handleInputChange('booking_status', ['Not_Canceled'])
                    }}
                  />
                  Not Canceled
                </label>
              </div>
            </div>

            {/* Row 2: Arrival Date Range | Market Segment */}
            {/* Arrival Date Range */}
            <div className="filter-group">
              <label>Arrival Date</label>
              <div className="date-range-inputs">
                <div className="date-picker-group">
                  <label className="date-label">From</label>
                  <DatePicker
                    selected={localFilters.arrival_date_from ? new Date(localFilters.arrival_date_from + '-01') : null}
                    onChange={(date: Date | null) => {
                      if (date) {
                        const year = date.getFullYear()
                        const month = String(date.getMonth() + 1).padStart(2, '0')
                        handleInputChange('arrival_date_from', `${year}-${month}`)
                      } else {
                        handleInputChange('arrival_date_from', '')
                      }
                    }}
                    dateFormat="MMM yyyy"
                    showMonthYearPicker
                    placeholderText="Select month"
                    minDate={new Date('2015-01-01')}
                    maxDate={new Date('2019-12-31')}
                    wrapperClassName="date-picker-wrapper"
                    isClearable
                    strictParsing
                    customInput={<DatePickerInput />}
                  />
                </div>
                <span className="date-separator">to</span>
                <div className="date-picker-group">
                  <label className="date-label">To</label>
                  <DatePicker
                    selected={localFilters.arrival_date_to ? new Date(localFilters.arrival_date_to + '-01') : null}
                    onChange={(date: Date | null) => {
                      if (date) {
                        const year = date.getFullYear()
                        const month = String(date.getMonth() + 1).padStart(2, '0')
                        handleInputChange('arrival_date_to', `${year}-${month}`)
                      } else {
                        handleInputChange('arrival_date_to', '')
                      }
                    }}
                    dateFormat="MMM yyyy"
                    showMonthYearPicker
                    placeholderText="Select month"
                    minDate={localFilters.arrival_date_from ? new Date(localFilters.arrival_date_from + '-01') : new Date('2015-01-01')}
                    maxDate={new Date('2019-12-31')}
                    wrapperClassName="date-picker-wrapper"
                    isClearable
                    strictParsing
                    customInput={<DatePickerInput />}
                  />
                </div>
              </div>
            </div>

            {/* Market Segment */}
            <div className="filter-group">
              <label>Market Segment</label>
              <div className="checkbox-group checkbox-group-two-column">
                <label className="checkbox-label" style={{ gridColumn: '1 / -1', fontWeight: 600, borderBottom: '1px solid #e0e0e0', paddingBottom: '8px', marginBottom: '4px' }}>
                  <input
                    type="checkbox"
                    checked={
                      (!localFilters.market_segment || localFilters.market_segment.length === 0) ||
                      localFilters.market_segment.length === 7
                    }
                    onChange={() => handleCheckboxChange('market_segment', 'All')}
                  />
                  All
                </label>
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
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '6px', verticalAlign: 'middle' }}>
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              Apply Filters
            </button>
            <button className="clear-btn" onClick={handleClearFilters}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '6px', verticalAlign: 'middle' }}>
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
              Clear All
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default FilterPanel
