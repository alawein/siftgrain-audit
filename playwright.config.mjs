import {defineConfig} from '@playwright/test';
export default defineConfig({
  testDir:'./tests/browser',timeout:60000,fullyParallel:false,workers:1,
  use:{headless:true},
  projects:[{name:'chromium',use:{browserName:'chromium'}},
    {name:'firefox',use:{browserName:'firefox'}},
    {name:'webkit',use:{browserName:'webkit'}}],
  reporter:[['list'],['json',{outputFile:'.verification/browser-results.json'}]]
});
