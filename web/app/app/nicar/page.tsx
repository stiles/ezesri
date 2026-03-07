'use client'

import { useState, useEffect, useCallback } from 'react'

// ─── Slide data ──────────────────────────────────────────────────────────────

interface Slide {
  id: string
  content: React.ReactNode
}

function PalmSpringsPool() {
  return (
    <div className="flex flex-col items-center justify-center w-full max-w-6xl pb-16">
      <div className="rounded-xl overflow-hidden shadow-2xl max-h-[70vh]">
        <img
          src="/palm-springs-pool.png"
          alt="Swimming pool in Palm Springs"
          className="w-full h-auto"
        />
      </div>
      <p className="text-xl text-ink-400 mt-6 text-center max-w-2xl">Palm Springs, last summer</p>
    </div>
  )
}

function Title() {
  return (
    <div className="flex flex-col items-center justify-center text-center">
      <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-ember-500 to-ember-600 flex items-center justify-center mb-8">
        <svg className="w-12 h-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
      </div>
      <h1 className="text-6xl sm:text-7xl font-bold text-ink-100 mb-6">ezesri</h1>
      <p className="text-2xl sm:text-3xl text-ink-300 max-w-3xl leading-relaxed">
        Unlocking official GIS data without the pain
      </p>
      <p className="text-lg text-ink-500 mt-8">NICAR 2026</p>
    </div>
  )
}

