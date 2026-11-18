import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const here = dirname(fileURLToPath(import.meta.url))
const reviewDir = resolve(here, '../../REVIEW')
const codexPy = resolve(here, '../../tools/codex.py')
const PYTHON = process.env.PYTHON || 'python'

/**
 * La review ecrit les DEUX codex, et seulement s'ils passent le vrai
 * validateur (`tools/codex.py`, memes schemas que la CI). Un export refuse
 * n'ecrit rien : pas de fichier a moitie bon dans REVIEW/.
 */
function checkCodex(kind, text) {
  const dir = mkdtempSync(join(tmpdir(), 'codex-'))
  try {
    const path = join(dir, kind === 'postprod' ? 'codex_postprod.json' : 'codex_render.json')
    writeFileSync(path, text, 'utf8')
    const res = spawnSync(PYTHON, [codexPy, 'check', path, '--kind', kind], {
      encoding: 'utf8',
      env: { ...process.env, PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1' },
    })
    if (res.error) return { ok: false, error: `validateur indisponible: ${res.error.message}` }
    if (res.status !== 0) return { ok: false, error: (res.stdout || res.stderr || '').trim().split('\n').slice(-3).join(' | ') }
    return { ok: true, output: (res.stdout || '').trim() }
  } finally {
    rmSync(dir, { recursive: true, force: true })
  }
}

function saveCodexMiddleware(req, res, next) {
  const path = (req.url || '').split('?')[0]
  if (path !== '/api/save-codex' || req.method !== 'POST') {
    next()
    return
  }
  const chunks = []
  req.on('data', (chunk) => chunks.push(chunk))
  req.on('end', () => {
    const send = (code, body) => {
      res.statusCode = code
      res.setHeader('Content-Type', 'application/json')
      res.end(JSON.stringify(body))
    }
    try {
      const raw = Buffer.concat(chunks).toString('utf8')
      const body = JSON.parse(raw)
      const render = String(body.render || '')
      const postprod = String(body.postprod || '')
      if (!render || !postprod) return send(400, { ok: false, error: 'render et postprod requis' })
      const r1 = checkCodex('render', render)
      if (!r1.ok) return send(400, { ok: false, error: `codex_render refuse: ${r1.error}` })
      const r2 = checkCodex('postprod', postprod)
      if (!r2.ok) return send(400, { ok: false, error: `codex_postprod refuse: ${r2.error}` })
      mkdirSync(reviewDir, { recursive: true })
      writeFileSync(join(reviewDir, 'codex_render.json'), render.endsWith('\n') ? render : `${render}\n`, 'utf8')
      writeFileSync(join(reviewDir, 'codex_postprod.json'), postprod.endsWith('\n') ? postprod : `${postprod}\n`, 'utf8')
      send(200, { ok: true, paths: ['REVIEW/codex_render.json', 'REVIEW/codex_postprod.json'] })
    } catch (err) {
      send(400, { ok: false, error: String(err.message || err) })
    }
  })
}

function saveCodexPlugin() {
  return {
    name: 'save-codex',
    configureServer(server) {
      server.middlewares.use(saveCodexMiddleware)
    },
    configurePreviewServer(server) {
      server.middlewares.use(saveCodexMiddleware)
    },
  }
}

export default defineConfig({
  plugins: [react(), saveCodexPlugin()],
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
