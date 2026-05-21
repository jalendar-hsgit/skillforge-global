const fs = require('fs');
const path = require('path');

const OUT_DIR = path.join(__dirname, '..', 'public', 'templates');
if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

const FALLBACK_TEMPLATES = [
  'modern-pro','corporate','tech-stack','software','data','exec-black','minimal-blue','sleek','healthcare','c-suite','gray','senior','traditional','devops','vp','gradient','startup','security','nursing','marketing','clinical','banking','innovative','board','content','academic','dark-pro','designer','creative-bold','artistic'
];

function slugify(name) {
  return name.toString().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

function makeSVG(name, category) {
  const slug = slugify(name);
  const title = name;
  const cat = category || '';
  const svg = `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1600" viewBox="0 0 1200 1600">\n  <defs>\n    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">\n      <stop offset="0%" stop-color="#3b82f6"/>\n      <stop offset="50%" stop-color="#8b5cf6"/>\n      <stop offset="100%" stop-color="#ec4899"/>\n    </linearGradient>\n    <filter id="f1" x="-20%" y="-20%" width="140%" height="140%">\n      <feOffset result="offOut" in="SourceAlpha" dx="0" dy="6" />\n      <feGaussianBlur result="blurOut" in="offOut" stdDeviation="12" />\n      <feBlend in="SourceGraphic" in2="blurOut" mode="normal" />\n    </filter>\n  </defs>\n  <rect width="100%" height="100%" fill="url(#g1)" />\n  <g transform="translate(80,120)">\n    <rect x="0" y="0" width="1040" height="1360" rx="24" fill="#ffffff" opacity="0.06" />\n    <g transform="translate(48,48)">\n      <rect x="0" y="0" width="944" height="270" rx="12" fill="rgba(255,255,255,0.06)" />\n      <text x="20" y="110" font-family="Inter, Roboto, sans-serif" font-size="48" font-weight="700" fill="#ffffff">${title}</text>\n      <text x="20" y="160" font-family="Inter, Roboto, sans-serif" font-size="20" fill="#ffffff" opacity="0.9">${cat}</text>\n      <rect x="20" y="200" width="900" height="6" rx="3" fill="#ffffff" opacity="0.08" />\n    </g>\n    <g transform="translate(48,360)">\n      <rect x="0" y="0" width="448" height="220" rx="8" fill="#ffffff" opacity="0.04" />\n      <rect x="496" y="0" width="448" height="220" rx="8" fill="#ffffff" opacity="0.04" />\n      <rect x="0" y="248" width="944" height="76" rx="8" fill="#ffffff" opacity="0.025" />\n    </g>\n  </g>\n</svg>`;
  return svg;
}

async function fetchTemplatesFromApi() {
  try {
    // Use native fetch if available (Node 18+), otherwise skip
    if (typeof fetch === 'undefined') {
      console.log('Fetch not available, using fallback template list');
      return null;
    }
    
    const url = process.env.API_BASE || 'http://localhost:8001';
    const res = await fetch(`${url}/api/v1x/resume-templates`);
    if (!res.ok) {
      console.warn('Templates API responded with', res.status);
      return null;
    }
    const json = await res.json();
    return json.map(t => ({ name: t.name || t.id, category: t.category || '', slug: t.slug || slugify(t.name || String(t.id)) }));
  } catch (e) {
    console.warn('Failed to fetch templates from API:', e.message);
    return null;
  }
}

(async () => {
  let templates = null;
  templates = await fetchTemplatesFromApi();
  if (!templates) {
    templates = FALLBACK_TEMPLATES.map(name => ({ name, category: 'Generated', slug: slugify(name) }));
  }

  for (const t of templates) {
    const name = t.name;
    const cat = t.category || '';
    const slug = t.slug || slugify(name);
    const svg = makeSVG(name, cat);
    const outPath = path.join(OUT_DIR, `${slug}.svg`);
    fs.writeFileSync(outPath, svg, 'utf8');
    console.log('Wrote', outPath);
  }

  console.log('Preview generation complete.');
})();
