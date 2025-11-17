import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import api from '../lib/api'

const querySchema = z.object({
  domain: z.enum(['agriculture', 'civil', 'family', 'university']),
  query_text: z.string().min(50, 'Query must be at least 50 characters'),
  urgency_level: z.enum(['low', 'medium', 'high']).default('medium'),
})

type QueryForm = z.infer<typeof querySchema>

export default function QueryPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<QueryForm>({
    resolver: zodResolver(querySchema),
    defaultValues: {
      urgency_level: 'medium',
    },
  })

  const queryText = watch('query_text') || ''

  const onSubmit = async (data: QueryForm) => {
    setLoading(true)
    try {
      const response = await api.post('/queries', data)
      navigate(`/query/${response.data.id}`)
    } catch (err: any) {
      console.error('Query submission failed:', err)
      alert(err.response?.data?.detail || 'Failed to submit query')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-3xl">
        <h1 className="text-3xl font-bold mb-8">Submit Legal Query</h1>

        {/* Step Indicator */}
        <div className="flex justify-between mb-8">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center flex-1">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  s <= step ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
                }`}
              >
                {s}
              </div>
              {s < 3 && (
                <div
                  className={`flex-1 h-1 mx-2 ${s < step ? 'bg-blue-600' : 'bg-gray-200'}`}
                />
              )}
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="bg-white p-6 rounded-lg shadow">
          {step === 1 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Select Legal Domain</h2>
              <div className="grid md:grid-cols-2 gap-4">
                {[
                  { value: 'agriculture', label: 'Agriculture', icon: '🌾' },
                  { value: 'civil', label: 'Civil Law', icon: '⚖️' },
                  { value: 'family', label: 'Family & Marriage', icon: '👨‍👩‍👧‍👦' },
                  { value: 'university', label: 'University', icon: '🎓' },
                ].map((domain) => (
                  <label
                    key={domain.value}
                    className={`border-2 rounded-lg p-4 cursor-pointer hover:border-blue-500 ${
                      watch('domain') === domain.value ? 'border-blue-600 bg-blue-50' : 'border-gray-200'
                    }`}
                  >
                    <input
                      {...register('domain')}
                      type="radio"
                      value={domain.value}
                      className="sr-only"
                      onChange={() => setStep(2)}
                    />
                    <div className="text-2xl mb-2">{domain.icon}</div>
                    <div className="font-semibold">{domain.label}</div>
                  </label>
                ))}
              </div>
              {errors.domain && (
                <p className="mt-2 text-sm text-red-600">{errors.domain.message}</p>
              )}
            </div>
          )}

          {step === 2 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Describe Your Issue</h2>
              <textarea
                {...register('query_text')}
                rows={8}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Describe your legal concern in detail (minimum 50 characters)..."
              />
              <div className="mt-2 text-sm text-gray-600">
                {queryText.length}/50 characters (minimum)
              </div>
              {errors.query_text && (
                <p className="mt-2 text-sm text-red-600">{errors.query_text.message}</p>
              )}

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Urgency Level
                </label>
                <select
                  {...register('urgency_level')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div className="mt-6 flex gap-4">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Back
                </button>
                <button
                  type="button"
                  onClick={() => setStep(3)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Next
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Review and Submit</h2>
              <div className="space-y-4 mb-6">
                <div>
                  <span className="font-semibold">Domain:</span>{' '}
                  {watch('domain')?.charAt(0).toUpperCase() + watch('domain')?.slice(1)}
                </div>
                <div>
                  <span className="font-semibold">Query:</span>
                  <p className="mt-1 text-gray-700">{watch('query_text')}</p>
                </div>
                <div>
                  <span className="font-semibold">Urgency:</span>{' '}
                  {watch('urgency_level')?.charAt(0).toUpperCase() + watch('urgency_level')?.slice(1)}
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded p-4 mb-6">
                <p className="text-sm text-yellow-800">
                  <strong>Important:</strong> This AI service provides advisory guidance only and
                  does not constitute legal representation. For complex matters, please consult a
                  qualified lawyer.
                </p>
              </div>

              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Submitting...' : 'Submit Query'}
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  )
}

