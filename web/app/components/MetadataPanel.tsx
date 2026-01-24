'use client'

import { LayerMetadata } from '@/lib/api'

interface MetadataPanelProps {
  metadata: LayerMetadata
}

// Common WKID to friendly name mapping
const PROJECTION_NAMES: Record<number, string> = {
  4326: 'WGS 84',
  3857: 'Web Mercator',
  102100: 'Web Mercator',
  4269: 'NAD83',
  4267: 'NAD27',
  102003: 'Albers USA',
  102008: 'Albers North America',
  26910: 'UTM 10N (NAD83)',
  26911: 'UTM 11N (NAD83)',
  26912: 'UTM 12N (NAD83)',
  26913: 'UTM 13N (NAD83)',
  26914: 'UTM 14N (NAD83)',
  26915: 'UTM 15N (NAD83)',
  26916: 'UTM 16N (NAD83)',
  26917: 'UTM 17N (NAD83)',
  26918: 'UTM 18N (NAD83)',
  26919: 'UTM 19N (NAD83)',
  2227: 'CA State Plane III',
  2228: 'CA State Plane IV',
  2229: 'CA State Plane V',
  2230: 'CA State Plane VI',
}

function getProjectionName(wkid: number | null | undefined): string {
  if (!wkid) return '—'
  return PROJECTION_NAMES[wkid] || `EPSG:${wkid}`
}

export default function MetadataPanel({ metadata }: MetadataPanelProps) {
  const formatNumber = (n: number | null | undefined) => {
    if (n === null || n === undefined) return '—'
    return n.toLocaleString()
  }
  
  return (
    <div className="animate-slide-up space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-semibold text-ink-100">{metadata.name}</h2>
        {metadata.description && (
          <p className="mt-1 text-sm text-ink-400 max-w-xl">{metadata.description}</p>
        )}
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-ink-900/30 rounded-lg p-4 border border-ink-800">
          <div className="text-2xl font-semibold text-ink-100">
            {formatNumber(metadata.featureCount)}
          </div>
          <div className="text-xs text-ink-400 uppercase tracking-wide mt-1">Features</div>
        </div>
        <div className="bg-ink-900/30 rounded-lg p-4 border border-ink-800">
          <div className="text-2xl font-semibold text-ink-100">
            {metadata.fields.length}
          </div>
          <div className="text-xs text-ink-400 uppercase tracking-wide mt-1">Fields</div>
        </div>
        <div className={`rounded-lg p-4 border ${metadata.hasGeometry ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-amber-500/10 border-amber-500/30'}`}>
          <div className={`text-lg font-semibold ${metadata.hasGeometry ? 'text-emerald-300' : 'text-amber-300'}`}>
            {metadata.hasGeometry ? (metadata.geometryType || 'Geometry') : 'Table'}
          </div>
          <div className="text-xs text-ink-400 uppercase tracking-wide mt-1">Type</div>
        </div>
        <div className="bg-ink-900/30 rounded-lg p-4 border border-ink-800">
          <div className="text-lg font-semibold text-ink-100">
            {getProjectionName(metadata.spatialReference)}
          </div>
          <div className="text-xs text-ink-400 uppercase tracking-wide mt-1">Projection</div>
        </div>
      </div>
      
      {/* Fields table */}
      <div>
        <h3 className="text-sm font-medium text-ink-300 mb-3">Fields</h3>
        <div className="bg-ink-900/30 rounded-lg border border-ink-800 overflow-hidden">
          <div className="max-h-80 overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="bg-ink-900/50 sticky top-0">
                <tr>
                  <th className="text-left px-4 py-2 text-ink-400 font-medium">Name</th>
                  <th className="text-left px-4 py-2 text-ink-400 font-medium">Type</th>
                  <th className="text-left px-4 py-2 text-ink-400 font-medium">Sample values</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-800">
                {metadata.fields.map((field, i) => {
                  const samples = metadata.sampleValues?.[field.name]
                  return (
                    <tr key={i} className="hover:bg-ink-800/30 transition-colors">
                      <td className="px-4 py-2 font-mono text-ink-200">{field.name}</td>
                      <td className="px-4 py-2 text-ink-400">{field.type}</td>
                      <td className="px-4 py-2 text-ink-400 max-w-xs">
                        {samples ? (
                          <span className="font-mono text-xs text-ember-400/70">
                            {samples.map((v, j) => (
                              <span key={j}>
                                {j > 0 && <span className="text-ink-600">, </span>}
                                &quot;{v.length > 20 ? v.slice(0, 20) + '…' : v}&quot;
                              </span>
                            ))}
                          </span>
                        ) : (
                          <span className="text-ink-600">—</span>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
