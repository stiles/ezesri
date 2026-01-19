'use client'

import { useState } from 'react'
import { LayerMetadata } from '@/lib/api'

interface FilterOptionsProps {
  metadata: LayerMetadata
  where: string
  bbox: string
  onWhereChange: (where: string) => void
  onBboxChange: (bbox: string) => void
}

export default function FilterOptions({ 
  metadata, 
  where, 
  bbox, 
  onWhereChange, 
  onBboxChange 
}: FilterOptionsProps) {
  const [showBbox, setShowBbox] = useState(false)
  
  // Get text/string fields for suggestions
  const textFields = metadata.fields
    .filter(f => f.type === 'String' || f.type === 'esriFieldTypeString')
    .slice(0, 5)
  
  const numericFields = metadata.fields
    .filter(f => ['Integer', 'Double', 'SmallInteger', 'Single', 'OID'].some(t => f.type.includes(t)))
    .slice(0, 3)
  
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-ink-300">Filters (optional)</h3>
      
      {/* Where clause */}
      <div>
        <label className="block text-xs text-ink-500 mb-2">SQL Where Clause</label>
        <input
          type="text"
          value={where}
          onChange={(e) => onWhereChange(e.target.value)}
          placeholder="e.g., STATUS = 'ACTIVE' AND YEAR > 2020"
          className="w-full px-4 py-2.5 bg-ink-900/50 border border-ink-700 rounded-lg 
                     text-ink-100 placeholder:text-ink-600 font-mono text-sm
                     focus:border-ember-500/50 transition-colors"
        />
        {(textFields.length > 0 || numericFields.length > 0) && (
          <div className="mt-2 flex flex-wrap gap-2">
            <span className="text-xs text-ink-600">Fields:</span>
            {textFields.map((f, i) => (
              <button
                key={i}
                onClick={() => onWhereChange(`${f.name} = ''`)}
                className="text-xs font-mono text-ember-400/70 hover:text-ember-400 transition-colors"
              >
                {f.name}
              </button>
            ))}
            {numericFields.map((f, i) => (
              <button
                key={i}
                onClick={() => onWhereChange(`${f.name} > 0`)}
                className="text-xs font-mono text-sky-400/70 hover:text-sky-400 transition-colors"
              >
                {f.name}
              </button>
            ))}
          </div>
        )}
      </div>
      
      {/* Bounding box toggle */}
      {metadata.hasGeometry && (
        <div>
          <button
            onClick={() => setShowBbox(!showBbox)}
            className="flex items-center gap-2 text-sm text-ink-400 hover:text-ink-200 transition-colors"
          >
            <svg 
              className={`w-4 h-4 transition-transform ${showBbox ? 'rotate-90' : ''}`} 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            Bounding Box Filter
          </button>
          
          {showBbox && (
            <div className="mt-3 animate-slide-up">
              <label className="block text-xs text-ink-500 mb-2">
                Coordinates (WGS84): xmin, ymin, xmax, ymax
              </label>
              <input
                type="text"
                value={bbox}
                onChange={(e) => onBboxChange(e.target.value)}
                placeholder="e.g., -118.5,33.7,-117.8,34.3"
                className="w-full px-4 py-2.5 bg-ink-900/50 border border-ink-700 rounded-lg 
                           text-ink-100 placeholder:text-ink-600 font-mono text-sm
                           focus:border-ember-500/50 transition-colors"
              />
              {metadata.extent && (
                <button
                  onClick={() => {
                    const { xmin, ymin, xmax, ymax } = metadata.extent!
                    onBboxChange(`${xmin},${ymin},${xmax},${ymax}`)
                  }}
                  className="mt-2 text-xs text-ember-400 hover:text-ember-300 transition-colors"
                >
                  Use layer extent
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
