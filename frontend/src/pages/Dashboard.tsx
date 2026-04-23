import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api, RunDetail } from '../api/client'

export default function Dashboard() {
  const [latestRun, setLatestRun] = useState<RunDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [running, setRunning] = useState(false)

  useEffect(() => {
    loadLatestRun()
  }, [])

  const loadLatestRun = async () => {
    try {
      const response = await api.getLatestRun()
      setLatestRun(response.data)
    } catch (error) {
      console.error('Failed to load latest run:', error)
    }
  }

  const handleRunAll = async () => {
    setRunning(true)
    try {
      await api.runAllSources()
      setTimeout(() => {
        loadLatestRun()
        setRunning(false)
      }, 2000)
    } catch (error) {
      console.error('Failed to run ingestion:', error)
      setRunning(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'partial': return 'bg-yellow-100 text-yellow-800'
      case 'running': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <button
          onClick={handleRunAll}
          disabled={running}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {running ? 'Running...' : 'Run All Sources'}
        </button>
      </div>

      {latestRun && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Latest Run</h3>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-500">Run ID</p>
              <p className="text-lg font-medium">{latestRun.run.id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Status</p>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(latestRun.run.status)}`}>
                {latestRun.run.status}
              </span>
            </div>
            <div>
              <p className="text-sm text-gray-500">Started</p>
              <p className="text-sm">{new Date(latestRun.run.started_at).toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Completed</p>
              <p className="text-sm">
                {latestRun.run.completed_at ? new Date(latestRun.run.completed_at).toLocaleString() : 'In progress'}
              </p>
            </div>
          </div>
          <Link to={`/runs/${latestRun.run.id}`} className="text-blue-600 hover:text-blue-800 text-sm">
            View Details →
          </Link>
        </div>
      )}

      {latestRun && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Source Status</h3>
          <div className="space-y-3">
            {latestRun.items.map((item) => (
              <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex-1">
                  <p className="font-medium">{item.source_name}</p>
                  <p className="text-sm text-gray-500">
                    {item.rows_loaded} rows loaded
                    {item.rows_failed > 0 && `, ${item.rows_failed} failed`}
                  </p>
                </div>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.status)}`}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
