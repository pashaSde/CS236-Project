import axios, { AxiosInstance } from 'axios'
import type { Dataset, DataResponse, StatsResponse, HealthResponse, FilterParams } from '../types/api'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: {
    indexes: null,
  },
})

api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await api.get<HealthResponse>('/api/health')
  return response.data
}

export const getDatasets = async (): Promise<Dataset[]> => {
  const response = await api.get<Dataset[]>('/api/datasets')
  return response.data
}

export const getData = async (dataset: string, params: FilterParams = {}): Promise<DataResponse> => {
  const response = await api.get<DataResponse>(`/api/data/${dataset}`, { params })
  return response.data
}

export const getStats = async (dataset: string): Promise<StatsResponse> => {
  const response = await api.get<StatsResponse>(`/api/stats/${dataset}`)
  return response.data
}

export const buildFilterParams = (filters: Record<string, any>): FilterParams => {
  /**
   * Converts frontend filter state to API-compatible filter parameters.
   * Filters out empty values and ensures arrays are non-empty.
   */
  const params: FilterParams = {}
  
  Object.keys(filters).forEach(key => {
    const value = filters[key]
    if (value !== null && value !== undefined && value !== '') {
      if (Array.isArray(value) && value.length > 0) {
        params[key as keyof FilterParams] = value as any
      } else if (!Array.isArray(value)) {
        params[key as keyof FilterParams] = value
      }
    }
  })
  
  return params
}

export default api

