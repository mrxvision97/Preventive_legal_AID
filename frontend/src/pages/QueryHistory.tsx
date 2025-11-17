import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../lib/api'

export default function QueryHistory() {
  const [queries, setQueries] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .get('/queries?limit=100')
      .then((res) => setQueries(res.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Query History</h1>

        {queries.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow text-center">
            <p className="text-gray-600 mb-4">No queries yet</p>
            <Link to="/query" className="text-blue-600 hover:text-blue-700">
              Ask your first legal question
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {queries.map((query) => (
              <Link
                key={query.id}
                to={`/query/${query.id}`}
                className="block bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                        {query.domain}
                      </span>
                      <span
                        className={`px-2 py-1 rounded text-sm ${
                          query.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : query.status === 'processing'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {query.status}
                      </span>
                    </div>
                    <p className="text-gray-700 mb-2">
                      {query.query_text.substring(0, 150)}
                      {query.query_text.length > 150 ? '...' : ''}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(query.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

