export interface AnalysisData {
  id: string
  timestamp: Date
  value: number
  category: string
  metadata?: Record<string, unknown>
}

export interface ExportOptions {
  format: 'pdf' | 'csv' | 'json' | 'xlsx'
  includeMetadata: boolean
  dateRange?: {
    start: Date
    end: Date
  }
}

export interface ChartConfig {
  title: string
  subtitle?: string
  dataKey: string
  type: 'line' | 'bar' | 'area' | 'pie' | 'scatter'
  responsive: boolean
}

export interface AppState {
  theme: 'light' | 'dark' | 'auto'
  language: string
  sidebarOpen: boolean
}

export interface AnalysisFilter {
  startDate?: Date
  endDate?: Date
  categories?: string[]
  minValue?: number
  maxValue?: number
}
