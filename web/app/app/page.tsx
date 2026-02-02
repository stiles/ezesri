'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import UrlInput from '@/components/UrlInput'
import MetadataPanel from '@/components/MetadataPanel'
import FilterOptions from '@/components/FilterOptions'
import DownloadButton from '@/components/DownloadButton'
import { fetchMetadata, fetchSampleValues, LayerMetadata } from '@/lib/api'

function HomeContent() {
  const searchParams = useSearchParams()
  const urlParam = searchParams.get('url')

  const [url, setUrl] = useState('')
  const [metadata, setMetadata] = useState<LayerMetadata | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasAutoFetched, setHasAutoFetched] = useState(false)
  
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

  // Auto-fetch if URL param is provided
  useEffect(() => {
    if (urlParam && !hasAutoFetched) {
      setHasAutoFetched(true)
      handleFetch(urlParam)
    }
  }, [urlParam, hasAutoFetched])
  
  return (
    <main className="min-h-screen">
      <Header />
      
      {/* Main content */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Hero section */}
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-ink-100 mb-4">
            Unlock GIS data from Esri REST services
          </h2>
          <p className="text-ink-400 max-w-2xl mx-auto">
            Paste any ArcGIS feature layer or map server URL. Get metadata, apply filters and export to GeoJSON. No installation needed.
          </p>
        </div>
        
        {/* URL Input */}
        <div className="mb-8">
          <UrlInput onFetch={handleFetch} isLoading={isLoading} initialUrl={urlParam || undefined} />
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
          <div className="text-center py-8">
            <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-ink-900/50 flex items-center justify-center">
              <svg className="w-7 h-7 text-ink-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-ink-300 mb-2">Paste a layer URL to get started</h3>
            <p className="text-sm text-ink-400 max-w-md mx-auto">
              Works with any public ArcGIS FeatureServer or MapServer layer endpoint.
              Look for URLs ending in <code className="text-ember-400/70">/FeatureServer/0</code> or <code className="text-ember-400/70">/MapServer/1</code>, 
              or browse our <a href="/directory" className="text-ember-400 hover:text-ember-300 transition-colors">directory of 24,000+ public services</a>.
            </p>
          </div>
        )}
      </div>
      
      <Footer />
    </main>
  )
}

export default function Home() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center gap-3 text-ink-400">
          <svg className="w-6 h-6 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <span>Loading...</span>
        </div>
      </div>
    }>
      <HomeContent />
    </Suspense>
  )
}
