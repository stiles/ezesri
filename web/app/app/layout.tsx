import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import Script from 'next/script'
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
  title: 'ezesri - Extract GeoJSON from ArcGIS REST Services',
  description: 'Extract GeoJSON from any ArcGIS FeatureServer or MapServer. View metadata, apply filters and download data. No installation required.',
  keywords: ['esri', 'arcgis', 'geojson', 'gis', 'data extraction', 'feature layer', 'map server', 'rest api', 'spatial data'],
  authors: [{ name: 'Matt Stiles', url: 'https://mattstiles.me' }],
  creator: 'Matt Stiles',
  metadataBase: new URL('https://ezesri.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://ezesri.com',
    siteName: 'ezesri',
    title: 'ezesri - Extract GeoJSON from ArcGIS REST Services',
    description: 'Extract GeoJSON from any ArcGIS FeatureServer or MapServer. View metadata, apply filters and download data. No installation required.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'ezesri - Extract GeoJSON from ArcGIS REST Services',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ezesri - Extract GeoJSON from ArcGIS REST Services',
    description: 'Extract GeoJSON from any ArcGIS FeatureServer or MapServer. No installation required.',
    creator: '@staboratory',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <head>
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-5ZE1JXPVXF"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-5ZE1JXPVXF');
          `}
        </Script>
      </head>
      <body className="min-h-screen bg-grid antialiased font-sans">
        {children}
      </body>
    </html>
  )
}
