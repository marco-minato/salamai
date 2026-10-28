// Test end-to-end del visualizzatore su Chrome headless (desktop e telefono).
// Serve dist/ sotto un sottopercorso con un server statico minimo (solo GET),
// verifica funzioni, errori e sola lettura, salva screenshot.
//
// Uso: npm run build && node scripts/e2e.mjs [--out cartella] [--chrome /usr/bin/google-chrome]
import { createServer } from 'node:http';
import { existsSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, extname, join, normalize, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const arg = (name, def) => {
  const i = process.argv.indexOf(name);
  return i > 0 ? process.argv[i + 1] : def;
};
const OUT = resolve(arg('--out', join(root, 'e2e-output')));
const CHROME = arg('--chrome', process.env.CHROME ?? '/usr/bin/google-chrome');
const SUBPATH = '/salamai/room3d/';
mkdirSync(OUT, { recursive: true });

// ---------------------------------------------------------------- server statico
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.glb': 'model/gltf-binary', '.png': 'image/png' };
const dist = join(root, 'dist');
const requests = [];
const server = createServer((req, res) => {
  requests.push(`${req.method} ${req.url}`);
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.writeHead(405).end();
    return;
  }
  const url = new URL(req.url, 'http://x');
  if (!url.pathname.startsWith(SUBPATH)) {
    res.writeHead(404).end();
    return;
  }
  let p = normalize(join(dist, decodeURIComponent(url.pathname.slice(SUBPATH.length))));
  if (!p.startsWith(dist)) {
    res.writeHead(403).end();
    return;
  }
  if (existsSync(p) && statSync(p).isDirectory()) p = join(p, 'index.html');
  if (!existsSync(p)) {
    res.writeHead(404).end();
    return;
  }
  res.writeHead(200, { 'content-type': TYPES[extname(p)] ?? 'application/octet-stream' });
  res.end(readFileSync(p));
});
// --url: prova un'installazione già servita (es. il container Nginx) invece del server interno
const EXTERNAL = arg('--url', null);
if (!EXTERNAL) await new Promise((r) => server.listen(0, '127.0.0.1', r));
const BASE = EXTERNAL ?? `http://127.0.0.1:${server.address().port}${SUBPATH}`;
console.log(`Base: ${BASE}`);

// ---------------------------------------------------------------- utilità
let failures = 0;
const ok = (cond, msg) => {
  console.log(`${cond ? '✓' : '✗'} ${msg}`);
  if (!cond) failures++;
};

const browser = await chromium.launch({
  executablePath: CHROME,
  headless: true,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
});

async function open(ctxOpts, query = '') {
  const ctx = await browser.newContext(ctxOpts);
  const page = await ctx.newPage();
  const net = [];
  page.on('request', (r) => net.push({ method: r.method(), url: r.url() }));
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(BASE + query);
  return { ctx, page, net, errors };
}

async function ready(page) {
  await page.waitForFunction(() => {
    const l = document.querySelector('#loading');
    return window.__salamai?.state?.a && l?.hidden;
  }, null, { timeout: 30000 });
  await page.waitForTimeout(300);
}

/** Posizione a schermo di un punto canonico nel riquadro i. */
async function screenOf(page, c, pane = 0) {
  return page.evaluate(([c, pane]) => {
    const s = window.__salamai.state;
    const cam = window.__salamai.getCamera();
    const p = s.panes[pane];
    const v = p.tf.toGltf(c).project(cam);
    const r = p.renderer.domElement.getBoundingClientRect();
    return { x: r.left + ((v.x + 1) / 2) * r.width, y: r.top + ((1 - v.y) / 2) * r.height };
  }, [c, pane]);
}

async function centerOf(page, id) {
  return page.evaluate((id) => {
    const e = window.__salamai.state.a.manifest.entities.find((x) => x.id === id);
    return e.center ?? e.bbox_center;
  }, id);
}

async function selectionText(page) {
  return page.locator('#selection').innerText();
}

