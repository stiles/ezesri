import { Metadata } from 'next'
import Markdown from '@/components/Markdown'

export const metadata: Metadata = {
  title: 'Installation - ezesri',
  description: 'How to install ezesri from PyPI. Requirements, optional dependencies and development setup.',
}

const content = `# Installation

You can install \`ezesri\` from PyPI using \`pip\`:

\`\`\`bash
pip install ezesri
\`\`\`

## Requirements

- Python 3.8 or higher
- geopandas and its dependencies (installed automatically)

## Optional dependencies

For certain output formats, you may need additional system libraries:

- **File Geodatabase** - Requires GDAL with FileGDB driver
- **GeoParquet** - Requires pyarrow

## Development installation

To install for development:

\`\`\`bash
git clone https://github.com/stiles/ezesri.git
cd ezesri
pip install -e .[docs]
\`\`\`
`

export default function InstallationPage() {
  return <Markdown content={content} />
}
