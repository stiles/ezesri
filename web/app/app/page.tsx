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
      
      // Fetch sample values in background for string and numeric fields
      const sampleFields = data.fields
        .filter(f => !['esriFieldTypeOID', 'esriFieldTypeGlobalID', 'OID', 'GlobalID'].includes(f.type))
        .slice(0, 15)
        .map(f => f.name)
      
      if (sampleFields.length > 0) {
        fetchSampleValues(inputUrl, sampleFields).then(samples => {
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
            Paste any ArcGIS feature layer or map server URL. Get metadata, apply filters and export to GeoJSON or CSV. No installation or code needed.
          </p>
        </div>
        
        {/* URL Input */}
        <div className="mb-8">
          <p className="text-sm text-ink-400 mb-3">
            Enter a layer URL to get started. Hint: look for URLs ending in <code className="text-ember-400/70">/FeatureServer/0</code> or <code className="text-ember-400/70">/MapServer/1</code>
          </p>
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
          <div className="space-y-3">
            {/* Directory callout */}
            <a
              href="/directory"
              className="block max-w-xl mx-auto mt-4 p-5 rounded-xl border border-ink-800 bg-ink-900/30 hover:border-ember-500/40 hover:bg-ink-900/50 transition-all group"
            >
              <div className="flex items-center gap-5">
                {/* Dot cluster — abstract map points */}
                <div className="flex-shrink-0 w-14 h-14 relative" aria-hidden="true">
                  <svg viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
                    <circle cx="14" cy="20" r="4" className="fill-ember-500/70" />
                    <circle cx="32" cy="12" r="3" className="fill-ember-400/50" />
                    <circle cx="44" cy="28" r="5" className="fill-ember-500/60" />
                    <circle cx="22" cy="38" r="3.5" className="fill-ember-400/40" />
                    <circle cx="38" cy="44" r="2.5" className="fill-ember-500/50" />
                    <circle cx="10" cy="44" r="2" className="fill-ember-400/30" />
                    <circle cx="48" cy="14" r="2" className="fill-ember-500/40" />
                  </svg>
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-ink-200 group-hover:text-ink-100 transition-colors">
                    Don&apos;t have a URL handy?
                  </p>
                  <p className="text-sm text-ink-400 mt-0.5">
                    Browse 24,000+ public services across 30+ categories.
                  </p>
                </div>
                <svg className="w-5 h-5 text-ink-600 group-hover:text-ember-400 flex-shrink-0 transition-colors ml-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </a>

            {/* CLI nudge */}
            <a
              href="/docs/installation"
              className="block max-w-xl mx-auto p-5 rounded-xl border border-ink-800 bg-ink-900/30 hover:border-ember-500/40 hover:bg-ink-900/50 transition-all group"
            >
              <div className="flex items-center gap-5">
                <div className="flex-shrink-0 w-14 h-14 rounded-xl bg-ink-800/40 flex items-center justify-center" aria-hidden="true">
                  <svg className="w-7 h-7 text-ink-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-ink-200 group-hover:text-ink-100 transition-colors">
                    Prefer the command line?
                  </p>
                  <p className="text-sm text-ink-400 mt-0.5">
                    <code className="font-mono text-ember-400/80">pip install ezesri</code> for more formats and scripting support.
                  </p>
                </div>
                <svg className="w-5 h-5 text-ink-600 group-hover:text-ember-400 flex-shrink-0 transition-colors ml-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </a>
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
