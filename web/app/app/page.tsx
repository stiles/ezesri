'use client'

import { useState } from 'react'
import UrlInput from '@/components/UrlInput'
import MetadataPanel from '@/components/MetadataPanel'
import FilterOptions from '@/components/FilterOptions'
import DownloadButton from '@/components/DownloadButton'
import { fetchMetadata, fetchSampleValues, LayerMetadata } from '@/lib/api'

export default function Home() {
  const [url, setUrl] = useState('')
  const [metadata, setMetadata] = useState<LayerMetadata | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Filter state
  const [where, setWhere] = useState('')
  const [bbox, setBbox] = useState('')
  
  const handleFetch = async (inputUrl: string) => {
    setIsLoading(true)
    setError(null)
    setMetadata(null)
    setUrl(inputUrl)
    setWhere('')
    setBbox('')
    
    try {
      const data = await fetchMetadata(inputUrl)
      setMetadata(data)
      
      // Fetch sample values in background for string/text fields
      const textFields = data.fields
        .filter(f => f.type === 'String' || f.type === 'esriFieldTypeString')
        .slice(0, 10)
        .map(f => f.name)
      
      if (textFields.length > 0) {
        fetchSampleValues(inputUrl, textFields).then(samples => {
          if (Object.keys(samples).length > 0) {
            setMetadata(prev => prev ? { ...prev, sampleValues: samples } : prev)
          }
        })
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch metadata')
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <main className="min-h-screen">
      {/* Header */}
      <header className="border-b border-ink-800 bg-ink-950/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-ember-500 to-ember-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-ink-100">ezesri</h1>
              <p className="text-xs text-ink-500">Extract Esri REST data</p>
            </div>
          </div>
          <a 
            href="https://github.com/stiles/ezesri" 
            target="_blank"
            rel="noopener noreferrer"
            className="text-ink-500 hover:text-ink-300 transition-colors"
          >
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
            </svg>
          </a>
        </div>
      </header>
      
      {/* Main content */}
      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Hero section */}
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-ink-100 mb-4">
            Unlock GIS data from Esri REST services
          </h2>
          <p className="text-ink-400 max-w-2xl mx-auto">
            Paste any ArcGIS feature layer or map server URL.<br></br> 
            Get metadata, apply filters and export to GeoJSON. No installation required.
          </p>
        </div>
        
        {/* URL Input */}
        <div className="mb-12">
          <UrlInput onFetch={handleFetch} isLoading={isLoading} />
        </div>
        
        {/* Error state */}
        {error && (
          <div className="mb-8 p-4 bg-red-500/10 border border-red-500/30 rounded-lg animate-slide-up">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-red-400 font-medium">Failed to fetch layer</p>
                <p className="text-red-400/70 text-sm mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}
        
        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center py-16">
            <div className="flex items-center gap-3 text-ink-400">
              <svg className="w-6 h-6 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span>Fetching layer metadata...</span>
            </div>
          </div>
        )}
        
        {/* Results */}
        {metadata && !isLoading && (
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Left column - Metadata */}
            <div className="lg:col-span-2 space-y-8">
              <MetadataPanel metadata={metadata} />
            </div>
            
            {/* Right column - Filters & Download */}
            <div className="space-y-8">
              <div className="bg-ink-900/20 rounded-xl border border-ink-800 p-6 space-y-6 sticky top-24">
                <FilterOptions
                  metadata={metadata}
                  where={where}
                  bbox={bbox}
                  onWhereChange={setWhere}
                  onBboxChange={setBbox}
                />
                
                <div className="border-t border-ink-800 pt-6">
                  <DownloadButton
                    url={url}
                    metadata={metadata}
                    where={where}
                    bbox={bbox}
                  />
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Empty state */}
        {!metadata && !isLoading && !error && (
          <div className="text-center py-16">
            <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-ink-900/50 flex items-center justify-center">
              <svg className="w-8 h-8 text-ink-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-ink-300 mb-2">Paste a layer URL to get started</h3>
            <p className="text-sm text-ink-500 max-w-md mx-auto">
              Works with any public ArcGIS FeatureServer or MapServer layer endpoint.
              Look for URLs ending in <code className="text-ember-400/70">/FeatureServer/0</code> or <code className="text-ember-400/70">/MapServer/1</code>
            </p>
          </div>
        )}
      </div>
      
      {/* Footer */}
      <footer className="border-t border-ink-800 mt-24">
        <div className="max-w-5xl mx-auto px-6 py-8">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-ink-100">ezesri</h3>
            <p className="text-sm text-ink-500">
              Extract data from Esri REST services without the hassle.
            </p>
            <div className="flex flex-col gap-1 text-sm">
              <a href="/docs" className="text-ember-400 hover:text-ember-300 transition-colors">
                Read the docs
              </a>
              <a 
                href="https://github.com/stiles/ezesri" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-ember-400 hover:text-ember-300 transition-colors"
              >
                View the code
              </a>
              <a 
                href="https://buymeacoffee.com/mattstiles" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-ember-400 hover:text-ember-300 transition-colors"
              >
                Support this tool
              </a>
            </div>
            <div className="border-t border-ink-800 pt-4 mt-4">
              <p className="text-sm text-ink-500">
                © 2025{' '}
                <a 
                  href="https://mattstiles.me" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-ember-400 hover:text-ember-300 transition-colors"
                >
                  Matt Stiles
                </a>
              </p>
            </div>
          </div>
        </div>
      </footer>
    </main>
  )
}
