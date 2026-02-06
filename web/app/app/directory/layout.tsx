import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Public GIS data directory | ezesri',
  description: 'Browse 24,000+ public ArcGIS Feature Services across 30+ categories from government agencies. Find boundaries, demographics, health, crime data, transportation and more.',
  keywords: ['arcgis directory', 'public gis data', 'feature services', 'government data', 'parcels', 'zoning', 'elections', 'crime data', 'open data', 'esri'],
  alternates: {
    canonical: '/directory',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://ezesri.com/directory',
    siteName: 'ezesri',
    title: 'Public GIS data directory | ezesri',
    description: 'Browse 24,000+ public ArcGIS Feature Services across 30+ categories from government agencies. Find boundaries, demographics, health and crime data and more.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'ezesri - Public GIS data directory',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Public GIS data directory | ezesri',
    description: 'Browse 24,000+ public ArcGIS Feature Services across 30+ categories. Find boundaries, demographics, health and crime data and more.',
    creator: '@staboratory',
    images: ['/og-image.png'],
  },
}

export default function DirectoryLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
