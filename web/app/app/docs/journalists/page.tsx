import { Metadata } from 'next'
import Markdown from '@/components/Markdown'

export const metadata: Metadata = {
  title: 'Tips for Journalists - ezesri',
  description: 'How journalists can use ezesri and ArcGIS data for investigative reporting. Search tips, story ideas, and hidden data sources.',
  openGraph: {
    title: 'Tips for Journalists - ezesri',
    description: 'How journalists can use ezesri and ArcGIS data for investigative reporting.',
  },
}

const content = `# Tips for journalists

Local governments often publish spatial data to Esri before (or instead of) posting it anywhere else. Their GIS department is sometimes more open than their records office. Here's how to find stories in that data.

## You don't need GIS software or coding skills!

Just because these data sets are geospatial doesn't mean you need to map them. The web app exports to **CSV** — open layers in Excel, Google Sheets or R/Python. 

Point data includes lat/lon columns automatically. For polygons, you still get all the attribute data in a spreadsheet-friendly format.

## Search the directory

Use the [data directory](/directory) to search by keyword. Try your city or county name plus these terms:

### Local development

- **"permits"** or **"building permits"** — Shows where construction is happening before it's announced
- **"zoning"** — Rezoning requests often signal coming development fights
- **"TIF"** or **"tax increment"** — Public subsidies to developers, often underreported
- **"assessments"** or **"property"** — Property values, ownership changes, sales history

### Environment

- **"brownfield"** — Contaminated sites awaiting cleanup
- **"lead"** — Lead service lines (a major issue in older cities)
- **"flood"** or **"FEMA"** — Flood zone maps, damage assessments
- **"stormwater"** or **"sewer"** — Infrastructure age and condition
- **"air quality"** — Monitoring stations, often near industrial areas

### Public safety

- **"incidents"** or **"911"** — Often more granular than published crime stats
- **"fire"** — Fire incident locations, response times
- **"code violations"** — Slumlords, housing conditions
- **"crashes"** or **"traffic"** — Accident patterns, dangerous intersections
- **"police"** — Police station locations

### Hidden gems

- **"vacant"** — Vacant property registries reveal blight patterns
- **"foreclosure"** — Often published before it hits court records
- **"inspections"** — Restaurant health scores, rental inspections
- **"ownership"** — Parcel data sometimes includes owner names and addresses

## Story ideas

### 1. The permit map
Download building permits for the last year. Map them. Are permits clustered in wealthy areas? Are there neighborhoods with zero investment? Compare to demographic data.

### 2. Flood zone + development
Overlay new construction permits with FEMA flood zones. Are developers building in flood-prone areas? Who approved the permits? (You could do the same with wildfire prone areas).

### 3. Crime and public safety
Download crime data for the last year. Map it. Are crimes clustered in wealthy areas? Are there strange geospatial patterns with crime categories in neighborhoods? Hint: Try this for Washington, DC. You'll see the patterns right away. 

## Pro tips

1. **Check the layer count** — Services with 10+ layers often contain the full database, not just a curated slice

2. **Look at field names** — Fields like \`OWNER_NAME\`, \`ASSESSED_VALUE\`, or \`VIOLATION_DATE\` tell you what's really in the data

3. **Filter before downloading** — Use SQL WHERE or Python subsetting to get just what you need (e.g., \`YEAR = 2024\` or \`STATUS = 'OPEN'\`). You can do this with the web app or Python library. 

4. **Compare over time** — Download the same layer monthly. Changes in the data *are* the story.

5. **FOIA the metadata** — If you find an interesting layer, FOIA the agency for the data dictionary and update schedule. The Python library has a function for extracting the complete metadata in a useful format.

## Need help?

For large datasets (100K+ features), use the [Python CLI](/docs/installation) instead of the web app. It has no limits and can export to more formats.

\`\`\`bash
pip install ezesri
ezesri fetch <URL> --format geojson --out data.geojson
\`\`\`

Questions? Reach out on [GitHub](https://github.com/stiles/ezesri/issues) or via email at [mattstiles@gmail.com](mailto:mattstiles@gmail.com).
`

export default function JournalistsPage() {
  return <Markdown content={content} />
}
