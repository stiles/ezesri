'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navItems = [
  { href: '/docs', label: 'Introduction' },
  { href: '/docs/installation', label: 'Installation' },
  { href: '/docs/usage', label: 'Usage' },
  { href: '/docs/developer', label: 'Developer guide' },
  { href: '/docs/testing', label: 'Testing' },
  { href: '/docs/license', label: 'License' },
]

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-ink-800 bg-ink-950/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-ember-500 to-ember-600 
                          flex items-center justify-center text-white font-bold text-sm
                          group-hover:from-ember-400 group-hover:to-ember-500 transition-all">
              ez
            </div>
            <span className="font-semibold text-ink-100">ezesri</span>
          </Link>
          <nav className="flex items-center gap-6 text-sm">
            <Link href="/" className="text-ink-400 hover:text-ink-200 transition-colors">
              App
            </Link>
            <Link href="/docs" className="text-ember-400 hover:text-ember-300 transition-colors">
              Docs
            </Link>
            <a 
              href="https://github.com/stiles/ezesri" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-ink-400 hover:text-ink-200 transition-colors"
            >
              GitHub
            </a>
            <a 
              href="https://pypi.org/project/ezesri/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-ink-400 hover:text-ink-200 transition-colors"
            >
              PyPI
            </a>
          </nav>
        </div>
      </header>
      
      <div className="max-w-6xl mx-auto flex">
        {/* Sidebar */}
        <aside className="w-64 flex-shrink-0 border-r border-ink-800 min-h-[calc(100vh-65px)] sticky top-[65px] self-start">
          <nav className="p-6 space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`
                    block px-3 py-2 rounded-lg text-sm transition-colors
                    ${isActive 
                      ? 'bg-ember-600/20 text-ember-300 border-l-2 border-ember-500' 
                      : 'text-ink-400 hover:text-ink-200 hover:bg-ink-800/50'
                    }
                  `}
                >
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </aside>
        
        {/* Main content */}
        <main className="flex-1 px-12 py-10 max-w-none">
          {children}
        </main>
      </div>
    </div>
  )
}
