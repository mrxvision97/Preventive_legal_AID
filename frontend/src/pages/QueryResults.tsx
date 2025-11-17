import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../lib/api'

export default function QueryResults() {
  const { id } = useParams()
  const [query, setQuery] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      api
        .get(`/queries/${id}`)
        .then((res) => setQuery(res.data))
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Loading query results...</p>
        </div>
      </div>
    )
  }

  if (!query) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Query not found</p>
          <Link to="/dashboard" className="text-blue-600 hover:text-blue-700">
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  const response = query.ai_response

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        <Link to="/dashboard" className="text-blue-600 hover:text-blue-700 mb-4 inline-block">
          ← Back to Dashboard
        </Link>

        {query.status === 'processing' && (
          <div className="bg-white p-8 rounded-lg shadow text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-lg">Processing your query...</p>
            <p className="text-gray-600 mt-2">This may take a few moments</p>
          </div>
        )}

        {query.status === 'completed' && response && (
          <div className="space-y-6">
            {/* Risk Assessment */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-2xl font-bold mb-4">Risk Assessment</h2>
              <div className="flex items-center gap-4 mb-4">
                <span
                  className={`px-4 py-2 rounded-full font-semibold ${
                    response.risk_level === 'low'
                      ? 'bg-green-100 text-green-800'
                      : response.risk_level === 'medium'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {response.risk_level.toUpperCase()} RISK
                </span>
                <span className="text-2xl font-bold">Risk Score: {response.risk_score}/100</span>
              </div>
              <p className="text-gray-700">{response.risk_explanation}</p>
            </div>

            {/* Legal Analysis */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-2xl font-bold mb-4">Understanding Your Situation</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{response.analysis}</p>
            </div>

            {/* Pros and Cons */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-green-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-4 text-green-800">Pros</h3>
                <ul className="space-y-2">
                  {response.pros?.map((pro: string, i: number) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span className="text-gray-700">{pro}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="bg-red-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-4 text-red-800">Cons</h3>
                <ul className="space-y-2">
                  {response.cons?.map((con: string, i: number) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-red-600">✗</span>
                      <span className="text-gray-700">{con}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Preventive Roadmap */}
            {response.preventive_roadmap && (
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-2xl font-bold mb-4">Preventive Roadmap</h2>
                <ol className="space-y-4">
                  {response.preventive_roadmap.map((step: any, i: number) => (
                    <li key={i} className="flex gap-4">
                      <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold">
                        {step.step_number || i + 1}
                      </span>
                      <div className="flex-1">
                        <p className="font-semibold">{step.action}</p>
                        <p className="text-gray-600 text-sm mt-1">{step.importance}</p>
                        {step.deadline && (
                          <p className="text-sm text-orange-600 mt-1">Deadline: {step.deadline}</p>
                        )}
                      </div>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* Legal References */}
            {response.legal_references && (
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-2xl font-bold mb-4">Legal References</h2>
                <div className="space-y-4">
                  {response.legal_references.map((ref: any, i: number) => (
                    <div key={i} className="border-l-4 border-blue-600 pl-4">
                      <h4 className="font-semibold">{ref.act_name}</h4>
                      {ref.section_number && (
                        <p className="text-sm text-gray-600">Section: {ref.section_number}</p>
                      )}
                      <p className="text-gray-700 mt-1">{ref.summary}</p>
                      <p className="text-sm text-gray-600 mt-1">{ref.relevance}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Warnings */}
            {response.warnings && response.warnings.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-4 text-yellow-800">⚠️ Important Warnings</h3>
                <ul className="space-y-2">
                  {response.warnings.map((warning: string, i: number) => (
                    <li key={i} className="text-yellow-800">• {warning}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Next Steps */}
            {response.next_steps && (
              <div className="bg-blue-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-4 text-blue-800">Immediate Next Steps</h3>
                <ul className="space-y-2">
                  {response.next_steps.map((step: string, i: number) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-blue-600">→</span>
                      <span className="text-gray-700">{step}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {response.lawyer_consultation_recommended && (
              <div className="bg-red-50 border border-red-200 p-6 rounded-lg">
                <p className="text-red-800 font-semibold">
                  ⚠️ Professional lawyer consultation is strongly recommended for this matter.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

