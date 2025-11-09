'use client'

import { useState } from 'react'

export default function FeedbackBar() {
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null)
  const [comment, setComment] = useState('')
  const [showComment, setShowComment] = useState(false)

  const handleFeedback = (type: 'up' | 'down') => {
    setFeedback(type)
    setShowComment(type === 'down')

    // Log to console (could be replaced with API call)
    console.log('Feedback:', type)
  }

  const handleSubmitComment = () => {
    console.log('Feedback comment:', comment)
    setComment('')
    setShowComment(false)
    alert('Thank you for your feedback!')
  }

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="space-y-4">
        <p className="text-sm font-medium text-gray-700">
          Were these recommendations helpful?
        </p>

        <div className="flex gap-4">
          <button
            onClick={() => handleFeedback('up')}
            className={`px-4 py-2 rounded-lg border-2 transition-colors ${
              feedback === 'up'
                ? 'border-green-500 bg-green-50 text-green-700'
                : 'border-gray-300 hover:border-green-500 text-gray-700'
            }`}
          >
            👍 Helpful
          </button>

          <button
            onClick={() => handleFeedback('down')}
            className={`px-4 py-2 rounded-lg border-2 transition-colors ${
              feedback === 'down'
                ? 'border-red-500 bg-red-50 text-red-700'
                : 'border-gray-300 hover:border-red-500 text-gray-700'
            }`}
          >
            👎 Not Helpful
          </button>
        </div>

        {showComment && (
          <div className="space-y-2">
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Tell us what went wrong..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              rows={3}
            />
            <button
              onClick={handleSubmitComment}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Submit Feedback
            </button>
          </div>
        )}

        {feedback === 'up' && !showComment && (
          <p className="text-sm text-green-600">
            Thank you for your feedback!
          </p>
        )}
      </div>
    </div>
  )
}
