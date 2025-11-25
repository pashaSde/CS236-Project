import axios, { AxiosInstance } from 'axios'
import type { Dataset, DataResponse, StatsResponse, HealthResponse, FilterParams } from '../types/api'

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: {
    indexes: null, // Send arrays as repeated query params: booking_status=Canceled&booking_status=Not_Canceled
  },
})

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

/**
 * Health check
 */
export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await api.get<HealthResponse>('/api/health')
  return response.data
}

/**
 * Get list of available datasets
 */
export const getDatasets = async (): Promise<Dataset[]> => {
  const response = await api.get<Dataset[]>('/api/datasets')
  return response.data
}

/**
 * Get data from a dataset with optional filters and pagination
 */
export const getData = async (dataset: string, params: FilterParams = {}): Promise<DataResponse> => {
  const response = await api.get<DataResponse>(`/api/data/${dataset}`, { params })
  return response.data
}

/**
 * Get statistics for a dataset
 */
export const getStats = async (dataset: string): Promise<StatsResponse> => {
  const response = await api.get<StatsResponse>(`/api/stats/${dataset}`)
  return response.data
}

/**
 * Build query params from filters
 */
export const buildFilterParams = (filters: Record<string, any>): FilterParams => {
  const params: FilterParams = {}
  
  Object.keys(filters).forEach(key => {
    const value = filters[key]
    if (value !== null && value !== undefined && value !== '') {
      // Handle arrays
      if (Array.isArray(value) && value.length > 0) {
        params[key as keyof FilterParams] = value as any
      }
      // Handle single values
      else if (!Array.isArray(value)) {
        params[key as keyof FilterParams] = value
      }
    }
  })
  
  return params
}

export default api

