import Markdown from '@/components/Markdown'

const content = `# Welcome to ezesri

\`ezesri\` is a lightweight Python package for extracting data and metadata from Esri REST API endpoints. It provides a modular API and optional CLI for exporting feature layers and metadata to common formats, with robust handling of Esri-specific pagination and filtering.

## Features

- **Simple API** - Fetch metadata and extract layers with just a few lines of Python
- **CLI included** - Quick data extraction from the command line
- **Multiple formats** - Export to GeoJSON, Shapefile, GeoPackage, File Geodatabase, GeoParquet and more
- **Pagination handling** - Automatically handles Esri's feature limits
- **Filtering** - Filter by attributes or bounding box

## Quick start

Install from PyPI:

\`\`\`bash
pip install ezesri
\`\`\`

Extract a layer:

\`\`\`python
import ezesri

url = "https://services.arcgis.com/.../FeatureServer/0"
gdf = ezesri.extract_layer(url)
gdf.to_file("output.geojson", driver="GeoJSON")
\`\`\`

Or use the CLI:

\`\`\`bash
ezesri fetch <URL> --format geojson --out output.geojson
\`\`\`

## Web app

Don't have Python installed? Use the [web app](/) to extract GeoJSON directly in your browser.
`

export default function DocsPage() {
  return <Markdown content={content} />
}
