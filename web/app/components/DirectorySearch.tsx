interface CategoryStat {
  key: string
  name: string
  count: number
  layers: number
}

export type SortOption = 'views' | 'title' | 'layers'

interface DirectorySearchProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  categories: CategoryStat[]
  selectedCategories: Set<string>
  onToggleCategory: (key: string) => void
  onClearFilters: () => void
  resultCount: number
  sortBy: SortOption
  onSortChange: (sort: SortOption) => void
}

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'views', label: 'Most viewed' },
  { value: 'title', label: 'A-Z' },
  { value: 'layers', label: 'Most layers' },
]

export default function DirectorySearch({
  searchQuery,
  onSearchChange,
  categories,
  selectedCategories,
  onToggleCategory,
  onClearFilters,
  resultCount,
  sortBy,
  onSortChange,
}: DirectorySearchProps) {
  const hasFilters = searchQuery.trim() || selectedCategories.size > 0

  return (
    <div className="space-y-4">
      {/* Search input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <svg className="w-5 h-5 text-ink-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search by title, place, tags..."
          className="w-full pl-12 pr-4 py-3 bg-ink-900/50 border border-ink-800 rounded-xl text-ink-100 placeholder-ink-500 focus:border-ember-500/50 transition-colors"
        />
        {searchQuery && (
          <button
            onClick={() => onSearchChange('')}
            className="absolute inset-y-0 right-0 pr-4 flex items-center text-ink-400 hover:text-ink-300"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Category pills */}
      <div className="flex flex-wrap gap-2">
        {categories.map(cat => {
          const isSelected = selectedCategories.has(cat.key)
          return (
            <button
              key={cat.key}
              onClick={() => onToggleCategory(cat.key)}
              className={`
                px-3 py-1.5 rounded-full text-sm font-medium transition-all
                ${isSelected
                  ? 'bg-ember-500 text-white'
                  : 'bg-ink-900/50 text-ink-400 border border-ink-800 hover:border-ink-700 hover:text-ink-300'
                }
              `}
            >
              {cat.name}
              <span className={`ml-1.5 ${isSelected ? 'text-white/70' : 'text-ink-600'}`}>
                {cat.count}
              </span>
            </button>
          )
        })}
      </div>

      {/* Results count, sort, and clear */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-ink-400">
          {resultCount.toLocaleString()} {resultCount === 1 ? 'service' : 'services'}
          {hasFilters && ' found'}
        </span>
        <div className="flex items-center gap-4">
          {hasFilters && (
            <button
              onClick={onClearFilters}
              className="text-ember-400 hover:text-ember-300 transition-colors"
            >
              Clear filters
            </button>
          )}
          <div className="flex items-center gap-2">
            <span className="text-ink-600">Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => onSortChange(e.target.value as SortOption)}
              className="bg-ink-900/50 border border-ink-800 rounded-lg px-2 py-1 text-ink-300 text-sm focus:border-ember-500/50 transition-colors cursor-pointer"
            >
              {SORT_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </div>
  )
}
