'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert'),crypto=require('crypto');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
const read=n=>fs.readFileSync(path.join(root,n),'utf8');
const v31=read('V31_original.html');
const v32=read('Survival_Paradise_Autonomous_Simulation_V32.html');
const v33=read('Survival_Paradise_Autonomous_Simulation_V33.html');
const images=s=>s.match(/data:image\/png;base64,[A-Za-z0-9+/=]+/g)||[];
assert.equal(images(v31).length,2);
assert.deepStrictEqual(images(v31),images(v33),'original V31 character/weapon PNGs must be byte-identical');
assert.deepStrictEqual(images(v32),images(v33),'V32 image data must be completely unchanged');
new (require('vm').Script)(v33.match(/<script>([\s\S]*?)<\/script>/)[1],{filename:'V33.html'});
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const errors=[];
 const open=async (size,isMobile)=>{
  const page=await browser.newPage({viewport:size,isMobile,hasTouch:isMobile});
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto('file://'+path.join(root,'Survival_Paradise_Autonomous_Simulation_V33.html'));
  await page.waitForFunction(()=>SP_TEST_API.getState().bodyAtlasReady&&SP_TEST_API.getState().gearAtlasReady,{timeout:20000});
  return page;
 };
 const desktop=await open({width:1280,height:850},false);
 assert.equal(await desktop.locator('#igSettingsButton').count(),1);
 await desktop.locator('#igSettingsButton').click();
 assert.equal(await desktop.evaluate(()=>SP_TEST_API.settings.isOpen()),true);
 assert.equal(await desktop.evaluate(()=>SCENE.paused),true);
 await desktop.screenshot({path:'artifacts/V33_Desktop_InGame_Settings.png'});
 await desktop.locator('#igPictured').click();
 const picture=await desktop.evaluate(()=>SP_TEST_API.settings.get());
 for(const [k,v] of Object.entries({loadout:'mixed',population:9,speed:.75,scale:95,hand:90,support:12,showHands:true,showWeapons:true,anchors:true,hitboxes:false})){
  assert.equal(picture[k],v,'pictured preset '+k);
 }
 await desktop.locator('#ig_support').evaluate(el=>{el.value='8';el.dispatchEvent(new Event('input',{bubbles:true}));});
 assert.equal(await desktop.evaluate(()=>SCENE.supportReach),8);
 await desktop.locator('#ig_showHands').uncheck();
 assert.equal(await desktop.evaluate(()=>SCENE.handsVisible),false);
 await desktop.locator('#ig_v32Aim').uncheck();
 assert.equal(await desktop.evaluate(()=>V32.aim),false);
 await desktop.locator('#igDone').click();
 assert.equal(await desktop.evaluate(()=>SP_TEST_API.settings.isOpen()),false);
 assert.equal(await desktop.evaluate(()=>SCENE.paused),false,'closing auto-paused menu restores prior running state');
 // Verify saved values survive reload and that sidebar remains synchronized.
 await desktop.reload();
 await desktop.waitForFunction(()=>SP_TEST_API.getState().bodyAtlasReady);
 assert.equal(await desktop.locator('#support').inputValue(),'8');
 assert.equal(await desktop.locator('#showHands').isChecked(),false);
 assert.equal(await desktop.locator('#v32Aim').isChecked(),false);
 assert.equal(await desktop.locator('#population').inputValue(),'9');
 await desktop.locator('#igSettingsButton').click();
 assert.equal(await desktop.locator('#ig_support').inputValue(),'8');
 await desktop.locator('#igDefaults').click();
 assert.equal(await desktop.locator('#ig_support').inputValue(),'0');
 assert.equal(await desktop.locator('#showHands').isChecked(),true);
 await desktop.locator('#igDone').click();
 // Mobile geometry and touch interaction, including scrollable settings panel.
 const mobile=await open({width:393,height:852},true);
 await mobile.locator('#igSettingsButton').tap();
 await mobile.waitForTimeout(200);
 assert.equal(await mobile.evaluate(()=>SP_TEST_API.settings.isOpen()),true);
 const geom=await mobile.locator('.ig-dialog').boundingBox();
 assert(geom&&geom.x>=0&&geom.x+geom.width<=395,'mobile settings panel must fit viewport');
 assert(geom.y>=0&&geom.y+geom.height<=854,'mobile settings height must fit viewport');
 await mobile.screenshot({path:'artifacts/V33_Android_InGame_Settings.png'});
 await mobile.locator('#igNight').tap();
 assert.equal(await mobile.evaluate(()=>SCENE.night),true);
 await mobile.locator('#igNight').tap();
 await mobile.locator('#igDone').tap();
 assert.equal(await mobile.evaluate(()=>SCENE.paused),false);
 assert.deepStrictEqual(errors,[],'browser runtime errors');
 const report={result:'pass',version:'V33',characterAtlasUnchanged:true,weaponAndHandsAtlasUnchanged:true,
   originalBodiesAndGearHashes:images(v33).map(s=>crypto.createHash('sha256').update(s).digest('hex')),
   desktopPreset:picture,desktopMenu:true,mobileSettingsWithinViewport:true,
   preferencesPersistedAfterReload:true,automaticPauseResume:true,errors};
 fs.mkdirSync('artifacts',{recursive:true});
 fs.writeFileSync('artifacts/V33_Settings_QA_Report.json',JSON.stringify(report,null,2));
 await browser.close();
 console.log('V33 IN-GAME SETTINGS QA PASS');
})().catch(e=>{console.error(e);process.exit(1);});
