interface Recommendation {
  code: string
  title: string
  reason: string
  fulfills: string[]
  prereq_ok: boolean
  citations: string[]
}

interface RecommendationCardProps {
  recommendation: Recommendation
}

export default function RecommendationCard({ recommendation }: RecommendationCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-3">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">
            {recommendation.code}
          </h3>
          <p className="text-gray-600">{recommendation.title}</p>
        </div>

        {/* Prerequisite status */}
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium ${
            recommendation.prereq_ok
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}
        >
          {recommendation.prereq_ok ? '✓ Prereqs OK' : '⚠ Missing Prereqs'}
        </span>
      </div>

      {/* Reason */}
      <p className="text-gray-700">{recommendation.reason}</p>

      {/* Fulfills badges */}
      {recommendation.fulfills.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <span className="text-sm text-gray-600">Fulfills:</span>
          {recommendation.fulfills.map((req, i) => (
            <span
              key={i}
              className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm"
            >
              {req}
            </span>
          ))}
        </div>
      )}

      {/* Citations */}
      {recommendation.citations.length > 0 && (
        <div className="flex items-center gap-2 pt-2 border-t border-gray-200">
          <span className="text-sm text-gray-600">Sources:</span>
          {recommendation.citations.map((url, i) => (
            <a
              key={i}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary-600 hover:text-primary-700 hover:underline"
            >
              <svg
                className="w-4 h-4 inline"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
              {' '}Link {i + 1}
            </a>
          ))}
        </div>
      )}
    </div>
  )
}
