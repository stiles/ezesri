'use client'

import { LayerMetadata } from '@/lib/api'

interface MetadataPanelProps {
  metadata: LayerMetadata
}

export default function MetadataPanel({ metadata }: MetadataPanelProps) {
  const formatNumber = (n: number | null | undefined) => {
    if (n === null || n === undefined) return '—'
    return n.toLocaleString()
  }
  
  return (
    <div className="animate-slide-up space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-ink-100">{metadata.name}</h2>
          {metadata.description && (
            <p className="mt-1 text-sm text-ink-400 max-w-xl">{metadata.description}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          {metadata.hasGeometry && (
            <span className="px-2 py-1 text-xs font-medium bg-emerald-500/10 text-emerald-400 rounded">
              {metadata.geometryType || 'Geometry'}
            </span>
          )}
          {!metadata.hasGeometry && (
            <span className="px-2 py-1 text-xs font-medium bg-amber-500/10 text-amber-400 rounded">
              Table (no geometry)
            </span>
          )}
        </div>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-ink-900/30 rounded-lg p-4 border border-ink-800">
          <div className="text-2xl font-semibold text-ink-100">
            {formatNumber(metadata.featureCount)}
          </div>
          <div className="text-xs text-ink-500 uppercase tracking-wide mt-1">Features</div>
        </div>
        <div className="bg-ink-900/30 rounded-lg p-4 border border-ink-800">
          <div className="text-2xl font-semibold text-ink-100">
            {metadata.fields.length}
          </div>
          <div className="text-xs text-ink-500 uppercase tracking-wide mt-1">Fields</div>
        </div>
        <div className="bg-ink-900/30 rounded-lg p-4 border border-ink-800">
          <div className="text-2xl font-semibold text-ink-100">
            {metadata.spatialReference || '—'}
          </div>
          <div className="text-xs text-ink-500 uppercase tracking-wide mt-1">WKID</div>
        </div>
        <div className="bg-ink-900/30 rounded-lg p-4 border border-ink-800">
          <div className="text-2xl font-semibold text-ink-100">
            {formatNumber(metadata.maxRecordCount)}
          </div>
          <div className="text-xs text-ink-500 uppercase tracking-wide mt-1">Max Records</div>
        </div>
      </div>
      
      {/* Fields table */}
      <div>
        <h3 className="text-sm font-medium text-ink-300 mb-3">Fields</h3>
        <div className="bg-ink-900/30 rounded-lg border border-ink-800 overflow-hidden">
          <div className="max-h-64 overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="bg-ink-900/50 sticky top-0">
                <tr>
                  <th className="text-left px-4 py-2 text-ink-400 font-medium">Name</th>
                  <th className="text-left px-4 py-2 text-ink-400 font-medium">Type</th>
                  <th className="text-left px-4 py-2 text-ink-400 font-medium hidden sm:table-cell">Alias</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-800">
                {metadata.fields.map((field, i) => (
                  <tr key={i} className="hover:bg-ink-800/30 transition-colors">
                    <td className="px-4 py-2 font-mono text-ink-200">{field.name}</td>
                    <td className="px-4 py-2 text-ink-400">{field.type}</td>
                    <td className="px-4 py-2 text-ink-500 hidden sm:table-cell">{field.alias || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
