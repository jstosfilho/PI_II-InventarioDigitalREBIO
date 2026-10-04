const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('C:/Users/Jorge Filho/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

(async()=>{
 const out=path.resolve('tmp/figma-qa');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1024}});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  // Revisões automáticas usam tiles simulados, sem acessar servidores OSM.
  const tileRequests=[];
  await page.route('https://tile.openstreetmap.org/**',async route=>{
   tileRequests.push(await route.request().allHeaders());
   await route.fulfill({status:200,contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=','base64')});
  });
  async function capture(name,fullPage=false){await page.waitForLoadState('networkidle');await page.waitForTimeout(350);await page.screenshot({path:path.join(out,name),fullPage});}
  await page.goto('http://127.0.0.1:5051/',{waitUntil:'networkidle'});
  await capture('01-login.png');
  await page.locator('#username').fill('revisao');await page.locator('#password').fill('somente-teste-figma');await page.locator('#login-button').click();
  await page.locator('#workspace').waitFor({state:'visible'});await page.locator('.record').first().waitFor();
  await capture('02-inventario.png');
  await page.locator('.record').filter({hasText:'Trilha do Mirante'}).click();await page.locator('#detail-panel').waitFor({state:'visible'});
  await capture('03-detalhes.png');
  await page.locator('#detail-actions').getByRole('button',{name:'Editar',exact:true}).click();
  await capture('04-edicao.png');
  await page.locator('#editor-back').click();await page.locator('#detail-actions').getByRole('button',{name:'Excluir',exact:true}).click();
  await capture('05-exclusao.png');await page.locator('#cancel-delete').click();
  await page.locator('#detail-back').click();await page.locator('#new-feature').click();await capture('06-novo.png');
  await page.locator('#name').fill('Trilha teste visual');
  await page.locator('#geometry-file').setInputFiles({name:'revisao.gpx',mimeType:'application/gpx+xml',buffer:Buffer.from('<gpx><trk><trkseg><trkpt lon="-46.30" lat="-23.77"/><trkpt lon="-46.31" lat="-23.78"/></trkseg></trk></gpx>')});
  await page.locator('#import-status').filter({hasText:'Geometria validada'}).waitFor();await page.locator('#save').click();await page.locator('#detail-panel h1').filter({hasText:'Trilha teste visual'}).waitFor();
  await page.locator('#detail-actions').getByRole('button',{name:'Editar',exact:true}).click();await page.locator('#description').fill('Descrição alterada pela verificação visual');await page.locator('#save').click();await page.locator('#detail-panel h1').waitFor();
  await page.locator('#detail-actions').getByRole('button',{name:'Excluir',exact:true}).click();await page.locator('#confirm-delete').click();await page.locator('#list-panel').waitFor({state:'visible'});
  if(await page.locator('.record').filter({hasText:'Trilha teste visual'}).count())throw new Error('Item de teste não foi excluído.');
  await page.locator('#new-feature').click();await page.locator('#kind').selectOption('nascente');await page.locator('#coords-tab').click();await page.locator('#name').fill('Nascente teste visual');await page.locator('#coordinates').fill('-46.32, -23.79');await page.locator('#save').click();await page.locator('#detail-panel h1').filter({hasText:'Nascente teste visual'}).waitFor();
  await page.locator('#detail-actions').getByRole('button',{name:'Excluir',exact:true}).click();await page.locator('#confirm-delete').click();await page.locator('#list-panel').waitFor({state:'visible'});
  await page.setViewportSize({width:390,height:844});await capture('07-mobile.png',true);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth);
  if(overflow)throw new Error('Rolagem horizontal indevida em celular.');
  if(errors.length)throw new Error('Erros JavaScript: '+errors.join('; '));
  if(!tileRequests.length||tileRequests.some(headers=>headers.referer!=='http://127.0.0.1:5051/'))throw new Error('O navegador não enviou a origem como Referer aos tiles.');
  console.log(JSON.stringify({status:'ok',screenshots:7,flows:['login','lista','detalhes','editar','cancelar exclusão','importar GPX','salvar trilha','excluir teste','coordenadas manuais','salvar nascente','mobile'],pageErrors:errors,horizontalOverflow:overflow,tileReferer:'http://127.0.0.1:5051/',tilesMocked:true},null,2));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
