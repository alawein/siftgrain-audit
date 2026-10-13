import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
import {writeFileSync,mkdirSync} from 'node:fs';
const url=pathToFileURL(resolve('site/acceptance.html')).href;
test('offline report, all vibes, both appearances, keyboard and missing filter',async({page},testInfo)=>{
  const requests=[],errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.route('http**://**',route=>{requests.push(route.request().url());route.abort()});
  await page.goto(url);
  for(const theme of ['dark','light'])for(const vibe of ['cartoon','calm','pixel','lab']){
    await page.selectOption('#appearance',theme);await page.selectOption('#vibe',vibe);
    await expect(page.locator('html')).toHaveAttribute('data-theme',theme);
    await expect(page.locator('html')).toHaveAttribute('data-vibe',vibe);
    const a11y=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
    expect(a11y.violations).toEqual([]);
  }
  await page.selectOption('#status-filter','missing');
  await expect(page.locator('#trial-table tbody tr:visible')).toHaveCount(1);
  await expect(page.locator('#filter-status')).toContainText('denominator is unchanged');
  await page.keyboard.press('Tab');expect(await page.evaluate(()=>document.activeElement.tagName)).not.toBe('BODY');
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:`.verification/${testInfo.project.name}-mobile.png`,fullPage:true});
  expect(requests).toEqual([]);expect(errors).toEqual([]);
});
test('blocked storage, reduced motion and absent WebGL remain usable',async({page})=>{
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.addInitScript(()=>{Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}});HTMLCanvasElement.prototype.getContext=()=>null});
  await page.goto(url);await expect(page.locator('html')).toHaveAttribute('data-theme','dark');
  await page.selectOption('#vibe','calm');await page.selectOption('#appearance','light');
  expect(await page.locator('.trial-cell.missing').evaluate(e=>getComputedStyle(e).animationName)).toBe('none');
  await expect(page.locator('#trial-table')).toBeVisible();
});
test('local-file interaction and frame measurements',async({page},testInfo)=>{
  await page.addInitScript(()=>{window.censusEvents=[];try{new PerformanceObserver(list=>window.censusEvents.push(...list.getEntries().filter(e=>e.interactionId>0).map(e=>e.duration))).observe({type:'event',buffered:true,durationThreshold:16})}catch{}});
  await page.goto(url);for(let i=0;i<12;i++)await page.locator('#motion').click();
  const measurements=await page.evaluate(async()=>{
    const lcp=[];try{new PerformanceObserver(list=>lcp.push(...list.getEntries().map(e=>e.startTime))).observe({type:'largest-contentful-paint',buffered:true})}catch{}
    const durations=[];for(let i=0;i<20;i++){const start=performance.now();document.getElementById('status-filter').value=i%2?'missing':'all';document.getElementById('status-filter').dispatchEvent(new Event('change'));await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame);durations.push(performance.now()-start)}
    const frames=[];let last=performance.now();for(let i=0;i<60;i++){await new Promise(requestAnimationFrame);const now=performance.now();frames.push(now-last);last=now}
    return {lcp_ms:lcp.length?Math.max(...lcp):null,interaction_to_two_frames_ms:durations,frame_intervals_ms:frames,trusted_interaction_durations_ms:window.censusEvents,lab_inp_candidate_ms:window.censusEvents.length?Math.max(...window.censusEvents):null,inp_ms:null,inp_reason:'Field INP unavailable; trusted Event Timing durations are a small lab session and reported separately',hardware:navigator.userAgent};
  });mkdirSync('.verification',{recursive:true});writeFileSync(`.verification/perf-${testInfo.project.name}.json`,JSON.stringify(measurements,null,2));
  expect(Math.max(...measurements.interaction_to_two_frames_ms)).toBeLessThan(200);if(measurements.lab_inp_candidate_ms!==null)expect(measurements.lab_inp_candidate_ms).toBeLessThan(200);
});