function TheProblem() {
  return (
    <div className="max-w-4xl">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-4">The problem</p>
      <h2 className="text-4xl sm:text-5xl font-bold text-ink-100 mb-10 leading-tight">
        Thousands of agencies publish GIS data through Esri.
      </h2>
      <div className="grid sm:grid-cols-2 gap-6">
        {[
          { label: 'Parcels', path: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0h4' },
          { label: 'Crime', path: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' },
          { label: 'Elections', path: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' },
          { label: 'Zoning', path: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7' },
          { label: 'Infrastructure', path: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4' },
          { label: 'Environment', path: 'M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
        ].map((item) => (
          <div key={item.label} className="flex items-center gap-4 p-4 rounded-lg bg-ink-900/40 border border-ink-800">
            <svg className="w-6 h-6 text-ember-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={item.path} />
            </svg>
            <span className="text-xl text-ink-200">{item.label}</span>
          </div>
        ))}
      </div>
      <p className="text-2xl text-ink-400 mt-10">
        Getting that data out? That&apos;s the tricky part.
      </p>
    </div>
  )
}

function OneOffScript() {
  return (
    <div className="flex flex-col items-center justify-center w-full max-w-6xl pb-16">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-6">Before ezesri</p>
      <h2 className="text-3xl sm:text-4xl font-bold text-ink-100 mb-6 leading-tight text-center">
        I was writing one-off extraction scripts for every project
      </h2>
      <div className="rounded-xl border border-ink-800 overflow-hidden shadow-2xl max-h-[60vh]">
        <img
          src="/one-off-script-example.png"
          alt="GitHub repository showing fetch_esri_service.py - a custom one-off extraction script"
          className="w-full h-auto"
        />
      </div>
      <p className="text-lg text-ink-500 mt-4">A script I wrote for an LA trees project &mdash; 53 lines just to download one layer</p>
    </div>
  )
}

function SeenThisWildfires() {
  return (
    <div className="flex flex-col items-center justify-center w-full max-w-6xl pb-16">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-6">You&apos;ve seen this before</p>
      <div className="rounded-xl border border-ink-800 overflow-hidden shadow-2xl max-h-[70vh]">
        <img
          src="/noaa_wildfires.png"
          alt="NOAA / USGS wildfire map powered by Esri ArcGIS"
          className="w-full h-auto"
        />
      </div>
      <p className="text-lg text-ink-500 mt-4">NOAA / USGS wildfire map &mdash; powered by Esri ArcGIS</p>
    </div>
  )
}

function SeenThisMeasles() {
  return (
    <div className="flex flex-col items-center justify-center w-full max-w-6xl pb-16">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-6">You&apos;ve seen this too</p>
      <div className="rounded-xl border border-ink-800 overflow-hidden shadow-2xl max-h-[70vh]">
        <img
          src="/johns_hopkins_measles.png"
          alt="Johns Hopkins measles case tracker powered by Esri ArcGIS"
          className="w-full h-auto"
        />
      </div>
      <p className="text-lg text-ink-500 mt-4">Johns Hopkins measles case tracker &mdash; powered by Esri ArcGIS</p>
    </div>
  )
}

function RawEsriPage1() {
  return (
    <div className="flex flex-col items-center justify-center w-full max-w-6xl pb-16">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-6">What you actually see</p>
      <h2 className="text-3xl sm:text-4xl font-bold text-ink-100 mb-6 leading-tight text-center">
        This is what an Esri REST endpoint looks like
      </h2>
      <div className="rounded-xl border border-ink-800 overflow-hidden shadow-2xl bg-white max-h-[60vh]">
        <img
          src="/ezesri-mlb-1.png"
          alt="Raw Esri REST API page showing MLB stadiums layer metadata"
          className="w-full h-auto"
        />
      </div>
      <p className="text-lg text-ink-500 mt-4">MLB stadiums layer &mdash; service metadata</p>
    </div>
  )
}

function RawEsriPage2() {
  return (
    <div className="flex flex-col items-center justify-center w-full max-w-6xl pb-16">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-6">The fields</p>
      <h2 className="text-3xl sm:text-4xl font-bold text-ink-100 mb-6 leading-tight text-center">
        Not exactly user-friendly
      </h2>
      <div className="rounded-xl border border-ink-800 overflow-hidden shadow-2xl bg-white max-h-[60vh]">
        <img
          src="/ezesri-mlb-2.png"
          alt="Raw Esri REST API page showing field definitions"
          className="w-full h-auto"
        />
      </div>
      <p className="text-lg text-ink-500 mt-4">Field definitions &mdash; JSON formatting, SQL types, technical metadata</p>
    </div>
  )
}

function AudienceCheck() {
  return (
    <div className="flex flex-col items-center justify-center text-center max-w-3xl">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-6">Quick check</p>
      <h2 className="text-4xl sm:text-5xl font-bold text-ink-100 leading-tight">
        Who has ever tried to download data from an ArcGIS REST endpoint?
      </h2>
      <p className="text-2xl text-ink-400 mt-10">
        How did that go?
      </p>
    </div>
  )
}

function ExistingOptions() {
  return (
    <div className="max-w-4xl">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-4">The landscape</p>
      <h2 className="text-4xl sm:text-5xl font-bold text-ink-100 mb-12 leading-tight">
        Existing options
      </h2>
      <div className="space-y-4">
        {[
          { tool: 'ArcGIS Hub', downside: 'Click-through UI, one layer at a time, limited filtering' },
          { tool: 'ArcGIS API for Python', downside: 'Heavy dependencies, overkill for simple extraction' },
          { tool: 'esri-dump / pysridump', downside: 'Not actively maintained, limited formats' },
          { tool: 'ogr2ogr (GDAL)', downside: 'Powerful but complex, not Python-native' },
        ].map((item) => (
          <div key={item.tool} className="flex items-start gap-6 p-5 rounded-lg bg-ink-900/40 border border-ink-800">
            <span className="font-mono text-lg text-ink-200 w-56 flex-shrink-0">{item.tool}</span>
            <span className="text-lg text-ink-400">{item.downside}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function WhatIsEzesri() {
  return (
    <div className="max-w-4xl">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-4">The solution</p>
      <h2 className="text-4xl sm:text-5xl font-bold text-ink-100 mb-12 leading-tight">
        Three ways in
      </h2>
      <div className="grid gap-6">
        {[
          {
            num: '1',
            title: 'Web app',
            desc: 'No installation, works in any browser',
            detail: 'ezesri.com',
          },
          {
            num: '2',
            title: 'Python CLI',
            desc: 'For power users and automation',
            detail: 'pip install ezesri',
          },
          {
            num: '3',
            title: 'Service directory',
            desc: 'Discover what\'s out there',
            detail: 'ezesri.com/directory',
          },
        ].map((item) => (
          <div key={item.num} className="flex items-start gap-6 p-6 rounded-xl bg-ink-900/40 border border-ink-800">
            <span className="text-3xl font-bold text-ember-500">{item.num}</span>
            <div>
              <h3 className="text-2xl font-semibold text-ink-100">{item.title}</h3>
              <p className="text-lg text-ink-400 mt-1">{item.desc}</p>
              <p className="text-sm font-mono text-ember-400/70 mt-2">{item.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function TheNumbers() {
  return (
    <div className="flex flex-col items-center justify-center text-center">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-8">By the numbers</p>
      <div className="grid grid-cols-2 gap-x-16 gap-y-12">
        {[
          { value: '24,600+', label: 'Public ArcGIS services' },
          { value: '120,000+', label: 'Individual layers' },
          { value: '34', label: 'Categories' },
          { value: '15.9B', label: 'Total views' },
        ].map((stat) => (
          <div key={stat.label}>
            <p className="text-5xl sm:text-6xl font-bold text-ember-400">{stat.value}</p>
            <p className="text-lg text-ink-400 mt-2">{stat.label}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function OutputFormats() {
  return (
    <div className="max-w-4xl">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-4">Export</p>
      <h2 className="text-4xl sm:text-5xl font-bold text-ink-100 mb-12 leading-tight">
        Output formats
      </h2>
      <div className="grid sm:grid-cols-2 gap-4">
        {[
          { format: 'CSV', use: 'Spreadsheets, quick analysis' },
          { format: 'GeoJSON', use: 'Web mapping, QGIS' },
          { format: 'Shapefile', use: 'Legacy GIS workflows' },
          { format: 'GeoPackage', use: 'Modern GIS, multi-layer' },
          { format: 'GeoParquet', use: 'Big data, columnar analysis' },
          { format: 'NDJSON', use: 'Streaming, piping' },
        ].map((item) => (
          <div key={item.format} className="flex items-center gap-4 p-4 rounded-lg bg-ink-900/40 border border-ink-800">
            <span className="font-mono text-lg text-ember-400 w-28 flex-shrink-0">{item.format}</span>
            <span className="text-ink-400">{item.use}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function TheDirectory() {
  return (
    <div className="max-w-4xl">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-4">Discovery</p>
      <h2 className="text-4xl sm:text-5xl font-bold text-ink-100 mb-8 leading-tight">
        The directory
      </h2>
      <p className="text-xl text-ink-300 mb-10 leading-relaxed">
        Browse and search 24,600+ public services from government agencies worldwide.
        Filter by 34 categories. Sort by popularity. One-click extraction.
      </p>
      <div className="rounded-xl border border-ink-800 bg-ink-900/40 p-8">
        <p className="text-sm text-ink-500 uppercase tracking-wider mb-6">Categories include</p>
        <div className="flex flex-wrap gap-2">
          {[
            'Parcels', 'Crime', 'Elections', 'Zoning', 'Boundaries',
            'Infrastructure', 'Transportation', 'Health', 'Education',
            'Environment', 'Demographics', 'Permits', 'Emergency',
            'Agriculture', 'Wildlife', 'Energy', 'Aviation',
          ].map((cat) => (
            <span
              key={cat}
              className="px-3 py-1.5 rounded-full bg-ink-800/60 text-sm text-ink-300 border border-ink-700/50"
            >
              {cat}
            </span>
          ))}
          <span className="px-3 py-1.5 rounded-full bg-ember-500/10 text-sm text-ember-400 border border-ember-500/20">
            + 17 more
          </span>
        </div>
      </div>
    </div>
  )
}

function HowItWorks() {
  return (
    <div className="max-w-4xl">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-4">Under the hood</p>
      <h2 className="text-4xl sm:text-5xl font-bold text-ink-100 mb-12 leading-tight">
        How extraction works
      </h2>
      <div className="space-y-4">
        {[
          { step: 'You', desc: 'paste a URL (or use the CLI)' },
          { step: 'ezesri', desc: 'asks the Esri service for records' },
          { step: 'Esri', desc: 'returns 1,000 records (max per request)' },
          { step: 'ezesri', desc: '"Great, give me the next 1,000"' },
          { step: '...', desc: 'repeat until done' },
          { step: 'You', desc: 'get the complete dataset' },
        ].map((item, i) => (
          <div key={i} className="flex items-center gap-6">
            <span className="w-16 text-right font-mono text-sm text-ember-400 flex-shrink-0">{item.step}</span>
            <div className="w-2 h-2 rounded-full bg-ember-500 flex-shrink-0" />
            <span className="text-xl text-ink-300">{item.desc}</span>
          </div>
        ))}
      </div>
      <p className="text-lg text-ink-500 mt-10">
        Esri services cap responses. ezesri handles pagination automatically so you get everything.
      </p>
    </div>
  )
}

function DemoWeb() {
  return (
    <div className="flex flex-col items-center justify-center text-center">
      <div className="w-16 h-16 rounded-xl bg-ink-800/60 flex items-center justify-center mb-8">
        <svg className="w-9 h-9 text-ember-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
        </svg>
      </div>
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-4">Demo</p>
      <h2 className="text-4xl sm:text-5xl font-bold text-ink-100 mb-6 leading-tight">
        The web app
      </h2>
      <p className="text-xl text-ink-400 max-w-2xl">
        Paste a URL. See the metadata. 
      </p>
      <p className="text-xl text-ink-400 max-w-2xl">
        Filter. Download. No installation required.
      </p>
      <p className="font-mono text-ember-400/70 text-lg mt-8">ezesri.com</p>
    </div>
  )
}

function DemoCli() {
  return (
    <div className="flex flex-col items-center justify-center text-center">
      <div className="w-16 h-16 rounded-xl bg-ink-800/60 flex items-center justify-center mb-8">
        <svg className="w-9 h-9 text-ember-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-4">Demo</p>
      <h2 className="text-4xl sm:text-5xl font-bold text-ink-100 mb-6 leading-tight">
        The command line
      </h2>
      <p className="text-xl text-ink-400 max-w-2xl">
        For bigger jobs, automation and scripting.
      </p>
      <div className="mt-10 rounded-xl bg-ink-950 border border-ink-800 p-6 text-left font-mono max-w-2xl w-full">
        <p className="text-ink-500 text-sm mb-3"># Install</p>
        <p className="text-ink-200">pip install ezesri</p>
        <p className="text-ink-500 text-sm mt-5 mb-3"># Inspect a layer</p>
        <p className="text-ink-200">ezesri metadata &lt;URL&gt;</p>
        <p className="text-ink-500 text-sm mt-5 mb-3"># Extract with a filter</p>
        <p className="text-ink-200">ezesri fetch &lt;URL&gt; --where &quot;STATUS = &apos;ACTIVE&apos;&quot; --format csv</p>
        <p className="text-ink-500 text-sm mt-5 mb-3"># Bulk export an entire service</p>
        <p className="text-ink-200">ezesri bulk-fetch &lt;SERVICE_URL&gt; ./output --format gpkg --workers 4</p>
      </div>
    </div>
  )
}

function PythonLibrary() {
  return (
    <div className="max-w-3xl">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-4">Python library</p>
      <h2 className="text-4xl sm:text-5xl font-bold text-ink-100 mb-10 leading-tight">
        Four lines to data
      </h2>
      <div className="rounded-xl bg-ink-950 border border-ink-800 p-8 font-mono text-base leading-relaxed">
        <p className="text-ink-500">import ezesri</p>
        <p className="text-ink-200 mt-4">
          <span className="text-ink-500">url = </span>
          <span className="text-ember-400/80">&quot;https://gis.countyofriverside.us/.../MapServer/8&quot;</span>
        </p>
        <p className="text-ink-200 mt-6">
          <span className="text-ink-500">gdf = </span>
          ezesri.extract_layer(url, where=<span className="text-ember-400/80">&quot;APN LIKE &apos;750%&apos;&quot;</span>)
        </p>
        <p className="text-ink-200 mt-2">
          gdf.to_file(<span className="text-ember-400/80">&quot;parcels.gpkg&quot;</span>, driver=<span className="text-ember-400/80">&quot;GPKG&quot;</span>)
        </p>
      </div>
      <p className="text-lg text-ink-400 mt-8">
        Returns a GeoDataFrame. Filter, join, plot, export. Whatever you need!
      </p>
    </div>
  )
}

function WhenToUseWhat() {
  return (
    <div className="max-w-4xl">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-4">Choose your path</p>
      <h2 className="text-4xl sm:text-5xl font-bold text-ink-100 mb-12 leading-tight">
        When to use what
      </h2>
      <div className="space-y-4">
        {[
          { scenario: 'Quick grab, under 100K features', use: 'Web app' },
          { scenario: 'Large or filtered dataset', use: 'CLI' },
          { scenario: 'Bulk download, all layers', use: 'CLI with bulk-fetch' },
          { scenario: 'Discover available data', use: 'Directory' },
          { scenario: 'Scripted pipeline, repeatable', use: 'Python library' },
        ].map((item) => (
          <div key={item.scenario} className="flex items-center gap-6 p-5 rounded-lg bg-ink-900/40 border border-ink-800">
            <span className="text-lg text-ink-300 flex-1">{item.scenario}</span>
            <span className="font-medium text-ember-400 text-lg">{item.use}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function GetStarted() {
  return (
    <div className="flex flex-col items-center justify-center text-center">
      <p className="text-sm font-medium text-ember-400 uppercase tracking-wider mb-6">Get started</p>
      <h2 className="text-4xl sm:text-5xl font-bold text-ink-100 mb-12 leading-tight">
        Everything you need
      </h2>
      <div className="grid sm:grid-cols-2 gap-6 max-w-2xl w-full text-left">
        {[
          { label: 'Web app', value: 'ezesri.com', href: 'https://ezesri.com' },
          { label: 'Directory', value: 'ezesri.com/directory', href: 'https://ezesri.com/directory' },
          { label: 'Install', value: 'pip install ezesri', href: null },
          { label: 'Docs', value: 'ezesri.com/docs', href: 'https://ezesri.com/docs' },
          { label: 'Source', value: 'github.com/stiles/ezesri', href: 'https://github.com/stiles/ezesri' },
          { label: 'Journalist tips', value: 'ezesri.com/docs/journalists', href: 'https://www.ezesri.com/docs/journalists' },
        ].map((item) => (
          <div key={item.label} className="p-5 rounded-xl bg-ink-900/40 border border-ink-800">
            <p className="text-sm text-ink-500 mb-1">{item.label}</p>
            {item.href ? (
              <a href={item.href} target="_blank" rel="noopener noreferrer" className="font-mono text-lg text-ember-300 hover:text-ember-200 transition-colors">
                {item.value}
              </a>
            ) : (
              <p className="font-mono text-lg text-ember-300">{item.value}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function Questions() {
  return (
    <div className="flex flex-col items-center justify-center text-center">
      <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-ember-500 to-ember-600 flex items-center justify-center mb-8">
        <svg className="w-12 h-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
      </div>
      <h2 className="text-5xl sm:text-6xl font-bold text-ink-200 mb-6">Questions?</h2>
      <p className="text-xl text-ink-400 mt-4">
        Matt Stiles
      </p>
      <div className="flex items-center gap-5 mt-6 text-ink-200">
        <a href="https://mattstiles.me" target="_blank" rel="noopener noreferrer" className="hover:text-ink-300 transition-colors">
          mattstiles.me
        </a>
        <span className="text-ink-500">•</span>
        <a href="https://ezesri.com/nicar" target="_blank" rel="noopener noreferrer" className="hover:text-ink-300 transition-colors">
        ezesri.com/nicar
        </a>
        <span className="text-ink-500">•</span>
        <a href="https://github.com/stiles/ezesri" target="_blank" rel="noopener noreferrer" className="hover:text-ink-300 transition-colors">
          github.com/stiles/ezesri
        </a>
      </div>
    </div>
  )
}

// ─── Slide deck ──────────────────────────────────────────────────────────────

const slides: Slide[] = [
  { id: 'title', content: <Title /> },
  { id: 'palm-springs', content: <PalmSpringsPool /> },
  { id: 'problem', content: <TheProblem /> },
  { id: 'one-off-script', content: <OneOffScript /> },
  { id: 'seen-wildfires', content: <SeenThisWildfires /> },
  { id: 'seen-measles', content: <SeenThisMeasles /> },
  { id: 'raw-esri-1', content: <RawEsriPage1 /> },
  { id: 'raw-esri-2', content: <RawEsriPage2 /> },
  { id: 'audience', content: <AudienceCheck /> },
  { id: 'options', content: <ExistingOptions /> },
  { id: 'what', content: <WhatIsEzesri /> },
  { id: 'numbers', content: <TheNumbers /> },
  { id: 'formats', content: <OutputFormats /> },
  { id: 'directory', content: <TheDirectory /> },
  { id: 'how', content: <HowItWorks /> },
  { id: 'demo-web', content: <DemoWeb /> },
  { id: 'demo-cli', content: <DemoCli /> },
  { id: 'python', content: <PythonLibrary /> },
  { id: 'when', content: <WhenToUseWhat /> },
  { id: 'start', content: <GetStarted /> },
  { id: 'questions', content: <Questions /> },
]

// ─── Presenter component ─────────────────────────────────────────────────────

export default function NicarPresentation() {
  const [current, setCurrent] = useState(0)
  const [isTransitioning, setIsTransitioning] = useState(false)

  const goTo = useCallback((index: number) => {
    if (index < 0 || index >= slides.length || index === current) return
    setIsTransitioning(true)
    setTimeout(() => {
      setCurrent(index)
      setIsTransitioning(false)
    }, 150)
  }, [current])

  const next = useCallback(() => goTo(current + 1), [current, goTo])
  const prev = useCallback(() => goTo(current - 1), [current, goTo])

  // Keyboard navigation
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
        e.preventDefault()
        next()
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        e.preventDefault()
        prev()
      } else if (e.key === 'Home') {
        e.preventDefault()
        goTo(0)
      } else if (e.key === 'End') {
        e.preventDefault()
        goTo(slides.length - 1)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [next, prev, goTo])

  return (
    <div className="min-h-screen bg-ink-950 relative overflow-hidden select-none">
      {/* Slide content */}
      <div
        className={`min-h-screen flex items-center justify-center px-8 sm:px-16 py-16 transition-opacity duration-150 ${
          isTransitioning ? 'opacity-0' : 'opacity-100'
        }`}
      >
        {slides[current].content}
      </div>

      {/* Navigation controls */}
      <div className="fixed bottom-0 left-0 right-0 flex items-center justify-between px-6 py-4">
        {/* Slide counter */}
        <span className="text-sm font-mono text-ink-600">
          {current + 1} / {slides.length}
        </span>

        {/* Arrow buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={prev}
            disabled={current === 0}
            className="p-2 rounded-lg text-ink-600 hover:text-ink-300 hover:bg-ink-800/50 disabled:opacity-20 disabled:cursor-default transition-all"
            aria-label="Previous slide"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={next}
            disabled={current === slides.length - 1}
            className="p-2 rounded-lg text-ink-600 hover:text-ink-300 hover:bg-ink-800/50 disabled:opacity-20 disabled:cursor-default transition-all"
            aria-label="Next slide"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Progress bar */}
      <div className="fixed top-0 left-0 right-0 h-0.5 bg-ink-900">
        <div
          className="h-full bg-ember-500 transition-all duration-300 ease-out"
          style={{ width: `${((current + 1) / slides.length) * 100}%` }}
        />
      </div>
    </div>
  )
}
