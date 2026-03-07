# ezesri -- slide content

Slide-by-slide content for the NICAR 2026 presentation. Format-agnostic: port to Google Slides, Keynote, Reveal.js or Marp as needed. One idea per slide, large fonts.

---

## Slide 1: Title

**ezesri**  
Unlocking government GIS data without the pain

NICAR 2026

---

## Slide 2: Palm Springs pool

[full-screen image: palm-springs-pool.png]

Caption: "Palm Springs, last summer"

---

## Slide 3: The problem

Thousands of government agencies publish geospatial data through Esri ArcGIS REST services.

Parcels. Crime. Elections. Zoning. Infrastructure. Environmental data.

Getting that data out? That's the hard part.

---

## Slide 4: Before ezesri

[full-screen: one-off-script-example.png]

I was writing one-off extraction scripts for every project

A script I wrote for an LA trees project — 53 lines just to download one layer

---

## Slide 4: You've seen this before

[full-screen: noaa_wildfires.png]

NOAA / USGS wildfire map -- powered by Esri ArcGIS

---

## Slide 4: You've seen this too

[full-screen: johns_hopkins_measles.png]

Johns Hopkins measles case tracker -- powered by Esri ArcGIS

---

## Slide 5: What you actually see (1)

[full-screen: ezesri-mlb-1.png]

This is what an Esri REST endpoint looks like

MLB stadiums layer -- service metadata

---

## Slide 6: What you actually see (2)

[full-screen: ezesri-mlb-2.png]

Not exactly user-friendly

Field definitions -- JSON formatting, SQL types, technical metadata

---

## Slide 7: Audience check

Quick show of hands:

Who has ever tried to download data from an ArcGIS REST endpoint?

How did that go?

---

## Slide 8: The existing options

| Tool | Downside |
|------|----------|
| ArcGIS Hub | Click-through interface, one layer at a time, limited filtering |
| ArcGIS API for Python | Heavy dependencies, overkill for simple extraction |
| esri-dump / pysridump | Not actively maintained, limited formats |
| ogr2ogr (GDAL) | Powerful but complex, not Python-native |

---

## Slide 7: What is ezesri?

A lightweight toolkit for extracting data from Esri REST endpoints.

Three ways in:

1. **Web app** -- no installation, works in any browser
2. **Python CLI** -- for power users and automation
3. **Service directory** -- discover what's out there

---

## Slide 8: The numbers

- **24,600+** public ArcGIS services cataloged
- **120,000+** individual layers
- **34** categories (parcels, crime, elections, health, environment ...)
- **15.9 billion** total views across cataloged services

---

## Slide 9: Output formats

| Format | Best for |
|--------|----------|
| CSV | Spreadsheets, quick analysis |
| GeoJSON | Web mapping, QGIS |
| Shapefile | Legacy GIS workflows |
| GeoPackage | Modern GIS, multi-layer |
| GeoParquet | Big data, columnar analysis |
| NDJSON | Streaming, piping |

---

## Slide 10: The directory

[screenshot of ezesri.com/directory]

Browse and search 24,600+ public services from government agencies worldwide.

Filter by 34 categories. Sort by popularity. One-click extraction.

---

## Slide 11: How the directory is built

1. Harvest ArcGIS Online portal by 34 category queries
2. Enrich results with service-level metadata
3. Extract place names from tags, owners, attribution
4. Deduplicate and sort by popularity
5. Publish to ezesri.com/directory

---

## Slide 12: How extraction works

```
Your browser (or CLI)
        |
    ezesri API
        |
  Esri REST service
        |
  "Here are 1,000 records" (max per request)
        |
  ezesri: "Great, give me the next 1,000"
        |
  ... (repeat until done)
        |
  Complete dataset
```

Esri services cap responses (usually 1,000-2,000 records). ezesri handles pagination automatically so you get everything.

---

## Slide 13: Demo time -- web app

Let's extract some real data.

[switch to browser]

---

## Slide 14: Demo time -- CLI

For bigger jobs, automation and scripting.

[switch to terminal]

---

## Slide 15: When to use what

| Scenario | Use |
|----------|-----|
| Quick grab, under 100K features | Web app |
| Large dataset, filtered extract | CLI |
| Bulk download, all layers | CLI with `bulk-fetch` |
| Discover available data | Directory |
| Scripted pipeline, repeatable | Python library |

---

## Slide 16: Get started

**Web app**: [ezesri.com](https://ezesri.com)  
**Directory**: [ezesri.com/directory](https://ezesri.com/directory)  
**Install**: `pip install ezesri`  
**Docs**: [ezesri.com/docs](https://ezesri.com/docs)  
**Source**: [github.com/mstiles/ezesri](https://github.com/mstiles/ezesri)

---

## Slide 17: Questions?

[contact info]
