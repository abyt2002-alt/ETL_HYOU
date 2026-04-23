import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api, SourceConfig } from '../api/client'

export default function Sources() {
  const [sources, setSources] = useState<SourceConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [runningSource, setRunningSource] = useState<string | null>(null)

  useEffect(() => {
    loadSources()
  }, [])

  const loadSources = async () => {
    try {
      const response = await api.getSources()
      setSources(response.data)
    } catch (error) {
      console.error('Failed to load sources:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRunSource = async (sourceName: string) => {
    setRunningSource(sourceName)
    try {
      await api.runSingleSource(sourceName)
      setTimeout(() => setRunningSource(null), 2000)
    } catch (error) {
      console.error('Failed to run source:', error)
      setRunningSource(null)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading sources...</div>
  }

  return (
    <div className="px-4 sm:px-0">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Data Sources</h2>
      
      <div className="grid gap-6">
        {sources.map((source) => (
          <div key={source.source_name} className="bg-white shadow rounded-lg p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{source.source_name}</h3>
                <p className="text-sm text-gray-500">Sheet: {source.sheet_tab_name}</p>
                <p className="text-sm text-gray-500">Table: {source.target_table_name}</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleRunSource(source.source_name)}
                  disabled={runningSource === source.source_name}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {runningSource === source.source_name ? 'Running...' : 'Run'}
                </button>
                <Link
                  to={`/data/${source.target_table_name}`}
                  className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300"
                >
                  Preview
                </Link>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="font-medium text-gray-700 mb-1">Required Columns</p>
                <ul className="list-disc list-inside text-gray-600">
                  {source.required_columns.map((col) => (
                    <li key={col}>{col}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="font-medium text-gray-700 mb-1">Field Types</p>
                <div className="text-gray-600">
                  {Object.entries(source.field_types).map(([field, type]) => (
                    <div key={field} className="flex justify-between">
                      <span>{field}:</span>
                      <span className="text-gray-500">{type}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
