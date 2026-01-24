'use client'

import { usePathname } from 'next/navigation'

export default function Header() {
  const pathname = usePathname()
  
  return (
    <header className="border-b border-ink-800 bg-ink-950/50 backdrop-blur-sm sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between">
        <a href="/" className="flex items-center gap-2 sm:gap-3 hover:opacity-80 transition-opacity">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-ember-500 to-ember-600 flex items-center justify-center flex-shrink-0">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
          </div>
          <div>
            <h1 className="text-base sm:text-lg font-semibold text-ink-100">ezesri</h1>
            <p className="text-xs text-ink-400 hidden sm:block">Extract Esri REST data</p>
          </div>
        </a>
        <div className="flex items-center gap-3 sm:gap-6">
          <nav className="flex items-center gap-3 sm:gap-4 text-sm">
            <a 
              href="/"
              className={`transition-colors ${
                pathname === '/' 
                  ? 'text-ember-400 font-medium' 
                  : 'text-ink-400 hover:text-ink-200'
              }`}
            >
              Extract
            </a>
            <a 
              href="/directory"
              className={`transition-colors ${
                pathname === '/directory' 
                  ? 'text-ember-400 font-medium' 
                  : 'text-ink-400 hover:text-ink-200'
              }`}
            >
              Directory
            </a>
            <a 
              href="/docs"
              className={`transition-colors hidden sm:block ${
                pathname?.startsWith('/docs')
                  ? 'text-ember-400 font-medium' 
                  : 'text-ink-400 hover:text-ink-200'
              }`}
            >
              Docs
            </a>
          </nav>
          <a 
            href="https://github.com/stiles/ezesri" 
            target="_blank"
            rel="noopener noreferrer"
            className="text-ink-400 hover:text-ink-300 transition-colors"
          >
            <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="currentColor" viewBox="0 0 24 24">
              <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
            </svg>
          </a>
        </div>
      </div>
    </header>
  )
}
