'use client'

import { useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import CompletedCoursesInput from '@/components/CompletedCoursesInput'
import RecommendationCard from '@/components/RecommendationCard'
import FeedbackBar from '@/components/FeedbackBar'

const TRACKS = ['pre-med', 'pre-law', 'pre-grad', 'pre-mba']

interface Recommendation {
  code: string
  title: string
  reason: string
  fulfills: string[]
  prereq_ok: boolean
  citations: string[]
}

interface RecommendResponse {
  recommendations: Recommendation[]
  notes: string[]
  assumptions: string[]
  warnings: string[]
}

function DemoContent() {
  const searchParams = useSearchParams()
  const program_id = searchParams.get('program_id') || ''
  const university = searchParams.get('university') || ''
  const major = searchParams.get('major') || ''

  const [completedCourses, setCompletedCourses] = useState<string[]>([])
  const [selectedTrack, setSelectedTrack] = useState<string>('')
  const [creditsTarget, setCreditsTarget] = useState(15)
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState<RecommendResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleGetRecommendations = async () => {
    setLoading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await fetch(`${apiUrl}/api/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          university,
          program_id,
          track: selectedTrack || null,
          completed: completedCourses,
          credits_target: creditsTarget,
          preferences: {}
        })
      })

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`)
      }

      const data = await res.json()
      setResponse(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Academic Advisor
          </h1>
          <p className="text-lg text-gray-600">
            {university} - {major}
          </p>
          <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-800">
            <strong>Unofficial advisor.</strong> Always confirm with your department.
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Input Form */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-6 space-y-6">
              <h2 className="text-2xl font-semibold text-gray-900">
                Your Progress
              </h2>

              {/* Completed Courses */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Completed Courses
                </label>
                <CompletedCoursesInput
                  programId={program_id}
                  value={completedCourses}
                  onChange={setCompletedCourses}
                />
                <p className="mt-2 text-sm text-gray-500">
                  {completedCourses.length} courses completed
                </p>
              </div>

              {/* Track Selection */}
              <div>
                <label htmlFor="track" className="block text-sm font-medium text-gray-700 mb-2">
                  Career Track (Optional)
                </label>
                <select
                  id="track"
                  value={selectedTrack}
                  onChange={(e) => setSelectedTrack(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">None</option>
                  {TRACKS.map(track => (
                    <option key={track} value={track}>
                      {track.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                    </option>
                  ))}
                </select>
              </div>

              {/* Credits Target */}
              <div>
                <label htmlFor="credits" className="block text-sm font-medium text-gray-700 mb-2">
                  Target Credit Load: {creditsTarget} credits
                </label>
                <input
                  id="credits"
                  type="range"
                  min="12"
                  max="21"
                  value={creditsTarget}
                  onChange={(e) => setCreditsTarget(parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>12</span>
                  <span>21</span>
                </div>
              </div>

              {/* Submit Button */}
              <button
                onClick={handleGetRecommendations}
                disabled={loading}
                className="w-full bg-primary-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Generating Recommendations...' : 'Get Recommendations'}
              </button>
            </div>
          </div>

          {/* Right Column: Recommendations */}
          <div className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
                <strong>Error:</strong> {error}
              </div>
            )}

            {response && (
              <>
                {/* Warnings */}
                {response.warnings.length > 0 && (
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                    <h3 className="font-semibold text-orange-900 mb-2">Warnings</h3>
                    <ul className="list-disc list-inside space-y-1 text-sm text-orange-800">
                      {response.warnings.map((warning, i) => (
                        <li key={i}>{warning}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                <div className="space-y-4">
                  <h2 className="text-2xl font-semibold text-gray-900">
                    Recommended Courses
                  </h2>
                  {response.recommendations.map((rec, i) => (
                    <RecommendationCard key={i} recommendation={rec} />
                  ))}
                </div>

                {/* Notes */}
                {response.notes.length > 0 && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="font-semibold text-blue-900 mb-2">Notes</h3>
                    <ul className="list-disc list-inside space-y-1 text-sm text-blue-800">
                      {response.notes.map((note, i) => (
                        <li key={i}>{note}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Assumptions */}
                {response.assumptions.length > 0 && (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-900 mb-2">Assumptions</h3>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                      {response.assumptions.map((assumption, i) => (
                        <li key={i}>{assumption}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Feedback */}
                <FeedbackBar />
              </>
            )}

            {!response && !loading && !error && (
              <div className="bg-white rounded-xl shadow-lg p-12 text-center">
                <div className="text-gray-400 mb-4">
                  <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <p className="text-gray-600">
                  Fill in your information and click "Get Recommendations" to start
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function DemoPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <DemoContent />
    </Suspense>
  )
}
