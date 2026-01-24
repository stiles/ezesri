import { useRouter } from 'next/navigation'

interface Layer {
  id: number
  name: string
  type: string | null
}

interface Service {
  id: string
  title: string
  place: string
  category: string
  categoryKey: string
  url: string
  description: string
  owner: string
  numViews: number
  tags: string[]
  layers: Layer[]
  layerCount: number
  capabilities: string
  maxRecordCount: number | null
}

interface ServiceCardProps {
  service: Service
  isExpanded: boolean
  onToggle: () => void
}

export default function ServiceCard({ service, isExpanded, onToggle }: ServiceCardProps) {
  const router = useRouter()

  const formatViews = (n: number) => {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M views`
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K views`
    return `${n.toLocaleString()} views`
  }

  const handleExtract = () => {
    // Navigate to home page with URL pre-filled
    const extractUrl = service.layers.length === 1
      ? `${service.url}/${service.layers[0].id}`
      : service.url
    router.push(`/?url=${encodeURIComponent(extractUrl)}`)
  }

  const supportsQuery = service.capabilities?.includes('Query')

  return (
    <div className="bg-ink-900/20 border border-ink-800 rounded-xl overflow-hidden transition-all hover:border-ink-700">
      {/* Header - always visible */}
      <button
        onClick={onToggle}
        className="w-full px-5 py-4 flex items-start gap-4 text-left"
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-medium text-ink-100 truncate">{service.title}</h3>
            <span className="px-2 py-0.5 rounded-full text-xs bg-ink-800 text-ink-400">
              {service.category}
            </span>
          </div>
          <div className="flex items-center gap-3 mt-1 text-sm text-ink-400">
            <span>{service.place}</span>
            {service.layerCount > 0 && (
              <>
                <span className="text-ink-700">·</span>
                <span>{service.layerCount} {service.layerCount === 1 ? 'layer' : 'layers'}</span>
              </>
            )}
            {service.numViews > 0 && (
              <>
                <span className="text-ink-700">·</span>
                <span>{formatViews(service.numViews)}</span>
              </>
            )}
          </div>
        </div>
        <svg
          className={`w-5 h-5 text-ink-400 transition-transform flex-shrink-0 mt-1 ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded content */}
      <div
        className={`overflow-hidden transition-all duration-200 ${
          isExpanded ? 'max-h-[800px] opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="px-5 pb-5 space-y-4 border-t border-ink-800 pt-4">
          {/* Description */}
          {service.description && (
            <p className="text-sm text-ink-400 line-clamp-3">
              {service.description}
            </p>
          )}

          {/* Metadata grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-ink-600 text-xs uppercase tracking-wide mb-1">Owner</div>
              <div className="text-ink-300 truncate">{service.owner || 'Unknown'}</div>
            </div>
            <div>
              <div className="text-ink-600 text-xs uppercase tracking-wide mb-1">Capabilities</div>
              <div className="text-ink-300">
                {supportsQuery ? (
                  <span className="text-green-400">Query supported</span>
                ) : (
                  <span className="text-ink-400">Limited</span>
                )}
              </div>
            </div>
            {service.maxRecordCount && (
              <div>
                <div className="text-ink-600 text-xs uppercase tracking-wide mb-1">Max records</div>
                <div className="text-ink-300">{service.maxRecordCount.toLocaleString()}</div>
              </div>
            )}
            <div>
              <div className="text-ink-600 text-xs uppercase tracking-wide mb-1">Views</div>
              <div className="text-ink-300">{service.numViews.toLocaleString()}</div>
            </div>
          </div>

          {/* Layers */}
          {service.layers.length > 0 && (
            <div>
              <div className="text-ink-600 text-xs uppercase tracking-wide mb-2">Layers</div>
              <div className="flex flex-wrap gap-2">
                {service.layers.slice(0, 10).map(layer => (
                  <span
                    key={layer.id}
                    className="px-2 py-1 rounded bg-ink-800/50 text-xs text-ink-300"
                  >
                    {layer.name}
                  </span>
                ))}
                {service.layers.length > 10 && (
                  <span className="px-2 py-1 text-xs text-ink-400">
                    +{service.layers.length - 10} more
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Tags */}
          {service.tags.length > 0 && (
            <div>
              <div className="text-ink-600 text-xs uppercase tracking-wide mb-2">Tags</div>
              <div className="flex flex-wrap gap-2">
                {service.tags.slice(0, 8).map((tag, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 rounded-full text-xs bg-ink-900 text-ink-400 border border-ink-800"
                  >
                    {tag}
                  </span>
                ))}
                {service.tags.length > 8 && (
                  <span className="text-xs text-ink-600">+{service.tags.length - 8} more</span>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={handleExtract}
              disabled={!supportsQuery}
              className={`
                px-4 py-2 rounded-lg font-medium text-sm transition-all
                ${supportsQuery
                  ? 'bg-ember-500 text-white hover:bg-ember-600'
                  : 'bg-ink-800 text-ink-400 cursor-not-allowed'
                }
              `}
            >
              Extract with ezesri
            </button>
            <a
              href={service.url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 rounded-lg font-medium text-sm bg-ink-800 text-ink-300 hover:bg-ink-700 transition-colors"
            >
              View service
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
