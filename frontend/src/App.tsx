import { useState, useEffect } from 'react'
import DataGrid from './components/DataGrid'
import FilterPanel from './components/FilterPanel'
import StatsPanel from './components/StatsPanel'
import { getDatasets, getStats } from './api/client'
import type { Dataset, StatsResponse, Filters } from './types/api'
import './App.css'

function App() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null)
  const [stats, setStats] = useState<StatsResponse | null>(null)
  const [filters, setFilters] = useState<Filters>({})
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Load available datasets on mount
  useEffect(() => {
    loadDatasets()
  }, [])

  // Load stats when dataset changes
  useEffect(() => {
    if (selectedDataset) {
      loadStats(selectedDataset.name)
    }
  }, [selectedDataset])

  const loadDatasets = async () => {
    try {
      setLoading(true)
      const data = await getDatasets()
      setDatasets(data)
      if (data.length > 0) {
        setSelectedDataset(data[0])
      }
      setError(null)
    } catch (err) {
      setError('Failed to load datasets: ' + (err as Error).message)
      console.error('Error loading datasets:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async (datasetName: string) => {
    try {
      const data = await getStats(datasetName)
      setStats(data)
    } catch (err) {
      console.error('Error loading stats:', err)
    }
  }

  const handleDatasetChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const dataset = datasets.find(d => d.name === event.target.value)
    setSelectedDataset(dataset || null)
    setFilters({}) // Reset filters when changing dataset
  }

  const handleFilterChange = (newFilters: Filters) => {
    setFilters(newFilters)
  }

  if (loading) {
    return (
      <div className="app">
        <div className="loading">Loading datasets...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app">
        <div className="error">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={loadDatasets}>Retry</button>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🏨 Hotel Reservations Data Viewer</h1>
        <p>Interactive data exploration with filtering and analysis</p>
      </header>

      <div className="dataset-selector">
        <label htmlFor="dataset-select">
          <strong>Select Dataset:</strong>
        </label>
        <select 
          id="dataset-select"
          value={selectedDataset?.name ?? ''} 
          onChange={handleDatasetChange}
        >
          {datasets.map(dataset => (
            <option key={dataset.name} value={dataset.name}>
              {dataset.display_name} ({dataset.row_count.toLocaleString()} rows)
            </option>
          ))}
        </select>
      </div>

      {stats && <StatsPanel stats={stats} />}

      <FilterPanel
        dataset={selectedDataset}
        filters={filters}
        onFilterChange={handleFilterChange}
      />

      {selectedDataset && (
        <DataGrid
          dataset={selectedDataset}
          filters={filters}
        />
      )}

      <footer className="app-footer">
        <p>CS236 Project - Hotel Reservations Analysis</p>
      </footer>
    </div>
  )
}

export default App