// ---------------------------------------------------------------- desktop
{
  const { ctx, page, net, errors } = await open({ viewport: { width: 1440, height: 900 } });
  await ready(page);
  ok(await page.locator('#error').isHidden(), 'desktop: caricamento senza errori');
  ok((await page.locator('canvas').count()) === 1, 'desktop: un riquadro 3D');
  const openTexts = await page.evaluate(() => {
    const o = window.__salamai.state.a.manifest.openings;
    return { info: document.querySelector('#layout-info').innerText, hatch: o.hatch.texts.summary, door: o.door.texts.summary };
  });
  ok(openTexts.info.includes(openTexts.hatch) && openTexts.info.includes(openTexts.door),
    'desktop: avvisi botola/porta presi dal manifest della revisione caricata');
  await page.screenshot({ path: join(OUT, 'desktop_asson.png') });

  // rotazione con il mouse: la camera si sposta
  const cam0 = await page.evaluate(() => window.__salamai.getCamera().position.toArray());
  const box = await page.locator('canvas').boundingBox();
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width / 2 + 150, box.y + box.height / 2 + 40, { steps: 8 });
  await page.mouse.up();
  const cam1 = await page.evaluate(() => window.__salamai.getCamera().position.toArray());
  ok(cam0.some((v, i) => Math.abs(v - cam1[i]) > 1e-3), 'desktop: rotazione con trascinamento del mouse');
  await page.mouse.wheel(0, -400);
  await page.waitForTimeout(200);

  // selezione di una ventola dalla vista assonometrica
  await page.click('[data-view="axon"]');
  await page.waitForTimeout(200);
  let pt = await screenOf(page, await centerOf(page, 'fan_01'));
  await page.mouse.click(pt.x, pt.y);
  await page.waitForTimeout(200);
  let sel = await selectionText(page);
  ok(sel.includes('fan_01') && sel.includes('nominale'), 'desktop: selezione fan_01 con pannello dati e direzione nominale');
  ok(sel.includes('ASSUNTO') || sel.includes('SCONOSCIUTO'), 'desktop: assunzioni evidenziate nel pannello');
  await page.screenshot({ path: join(OUT, 'desktop_selezione.png') });

  // vista frontale: la parete porta copre l'interno; trasparente -> si seleziona B1
  await page.selectOption('select[aria-label="Parete porta"]', 'visible');
  await page.click('[data-view="front"]');
  await page.waitForTimeout(200);
  pt = await screenOf(page, await centerOf(page, 'sensor_b1_sth01'));
  await page.mouse.click(pt.x, pt.y);
  await page.waitForTimeout(150);
  sel = await selectionText(page);
  ok(sel.includes('wall_y0'), 'desktop: con parete opaca si seleziona la parete porta');
  await page.selectOption('select[aria-label="Parete porta"]', 'transparent');
  await page.waitForTimeout(150);
  await page.mouse.click(pt.x, pt.y);
  await page.waitForTimeout(150);
  sel = await selectionText(page);
  ok(sel.includes('sensor_b1_sth01'), 'desktop: parete trasparente non intercetta, si raggiunge la sonda B1');
  await page.screenshot({ path: join(OUT, 'desktop_trasparenza.png') });

  // layer nascosto: la zona prodotto non si seleziona più
  await page.selectOption('select[aria-label="Parete porta"]', 'visible');
  await page.selectOption('select[aria-label="Soffitto"]', 'hidden');
  await page.click('[data-view="top"]');
  await page.waitForTimeout(200);
  pt = await screenOf(page, [0.40, 0.95, 1.40]);
  await page.mouse.click(pt.x, pt.y);
  await page.waitForTimeout(150);
  sel = await selectionText(page);
  ok(sel.includes('zone_cacciatorini'), 'desktop: dall\'alto, soffitto nascosto, si seleziona la zona cacciatorini');
  await page.uncheck('#layer-supporti_prodotto');
  await page.uncheck('#layer-estrazione_ingresso');
  await page.mouse.click(pt.x, pt.y);
  await page.waitForTimeout(150);
  sel = await selectionText(page);
  ok(!sel.includes('zone_cacciatorini'), 'desktop: i layer nascosti non sono selezionabili');
  const zoneVisible = await page.evaluate(() => window.__salamai.state.panes[0].objects.get('zone_salami').visible);
  ok(zoneVisible === false, 'desktop: layer "Supporti e prodotto" nascosto');
  await page.click('text=Mostra tutto');

  // quote
  await page.click('#btn-dims');
  await page.waitForTimeout(200);
  const dimCount = await page.locator('.dim-label:visible').count();
  ok(dimCount >= 10, `desktop: quote visibili (${dimCount})`);
  const dimText = await page.locator('.dim-label').allInnerTexts();
  ok(dimText.some((t) => t.includes('ASSUNTO')), 'desktop: quota della botola marcata ASSUNTO');
  await page.screenshot({ path: join(OUT, 'desktop_quote_alto.png') });
  await page.click('#btn-dims');

  // misura su distanza nota: luce della porta (65 cm) vista dall'esterno,
  // con il layer Aperture nascosto (l'anta aperta sta davanti allo stipite)
  await page.selectOption('select[aria-label="Soffitto"]', 'visible');
  await page.uncheck('#layer-aperture');
  await page.click('[data-view="front"]');
  await page.waitForTimeout(200);
  await page.click('#btn-measure');
  const a = await screenOf(page, [1.03, -0.1, 1.91]);
  const b = await screenOf(page, [1.70, -0.1, 1.91]);
  await page.mouse.click(a.x, a.y);
  await page.waitForTimeout(100);
  await page.mouse.click(b.x, b.y);
  await page.waitForTimeout(200);
  const mtxt = await page.locator('#measure').innerText();
  ok(/65,0 cm/.test(mtxt) && mtxt.includes('rettilinea 3D'), `desktop: misura luce porta = 65,0 cm (${mtxt.match(/Distanza[^\n]*/)?.[0]})`);
  ok(mtxt.includes('X 1,040') && mtxt.includes('X 1,690') && mtxt.includes('Z 1,900'), 'desktop: punti misura in coordinate canoniche (Z-up)');
  await page.screenshot({ path: join(OUT, 'desktop_misura.png') });
  await page.click('#btn-measure');
  await page.check('#layer-aperture');

  // confronto layout
  await page.selectOption('#sel-b', 'L900_DEMO');
  await ready(page);
  await page.waitForFunction(() => window.__salamai.state.panes.length === 2);
  await page.waitForTimeout(300);
  ok((await page.locator('canvas').count()) === 2, 'desktop: confronto con due riquadri');
  const diff = await page.locator('#diff').innerText();
  ok(/spostato\s+fan_02/.test(diff), 'desktop: fan_02 spostato');
  ok(/modificato\s+fan_03 — orientamento/.test(diff), 'desktop: fan_03 orientamento modificato');
  ok(/aggiunto\s+zone_left_products/.test(diff) && /rimosso\s+zone_cacciatorini/.test(diff), 'desktop: aggiunte e rimozioni per ID');
  ok(/exhaust_duct_01 — [^\n]*percorso/.test(diff), 'desktop: percorso tubazione modificato');
  ok(diff.includes('IPOTESI DIMOSTRATIVA'), 'desktop: layout B etichettato come ipotesi dimostrativa');
  const c0 = await page.evaluate(() => window.__salamai.getCamera().position.toArray());
  const bb = await page.locator('canvas').nth(1).boundingBox();
  await page.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2);
  await page.mouse.down();
  await page.mouse.move(bb.x + bb.width / 2 - 120, bb.y + bb.height / 2, { steps: 6 });
  await page.mouse.up();
  const sync = await page.evaluate(() => {
    const s = window.__salamai.state;
    const ctl = window.__salamai.getControls();
    return { same: ctl[0].object === ctl[1].object && ctl[0].target === ctl[1].target, pos: window.__salamai.getCamera().position.toArray() };
  });
  ok(sync.same && c0.some((v, i) => Math.abs(v - sync.pos[i]) > 1e-3), 'desktop: camera sincronizzata fra i riquadri');
  await page.screenshot({ path: join(OUT, 'desktop_confronto.png') });

  // sola lettura: solo GET, solo stessa origine
  const origin = new URL(BASE).origin;
  ok(net.every((r) => r.method === 'GET'), `desktop: solo richieste GET (${net.length})`);
  ok(net.every((r) => r.url.startsWith(origin) || r.url.startsWith('data:') || r.url.startsWith('blob:')), 'desktop: nessuna risorsa esterna (CDN o servizi)');
  ok(errors.length === 0, `desktop: nessun errore JavaScript ${errors.join(' | ')}`);
  await ctx.close();
}

