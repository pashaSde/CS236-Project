import { useState, useEffect, useMemo, useCallback } from 'react'
import { AgGridReact } from 'ag-grid-react'
import { ColDef } from 'ag-grid-community'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import { getData, buildFilterParams } from '../api/client'
import type { Dataset, Filters } from '../types/api'
import './DataGrid.css'

interface DataGridProps {
  dataset: Dataset
  filters: Filters
}

const DataGrid = ({ dataset, filters }: DataGridProps) => {
  const [rowData, setRowData] = useState<Record<string, any>[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [totalRecords, setTotalRecords] = useState<number>(0)
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [pageSize, setPageSize] = useState<number>(100)

  const columnDefs = useMemo<ColDef[]>(() => {
    if (!dataset || !dataset.columns) return []
    
    return dataset.columns.map(col => ({
      field: col.name,
      headerName: col.name.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' '),
      filter: true,
      sortable: true,
      resizable: true,
      width: col.name === 'id' ? 150 : 
             col.name === 'email' ? 200 :
             col.name.includes('price') ? 120 : 
             150,
      valueFormatter: col.type === 'double precision' || col.type === 'numeric' ? 
        (params) => params.value !== null && params.value !== undefined ? 
          Number(params.value).toFixed(2) : '' : 
        undefined,
    }))
  }, [dataset])

  const defaultColDef = useMemo<ColDef>(() => ({
    sortable: true,
    filter: true,
    resizable: true,
    minWidth: 100,
  }), [])

  const loadData = useCallback(async () => {
    if (!dataset) return

    try {
      setLoading(true)
      setError(null)

      const params = {
        page: currentPage,
        page_size: pageSize,
        ...buildFilterParams(filters),
      }

      const response = await getData(dataset.name, params)
      setRowData(response.data)
      setTotalRecords(response.total_records)
    } catch (err) {
      setError('Failed to load data: ' + (err as Error).message)
      console.error('Error loading data:', err)
    } finally {
      setLoading(false)
    }
  }, [dataset, filters, currentPage, pageSize])

  useEffect(() => {
    loadData()
  }, [loadData])

  useEffect(() => {
    setCurrentPage(1)
  }, [filters])

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage)
  }

  const handlePageSizeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setPageSize(Number(event.target.value))
    setCurrentPage(1)
  }

  const totalPages = Math.ceil(totalRecords / pageSize)

  if (error) {
    return (
      <div className="data-grid-container">
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      </div>
    )
  }

  return (
    <div className="data-grid-container">
      <div className="data-grid-header">
        <div className="data-info">
          <h3>{dataset.display_name}</h3>
          <p>
            Showing {rowData.length} of {totalRecords.toLocaleString()} records
            {Object.keys(filters).length > 0 && ' (filtered)'}
          </p>
        </div>

        <div className="pagination-controls">
          <label>
            Rows per page:
            <select value={pageSize} onChange={handlePageSizeChange}>
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="250">250</option>
              <option value="500">500</option>
              <option value="1000">1000</option>
            </select>
          </label>

          <div className="page-controls">
            <button 
              onClick={() => handlePageChange(1)} 
              disabled={currentPage === 1 || loading}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '4px', verticalAlign: 'middle' }}>
                <polyline points="11 17 6 12 11 7"></polyline>
                <polyline points="18 17 13 12 18 7"></polyline>
              </svg>
              First
            </button>
            <button 
              onClick={() => handlePageChange(currentPage - 1)} 
              disabled={currentPage === 1 || loading}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '4px', verticalAlign: 'middle' }}>
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
              Prev
            </button>
            
            <span className="page-indicator">
              Page {currentPage} of {totalPages}
            </span>

            <button 
              onClick={() => handlePageChange(currentPage + 1)} 
              disabled={currentPage >= totalPages || loading}
            >
              Next
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginLeft: '4px', verticalAlign: 'middle' }}>
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>
            <button 
              onClick={() => handlePageChange(totalPages)} 
              disabled={currentPage >= totalPages || loading}
            >
              Last
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginLeft: '4px', verticalAlign: 'middle' }}>
                <polyline points="13 17 18 12 13 7"></polyline>
                <polyline points="6 17 11 12 6 7"></polyline>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div className="ag-theme-alpine" style={{ height: 600, width: '100%' }}>
        <AgGridReact
          rowData={rowData}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          loading={loading}
          animateRows={true}
          pagination={false}
          enableCellTextSelection={true}
          suppressRowClickSelection={true}
        />
      </div>

      {loading && (
        <div className="loading-overlay">
          <div className="spinner">Loading...</div>
        </div>
      )}
    </div>
  )
}

export default DataGrid
