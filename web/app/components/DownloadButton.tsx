'use client'

import { useState } from 'react'
import { LayerMetadata, extractLayer, downloadBlob, ExtractParams } from '@/lib/api'

interface DownloadButtonProps {
  url: string
  metadata: LayerMetadata
  where: string
  bbox: string
}

type Format = 'geojson' | 'csv'

export default function DownloadButton({ url, metadata, where, bbox }: DownloadButtonProps) {
  const [format, setFormat] = useState<Format>('geojson')
  const [isDownloading, setIsDownloading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const handleDownload = async () => {
    setIsDownloading(true)
    setError(null)
    
    try {
      const params: ExtractParams = {
        url,
        format,
        where: where || '1=1',
        bbox: bbox || undefined,
      }
      
      const { blob } = await extractLayer(params)
      
      // Generate filename from layer name with correct extension
      const safeName = metadata.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()
      const extension = format === 'csv' ? 'csv' : 'geojson'
      downloadBlob(blob, `${safeName}.${extension}`)
      
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Download failed')
    } finally {
      setIsDownloading(false)
    }
  }
  
  const formats: { value: Format; label: string; icon: string; disabled: boolean; description: string }[] = [
    { 
      value: 'geojson', 
      label: 'GeoJSON', 
      icon: '{ }',
      disabled: false,
      description: 'For mapping'
    },
    { 
      value: 'csv', 
      label: 'CSV', 
      icon: '📊',
      disabled: false,
      description: 'For spreadsheets'
    },
  ]
  
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-ink-300">Export Format</h3>
      
      {/* Format selector */}
      <div className="flex gap-3">
        {formats.map((f) => (
          <button
            key={f.value}
            onClick={() => setFormat(f.value)}
            disabled={f.disabled}
            className={`
              flex-1 px-4 py-3 rounded-lg border transition-all
              ${format === f.value 
                ? 'bg-ember-600/20 border-ember-500/50 text-ember-300' 
                : 'bg-ink-900/30 border-ink-700 text-ink-400 hover:border-ink-600'
              }
              ${f.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            <div className="text-lg">{f.icon}</div>
            <div className="text-sm mt-1 font-medium">{f.label}</div>
            <div className="text-xs text-ink-500 mt-0.5">{f.description}</div>
          </button>
        ))}
      </div>
      
      {/* Download button */}
      <button
        onClick={handleDownload}
        disabled={isDownloading}
        className="w-full px-6 py-4 bg-gradient-to-r from-ember-600 to-ember-500 
                   hover:from-ember-500 hover:to-ember-400
                   disabled:from-ink-700 disabled:to-ink-700 disabled:text-ink-400
                   text-white font-semibold rounded-lg 
                   transition-all flex items-center justify-center gap-3
                   shadow-lg shadow-ember-900/30"
      >
        {isDownloading ? (
          <>
            <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Extracting...
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download {format === 'csv' ? 'CSV' : 'GeoJSON'}
          </>
        )}
      </button>
      
      {/* Feature count warning */}
      {metadata.featureCount && metadata.featureCount > 10000 && (
        <p className="text-xs text-amber-400/80 flex items-start gap-2">
          <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>
            This layer has {metadata.featureCount.toLocaleString()} features. 
            Large downloads may take a while. Consider adding a filter to reduce the size.
          </span>
        </p>
      )}
      
      {/* Error message */}
      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-400">
          <p>{error}</p>
          {error.includes('limit') && (
            <p className="mt-2 text-red-300">
              For unlimited extraction, install the Python CLI:{' '}
              <code className="bg-red-500/20 px-1.5 py-0.5 rounded font-mono text-xs">pip install ezesri</code>
            </p>
          )}
        </div>
      )}
      
      {/* CLI promotion */}
      <p className="text-xs text-ink-400 pt-2">
        Need shapefile or other formats?{' '}
        <a 
          href="https://ezesri.com/docs" 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-ember-400 hover:text-ember-300 underline underline-offset-2"
        >
          Try it the Python client or CLI. 
        </a>
      </p>
    </div>
  )
}
