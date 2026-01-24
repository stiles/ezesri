/**
 * API client for ezesri Lambda backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.ezesri.com'

export interface LayerMetadata {
  name: string
  description: string
  geometryType: string
  featureCount: number | null
  maxRecordCount: number
  spatialReference: number
  extent: {
    xmin: number
    ymin: number
    xmax: number
    ymax: number
    spatialReference: number
  } | null
  fields: Array<{
    name: string
    type: string
    alias: string
  }>
  hasGeometry: boolean
  sampleValues?: Record<string, string[]>
}

export interface ExtractParams {
  url: string
  format: 'geojson' | 'shapefile' | 'geoparquet'
  where?: string
  bbox?: string
}

export interface ApiError {
  error: string
  featureCount?: number
}

/**
 * Fetch metadata for an Esri layer
 */
export async function fetchMetadata(url: string): Promise<LayerMetadata> {
  const response = await fetch(`${API_URL}/metadata?url=${encodeURIComponent(url)}`)
  const data = await response.json()
  
  if (!response.ok || data.error) {
    throw new Error(data.error || 'Failed to fetch metadata')
  }
  
  return data
}

/**
 * Fetch sample values directly from Esri API
 * Returns a map of field names to sample values
 */
export async function fetchSampleValues(url: string, fields: string[]): Promise<Record<string, string[]>> {
  try {
    // Query 10 records to get sample values
    const queryUrl = `${url}/query?where=1=1&outFields=${fields.join(',')}&returnGeometry=false&resultRecordCount=10&f=json`
    const response = await fetch(queryUrl)
    const data = await response.json()
    
    if (!data.features || data.features.length === 0) {
      return {}
    }
    
    // Extract unique values for each field
    const samples: Record<string, string[]> = {}
    
    for (const fieldName of fields) {
      const values = data.features
        .map((f: { attributes: Record<string, unknown> }) => f.attributes[fieldName])
        .filter((v: unknown) => v !== null && v !== undefined && v !== '')
        .map((v: unknown) => String(v))
      
      // Get unique values, limit to 3
      const unique = Array.from(new Set(values)).slice(0, 3) as string[]
      if (unique.length > 0) {
        samples[fieldName] = unique
      }
    }
    
    return samples
  } catch {
    // Silently fail - sample values are optional
    return {}
  }
}

/**
 * Extract layer data
 * Returns blob for download
 */
export async function extractLayer(params: ExtractParams): Promise<{ blob: Blob; filename: string }> {
  const formData = new URLSearchParams()
  formData.append('url', params.url)
  formData.append('format', params.format)
  
  if (params.where && params.where !== '1=1') {
    formData.append('where', params.where)
  }
  
  if (params.bbox) {
    formData.append('bbox', params.bbox)
  }
  
  const response = await fetch(`${API_URL}/extract`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  })
  
  // Check content type to determine if it's an error
  const contentType = response.headers.get('content-type') || ''
  
  if (contentType.includes('application/json') || contentType.includes('application/geo+json')) {
    const data = await response.json()
    
    if (data.error) {
      throw new Error(data.error)
    }
    
    // GeoJSON response - convert to blob
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/geo+json' })
    return { blob, filename: 'export.geojson' }
  }
  
  if (contentType.includes('application/zip')) {
    // Shapefile zip response
    const blob = await response.blob()
    return { blob, filename: 'export.zip' }
  }
  
  if (contentType.includes('application/octet-stream')) {
    // GeoParquet response
    const blob = await response.blob()
    return { blob, filename: 'export.parquet' }
  }
  
  // Unexpected response
  const text = await response.text()
  throw new Error(`Unexpected response: ${text.substring(0, 200)}`)
}

/**
 * Trigger file download in browser
 */
export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
