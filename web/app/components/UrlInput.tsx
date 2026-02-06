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

  // Check if URL is a service-level URL (missing layer ID)
  const isServiceUrl = /\/(FeatureServer|MapServer)\/?$/i.test(url.trim())
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (url.trim()) {
      onFetch(url.trim())
    }
  }
  
  const exampleUrls = [
    {
      label: 'World cities',
      url: 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/World_Cities/FeatureServer/0'
    },
    {
      label: 'North Korea missle ranges',
      url: 'https://services.arcgis.com/hRUr1F8lE8Jq2uJo/ArcGIS/rest/services/NorthKoreaMissiles/FeatureServer/0'
    },
    {
      label: 'MLB stadiums',
      url: 'https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/Major_League_Baseball_Stadiums/FeatureServer/0'
    }
  ]
  
  return (
    <div className="space-y-3">
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

      {/* Warning for service-level URLs */}
      {isServiceUrl && (
        <div className="flex items-start gap-2 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-sm text-amber-400">
          <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <p className="font-medium">This looks like a service URL, not a layer URL</p>
            <p className="text-amber-400/80 mt-1">
              Add a layer number to the end, like <code className="bg-amber-500/20 px-1 rounded">/FeatureServer/0</code> or <code className="bg-amber-500/20 px-1 rounded">/MapServer/1</code>
            </p>
          </div>
        </div>
      )}
      
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