// ---------------------------------------------------------------- telefono
{
  const { ctx, page, errors } = await open({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  await ready(page);
  ok(await page.locator('#error').isHidden(), 'telefono: caricamento senza errori');
  await page.screenshot({ path: join(OUT, 'telefono_asson.png') });
  // trascinamento con un dito via CDP
  const cdp = await ctx.newCDPSession(page);
  const cam0 = await page.evaluate(() => window.__salamai.getCamera().position.toArray());
  const touch = (type, x, y) => cdp.send('Input.dispatchTouchEvent', { type, touchPoints: type === 'touchEnd' ? [] : [{ x, y }] });
  await touch('touchStart', 200, 400);
  for (let i = 1; i <= 8; i++) await touch('touchMove', 200 + i * 15, 400 + i * 4);
  await touch('touchEnd', 0, 0);
  await page.waitForTimeout(200);
  const cam1 = await page.evaluate(() => window.__salamai.getCamera().position.toArray());
  ok(cam0.some((v, i) => Math.abs(v - cam1[i]) > 1e-3), 'telefono: rotazione con un dito');
  // pizzico a due dita
  const d0 = await page.evaluate(() => window.__salamai.getCamera().position.length());
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: 150, y: 400, id: 1 }, { x: 250, y: 400, id: 2 }] });
  for (let i = 1; i <= 8; i++) {
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: 150 - i * 10, y: 400, id: 1 }, { x: 250 + i * 10, y: 400, id: 2 }] });
  }
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await page.waitForTimeout(200);
  const d1 = await page.evaluate(() => window.__salamai.getCamera().position.length());
  ok(Math.abs(d1 - d0) > 1e-3, 'telefono: zoom con due dita');
  // dall'alto (soffitto trasparente di default), lontano dalle frecce delle ventole
  await page.click('[data-view="top"]');
  await page.waitForTimeout(200);
  const pt = await screenOf(page, [2.63, 0.66, 0.85]);
  await page.touchscreen.tap(pt.x, pt.y);
  await page.waitForTimeout(200);
  await page.click('#btn-panel');
  await page.waitForTimeout(300);
  const sel = await selectionText(page);
  ok(sel.includes('heater_e1'), `telefono: selezione con tocco e pannello informazioni (${sel.split('\n')[0]})`);
  const noHScroll = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
  ok(noHScroll, 'telefono: nessuno scorrimento orizzontale della pagina');
  await page.screenshot({ path: join(OUT, 'telefono_pannello.png') });
  ok(errors.length === 0, `telefono: nessun errore JavaScript ${errors.join(' | ')}`);
  await ctx.close();
}

