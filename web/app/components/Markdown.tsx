'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface MarkdownProps {
  content: string
}

export default function Markdown({ content }: MarkdownProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => (
          <h1 className="text-3xl font-bold text-ink-100 mb-6 pb-4 border-b border-ink-800">
            {children}
          </h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-xl font-semibold text-ink-200 mt-10 mb-4">
            {children}
          </h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-lg font-medium text-ink-300 mt-6 mb-3">
            {children}
          </h3>
        ),
        p: ({ children }) => (
          <p className="text-ink-400 leading-relaxed mb-4">
            {children}
          </p>
        ),
        ul: ({ children }) => (
          <ul className="list-disc list-outside text-ink-400 mb-4 space-y-2 ml-6">
            {children}
          </ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal list-outside text-ink-400 mb-4 space-y-3 ml-6">
            {children}
          </ol>
        ),
        li: ({ children }) => (
          <li className="text-ink-400 pl-1">
            {children}
          </li>
        ),
        a: ({ href, children }) => (
          <a 
            href={href} 
            className="text-ember-400 hover:text-ember-300 underline underline-offset-2"
            target={href?.startsWith('http') ? '_blank' : undefined}
            rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
          >
            {children}
          </a>
        ),
        code: ({ className, children }) => {
          const isInline = !className
          if (isInline) {
            return (
              <code className="bg-ink-800 text-ember-300 px-1.5 py-0.5 rounded text-sm font-mono">
                {children}
              </code>
            )
          }
          return (
            <code className="text-sm">
              {children}
            </code>
          )
        },
        pre: ({ children }) => (
          <pre className="bg-ink-900 border border-ink-800 rounded-lg p-4 mb-6 overflow-x-auto font-mono text-sm text-ink-300">
            {children}
          </pre>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-ember-500 pl-4 my-4 text-ink-400 italic">
            {children}
          </blockquote>
        ),
        hr: () => (
          <hr className="border-ink-800 my-8" />
        ),
        strong: ({ children }) => (
          <strong className="font-semibold text-ink-200">
            {children}
          </strong>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  )
}
