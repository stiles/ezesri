# ezesri Web

Web interface for ezesri - extract data from Esri REST services without installing Python.

## Architecture

```
┌─────────────────┐         ┌─────────────────────────┐
│                 │         │                         │
│  Next.js App    │────────▶│  AWS Lambda             │
│  (Vercel)       │         │  (Function URL)         │
│                 │         │                         │
└─────────────────┘         └───────────┬─────────────┘
                                        │
                                        ▼
                            ┌─────────────────────────┐
                            │                         │
                            │  Esri REST Services     │
                            │                         │
                            └─────────────────────────┘
```

## Quick start

### 1. Deploy the backend (Lambda)

```bash
cd web/lambda

# Build
sam build

# Deploy (first time)
sam deploy --guided

# Note the Function URL from the output
```

### 2. Deploy the frontend (Vercel)

```bash
cd web/app

# Install dependencies
npm install

# Set your API URL (or use default: https://api.ezesri.com)
echo "NEXT_PUBLIC_API_URL=https://api.ezesri.com" > .env.local

# Deploy to Vercel
npx vercel --prod
```

Or set `NEXT_PUBLIC_API_URL` in Vercel dashboard under Settings → Environment Variables.

## Local development

### Backend

```bash
cd web/lambda
sam local start-api --port 3001
```

### Frontend

```bash
cd web/app
npm install
npm run dev
```

Frontend runs on http://localhost:3000, backend on http://localhost:3001.

## Directory structure

```
web/
├── lambda/           # AWS Lambda backend
│   ├── handler.py    # API handlers
│   ├── template.yaml # SAM template
│   └── README.md
│
└── app/              # Next.js frontend
    ├── app/          # App router pages
    ├── components/   # React components
    ├── lib/          # API client
    └── README.md
```

## Features

- **Metadata preview**: See layer name, fields, feature count, and extent
- **Filters**: SQL where clause and bounding box filters
- **Export formats**: GeoJSON and Shapefile (zipped)
- **No installation**: Works in any browser

## Costs

- **Lambda**: First 1M requests free, then ~$0.20/million
- **Vercel**: Free tier includes 100GB bandwidth
- **Total**: Essentially free for personal use
