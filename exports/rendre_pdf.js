// rendre_pdf.js — HTML → PDF A4 avec Chromium (Playwright), en-tête et pied de page numérotés.
// usage : node rendre_pdf.js entree.html sortie.pdf "Titre court"
const { chromium } = require('playwright');
const [,, entree, sortie, titre = ''] = process.argv;
(async () => {
  const opts = {};
  const fs = require('fs'); if (fs.existsSync('/opt/pw-browsers/chromium')) opts.executablePath = '/opt/pw-browsers/chromium';
  const browser = await chromium.launch(Object.assign({ args: ['--no-sandbox'] }, opts));
  const page = await browser.newPage();
  await page.goto('file://' + require('path').resolve(entree), { waitUntil: 'load' });
  await page.emulateMedia({ media: 'print' });
  await page.waitForTimeout(400);
  // Chromium : le gabarit d'en-tête ignore les tailles par défaut, il faut tout fixer en px, sans flex
  const style = 'font-family:Helvetica,Arial,sans-serif;font-size:9px;line-height:11px;color:#777;width:100%;margin:0 16mm;-webkit-print-color-adjust:exact';
  await page.pdf({ path: sortie, format: 'A4', printBackground: true, preferCSSPageSize: false,
    margin: { top: '20mm', bottom: '18mm', left: '16mm', right: '16mm' }, displayHeaderFooter: true,
    headerTemplate: `<div style="${style}"><span style="float:left">${titre.replace(/</g, '&lt;')}</span><span style="float:right" class="date"></span></div>`,
    footerTemplate: `<div style="${style}"><span style="float:left">Document de travail — à vérifier avant diffusion</span><span style="float:right">page <span class="pageNumber"></span> / <span class="totalPages"></span></span></div>` });
  await browser.close(); console.log('PDF :', sortie);
})().catch(e => { console.error('PDF impossible :', e.message); process.exit(1); });
