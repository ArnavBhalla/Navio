'use client'

import { useState, useEffect } from 'react'

interface CompletedCoursesInputProps {
  programId: string
  value: string[]
  onChange: (courses: string[]) => void
}

interface Course {
  code: string
  title: string
}

export default function CompletedCoursesInput({
  programId,
  value,
  onChange
}: CompletedCoursesInputProps) {
  const [input, setInput] = useState('')
  const [suggestions, setSuggestions] = useState<Course[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (input.length < 2) {
        setSuggestions([])
        return
      }

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const res = await fetch(
          `${apiUrl}/api/search?program_id=${programId}&q=${encodeURIComponent(input)}&limit=5`
        )
        if (res.ok) {
          const data = await res.json()
          setSuggestions(data)
        }
      } catch (err) {
        console.error('Error fetching suggestions:', err)
      }
    }

    const debounce = setTimeout(fetchSuggestions, 300)
    return () => clearTimeout(debounce)
  }, [input, programId])

  const addCourse = (code: string) => {
    if (!value.includes(code)) {
      onChange([...value, code])
    }
    setInput('')
    setSuggestions([])
    setShowSuggestions(false)
  }

  const removeCourse = (code: string) => {
    onChange(value.filter(c => c !== code))
  }

  return (
    <div className="space-y-2">
      {/* Input with typeahead */}
      <div className="relative">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder="Type course code or name..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
        />

        {/* Suggestions dropdown */}
        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-48 overflow-y-auto">
            {suggestions.map((course) => (
              <button
                key={course.code}
                onClick={() => addCourse(course.code)}
                className="w-full px-4 py-2 text-left hover:bg-gray-100 focus:bg-gray-100 focus:outline-none"
              >
                <div className="font-medium">{course.code}</div>
                <div className="text-sm text-gray-600">{course.title}</div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Selected courses */}
      <div className="flex flex-wrap gap-2">
        {value.map((code) => (
          <span
            key={code}
            className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm"
          >
            {code}
            <button
              onClick={() => removeCourse(code)}
              className="hover:text-primary-900"
            >
              ×
            </button>
          </span>
        ))}
      </div>
    </div>
  )
}
