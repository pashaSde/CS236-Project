/**
 * API Type Definitions
 */

export interface Dataset {
  name: string
  display_name: string
  row_count: number
  column_count: number
  columns: ColumnInfo[]
}

export interface ColumnInfo {
  name: string
  type: string
  nullable: boolean
}

export interface DataResponse {
  dataset: string
  total_records: number
  page: number
  page_size: number
  total_pages: number
  data: Record<string, any>[]
  filters_applied: Record<string, any>
}

export interface StatsResponse {
  dataset: string
  total_records: number
  statistics: Statistics
}

export interface Statistics {
  total_records: number
  unique_hotels?: number
  unique_countries?: number
  unique_market_segments?: number
  price_statistics: PriceStatistics
  booking_statistics: BookingStatistics
  cancellation_statistics: CancellationStatistics
}

export interface PriceStatistics {
  average: number | null
  minimum: number | null
  maximum: number | null
}

export interface BookingStatistics {
  avg_lead_time: number | null
  avg_weekend_nights: number | null
  avg_week_nights: number | null
}

export interface CancellationStatistics {
  canceled: number
  not_canceled: number
  cancellation_rate: number
}

export interface HealthResponse {
  status: string
  database_connected: boolean
  available_datasets: string[]
  timestamp: string
}

export interface FilterParams {
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  min_price?: number
  max_price?: number
  booking_status?: string[]
  arrival_year?: number
  arrival_month?: number
  arrival_date_from?: string
  arrival_date_to?: string
  market_segment?: string[]
  hotel?: string[]
  country?: string[]
  min_lead_time?: number
  max_lead_time?: number
  min_weekend_nights?: number
  max_weekend_nights?: number
  min_week_nights?: number
  max_week_nights?: number
}

export interface Filters {
  min_price?: string
  max_price?: string
  booking_status?: string[]
  arrival_year?: string
  arrival_month?: string
  arrival_date_from?: string
  arrival_date_to?: string
  market_segment?: string[]
  hotel?: string[]
  country?: string[]
}

