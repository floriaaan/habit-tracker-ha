const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const http=require('node:http');
const path=require('node:path');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
test('rings and water animate in both directions, preserve interrupted progress and respect reduced motion',async()=>{
  const server=http.createServer((req,res)=>{const file=req.url==='/card.js'?'custom_components/habit_tracker/www/habit-tracker-card.js':'tests/card.html';res.setHeader('Content-Type',req.url==='/card.js'?'text/javascript':'text/html');res.end(fs.readFileSync(path.join(root,file)));});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch({channel:'chrome',headless:true});
  try {
    const page=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'no-preference'});
    await page.goto(`http://127.0.0.1:${server.address().port}`);await page.waitForFunction(()=>window.fixtureReady);
    await page.waitForTimeout(850);
    const sample=()=>page.evaluate(()=>{
      const root=document.querySelector('#nutrition').shadowRoot;
      const water=root.querySelector('[data-motion="water-water-7"]');
      const arc=document.querySelector('#rings').shadowRoot.querySelector('[data-motion="arc-water"]');
      return {fill:new DOMMatrixReadOnly(getComputedStyle(water).transform).m22,arc:parseFloat(getComputedStyle(arc).strokeDasharray),animations:root.getAnimations().length};
    });
    assert.equal((await sample()).fill,0);
    await page.evaluate(()=>setWater(2000));await page.waitForTimeout(150);
    const up=await sample();assert(up.fill>0&&up.fill<1);assert(up.arc>0);
    await page.evaluate(()=>setWater(1750));
    const interrupted=await sample();assert(Math.abs(interrupted.fill-up.fill)<0.12,'animation restarted instead of resuming');
    await page.waitForTimeout(850);assert.equal((await sample()).fill,0);
    await page.evaluate(()=>setWater(2000));await page.waitForTimeout(850);assert.equal((await sample()).fill,1);
    const fullArc=(await sample()).arc;
    await page.evaluate(()=>setWater(1750));await page.waitForTimeout(150);
    const down=await sample();assert(down.fill>0&&down.fill<1);assert(down.arc<fullArc);
    await page.waitForTimeout(850);
    assert(await page.evaluate(()=>{const s=document.querySelector('#rings').shadowRoot;return s.querySelector('.overview svg').getBoundingClientRect().right<s.querySelector('.legend').getBoundingClientRect().left;}),'wide rings layout must have legend on the right');
    if(process.env.CARD_SCREENSHOT_DIR){fs.mkdirSync(process.env.CARD_SCREENSHOT_DIR,{recursive:true});await page.screenshot({path:path.join(process.env.CARD_SCREENSHOT_DIR,'desktop.png')});}
    await page.setViewportSize({width:390,height:844});await page.waitForTimeout(100);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    if(process.env.CARD_SCREENSHOT_DIR)await page.screenshot({path:path.join(process.env.CARD_SCREENSHOT_DIR,'mobile.png'),fullPage:true});
    await page.emulateMedia({reducedMotion:'reduce'});await page.evaluate(()=>setWater(2000));assert.equal((await sample()).fill,1);
    assert.equal(await page.evaluate(()=>document.querySelector('#nutrition').shadowRoot.getAnimations().length),0);
  } finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
});
