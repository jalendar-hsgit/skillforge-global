#!/usr/bin/env node
// Simple UI export tester: hits Next.js session proxy to fetch resume export via browser-like path.
// Usage: node backend/test-export-ui.mjs <resumeId?> <format=pdf?> <apiBase?>
// Reads cookies from backend/cookies.txt (expects a line like: token=...)

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const [, , argId, argFormat, argApi] = process.argv;
const format = (argFormat || process.env.EXPORT_FORMAT || 'pdf').toLowerCase();
const apiBase = (argApi || process.env.UI_API_BASE || 'http://localhost:3001').replace(/\/$/, '');

function readCookie() {
  const p = path.join(__dirname, 'cookies.txt');
  if (!fs.existsSync(p)) return '';
  const content = fs.readFileSync(p, 'utf8').trim();
  // allow multi-line, take first non-empty
  const line = content.split(/\r?\n/).map(s => s.trim()).find(Boolean) || '';
  return line; // e.g., token=....
}

function pickIdFromList(json) {
  if (!json) return null;
  // Support either array or {items:[...]}
  const list = Array.isArray(json) ? json : (Array.isArray(json.items) ? json.items : []);
  if (list.length === 0) return null;
  const first = list[0];
  return first.id || first.resume_id || first.uuid || null;
}

async function getFirstResumeId(cookie) {
  const url = `${apiBase}/api/session/v1x/resumes?limit=1`;
  const r = await fetch(url, { headers: { cookie } });
  if (!r.ok) throw new Error(`Failed to list resumes: ${r.status}`);
  const json = await r.json();
  const id = pickIdFromList(json);
  if (!id) throw new Error('No resume id found');
  return id;
}

function extFromFormat(fmt) {
  if (fmt === 'pdf') return 'pdf';
  if (fmt === 'docx' || fmt === 'word') return 'docx';
  if (fmt === 'txt' || fmt === 'text') return 'txt';
  return fmt;
}

async function main() {
  const cookie = readCookie();
  if (!cookie) {
    console.error('No cookie found in backend/cookies.txt; put "token=..." there');
    process.exit(2);
  }

  let resumeId = argId;
  if (!resumeId) {
    resumeId = await getFirstResumeId(cookie);
    console.log(`[info] Using first resume id: ${resumeId}`);
  }

  const url = `${apiBase}/api/session/v1x/resumes/${encodeURIComponent(resumeId)}/export?format=${encodeURIComponent(format)}`;
  console.log(`[fetch] GET ${url}`);
  const r = await fetch(url, { headers: { cookie } });
  const disp = r.headers.get('content-disposition') || '';
  const dbg = r.headers.get('x-debug-target') || '';
  console.log(`[resp] status=${r.status} content-type=${r.headers.get('content-type')}`);
  if (disp) console.log(`[resp] content-disposition=${disp}`);
  if (dbg) console.log(`[resp] x-debug-target=${dbg}`);

  if (!r.ok) {
    const text = await r.text().catch(() => '');
    console.error(`[error] Body: ${text}`);
    process.exit(1);
  }

  // Write file
  const data = new Uint8Array(await r.arrayBuffer());
  let filename = 'export';
  const m = /filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/i.exec(disp);
  const ext = extFromFormat(format);
  if (m) filename = decodeURIComponent(m[1] || m[2] || filename);
  if (!filename.toLowerCase().endsWith(`.${ext}`)) filename += `.${ext}`;
  const outPath = path.join(__dirname, filename);
  fs.writeFileSync(outPath, data);
  console.log(`[saved] ${outPath} (${data.length} bytes)`);
}

main().catch((e) => {
  console.error(e?.stack || e?.message || String(e));
  process.exit(1);
});
