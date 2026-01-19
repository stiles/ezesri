# ezesri Web Frontend

Next.js + Tailwind CSS frontend for the ezesri web interface.

## Development

```bash
# Install dependencies
npm install

# Create .env.local with your API URL
cp .env.example .env.local

# Start dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment variables

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Lambda Function URL from backend deployment |

## Deployment

### Option 1: Vercel (recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy (first time - will prompt to link project)
vercel

# Deploy to production
vercel --prod
```

Set `NEXT_PUBLIC_API_URL` in Vercel project settings → Environment Variables.

### Option 2: Static export

```bash
# Build static export
npm run build

# Output in .next/standalone/
```

Can be deployed to any static hosting (S3, Netlify, etc).

## Tech stack

- [Next.js 14](https://nextjs.org/) - React framework
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [TypeScript](https://www.typescriptlang.org/) - Type safety
