// rendre_video.js — rend la démo image par image (déterministe, sans écran), puis les 15 photos,
// puis assemble exports/demo-soiree.mp4 avec ffmpeg.
//   node exports/rendre_video.js                 vidéo + photos
//   node exports/rendre_video.js --photos        photos seulement
// Dépendances : node + playwright (npm i playwright ; npx playwright install chromium), ffmpeg.
// La démo charge three.js depuis un CDN : il faut le réseau, ou une copie locale de three.min.js.
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs'), { execSync } = require('child_process');
const ICI = __dirname, DEMO = 'file://' + path.join(ICI, '..', 'outils', 'demo-evenement.html');
const FR = path.join(ICI, '_frames'), PH = path.join(ICI, 'photos'), MP4 = path.join(ICI, 'demo-soiree.mp4');
const FPS = 12, SPH = 6;   // images/s, secondes par heure de soirée (16 h -> 2 h = 60 s)
const photosSeulement = process.argv.includes('--photos');
fs.mkdirSync(FR, { recursive: true }); fs.mkdirSync(PH, { recursive: true });
(async () => {
  const opts = { args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--allow-file-access-from-files', '--no-sandbox'] };
  if (fs.existsSync('/opt/pw-browsers/chromium')) opts.executablePath = '/opt/pw-browsers/chromium';
  const browser = await chromium.launch(opts);
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  await page.goto(DEMO); await page.waitForFunction(() => window.G && G.foule, null, { timeout: 60000 }); await page.waitForTimeout(1500);
  await page.evaluate(() => { lecture = false; ['logo','stats','ligne','phases'].forEach(id => document.getElementById(id).style.display = 'none');
    document.getElementById('hud').style.padding = '14px 24px 22px'; sun.shadow.mapSize.set(1024, 1024); if (sun.shadow.map){ sun.shadow.map.dispose(); sun.shadow.map = null; } });
  const n = photosSeulement ? 0 : 10 * SPH * FPS; const dt = 1 / FPS / SPH;
  for (let i = 0; i < n; i++){
    const T = 16 + i / (SPH * FPS);
    await page.evaluate(([T, dt]) => { t = T; appliquer(T, dt); cameraMaj(T, dt); renderer.render(scene, camera);
      document.getElementById('phase').textContent = document.getElementById('heure').textContent + ' · ' + P().nom; }, [T, dt]);
    await page.screenshot({ path: `${FR}/f${String(i).padStart(4,'0')}.jpg`, type: 'jpeg', quality: 88 });
    if (i % 100 === 0) console.log('frame', i, '/', n);
  }
  // photos pour les dossiers
  const shots = [
    {nom:'01-vue-d-ensemble-montage', t:16.3, pos:[-70,45,130], cible:[0,8,45]},
    {nom:'02-village-flancs', t:18.3},
    {nom:'03-scene-ouverte-catwalk', t:18.9},
    {nom:'04-dj-hayon-camion', t:19.8},
    {nom:'05-defile-des-luttes', t:20.9},
    {nom:'06-concert', t:21.6},
    {nom:'07-mapping', t:22.3, pos:[-18,6,46], cible:[0,18,0]},
    {nom:'08-lasers', t:22.9},
    {nom:'09-rap-second-set', t:23.6},
    {nom:'10-vue-de-dessus-nuit', t:23.0, pos:[0,95,70], cible:[0,0,45]},
    {nom:'11-tour-layher', t:19.8, pos:[-13,9,80], cible:[0,6,70]},
    {nom:'12-regie-podium', t:21.0, pos:[-10,5,58], cible:[0,2.5,65]},
    {nom:'13-passages-de-cables', t:20.2, pos:[-22,5,50], cible:[-27.5,0,38]},
    {nom:'14-legende-technique', t:19.8, leg:true, pos:[-70,50,130], cible:[0,5,45]},
    {nom:'15-plan-de-dessus-jour', t:16.2, pos:[0,120,60.01], cible:[0,0,60]},
  ];
  await page.evaluate(() => { document.getElementById('hud').style.display = 'none'; });
  for (const s of shots){
    await page.evaluate(([tt]) => { t = tt; modeCam = 'cine'; }, [s.t]);
    if (s.pos) await page.evaluate(([p, c]) => { modeCam = 'libre'; camera.position.set(...p); controls.target.set(...c); controls.update(); }, [s.pos, s.cible]);
    await page.evaluate(on => { document.getElementById('legpan').style.display = on ? 'block' : 'none'; G.legendes.forEach(sp => sp.visible = !!on); }, !!s.leg);
    await page.waitForTimeout(700);
    await page.screenshot({ path: `${PH}/${s.nom}.jpg`, type: 'jpeg', quality: 90 });
    console.log('photo', s.nom);
  }
  await browser.close();
  if (!photosSeulement){
    execSync(`ffmpeg -y -loglevel error -framerate ${FPS} -i "${FR}/f%04d.jpg" -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p -movflags +faststart "${MP4}"`, { stdio: 'inherit' });
    console.log('vidéo :', MP4, Math.round(fs.statSync(MP4).size / 1e5) / 10, 'Mo');
  }
  console.log('FIN');
})().catch(e => { console.error('FATAL', e); process.exit(1); });
