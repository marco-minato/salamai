// Verifica che il visualizzatore resti in sola lettura: nessuna richiesta
// diversa da GET, nessun canale verso dispositivi o servizi, nessuna scrittura.
// Uso: node scripts/check-readonly.mjs   (dopo npm run build)
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const walk = (d) => readdirSync(d).flatMap((f) => {
  const p = join(d, f);
  return statSync(p).isDirectory() ? walk(p) : [p];
});

const FORBIDDEN_SRC = [
  [/method\s*:\s*['"](POST|PUT|PATCH|DELETE)['"]/i, 'richiesta HTTP in scrittura'],
  [/\bXMLHttpRequest\b/, 'XMLHttpRequest'],
  [/\bWebSocket\b/, 'WebSocket'],
  [/\bEventSource\b/, 'EventSource'],
  [/sendBeacon/, 'navigator.sendBeacon'],
  [/localStorage\.setItem|indexedDB/, 'scrittura persistente nel browser'],
  [/https?:\/\//, 'URL assoluto (risorse o servizi esterni)'],
  [/homeassistant|\/api\/services|esphome/i, 'riferimento a servizi di attuazione'],
];
const FORBIDDEN_DIST = [
  [/\bnew WebSocket\b/, 'WebSocket nel bundle'],
  [/sendBeacon/, 'sendBeacon nel bundle'],
  [/new EventSource/, 'EventSource nel bundle'],
  [/<script[^>]+src=["']https?:/i, 'script da CDN'],
  [/<link[^>]+href=["']https?:/i, 'risorsa da CDN'],
];

let problems = 0;
for (const f of walk(join(root, 'src'))) {
  const txt = readFileSync(f, 'utf8');
  for (const [re, what] of FORBIDDEN_SRC) {
    if (re.test(txt)) {
      console.error(`✗ ${f}: ${what}`);
      problems++;
    }
  }
  for (const m of txt.matchAll(/fetch\(([^)]*)\)/g)) {
    if (!/method:\s*'GET'/.test(m[1])) {
      console.error(`✗ ${f}: fetch senza method 'GET' esplicito: ${m[0]}`);
      problems++;
    }
  }
}
let distFiles = [];
try {
  distFiles = walk(join(root, 'dist')).filter((f) => /\.(js|html|css)$/.test(f));
} catch {
  console.error('✗ dist/ assente: eseguire npm run build');
  problems++;
}
for (const f of distFiles) {
  const txt = readFileSync(f, 'utf8');
  for (const [re, what] of FORBIDDEN_DIST) {
    if (re.test(txt)) {
      console.error(`✗ ${f}: ${what}`);
      problems++;
    }
  }
}
if (problems) {
  console.error(`${problems} problemi: il visualizzatore non è in sola lettura`);
  process.exit(1);
}
console.log(`✓ sola lettura: ${walk(join(root, 'src')).length} sorgenti e ${distFiles.length} file del bundle controllati`);
