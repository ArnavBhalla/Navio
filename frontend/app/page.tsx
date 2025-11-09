'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

const PROGRAMS = [
  { university: 'Rice', major: 'Bioengineering', program_id: 'rice-bioe-2025' },
  { university: 'Rice', major: 'Computer Science', program_id: 'rice-cs-2025' },
  { university: 'UT Austin', major: 'Biomedical Engineering', program_id: 'utexas-bme-2025' },
  { university: 'UT Austin', major: 'Computer Science', program_id: 'utexas-cs-2025' },
  { university: 'Stanford', major: 'Bioengineering', program_id: 'stanford-bioe-2025' },
  { university: 'Stanford', major: 'Computer Science', program_id: 'stanford-cs-2025' },
]

export default function Home() {
  const router = useRouter()
  const [selectedUniversity, setSelectedUniversity] = useState('')
  const [selectedMajor, setSelectedMajor] = useState('')

  const universities = Array.from(new Set(PROGRAMS.map(p => p.university)))
  const majors = PROGRAMS
    .filter(p => !selectedUniversity || p.university === selectedUniversity)
    .map(p => p.major)

  const handleContinue = () => {
    const program = PROGRAMS.find(
      p => p.university === selectedUniversity && p.major === selectedMajor
    )
    if (program) {
      router.push(`/demo?program_id=${program.program_id}&university=${program.university}&major=${program.major}`)
    }
  }

  const canContinue = selectedUniversity && selectedMajor

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6">
      <div className="max-w-2xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold text-gray-900">
            Navio
          </h1>
          <p className="text-xl text-gray-600">
            Your AI-powered academic advisor
          </p>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
            <strong>Unofficial advisor.</strong> Always confirm with your department. Data updated 2025.
          </div>
        </div>

        {/* Selection Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
          <div>
            <label htmlFor="university" className="block text-sm font-medium text-gray-700 mb-2">
              Select Your University
            </label>
            <select
              id="university"
              value={selectedUniversity}
              onChange={(e) => {
                setSelectedUniversity(e.target.value)
                setSelectedMajor('')
              }}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">Choose a university...</option>
              {universities.map(uni => (
                <option key={uni} value={uni}>{uni}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="major" className="block text-sm font-medium text-gray-700 mb-2">
              Select Your Major
            </label>
            <select
              id="major"
              value={selectedMajor}
              onChange={(e) => setSelectedMajor(e.target.value)}
              disabled={!selectedUniversity}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">Choose a major...</option>
              {majors.map(major => (
                <option key={major} value={major}>{major}</option>
              ))}
            </select>
          </div>

          <button
            onClick={handleContinue}
            disabled={!canContinue}
            className="w-full bg-primary-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            Continue to Advisor
          </button>
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          Powered by GPT-4o and Claude Sonnet 4.5
        </div>
      </div>
    </main>
  )
}
