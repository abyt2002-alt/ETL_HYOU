import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api, RunDetail as RunDetailType } from '../api/client'

export default function RunDetail() {
  const { runId } = useParams<{ runId: string }>()
  const [runDetail, setRunDetail] = useState<RunDetailType | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (runId) {
      loadRunDetail(parseInt(runId))
    }
  }, [runId])

  const loadRunDetail = async (id: number) => {
    try {
      const response = await api.getRunDetail(id)
      setRunDetail(response.data)
    } catch (error) {
      console.error('Failed to load run detail:', error)
    } finally {
      setLoading(false)
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

  if (loading) {
    return <div className="text-center py-8">Loading run details...</div>
  }

  if (!runDetail) {
    return <div className="text-center py-8">Run not found</div>
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-4">
        <Link to="/runs" className="text-blue-600 hover:text-blue-800 text-sm">
          ← Back to Runs
        </Link>
      </div>

      <h2 className="text-2xl font-bold text-gray-900 mb-6">Run #{runDetail.run.id}</h2>

      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">Run Information</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Trigger Type</p>
            <p className="text-base font-medium">{runDetail.run.trigger_type}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Status</p>
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(runDetail.run.status)}`}>
              {runDetail.run.status}
            </span>
          </div>
          <div>
            <p className="text-sm text-gray-500">Started At</p>
            <p className="text-base">{new Date(runDetail.run.started_at).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Completed At</p>
            <p className="text-base">
              {runDetail.run.completed_at ? new Date(runDetail.run.completed_at).toLocaleString() : 'In progress'}
            </p>
          </div>
          <div className="col-span-2">
            <p className="text-sm text-gray-500">Summary</p>
            <p className="text-base">{runDetail.run.summary_message || 'No summary available'}</p>
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Source Items</h3>
        <div className="space-y-4">
          {runDetail.items.map((item) => (
            <div key={item.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="font-semibold text-gray-900">{item.source_name}</h4>
                  <p className="text-sm text-gray-500">{item.sheet_tab_name} → {item.target_table_name}</p>
                </div>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(item.status)}`}>
                  {item.status}
                </span>
              </div>
              
              <div className="grid grid-cols-3 gap-4 text-sm mb-2">
                <div>
                  <p className="text-gray-500">Rows Read</p>
                  <p className="font-medium">{item.rows_read}</p>
                </div>
                <div>
                  <p className="text-gray-500">Rows Loaded</p>
                  <p className="font-medium text-green-600">{item.rows_loaded}</p>
                </div>
                <div>
                  <p className="text-gray-500">Rows Failed</p>
                  <p className="font-medium text-red-600">{item.rows_failed}</p>
                </div>
              </div>

              {item.error_message && (
                <div className="mt-3 p-3 bg-red-50 rounded">
                  <p className="text-sm text-red-800">{item.error_message}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
