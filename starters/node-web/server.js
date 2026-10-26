// 표준 모듈만 쓰는 최소 웹 서버: 정적 파일(public/) + JSON API(/api/...). 실행: node server.js (PORT, 기본 3000, 0.0.0.0)
const http = require('node:http')
const fs = require('node:fs')
const path = require('node:path')

const ROOT = path.join(__dirname, 'public')
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png' }
const items = []

const json = (res, code, obj) => { res.writeHead(code, { 'content-type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(obj)) }

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x')
  if (url.pathname === '/api/health') return json(res, 200, { ok: true })
  if (url.pathname === '/api/items' && req.method === 'GET') return json(res, 200, items)
  if (url.pathname === '/api/items' && req.method === 'POST') {
    let body = ''
    for await (const c of req) { body += c; if (body.length > 1e6) return json(res, 413, { error: 'too large' }) }
    let data
    try { data = JSON.parse(body || '{}') } catch { return json(res, 400, { error: 'invalid json' }) }
    const text = String(data.text ?? '').trim()
    if (!text) return json(res, 400, { error: 'text required' })
    items.push({ id: items.length + 1, text })
    return json(res, 201, items.at(-1))
  }
  // 정적 파일 (경로 탈출 막기)
  const file = path.normalize(path.join(ROOT, url.pathname === '/' ? 'index.html' : url.pathname))
  if (!file.startsWith(ROOT)) return json(res, 403, { error: 'forbidden' })
  fs.readFile(file, (err, buf) => {
    if (err) return json(res, 404, { error: 'not found' })
    res.writeHead(200, { 'content-type': TYPES[path.extname(file)] ?? 'application/octet-stream' })
    res.end(buf)
  })
})

const PORT = Number(process.env.PORT ?? 3000)
server.listen(PORT, '0.0.0.0', () => console.log(`listening on 0.0.0.0:${PORT}`))
