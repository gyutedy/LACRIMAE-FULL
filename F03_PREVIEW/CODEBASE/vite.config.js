import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const here = dirname(fileURLToPath(import.meta.url))
const reviewOut = resolve(here, '../../REVIEW/sanguinala_review.json')

function saveReviewMiddleware(req, res, next) {
  const path = (req.url || '').split('?')[0]
  if (path !== '/api/save-review' || req.method !== 'POST') {
    next()
    return
  }
  const chunks = []
  req.on('data', (chunk) => chunks.push(chunk))
  req.on('end', () => {
    try {
      const raw = Buffer.concat(chunks).toString('utf8')
      JSON.parse(raw)
      mkdirSync(dirname(reviewOut), { recursive: true })
      writeFileSync(reviewOut, raw.endsWith('\n') ? raw : `${raw}\n`, 'utf8')
      res.statusCode = 200
      res.setHeader('Content-Type', 'application/json')
      res.end(JSON.stringify({ ok: true, path: 'REVIEW/sanguinala_review.json' }))
    } catch (err) {
      res.statusCode = 400
      res.setHeader('Content-Type', 'application/json')
      res.end(JSON.stringify({ ok: false, error: String(err.message || err) }))
    }
  })
}

function saveReviewPlugin() {
  return {
    name: 'save-review',
    configureServer(server) {
      server.middlewares.use(saveReviewMiddleware)
    },
    configurePreviewServer(server) {
      server.middlewares.use(saveReviewMiddleware)
    },
  }
}

export default defineConfig({
  plugins: [react(), saveReviewPlugin()],
  base: './',
  server: {
    host: true,
    port: 5174,
    allowedHosts: ['.monkeycode-ai.live'],
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
})
