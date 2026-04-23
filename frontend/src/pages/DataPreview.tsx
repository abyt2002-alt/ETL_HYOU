import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'

export default function DataPreview() {
  const { tableName } = useParams<{ tableName: string }>()
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (tableName) {
      loadData(tableName)
    }
  }, [tableName])

  const loadData = async (table: string) => {
    try {
      const response = await api.previewData(table, 50)
      setData(response.data.rows)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading data...</div>
  }

  if (data.length === 0) {
    return (
      <div className="px-4 sm:px-0">
        <div className="mb-4">
          <Link to="/sources" className="text-blue-600 hover:text-blue-800 text-sm">
            ← Back to Sources
          </Link>
        </div>
        <div className="text-center py-8">No data available</div>
      </div>
    )
  }

  const columns = Object.keys(data[0])

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-4">
        <Link to="/sources" className="text-blue-600 hover:text-blue-800 text-sm">
          ← Back to Sources
        </Link>
      </div>

      <h2 className="text-2xl font-bold text-gray-900 mb-6">Data Preview: {tableName}</h2>

      <div className="bg-white shadow rounded-lg overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((col) => (
                <th key={col} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((row, idx) => (
              <tr key={idx}>
                {columns.map((col) => (
                  <td key={col} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {row[col] !== null && row[col] !== undefined ? String(row[col]) : '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
