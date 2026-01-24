'use client'

import { useState, useEffect, useMemo } from 'react'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import DirectorySearch, { SortOption } from '@/components/DirectorySearch'
import ServiceCard from '@/components/ServiceCard'

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

interface CategoryStat {
  key: string
  name: string
  count: number
  layers: number
}

interface Catalog {
  generated: string
  summary: {
    totalServices: number
    totalLayers: number
    totalViews: number
    categoryCount: number
  }
  categories: CategoryStat[]
  services: Service[]
}

export default function DirectoryPage() {
  const [catalog, setCatalog] = useState<Catalog | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set())
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<SortOption>('views')

  useEffect(() => {
    fetch('/catalog.json')
      .then(res => res.json())
      .then(data => {
        setCatalog(data)
        setIsLoading(false)
      })
      .catch(err => {
        console.error('Failed to load catalog:', err)
        setIsLoading(false)
      })
  }, [])

  const filteredServices = useMemo(() => {
    if (!catalog) return []

    let services = [...catalog.services]

    // Filter by category
    if (selectedCategories.size > 0) {
      services = services.filter(s => selectedCategories.has(s.categoryKey))
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      services = services.filter(s =>
        s.title.toLowerCase().includes(query) ||
        s.place.toLowerCase().includes(query) ||
        s.description.toLowerCase().includes(query) ||
        s.tags.some(t => t.toLowerCase().includes(query)) ||
        s.category.toLowerCase().includes(query)
      )
    }

    // Sort
    switch (sortBy) {
      case 'views':
        services.sort((a, b) => b.numViews - a.numViews)
        break
      case 'title':
        services.sort((a, b) => {
          // Case-insensitive, ignore leading special characters
          const aTitle = a.title.replace(/^[^a-zA-Z0-9]+/, '').toLowerCase()
          const bTitle = b.title.replace(/^[^a-zA-Z0-9]+/, '').toLowerCase()
          return aTitle.localeCompare(bTitle)
        })
        break
      case 'layers':
        services.sort((a, b) => b.layerCount - a.layerCount)
        break
    }

    return services
  }, [catalog, searchQuery, selectedCategories, sortBy])

  const toggleCategory = (key: string) => {
    setSelectedCategories(prev => {
      const next = new Set(prev)
      if (next.has(key)) {
        next.delete(key)
      } else {
        next.add(key)
      }
      return next
    })
  }

  const clearFilters = () => {
    setSearchQuery('')
    setSelectedCategories(new Set())
  }

  const formatNumber = (n: number) => {
    if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(1)}B`
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
    return n.toLocaleString()
  }

  return (
    <main className="min-h-screen">
      <Header />

      {/* Main content */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Hero section */}
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-ink-100 mb-4">
            Public GIS Data Directory
          </h2>
          <p className="text-ink-400 max-w-2xl mx-auto mb-8">
            Browse thousands of public ArcGIS Feature Services from government agencies worldwide.
            Find parcels, zoning, elections, crime data and more.
          </p>

          {/* Summary stats */}
          {catalog && (
            <div className="flex flex-wrap justify-center gap-6 sm:gap-12">
              <div className="text-center">
                <div className="text-2xl sm:text-3xl font-bold text-ember-500">
                  {formatNumber(catalog.summary.totalServices)}
                </div>
                <div className="text-sm text-ink-400">Services</div>
              </div>
              <div className="text-center">
                <div className="text-2xl sm:text-3xl font-bold text-ember-500">
                  {formatNumber(catalog.summary.totalLayers)}
                </div>
                <div className="text-sm text-ink-400">Layers</div>
              </div>
              <div className="text-center">
                <div className="text-2xl sm:text-3xl font-bold text-ember-500">
                  {catalog.summary.categoryCount}
                </div>
                <div className="text-sm text-ink-400">Categories</div>
              </div>
              <div className="text-center">
                <div className="text-2xl sm:text-3xl font-bold text-ember-500">
                  {formatNumber(catalog.summary.totalViews)}
                </div>
                <div className="text-sm text-ink-400">Total views</div>
              </div>
            </div>
          )}
        </div>

        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center py-16">
            <div className="flex items-center gap-3 text-ink-400">
              <svg className="w-6 h-6 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span>Loading directory...</span>
            </div>
          </div>
        )}

        {/* Search and filters */}
        {catalog && !isLoading && (
          <>
            <DirectorySearch
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              categories={catalog.categories}
              selectedCategories={selectedCategories}
              onToggleCategory={toggleCategory}
              onClearFilters={clearFilters}
              resultCount={filteredServices.length}
              sortBy={sortBy}
              onSortChange={setSortBy}
            />

            {/* Results */}
            <div className="mt-8">
              {filteredServices.length === 0 ? (
                <div className="text-center py-16">
                  <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-ink-900/50 flex items-center justify-center">
                    <svg className="w-8 h-8 text-ink-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-ink-300 mb-2">No services found</h3>
                  <p className="text-sm text-ink-400">Try adjusting your search or filters</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {filteredServices.slice(0, 100).map(service => (
                    <ServiceCard
                      key={service.id || service.url}
                      service={service}
                      isExpanded={expandedId === (service.id || service.url)}
                      onToggle={() => setExpandedId(
                        expandedId === (service.id || service.url) ? null : (service.id || service.url)
                      )}
                    />
                  ))}
                  {filteredServices.length > 100 && (
                    <div className="text-center py-8 text-ink-400">
                      Showing first 100 of {filteredServices.length.toLocaleString()} results.
                      Use search to narrow down.
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </div>

      <Footer />
    </main>
  )
}
