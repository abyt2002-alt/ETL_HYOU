import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

interface PreprocessingSource {
  source_name: string;
  raw_table: string;
  curated_table: string;
  mapping_required: boolean;
  mapping_type: string | null;
}

interface PreprocessingRunItem {
  id: number;
  source_name: string;
  status: string;
  rows_read: number;
  rows_output: number;
  exact_duplicates_found: number;
  business_duplicates_found: number;
  mapping_matches: number;
  mapping_unmatched: number;
  unlabeled_count: number;
  issues_found: number;
  error_message: string | null;
}

interface PreprocessingRun {
  id: number;
  status: string;
  started_at: string;
  completed_at: string | null;
  summary_message: string | null;
}

export default function Preprocessing() {
  const [sources, setSources] = useState<PreprocessingSource[]>([]);
  const [latestRun, setLatestRun] = useState<PreprocessingRun | null>(null);
  const [runItems, setRunItems] = useState<PreprocessingRunItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    loadSources();
    loadLatestRun();
  }, []);

  const loadSources = async () => {
    try {
      const response = await apiClient.get('/preprocessing/sources');
      setSources(response.data);
    } catch (error) {
      console.error('Error loading sources:', error);
    }
  };

  const loadLatestRun = async () => {
    try {
      const response = await apiClient.get('/preprocessing/runs/latest');
      if (response.data) {
        setLatestRun(response.data);
        const detailResponse = await apiClient.get(`/preprocessing/runs/${response.data.id}`);
        setRunItems(detailResponse.data.items);
      }
    } catch (error) {
      console.error('Error loading latest run:', error);
    }
  };

  const runAllSources = async () => {
    setLoading(true);
    try {
      await apiClient.post('/preprocessing/run/all', {
        triggered_by: 'user',
        start_date: startDate || null,
        end_date: endDate || null
      });
      setTimeout(loadLatestRun, 2000);
    } catch (error) {
      console.error('Error running preprocessing:', error);
    } finally {
      setLoading(false);
    }
  };

  const runSingleSource = async (sourceName: string) => {
    setLoading(true);
    try {
      await apiClient.post(`/preprocessing/run/${sourceName}`, {
        triggered_by: 'user',
        start_date: startDate || null,
        end_date: endDate || null
      });
      setTimeout(loadLatestRun, 2000);
    } catch (error) {
      console.error('Error running preprocessing:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'running': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRunItemForSource = (sourceName: string) => {
    return runItems.find(item => item.source_name === sourceName);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Preprocessing</h1>
        <button
          onClick={runAllSources}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? 'Running...' : 'Run All Sources'}
        </button>
      </div>

      {/* Date Range Filter */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-3">Date Range (Optional)</h2>
        <div className="flex gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="border rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="border rounded px-3 py-2"
            />
          </div>
        </div>
      </div>

      {/* Latest Run Summary */}
      {latestRun && (
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-3">Latest Run</h2>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Run ID</p>
              <p className="font-semibold">{latestRun.id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <span className={`inline-block px-2 py-1 rounded text-sm ${getStatusColor(latestRun.status)}`}>
                {latestRun.status}
              </span>
            </div>
            <div>
              <p className="text-sm text-gray-600">Started</p>
              <p className="font-semibold">{new Date(latestRun.started_at).toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Summary</p>
              <p className="font-semibold">{latestRun.summary_message || 'N/A'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Source Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sources.map((source) => {
          const runItem = getRunItemForSource(source.source_name);
          return (
            <div key={source.source_name} className="bg-white p-6 rounded-lg shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold capitalize">{source.source_name}</h3>
                  <p className="text-sm text-gray-600">{source.raw_table} → {source.curated_table}</p>
                </div>
                <button
                  onClick={() => runSingleSource(source.source_name)}
                  disabled={loading}
                  className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:bg-gray-400"
                >
                  Run
                </button>
              </div>

              {runItem && (
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Status:</span>
                    <span className={`px-2 py-1 rounded text-xs ${getStatusColor(runItem.status)}`}>
                      {runItem.status}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Rows Read:</span>
                    <span className="font-semibold">{runItem.rows_read.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Rows Output:</span>
                    <span className="font-semibold">{runItem.rows_output.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Exact Duplicates:</span>
                    <span className="font-semibold">{runItem.exact_duplicates_found.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Business Duplicates:</span>
                    <span className="font-semibold">{runItem.business_duplicates_found.toLocaleString()}</span>
                  </div>
                  {source.mapping_required && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Mapping Matched:</span>
                        <span className="font-semibold">{runItem.mapping_matches.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Mapping Unmatched:</span>
                        <span className="font-semibold">{runItem.mapping_unmatched.toLocaleString()}</span>
                      </div>
                    </>
                  )}
                  {source.source_name === 'ga' && (
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Unlabeled:</span>
                      <span className="font-semibold">{runItem.unlabeled_count.toLocaleString()}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Issues Found:</span>
                    <span className="font-semibold">{runItem.issues_found}</span>
                  </div>
                  {runItem.error_message && (
                    <div className="mt-2 p-2 bg-red-50 rounded">
                      <p className="text-xs text-red-800">{runItem.error_message}</p>
                    </div>
                  )}
                </div>
              )}

              {!runItem && (
                <p className="text-sm text-gray-500 italic">No preprocessing run yet</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
