// Separate storage for each run preserves prior measurements and prevents mixing ports.
import {mkdtempSync,readFileSync,readdirSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {spawnSync} from 'node:child_process';
const root=resolve('.');mkdirSync('.verification',{recursive:true});
const directory=mkdtempSync(resolve('.verification/lhci-'));
const config=JSON.parse(readFileSync('lighthouserc.json','utf8'));
config.ci.collect.staticDistDir=resolve('site');config.ci.upload.outputDir=join(directory,'reports');
writeFileSync(join(directory,'config.json'),JSON.stringify(config));
const result=spawnSync(process.execPath,[resolve('node_modules/@lhci/cli/src/cli.js'),'autorun',`--config=${join(directory,'config.json')}`],{cwd:directory,stdio:'inherit',env:process.env});
const reports=readdirSync(join(directory,'.lighthouseci')).filter(n=>n.startsWith('lhr-')&&n.endsWith('.json')).map(n=>JSON.parse(readFileSync(join(directory,'.lighthouseci',n),'utf8')));
const output={access_date:'2026-10-13',scope:'Three Lighthouse localhost runs; not file:// or field INP',runs:reports.map(r=>({lcp_ms:r.audits['largest-contentful-paint'].numericValue,tbt_ms:r.audits['total-blocking-time'].numericValue,accessibility:r.categories.accessibility.score,performance:r.categories.performance.score,user_agent:r.userAgent})),exit_code:result.status};
writeFileSync(join(root,'.verification/lighthouse-results.json'),JSON.stringify(output,null,2)+'\n');
process.exit(result.status??1);
