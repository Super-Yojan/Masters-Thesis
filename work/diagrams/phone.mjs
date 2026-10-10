import fs from 'node:fs/promises';
import {chromium} from 'playwright';
const out='/Users/yojan/git/Masters-Thesis/outputs/TerraPhone_Architecture';
let a=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" role="img" aria-labelledby="TerraPhone_Architecture-title TerraPhone_Architecture-desc"><title id="TerraPhone_Architecture-title">TerraPhone architecture</title><desc id="TerraPhone_Architecture-desc">Phone sensors feed a Swift app and the shared Rust autonomy core through UniFFI, with fleet supervision through Zenoh and a planned physical motor connection.</desc><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#111"/></marker></defs>`;
function box(x,y,w,h,fill='#fff',dash=false){a+=`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="#111" stroke-width="1.5" ${dash?'stroke-dasharray="6 5"':''}/>`;}
function text(t,x,y,size=22,bold=false,fill='#111',anchor='start'){a+=`<text x="${x}" y="${y}" font-family="Arial" font-size="${size}" font-weight="${bold?700:400}" fill="${fill}" text-anchor="${anchor}">${t}</text>`;}
function path(d,dash=false){a+=`<path d="${d}" fill="none" stroke="#111" stroke-width="1.6" ${dash?'stroke-dasharray="6 5"':''} marker-end="url(#arrow)"/>`;}
function label(t,x,y,w){box(x-w/2,y-18,w,24,'#fff');text(t,x,y,14,true,'#111','middle');}
// Phone boundary and connections, drawn before nodes.
box(40,176,1200,348,'#f2f2f2');text('ON THE PHONE',64,208,15,true);
path('M304 376 H372');path('M556 376 H684');
path('M924 376 H1044');
path('M420 156 V240');path('M500 240 V156');
path('M1092 464 V552',true);

// Labels have a clear gap above their arrows.
box(574,332,92,26,'#f2f2f2');text('UNIFFI',620,350,14,true,'#111','middle');
box(950,332,76,26,'#f2f2f2');text('EFFORT',988,350,14,true,'#111','middle');
text('ZENOH',580,112,14,true);text('Goals / control',580,140,18);text('Status / telemetry',580,166,18);
// External supervisor.
box(372,40,184,116);text('ARGOS',392,78,28,true);text('Fleet supervision',392,108,18);text('Goals + takeover',392,136,17);
// Phone sensor inputs.
box(64,240,240,224);text('Phone sensors',88,280,26,true);text('ARKit camera + pose',88,328,20);text('Depth, where available',88,364,19);text('Core Motion IMU',88,400,20);text('Tracking + timestamps',88,436,18);
box(372,240,184,224);text('TerraPhone',396,280,25,true);text('Swift app',396,312,20);text('Sensor access',396,360,19);text('Lifecycle + UI',396,396,19);text('Device adapters',396,432,18);
box(684,240,240,224,'#111');text('Terra Rust Core',708,280,25,true,'#fff');text('State estimation',708,328,20,false,'#fff');text('Local occupancy map',708,364,18,false,'#fff');text('Authority + planning',708,400,19,false,'#fff');text('Velocity control',708,436,20,false,'#fff');
box(1044,240,172,224);text('Motor output',1064,280,22,true);text('Left / right',1064,328,19);text('wheel effort',1064,358,19);text('App displays',1064,406,18);text('effort today',1064,434,18);
// Physical hardware remains a planned route.
box(804,552,388,124,'#fff',true);text('Physical chassis',828,588,24,true);text('Planned phone-to-motor link',828,624,20);text('PWM adapter + hardware watchdog',828,654,18);
text('PLANNED',1108,546,14,true);
// Reuse statement is an architecture note, not an additional system component.
text('Same Rust algorithms run in the simulator.',64,584,21,true);text('Remote phone mode supervises the simulator over Zenoh.',64,618,18);text('It does not run a second onboard planner for that rover.',64,650,18);
a+='</svg>';
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TerraPhone Architecture</title><style>body{margin:0;background:#fff}.diagram-container{width:100%;overflow-x:auto}svg{display:block;width:100%;min-width:1280px}@media print{.diagram-container{overflow-x:visible}svg{min-width:0}}</style></head><body><div class="diagram-container">${a}</div></body></html>`;
await fs.writeFile(out+'.html',html);
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});const page=await browser.newPage({viewport:{width:1280,height:720},deviceScaleFactor:2});await page.goto('file://'+out+'.html');await page.evaluate(()=>document.fonts.ready);await page.locator('svg').screenshot({path:out+'.png',omitBackground:true});await browser.close();
