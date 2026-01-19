import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-sans',
})

const jetbrainsMono = JetBrains_Mono({ 
  subsets: ['latin'],
  variable: '--font-mono',
})

export const metadata: Metadata = {
  title: 'ezesri - Extract Esri REST Data',
  description: 'Download data from Esri REST services as GeoJSON or Shapefile. No installation required.',
  keywords: ['esri', 'arcgis', 'geojson', 'shapefile', 'gis', 'data extraction'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen bg-grid antialiased font-sans">
        {children}
      </body>
    </html>
  )
}
