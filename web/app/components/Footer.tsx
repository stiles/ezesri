export default function Footer() {
  return (
    <footer className="border-t border-ink-800 mt-16 sm:mt-24">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <div className="flex flex-col sm:flex-row justify-between gap-6">
          <div>
            <h3 className="text-lg font-semibold text-ink-100">ezesri</h3>
            <p className="text-sm text-ink-400 mt-1">
              Extract data from Esri REST services without the hassle.
            </p>
          </div>
          <div className="flex flex-col gap-1 text-sm">
            <a href="/docs" className="text-ember-400 hover:text-ember-300 transition-colors">
              Read the docs
            </a>
            <a 
              href="https://github.com/stiles/ezesri" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-ember-400 hover:text-ember-300 transition-colors"
            >
              View the code
            </a>
            <a 
              href="https://buymeacoffee.com/mattstiles" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-ember-400 hover:text-ember-300 transition-colors"
            >
              Support this tool
            </a>
          </div>
        </div>
        <div className="border-t border-ink-800 pt-4 mt-6">
          <p className="text-sm text-ink-400">
            © 2025{' '}
            <a 
              href="https://mattstiles.me" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-ember-400 hover:text-ember-300 transition-colors"
            >
              Matt Stiles
            </a>
          </p>
        </div>
      </div>
    </footer>
  )
}
