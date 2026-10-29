'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert'),crypto=require('crypto');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),v31=fs.readFileSync(path.join(root,'V31_original.html'),'utf8');
const v32=fs.readFileSync(path.join(root,'Survival_Paradise_Autonomous_Simulation_V32.html'),'utf8');
const images=s=>(s.match(/data:image\/png;base64,[A-Za-z0-9+/=]+/g)||[]);
const a=images(v31),b=images(v32);
assert.strictEqual(a.length,2,'expected two embedded original PNG atlases');
assert.deepStrictEqual(b,a,'LOCKED character/weapon PNGs MUST be byte-identical');
const extract=s=>s.match(/<script>([\s\S]*?)<\/script>/)[1];
new (require('vm').Script)(extract(v32),{filename:'V32.html'});
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
(async()=>{
  fs.mkdirSync('artifacts/frames',{recursive:true});
  const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
  const errors=[];
  const make=async(size,mobile)=>{
    const p=await browser.newPage({viewport:size,isMobile:mobile,hasTouch:mobile});
    p.on('pageerror',e=>errors.push(e.message));
    await p.goto('file://'+path.join(root,'Survival_Paradise_Autonomous_Simulation_V32.html'));
    await p.waitForFunction(()=>window.SP_TEST_API?.getState()?.gearAtlasReady&&window.SP_TEST_API?.getState()?.bodyAtlasReady,{timeout:20000});
    await p.waitForTimeout(1200);
    return p;
  };
  const desktop=await make({width:1280,height:850},false);
  await desktop.screenshot({path:'artifacts/Survival_Paradise_V32_Desktop.png',fullPage:true});
  await desktop.evaluate(()=>window.SP_TEST_API.setLoadout('all'));
  await desktop.waitForTimeout(500);
  // Inspect all twelve original weapon assemblies without changing their atlas data.
  for(let i=0;i<12;i++){
    await desktop.evaluate(i=>{SCENE.players[0].gun=i;SCENE.players[0].ammo=MAG[i];},i);
    await desktop.waitForTimeout(160);
    await desktop.screenshot({path:'artifacts/frames/frame'+String(i).padStart(2,'0')+'.png'});
  }
  const state=await desktop.evaluate(()=>window.SP_TEST_API.getState());
  assert.equal(state.assetVersion,'V32-nondestructive');
  assert.equal(state.sourceAtlasesUnmodified,true);
  assert.equal(state.obstacleCount,3);
  assert.equal(state.playerHealth.length,state.count);
  const gameSystems=await desktop.evaluate(()=>{
    const p=SCENE.players[0],t=SCENE.dummies[0];
    const original={x:p.x,y:p.y};
    t.x=p.x+8;t.y=p.y;t.health=1;t.alive=true;
    hitTarget(t,10,p); // produces a genuine loot drop via the V32 death hook
    update(.04);       // auto-pickup runs in the normal V32 update
    const picked=V32.picked;
    v32DamagePlayer(p,12);
    const hp=p.health;
    p.x=original.x;p.y=original.y;
    return {picked,hp,enemyHits:V32.enemyHits};
  });
  assert(gameSystems.picked>=1,'defeated enemy must produce collectible loot');
  assert(gameSystems.hp<100&&gameSystems.enemyHits>=1,'hostile damage must affect survivors');
  const mobile=await make({width:393,height:852},true);
  await mobile.screenshot({path:'artifacts/Survival_Paradise_V32_Android_Viewport.png',fullPage:true});
  await mobile.locator('#v32Aim').uncheck();
  assert.equal(await mobile.evaluate(()=>SP_TEST_API.getState().aim),false);
  await mobile.locator('#v32Aim').check();
  await mobile.locator('#pause').click();
  assert.equal(await mobile.evaluate(()=>SCENE.paused),true);
  await mobile.locator('#pause').click();
  await mobile.waitForTimeout(1500);
  assert.equal(await mobile.evaluate(()=>SP_TEST_API.getState().bodyAtlasReady),true);
  assert.deepStrictEqual(errors,[],'Runtime errors on browser pages');
  const report={status:'pass',baseline:'V31',version:'V32',atlases:{body:hash(a[0]),gear:hash(a[1])},desktop:state,
    mobile:await mobile.evaluate(()=>SP_TEST_API.getState()),pageErrors:errors,
    screenshots:['Survival_Paradise_V32_Desktop.png','Survival_Paradise_V32_Android_Viewport.png'],animationFrames:12};
  fs.writeFileSync('artifacts/V32_QA_Report.json',JSON.stringify(report,null,2));
  console.log('V32 QA PASS',JSON.stringify({sourceSpritesIdentical:true,playerCount:state.count,frames:12,shots:state.shots,pickups:state.pickups}));
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
