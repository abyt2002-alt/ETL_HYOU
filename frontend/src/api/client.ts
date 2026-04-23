import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface SourceConfig {
  source_name: string
  sheet_tab_name: string
  target_table_name: string
  required_columns: string[]
  optional_columns: string[]
  field_types: Record<string, string>
  date_fields: string[]
  numeric_fields: string[]
  load_mode: string
}

export interface IngestionRun {
  id: number
  trigger_type: string
  status: string
  started_at: string
  completed_at: string | null
  triggered_by: string
  summary_message: string | null
}

export interface IngestionRunItem {
  id: number
  run_id: number
  source_name: string
  sheet_tab_name: string
  target_table_name: string
  status: string
  rows_read: number
  rows_loaded: number
  rows_failed: number
  started_at: string
  completed_at: string | null
  error_message: string | null
}

export interface RunDetail {
  run: IngestionRun
  items: IngestionRunItem[]
}

export const api = {
  getSources: () => apiClient.get<SourceConfig[]>('/sources'),
  runAllSources: (triggeredBy: string = 'user') => 
    apiClient.post<IngestionRun>('/ingest/all', { triggered_by: triggeredBy }),
  runSingleSource: (sourceName: string, triggeredBy: string = 'user') => 
    apiClient.post<IngestionRun>(`/ingest/${sourceName}`, { triggered_by: triggeredBy }),
  getLatestRun: () => apiClient.get<RunDetail>('/runs/latest'),
  getRunHistory: (limit: number = 50) => apiClient.get<IngestionRun[]>(`/runs?limit=${limit}`),
  getRunDetail: (runId: number) => apiClient.get<RunDetail>(`/runs/${runId}`),
  previewData: (tableName: string, limit: number = 100) => 
    apiClient.get(`/data/${tableName}?limit=${limit}`),
}