// ---------------------------------------------------------------- errori
{
  const { ctx, page } = await open({ viewport: { width: 1200, height: 800 } }, '?layout=NON_ESISTE');
  await page.waitForSelector('#error:not([hidden])', { timeout: 15000 });
  ok((await page.locator('#error .msg').innerText()).includes('NON_ESISTE'), 'errori: layout inesistente segnalato');
  await ctx.close();
}
{
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 800 } });
  const page = await ctx.newPage();
  await page.route('**/manifest.json', (r) => r.fulfill({ status: 404, body: 'no' }));
  await page.goto(BASE);
  await page.waitForSelector('#error:not([hidden])', { timeout: 15000 });
  const msg = await page.locator('#error .msg').innerText();
  ok(msg.includes('mancante') && msg.includes('manifest.json'), 'errori: manifest mancante segnalato con il percorso');
  await page.screenshot({ path: join(OUT, 'errore_manifest.png') });
  await ctx.close();
}
{
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 800 } });
  const page = await ctx.newPage();
  await page.route('**/model-*.glb', (r) => r.fulfill({ status: 200, body: Buffer.from('glTF non valido') }));
  await page.goto(BASE);
  await page.waitForSelector('#error:not([hidden])', { timeout: 15000 });
  ok((await page.locator('#error .msg').innerText()).includes('GLB'), 'errori: GLB non corrispondente o incompatibile segnalato');
  await ctx.close();
}
{
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 800 } });
  const page = await ctx.newPage();
  await page.addInitScript(() => {
    const orig = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (type, ...rest) {
      return /webgl/.test(type) ? null : orig.call(this, type, ...rest);
    };
  });
  await page.goto(BASE);
  await page.waitForSelector('#error:not([hidden])', { timeout: 15000 });
  ok((await page.locator('#error .msg').innerText()).includes('WebGL'), 'errori: WebGL non disponibile segnalato');
  await page.screenshot({ path: join(OUT, 'errore_webgl.png') });
  await ctx.close();
}

await browser.close();
if (!EXTERNAL) server.close();
if (!EXTERNAL) ok(requests.every((r) => r.startsWith('GET ') || r.startsWith('HEAD ')), `server: ricevute solo richieste GET/HEAD (${requests.length})`);
console.log(failures ? `\n${failures} verifiche fallite` : '\nTutte le verifiche superate');
console.log(`Screenshot in ${OUT}`);
process.exit(failures ? 1 : 0);
