import { Metadata } from 'next'
import Markdown from '@/components/Markdown'

export const metadata: Metadata = {
  title: 'Developer guide - ezesri',
  description: 'Set up a development environment, run tests and contribute to ezesri.',
}

const content = `# Developer guide

This guide provides instructions for setting up a development environment, running tests, and contributing to \`ezesri\`.

## Setting up a development environment

To get started, clone the repository and install the package in editable mode with the \`docs\` extras:

\`\`\`bash
git clone https://github.com/stiles/ezesri.git
cd ezesri
pip install -e .[docs]
\`\`\`

## Running tests

This project uses \`pytest\` for unit testing. To run the test suite, simply run the following command:

\`\`\`bash
pytest
\`\`\`

For more details, see the [testing guide](/docs/testing).

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss your ideas.

### Code style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for public functions

### Pull request process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request
`

export default function DeveloperPage() {
  return <Markdown content={content} />
}
