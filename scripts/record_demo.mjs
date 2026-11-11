import {chromium} from '@playwright/test';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
import {mkdirSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
mkdirSync('.verification/recordings',{recursive:true});mkdirSync('brand/demos',{recursive:true});
const browser=await chromium.launch();
for(const vibe of ['cartoon','calm','pixel','lab']){
  const context=await browser.newContext({viewport:{width:1200,height:850},recordVideo:{dir:'.verification/recordings',size:{width:1200,height:850}}});
  const page=await context.newPage();await page.goto(pathToFileURL(resolve('site/acceptance.html')).href);
  await page.selectOption('#vibe',vibe);await page.locator('#motion').click();await page.locator('#trial-title').scrollIntoViewIfNeeded();
  await page.waitForTimeout(800);await page.selectOption('#status-filter','missing');
  await page.waitForTimeout(800);await page.selectOption('#status-filter','all');
  await page.waitForTimeout(800);await page.screenshot({path:`.verification/${vibe}-desktop.png`});
  const video=page.video();await context.close();
  execFileSync('ffmpeg',['-y','-hide_banner','-loglevel','error','-i',await video.path(),'-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',`brand/demos/${vibe}.mp4`]);
}
await browser.close();
