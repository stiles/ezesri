'use client'

import { useState, useEffect } from 'react'

interface UrlInputProps {
  onFetch: (url: string) => void
  isLoading: boolean
  initialUrl?: string
}

export default function UrlInput({ onFetch, isLoading, initialUrl }: UrlInputProps) {
  const [url, setUrl] = useState(initialUrl || '')

  // Update URL when initialUrl changes (e.g., from query param)
  useEffect(() => {
    if (initialUrl) {
      setUrl(initialUrl)
    }
  }, [initialUrl])
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (url.trim()) {
      onFetch(url.trim())
    }
  }
  
  const exampleUrls = [
    {
      label: 'US cities',
      url: 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/USA/MapServer/0'
    },
    {
      label: 'North Korea missle ranges',
      url: 'https://services.arcgis.com/hRUr1F8lE8Jq2uJo/ArcGIS/rest/services/NorthKoreaMissiles/FeatureServer/0'
    },
    {
      label: 'LAPD stations',
      url: 'https://services5.arcgis.com/7nsPwEMP38bSkCjy/ArcGIS/rest/services/LAPD_Police_Stations/FeatureServer/0'
    }
  ]
  
  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="flex gap-3">
        <div className="flex-1 relative">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste Esri REST layer URL..."
            className="w-full px-4 py-3 bg-ink-900/50 border border-ink-700 rounded-lg 
                       text-ink-100 placeholder:text-ink-400 font-mono text-sm
                       focus:border-ember-500/50 transition-colors"
            disabled={isLoading}
          />
          {url && (
            <button
              type="button"
              onClick={() => setUrl('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-400 hover:text-ink-300"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
        <button
          type="submit"
          disabled={!url.trim() || isLoading}
          className="px-6 py-3 bg-ember-600 hover:bg-ember-500 disabled:bg-ink-700 
                     disabled:text-ink-400 text-white font-medium rounded-lg 
                     transition-colors flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Loading...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Fetch
            </>
          )}
        </button>
      </form>
      
      <div className="flex items-center gap-1 text-sm text-ink-400">
        <span>For example:</span>
        {exampleUrls.map((example, i) => (
          <span key={i} className="flex items-center">
            <button
              onClick={() => setUrl(example.url)}
              className="text-ember-400 hover:text-ember-300 hover:underline transition-colors"
            >
              {example.label}
            </button>
            {i < exampleUrls.length - 1 && <span className="text-ink-300">,</span>}
          </span>
        ))}
      </div>
    </div>
  )
}
