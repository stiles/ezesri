export default function Footer() {
  return (
    <footer className="border-t border-ink-800 mt-16 sm:mt-24 bg-ink-950/60">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10 sm:py-12">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-8">
          {/* Brand */}
          <div className="max-w-sm">
            <h3 className="text-lg font-semibold text-ink-100">ezesri</h3>
            <p className="text-sm text-ink-400 mt-1.5 leading-relaxed">
              Web app, Python library and CLI for extracting data from Esri REST services.
            </p>
            <div className="flex items-center gap-3 mt-4">
              <a
                href="https://github.com/stiles/ezesri"
                target="_blank"
                rel="noopener noreferrer"
                className="text-ink-500 hover:text-ink-200 transition-colors"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
              </a>
            </div>
          </div>

          {/* Links */}
          <nav className="flex flex-col gap-2 text-sm sm:text-right">
            <a href="/docs" className="text-ink-400 hover:text-ink-200 transition-colors">
              Documentation
            </a>
            <a href="/directory" className="text-ink-400 hover:text-ink-200 transition-colors">
              Directory
            </a>
            <a
              href="https://buymeacoffee.com/mattstiles"
              target="_blank"
              rel="noopener noreferrer"
              className="text-ink-400 hover:text-ink-200 transition-colors"
            >
              Buy me a coffee?
            </a>
          </nav>
        </div>

        <div className="border-t border-ink-800 pt-4 mt-8">
          <p className="text-sm text-ink-500">
            &copy; {new Date().getFullYear()}{' '}
            <a
              href="https://mattstiles.me"
              target="_blank"
              rel="noopener noreferrer"
              className="text-ink-400 hover:text-ink-200 transition-colors"
            >
              Matt Stiles
            </a>
          </p>
        </div>
      </div>
    </footer>
  )
}
