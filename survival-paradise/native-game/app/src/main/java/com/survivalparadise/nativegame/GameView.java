package com.survivalparadise.nativegame;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.Rect;
import android.graphics.RectF;
import android.view.MotionEvent;
import android.view.View;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Locale;
import java.util.Random;

/**
 * Actual native Android 2D game loop and human player controls.
 * No WebView, HTML, JavaScript or hosted simulation runtime.
 * Preserves the two immutable approved V31 transparent PNG atlases.
 */
public final class GameView extends View {
    final MainActivity host;
    final Paint p=new Paint();
    private static final android.graphics.Typeface PIXEL_BOLD=
        android.graphics.Typeface.create("monospace",1);
    private static final android.graphics.Typeface PIXEL_NORMAL=
        android.graphics.Typeface.create("monospace",0);
    final Paint pixel=new Paint(Paint.ANTI_ALIAS_FLAG==0?0:0);
    Bitmap body,approvedWalkColors,stableBody,npcRoleAtlas,npcIdleAtlas,npcWalkV56,npcIdleV56,gear,approvedAxe;
    Bitmap pickaxeV81;
    Bitmap crosshairReticle;
    Bitmap biomeProps;
    final Paint reticlePaint=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);
    Bitmap campStatic; // immutable pre-rendered authored camp, not per-frame rectangles

    static final int ROLE_BANDIT=0,ROLE_GUARD=2,ROLE_MEDIC=4,ROLE_MECHANIC=6,
                     ROLE_TRADER=8,ROLE_CIVILIAN=10;
    static final float CAMP_X=1080,CAMP_Y=710;
    private static final float CAMP_TEXTURE_LEFT=CAMP_X-480,CAMP_TEXTURE_TOP=CAMP_Y-355;
    final Random rng=new Random(14901);
    static final float H=660, WORLD_W=3200, WORLD_H=2200;
    static final int[] RANGES={250,265,220,0,430,415,395,325,650,435,330,74};
    static final int[] MAG={12,6,28,1,30,30,28,6,5,75,8,1};
    static final float[] RATES={.35f,.54f,.14f,999,.13f,.19f,.2f,.68f,1.35f,.095f,.95f,.58f};
    static final int[] POWER={23,37,12,0,15,20,19,46,110,11,78,52};
    static final float[] MX=MuzzleGeometryV49.X;
    static final float[] MY=MuzzleGeometryV49.Y;
    static final float[] MAIN_X={103,103,103,97,102,101,101,101,101,102,101,102};
    static final float[] MAIN_Y={76,75,76,78,77,77,77,77,77,77,77,81};
    static final float[] OFF_X={0,0,0,0,135,146,148,151,145,149,141,0};
    static final float[] OFF_Y={0,0,0,0,77,75,72,75,73,71,74,0};
    static final int DK=0xff101b1a,WHITE=0xffedf2e6,OLIVE=0xff8ab397,ORANGE=0xffe8bc72,RED=0xffce766b;

    float scale=1,headScaleV82=1f,handScale=1,support=0,supportVertical=0,timeSpeed=1,zoom=1,walkSpeedMultiplier=1.30f,walkingAnimationMultiplierV79=1f;
    boolean showHands=true,showWeapons=true,anchors=false,hitboxes=false,enemyAI=true,
            aimRotation=true,recoilFX=true,lootEnabled=true,night=true;
    boolean playing=false,paused=false,settingsPause=false,wasPaused=false,hasSave=false,gameOver=false;
    boolean lampOn=true,neonEnabled=true,campfiresLit=true;
    int nightDarkness=211,flashlightReach=490;
    final LightingV47 lighting=new LightingV47();
    final WorldChunkCache terrainChunks=new WorldChunkCache((int)CAMP_X,(int)CAMP_Y);
    // V47: solar clock advances during gameplay, including smooth dawn/dusk.
    final GameClockV47 clock=new GameClockV47(21*60f);
    boolean automaticDayNight=true;
    int lightAlpha=210;
    static final float[][] FIXED_CAMPFIRES={{1170,805},{2140,1550},{300,780}};
    static final float[][] NEONS={
       {465,321,LightingV47.NEON_BLUE},{1775,343,LightingV47.NEON_PINK},
       {2455,1170,LightingV47.NEON_BLUE},{857,1710,LightingV47.NEON_PINK}};
    final ArrayList<float[]> builtCampfires=new ArrayList<>();
    final CampCraftV83 craftV83=new CampCraftV83();
    final SalvageWorldV84 salvageWorldV84=new SalvageWorldV84();
    final ItemIconsV84 itemIconsV84=new ItemIconsV84();
    int placingKindV84=-1,placingPointerV84=-1;
    float placingXv84,placingYv84;
    final ResourceWorldV80 harvestWorld=new ResourceWorldV80();
    final HarvestActionV81 harvestV81=new HarvestActionV81();
    float harvestImpactTimeV81=0f;
    float playerX=1000,playerY=1060,health=100,stamina=100,shotClock=0,reloadClock=0,recoil=0;
    float aimX=1,aimY=0,stickX=0,stickY=0;
    int face=1,gun=0,ammo=12,kills=0,wave=1,scrap=0,medkits=0,ammoPacks=0,enemyCount=0;
    int wood=0,stone=0,fiber=0;
    String gatherFeedback="";float gatherFeedbackTime=0f;
    float worldTimer=0,autSaveClock=0,shake=0;
    long lastFrame=0;
    float viewW=1200,viewH=660,drawScale=1,camX=0,camY=0;
    int leftPointer=-1,rightPointer=-1,firePointer=-1,fireLeftPointer=-1;
    int editPointer=-1,editControl=-1,editX=0,editY=0;
    float editGrabX=0,editGrabY=0;
    int selectedHudControl=0;
    static final int MOVE_PAD=LegacyControlsV58.COUNT,AIM_PAD=MOVE_PAD+1,HUD_ITEMS=MOVE_PAD+2;
    int panelPointer=-1;float panelGrabX,panelGrabY;
    float panelX=0,panelY=62,panelScale=1f;
    boolean editControls=false,showStatusBars=true,showCrosshair=true,lookAheadEnabled=true;
    float lookAheadStrength=0f,lookAheadThreshold=.72f,aimDeflection=0f;
    float lookAheadSmooth=5f;
    float cameraLookX=0f,cameraLookY=0f,cameraPanLimit=65f;
    float cursorWorldX=0f,cursorWorldY=0f,cursorMoveX=0f,cursorMoveY=0f;
    float aimStickX=0f,aimStickY=0f; // sliding physical right-stick thumb
    float aimCursorDistance=190f,crosshairRestPercent=100f; // tuned per-weapon radial resting reticle
    long updateNs=0,worldNs=0,lightingNs=0;
    boolean cursorInitialized=false;
    float cursorSpeed=650f,aimDeadzone=.17f,aimResponseCurve=1.75f;
    float aimSteeringPercent=100f,cameraPanSpeed=350f,targetAimX=1f,targetAimY=0f;
    boolean legacyDirectionalAim=false;
    float reticleSize=1f;
    int[] hotbar=new int[6];
    float hotbarX=0,hotbarY=0,hotbarScale=1f;
    int hotbarOpacity=90,selectedHotbar=0;
    int hotbarPointer=-1;
    static final int HOTBAR=HUD_ITEMS,EDITOR_ITEMS=HOTBAR+1;
    static final String[] HOTBAR_TYPES={
        "EMPTY","MEDKIT","AMMO","PISTOL","SHOTGUN","UZI","FOOD","WATER","TORCH",
        "BARRICADE","LIGHT POST"};
    int foodCount=2,waterCount=2;
    float hotbarGrabX,hotbarGrabY;
    float hunger=100f,thirst=100f,fatigue=0f;
    float knifeDuration=0f,knifeCooldown=0f;
    int knifeDirection=0;
    boolean knifeHitPending=false;
    Bandit knifeTarget=null;
    boolean runHeld=false,crouchHeld=false,dualTorch=true;
    float fireButtonX=0,fireButtonY=0,fireButtonSize=1f;
    boolean firing=false,moving=false;
    // V54.1: old control geometry remains default; test UI can tune it live.
    float movePadScale=1f,aimPadScale=1f,moveSensitivity=1f,aimSensitivity=1f;
    int controlOpacity=100,hudOpacityV73=100,topButtonOpacityV76=22;
    boolean showPerf=false,showChunkGrid=false;
    int npcSleepRadius=1200;
    int lastVisibleNpcs=0;
    int lastCulledNpcs=0;
    float smoothedFrameMs=16.67f;
    long drawFrames=0;
    final AnimationCycle playerAnimation=new AnimationCycle();
    // Keep projectile collision against the exact approved atlas alpha, not an
    // unrelated circle near the characters' feet.
    CharacterCollision.PixelMask bodyMask=(x,y)->false;
    CharacterCollision.PixelMask walkMask=(x,y)->false;
    static PackedAlphaMaskV75 packAlpha(Bitmap bitmap){
        int w=bitmap.getWidth(),h=bitmap.getHeight();
        int[] rgba=new int[w*h];
        bitmap.getPixels(rgba,0,w,0,0,w,h);
        return PackedAlphaMaskV75.fromArgb(rgba,w,h);
    }
    final ArrayList<Bandit> enemies=new ArrayList<>();
    final ArrayList<Survivor> friends=new ArrayList<>();
    final ArrayList<Survivor> campStaff=new ArrayList<>();
    final ArrayList<Shot> shots=new ArrayList<>();
    final ArrayList<Drop> drops=new ArrayList<>();
    final ArrayList<Spark> sparks=new ArrayList<>();
    final ArrayList<Flash> flashes=new ArrayList<>();
    final ArrayList<Cover> covers=new ArrayList<>();
    int allySetting=1,allyCurrent=1;
    int followMode=FollowFormationV61.SCATTER,followSpacing=125;
    float followHeadingX=1f,followHeadingY=0f;
    final Rect src=new Rect();
    final RectF dest=new RectF();
    final float PAD=46;
    static class Bandit {float x,y,hp=78,cd,hit;int face=1;boolean active=true;
        final AnimationCycle animation=new AnimationCycle();
        int variant;
        Bandit(float a,float b,int variant){x=a;y=b;cd=.7f;this.variant=variant;}}
    static class Survivor {float x,y,homeX,homeY,cd,aimX=1,aimY=0;int gun,face=1,variant;
        final AnimationCycle animation=new AnimationCycle();
        Survivor(float a,float b,int g,int variant){x=a;y=b;homeX=a;homeY=b;gun=g;this.variant=variant;}}
    static class Shot {float x,y,vx,vy,life,damage;boolean hostile;int color;
        Shot(float x,float y,float vx,float vy,float damage,boolean enemy){
            this.x=x;this.y=y;this.vx=vx;this.vy=vy;this.damage=damage;this.life=Ballistics.PROJECTILE_LIFE;
            this.hostile=enemy;this.color=enemy?0xffffa88a:0xffeada9e;
        }}
    static class Flash {float x,y,dx,dy,ttl=.065f;
        Flash(float x,float y,float dx,float dy){this.x=x;this.y=y;this.dx=dx;this.dy=dy;}}
    static class Drop {float x,y,ttl=40;int type;
        Drop(float x,float y,int type){this.x=x;this.y=y;this.type=type;}}
    static class Spark {float x,y,vx,vy,ttl=.3f;int color;
        Spark(float x,float y,float vx,float vy,int c){this.x=x;this.y=y;this.vx=vx;this.vy=vy;color=c;}}
    static class Cover {float x,y,w,h;int kind;
        Cover(float a,float b,float c,float d,int k){x=a;y=b;w=c;h=d;kind=k;}}

    GameView(MainActivity activity){
        super(activity);host=activity;
        setFocusable(true);setLayerType(View.LAYER_TYPE_HARDWARE,null);
        pixel.setAntiAlias(false);pixel.setFilterBitmap(false);
        try(InputStream ret=getResources().getAssets().open("crosshair_v62.png.b64")){
            ByteArrayOutputStream reticleBytes=new ByteArrayOutputStream();
            byte[] buffer=new byte[4096];int count;
            while((count=ret.read(buffer))>=0)reticleBytes.write(buffer,0,count);
            byte[] raw=android.util.Base64.decode(reticleBytes.toByteArray(),
                android.util.Base64.DEFAULT);
            crosshairReticle=BitmapFactory.decodeByteArray(raw,0,raw.length);
            if(crosshairReticle==null||crosshairReticle.getWidth()!=96)
                throw new IllegalStateException("Approved crimson reticle failed decoding");
        }catch(Exception fail){throw new IllegalStateException(
             "Missing approved V62 reticle asset",fail);}
        try(InputStream bs=getResources().getAssets().open("body.png");
            InputStream gs=getResources().getAssets().open("gear.png")){
            body=BitmapFactory.decodeStream(bs);gear=BitmapFactory.decodeStream(gs);
            // The V44 walk atlas uses ONLY original V41 colors and upper-body
            // pixels. User's reference contributes the 4 lower-leg OUTLINES,
            // not its red/blue/skin palette. Idle always uses unchanged body.png.
            try(InputStream walk=getResources().getAssets().open("approved_v44_walk_palette.png")){
                approvedWalkColors=BitmapFactory.decodeStream(walk);
                if(approvedWalkColors==null||approvedWalkColors.getWidth()!=1040||
                   approvedWalkColors.getHeight()!=160)
                    throw new IllegalStateException("V44 color-locked walking atlas invalid");
            }
            try(InputStream stable=getResources().getAssets().open("stable_v51_body.png");
                InputStream npcs=getResources().getAssets().open("npc_roles_v51.png")){
                stableBody=BitmapFactory.decodeStream(stable);
                npcRoleAtlas=BitmapFactory.decodeStream(npcs);
                if(stableBody.getWidth()!=1040||stableBody.getHeight()!=160||
                   npcRoleAtlas.getWidth()!=1040||npcRoleAtlas.getHeight()!=1920)
                    throw new IllegalStateException("V51 character atlases not correctly built");
            }
            // V52: Role palettes applied to the ORIGINAL planted idle body frame.
            // The V51 reconstructed walk atlas is never substituted for idle.
            try(InputStream roleIdle=getResources().getAssets().open("npc_idle_v52.png")){
                npcIdleAtlas=BitmapFactory.decodeStream(roleIdle);
                if(npcIdleAtlas==null||npcIdleAtlas.getWidth()!=260||
                   npcIdleAtlas.getHeight()!=1920)
                    throw new IllegalStateException("V52 original-pose NPC idle atlas invalid");
            }
            // V56 restored approved walking sheet: NPC recolors only,
            // frame pixels/alpha and player character source remain immutable.
            try(InputStream w=getResources().getAssets().open("npc_walk_v56.png");
                InputStream i=getResources().getAssets().open("npc_idle_v56.png")){
                npcWalkV56=BitmapFactory.decodeStream(w);
                npcIdleV56=BitmapFactory.decodeStream(i);
                if(npcWalkV56==null||npcWalkV56.getWidth()!=1040||npcWalkV56.getHeight()!=1920||
                   npcIdleV56==null||npcIdleV56.getWidth()!=260||npcIdleV56.getHeight()!=1920)
                    throw new IllegalStateException("V56 approved-skeleton role atlases invalid");
            }
            try(InputStream axe=getResources().getAssets().open("approved_v29_axe.png")){
                approvedAxe=BitmapFactory.decodeStream(axe);
            }
        }catch(Exception e){body=null;gear=null;}
        try(InputStream env=getResources().getAssets().open("world_props_v74.png")){
            biomeProps=BitmapFactory.decodeStream(env);
            if(biomeProps==null||biomeProps.getWidth()!=BiomeWorldV74.CELL*BiomeWorldV74.SPRITES||
                biomeProps.getHeight()!=BiomeWorldV74.CELL)biomeProps=null;
        }catch(Exception ignored){biomeProps=null;}
        // Build lossless alpha masks once, not per-bullet on the render thread.
        if(body!=null)bodyMask=packAlpha(body);
        if(approvedWalkColors!=null)walkMask=packAlpha(approvedWalkColors);
        pickaxeV81=makePixelPickaxeV81();
        initCovers();reloadSettings();hasSave=host.prefs.getBoolean("hasSave",false);
    }
    void initCovers(){
        covers.add(new Cover(350,280,280,180,0));
        covers.add(new Cover(1650,300,330,215,0));
        covers.add(new Cover(2350,1120,345,275,0));
        covers.add(new Cover(750,1660,310,220,0));
        covers.add(new Cover(1300,850,95,37,1));
        covers.add(new Cover(1920,1020,110,48,1));
        covers.add(new Cover(2100,710,120,36,1));
        covers.add(new Cover(650,1160,100,38,1));
        covers.add(new Cover(1360,1570,110,40,1));
        covers.add(new Cover(2520,1760,110,40,1));
    }
    boolean isPlaying(){return playing;}
    void reloadSettings(){
        scale=host.setting("scale",100)/100f;
        headScaleV82=HeadKnifeV82.headMultiplier(host.setting("headSizeV82",HeadKnifeV82.HEAD_DEFAULT));
        handScale=host.setting("hand",100)/100f;
        support=host.setting("support",0);
        supportVertical=host.setting("supportY",0);
        timeSpeed=host.setting("speed",100)/100f;
        walkSpeedMultiplier=PlayerMovementV77.multiplier(host.setting("walkSpeedV77",PlayerMovementV77.DEFAULT_PERCENT));
        walkingAnimationMultiplierV79=WalkingAnimationV79.multiplier(
            host.setting("walkingAnimationSpeedV79",WalkingAnimationV79.DEFAULT_PERCENT));
        movePadScale=host.setting("movePadSize",180)/100f;
        aimPadScale=host.setting("aimPadSize",180)/100f;
        moveSensitivity=host.setting("moveSensitivity",100)/100f;
        aimSensitivity=host.setting("aimSensitivity",100)/100f;
        controlOpacity=host.setting("controlOpacity",100);
        hudOpacityV73=CameraHudV73.opacity(host.setting("hudOpacityV73",100));
        topButtonOpacityV76=Math.max(0,Math.min(65,host.setting("topButtonOpacityV76",22)));
        dualTorch=host.option("dualTorch",true);
        editControls=host.option("editControls",false);
        selectedHudControl=Math.min(EDITOR_ITEMS-1,host.setting("selectedButton",0));
        panelX=host.setting("hudPanelX",0);
        panelY=host.setting("hudPanelY",62);
        panelScale=host.setting("hudPanelSize",100)/100f;
        showStatusBars=host.option("showStatusBars",true);
        showCrosshair=host.option("showCrosshair",true);
        // V71 rollback: old panning preference must not override classic aim.
        lookAheadEnabled=host.option("classicAimCameraV71",true);
        lookAheadThreshold=host.setting("lookAheadThreshold",72)/100f;
        lookAheadStrength=host.setting("lookAheadStrength",420);
        lookAheadSmooth=host.setting("lookAheadSmooth",8);
        // Fresh preference key avoids V67/V68 legacy 420px look-ahead values.
        // Percentage adjusts the circular maximum automatically by weapon type.
        cameraPanLimit=host.setting("cameraPanPercentV72",72);
        // New preference key intentionally migrates V63's 500px/s ceiling to a fast V64 default.
        // Separate V68 keys intentionally migrate the excessively fast V67
        // defaults without changing earlier player preference storage.
        cursorSpeed=host.setting("cursorSpeedV68",650);
        aimDeadzone=host.setting("aimDeadzoneV68",17)/100f;
        aimResponseCurve=host.setting("aimCurveV68",175)/100f;
        aimSteeringPercent=host.setting("aimSteeringV68",100);
        cameraPanSpeed=host.setting("cameraPanSpeedV68",350);
        legacyDirectionalAim=host.option("legacyDirectionalAim",false);
        crosshairRestPercent=host.setting("crosshairRestPercent",100);
        reticleSize=host.setting("reticleSize",100)/100f;
        hotbarX=host.setting("uiX"+HOTBAR,-17);
        hotbarY=host.setting("uiY"+HOTBAR,0);
        hotbarScale=host.setting("uiSize"+HOTBAR,105)/100f;
        hotbarOpacity=host.setting("uiAlpha"+HOTBAR,90);
        for(int i=0;i<6;i++)hotbar[i]=host.setting("hotbar"+i,
            i==0?1:i==1?2:i==2?3:i==3?4:i==4?6:7);
        fireButtonX=host.setting("fireButtonX",0);
        fireButtonY=host.setting("fireButtonY",0);
        fireButtonSize=host.setting("fireButtonSize",100)/100f;
        zoom=CameraHudV73.zoom(host.setting("cameraZoom",100));
        showPerf=host.option("testPerf",false);
        showChunkGrid=host.option("testChunkGrid",false);
        npcSleepRadius=host.setting("npcSleepRadius",1200);
        followMode=Math.max(0,Math.min(4,host.setting("followMode",0)));
        followSpacing=host.setting("followSpacing",125);
        lighting.setPixelScale(host.setting("lightResolution",220)/100f);
        lighting.setFastPointLights(host.option("fastPointLights",true));
        lighting.setStaticCache(host.option("staticLightCache",true));
        terrainChunks.setLimits(host.setting("testCacheMax",36),
                                host.setting("testPreloadRadius",2));
        showHands=host.option("hands",true);
        showWeapons=host.option("weapons",true);
        anchors=host.option("anchors",false);
        hitboxes=host.option("hitboxes",false);
        enemyAI=host.option("enemyAI",true);
        aimRotation=host.option("aimRotation",true);
        recoilFX=host.option("recoil",true);
        lootEnabled=host.option("loot",true);
        automaticDayNight=host.option("autoDayNight",true);
        night=host.option("night",true);
        clock.configure(host.setting("dayLength",36));
        lampOn=host.option("lampOn",true);
        neonEnabled=host.option("neonLights",true);
        campfiresLit=host.option("campfiresLit",true);
        nightDarkness=Math.round(255f*host.setting("darkness",83)/100f);
        flashlightReach=host.setting("beamReach",490);
        int next=host.setting("gun",0);
        if(next!=gun){gun=Math.max(0,Math.min(11,next));ammo=MAG[gun];reloadClock=0;}
        refreshDaylight();
        allySetting=host.setting("survivors",1);
        if(playing)adjustFriends();
        invalidate();
    }
    void refreshDaylight(){
        lightAlpha=automaticDayNight?clock.darkness(nightDarkness):(night?nightDarkness:0);
    }
    void adjustFriends(){
        while(friends.size()<allySetting-1){
            friends.add(new Survivor(playerX-30+rng.nextInt(100),playerY-30+rng.nextInt(100),
                    2+friends.size()%9,ROLE_GUARD+friends.size()%2));
        }
        while(friends.size()>allySetting-1)friends.remove(friends.size()-1);
        allyCurrent=1+friends.size();
    }
    void newGame(){
        playerX=CAMP_X;playerY=CAMP_Y;health=100;stamina=100;
        hunger=100;thirst=100;fatigue=0;foodCount=2;waterCount=2;
        knifeDuration=0;knifeCooldown=0;
        cameraLookX=0;cameraLookY=0;aimDeflection=0;
        cursorInitialized=false;cursorMoveX=0;cursorMoveY=0;
        playerAnimation.reset();moving=false;stickX=0;stickY=0;shotClock=0;
        gun=Math.max(0,Math.min(11,host.setting("gun",0)));ammo=MAG[gun];
        kills=0;wave=1;scrap=0;medkits=1;ammoPacks=2;
        wood=0;stone=0;fiber=0;harvestWorld.clear();salvageWorldV84.clear();
        placingKindV84=-1;placingPointerV84=-1;harvestV81.cancel();
        harvestImpactTimeV81=0;gatherFeedback="";gatherFeedbackTime=0;
        worldTimer=0;autSaveClock=0;
        clock.setClock(night?21*60f:12*60f,1);
        face=1;aimX=1;aimY=0;refreshDaylight();
        enemies.clear();friends.clear();campStaff.clear();shots.clear();drops.clear();sparks.clear();flashes.clear();builtCampfires.clear();
        craftV83.clear();removeBarricadeCoverV83();
        initCampStaff();
        playing=true;paused=false;settingsPause=false;gameOver=false;
        adjustFriends();spawnWave();
        saveProgress();invalidate();
    }
    void continueGame(){
        if(!hasSave){newGame();return;}
        playerAnimation.reset();moving=false;stickX=0;stickY=0;
        clock.setClock(host.prefs.getFloat("clockMinutes",night?21*60f:12*60f),
            host.setting("clockDay",1));
        aimX=host.prefs.getFloat("aimX",1f);aimY=host.prefs.getFloat("aimY",0f);
        float lengthAim=(float)Math.hypot(aimX,aimY);
        if(lengthAim<.01f){aimX=1;aimY=0;}else{aimX/=lengthAim;aimY/=lengthAim;}
        face=aimX<-.025f?-1:1;
        refreshDaylight();
        playerX=host.prefs.getFloat("px",1000);playerY=host.prefs.getFloat("py",1060);
        health=host.prefs.getFloat("hp",100);
        stamina=host.prefs.getFloat("stamina",100);
        hunger=host.prefs.getFloat("hunger",100);
        thirst=host.prefs.getFloat("thirst",100);
        fatigue=host.prefs.getFloat("fatigue",0);
        foodCount=host.setting("foodCount",2);
        waterCount=host.setting("waterCount",2);
        knifeDuration=0;knifeCooldown=0;cameraLookX=0;cameraLookY=0;
        cursorInitialized=false;cursorMoveX=0;cursorMoveY=0;
        kills=host.setting("kills",0);
        wave=Math.max(1,host.setting("wave",1));
        scrap=host.setting("scrap",0);medkits=host.setting("medkits",1);ammoPacks=host.setting("ammoPacks",2);
        wood=host.setting("woodV80",0);stone=host.setting("stoneV80",0);fiber=host.setting("fiberV80",0);
        harvestWorld.decode(host.prefs.getString("depleted_resources_v80",""));
        harvestV81.cancel();harvestImpactTimeV81=0f;
        gatherFeedback="";gatherFeedbackTime=0;
        gun=Math.max(0,Math.min(11,host.setting("gun",0)));
        ammo=Math.max(0,Math.min(MAG[gun],host.setting("ammo",MAG[gun])));
        enemies.clear();friends.clear();shots.clear();drops.clear();sparks.clear();flashes.clear();
        restoreCampfires();
        craftV83.decode(host.prefs.getString("camp_buildings_v83",""));
        craftV83.decodeStock(host.prefs.getString("camp_stock_v84",""));
        salvageWorldV84.decode(host.prefs.getString("salvaged_scrap_v84",""));
        placingKindV84=-1;placingPointerV84=-1;
        removeBarricadeCoverV83();restoreBarricadeCoverV83();
        campStaff.clear();initCampStaff();
        playing=true;paused=false;gameOver=false;
        adjustFriends();spawnWave();invalidate();
    }
    String encodeCampfires(){
        StringBuilder sb=new StringBuilder();
        for(float[] f:builtCampfires){if(sb.length()>0)sb.append(';');sb.append((int)f[0]).append(',').append((int)f[1]);}
        return sb.toString();
    }
    void restoreCampfires(){
        builtCampfires.clear();
        String raw=host.prefs.getString("campfire_locations","");
        for(String pair:raw.split(";")){
            String[] coords=pair.split(",");
            if(coords.length!=2)continue;
            try{
                float x=Float.parseFloat(coords[0]),y=Float.parseFloat(coords[1]);
                if(Float.isFinite(x)&&Float.isFinite(y)&&builtCampfires.size()<16)
                    builtCampfires.add(new float[]{x,y});
            }catch(NumberFormatException ignored){}
        }
    }
    void removeBarricadeCoverV83(){
        for(Iterator<Cover> it=covers.iterator();it.hasNext();)
            if(it.next().kind==3)it.remove();
    }
    void restoreBarricadeCoverV83(){
        for(CampCraftV83.Structure s:craftV83.objects)
            if(s.kind==CampCraftV83.BARRICADE)
                covers.add(new Cover(s.x-39,s.y-15,78,27,3));
    }
    /** Crafting yields a storable backpack item; no immediate construction. */
    boolean craftIntoBagV84(int kind){
        if(!playing||gameOver){craftV83.error="Start a game first";return false;}
        int[] resources={wood,stone,fiber,scrap};
        if(!craftV83.craftToBag(kind,resources))return false;
        wood=resources[0];stone=resources[1];fiber=resources[2];scrap=resources[3];
        gatherFeedback="CRAFTED "+(kind==0?"BARRICADE":"LIGHT POST")+" (BAG)";
        gatherFeedbackTime=2.2f;saveProgress();invalidate();return true;
    }
    boolean selectPlaceItemV84(int kind){
        if(!playing||gameOver||kind<0||kind>1||craftV83.stock[kind]<1){
            craftV83.error="No crafted item in backpack";return false;
        }
        placingKindV84=kind;placingPointerV84=-1;
        placingXv84=playerX+face*130f;placingYv84=playerY+28f;
        invalidate();return true;
    }
    void cancelPlaceV84(){placingKindV84=-1;placingPointerV84=-1;}
    /** Placement consumes one finished item only when valid. */
    boolean placeAtV84(float x,float y){
        if(placingKindV84<0||!playing||paused||editControls)return false;
        placingXv84=x;placingYv84=y;
        if(distance(x,y,playerX,playerY)>420f){
            craftV83.error="Move closer to build";return false;
        }
        if(blocked(x,y,48f)){craftV83.error="Clear ground needed";return false;}
        for(float[] f:FIXED_CAMPFIRES)if(distance(x,y,f[0],f[1])<115f){
            craftV83.error="Too close to campfire";return false;
        }
        for(float[] f:builtCampfires)if(distance(x,y,f[0],f[1])<115f){
            craftV83.error="Too close to campfire";return false;
        }
        int kind=placingKindV84;
        if(!craftV83.placeFromBag(kind,x,y))return false;
        if(kind==CampCraftV83.BARRICADE)
            covers.add(new Cover(x-39,y-15,78,27,3));
        gatherFeedback=kind==0?"BARRICADE PLACED":"LIGHT POST PLACED";
        gatherFeedbackTime=2.7f;cancelPlaceV84();saveProgress();invalidate();return true;
    }
    /** Legacy direct placement, not exposed by V84 UI. */
    boolean craftPlaceV83(int kind){
        if(!playing||gameOver){craftV83.error="Start a game first";return false;}
        if(harvestV81.active){craftV83.error="Finish harvesting first";return false;}
        float x=playerX+face*110f,y=playerY+28f;
        if(blocked(x,y,43)){craftV83.error="Find clear ground";return false;}
        for(float[] fire:FIXED_CAMPFIRES)if(distance(x,y,fire[0],fire[1])<110){
            craftV83.error="Move away from campfire";return false;
        }
        for(float[] fire:builtCampfires)if(distance(x,y,fire[0],fire[1])<110){
            craftV83.error="Move away from campfire";return false;
        }
        int[] ingredients={wood,stone,fiber,scrap};
        if(!craftV83.craft(kind,x,y,ingredients))return false;
        wood=ingredients[0];stone=ingredients[1];fiber=ingredients[2];scrap=ingredients[3];
        if(kind==CampCraftV83.BARRICADE)
            covers.add(new Cover(x-39,y-15,78,27,3));
        gatherFeedback=kind==CampCraftV83.BARRICADE?"BUILT BARRICADE":"BUILT LIGHT POST";
        gatherFeedbackTime=2.5f;saveProgress();invalidate();
        return true;
    }
    /** Chunky dark-outlined world props, depth-sorted with NPCs. */
    void drawCraftStructureV83(Canvas c,CampCraftV83.Structure node){
        float x=node.x,y=node.y;
        if(node.kind==CampCraftV83.BARRICADE){
            rect(c,x-43,y-25,86,40,0xff172522);
            rect(c,x-38,y-21,76,12,0xff775a3e);
            rect(c,x-38,y-6,76,11,0xff997649);
            rect(c,x-38,y+8,76,5,0xff625037);
            rect(c,x-31,y-27,9,43,0xff28372e);
            rect(c,x+22,y-27,9,43,0xff28372e);
            for(int i=-29;i<27;i+=18)rect(c,x+i,y-18,5,3,0xffc2a276);
        }else{
            rect(c,x-10,y-92,20,94,0xff16241f);
            rect(c,x-5,y-88,10,86,0xff786043);
            rect(c,x-21,y-99,42,12,0xff2a3f39);
            rect(c,x-17,y-95,34,6,0xff978356);
            rect(c,x-13,y-87,26,13,0xffd5ae69);
            rect(c,x-8,y-83,16,8,0xffffdf8f);
            rect(c,x-9,y-3,18,6,0xff394d40);
        }
    }
    void placeCampfire(){
        if(scrap<3){android.widget.Toast.makeText(host,"Campfire needs 3 scrap",android.widget.Toast.LENGTH_SHORT).show();return;}
        if(builtCampfires.size()>=16){android.widget.Toast.makeText(host,"Campfire limit reached",android.widget.Toast.LENGTH_SHORT).show();return;}
        float x=playerX+face*65,y=playerY+35;
        if(blocked(x,y,15)){android.widget.Toast.makeText(host,"Clear ground needed",android.widget.Toast.LENGTH_SHORT).show();return;}
        scrap-=3;builtCampfires.add(new float[]{x,y});saveProgress();
    }
    void toggleNight(){
        if(automaticDayNight){
            // Testing convenience: jump to a fixed phase, but the cycle
            // immediately continues progressing automatically afterward.
            clock.jumpToHour(clock.nightFraction()>.5f?12f:22f);
        }else{
            night=!night;
            host.prefs.edit().putBoolean("night",night).apply();
        }
        refreshDaylight();saveProgress();invalidate();
    }
    void toggleLamp(){
        lampOn=!lampOn;
        host.prefs.edit().putBoolean("lampOn",lampOn).apply();
    }
    void initCampStaff(){
        // Approved roles and both sexes share the same exact V51 idle/walk geometry.
        // Distinct NPC identities are sourced from the role art already in the repo.
        campStaff.add(new Survivor(CAMP_X-175,CAMP_Y-75,3,ROLE_TRADER));
        campStaff.add(new Survivor(CAMP_X-126,CAMP_Y-78,3,ROLE_MEDIC+1));
        campStaff.add(new Survivor(CAMP_X+179,CAMP_Y-67,3,ROLE_MECHANIC));
        campStaff.add(new Survivor(CAMP_X+156,CAMP_Y+84,2,ROLE_GUARD+1));
        campStaff.add(new Survivor(CAMP_X-180,CAMP_Y+96,3,ROLE_CIVILIAN));
    }
    void spawnWave(){
        enemies.clear();enemyCount=5+Math.min(17,wave*2);
        for(int i=0;i<enemyCount;i++){
            float a=(float)(rng.nextDouble()*Math.PI*2);
            float distance=430+rng.nextInt(620);
            float x=playerX+(float)Math.cos(a)*distance;
            float y=playerY+(float)Math.sin(a)*distance;
            if(blocked(x,y,22)){x+=140;y+=130;}
            // Prevent hostile wave placement in the protected spawn clearing.
            if(distance(x,y,CAMP_X,CAMP_Y)<450){x+=520;}
            enemies.add(new Bandit(x,y,i%2));
        }
    }
    void saveProgress(){
        if(!playing||gameOver)return;
        host.prefs.edit().putBoolean("hasSave",true).putFloat("px",playerX).putFloat("py",playerY)
                .putFloat("hp",health).putFloat("stamina",stamina)
                .putFloat("hunger",hunger).putFloat("thirst",thirst)
                .putFloat("fatigue",fatigue).putInt("foodCount",foodCount)
                .putInt("waterCount",waterCount).putInt("kills",kills).putInt("wave",wave)
                .putInt("scrap",scrap).putInt("medkits",medkits)
                .putInt("ammoPacks",ammoPacks).putInt("ammo",ammo)
                .putInt("woodV80",wood).putInt("stoneV80",stone).putInt("fiberV80",fiber)
                .putString("depleted_resources_v80",harvestWorld.encode())
                .putString("campfire_locations",encodeCampfires())
                .putString("camp_buildings_v83",craftV83.encode())
                .putString("camp_stock_v84",craftV83.encodeStock())
                .putString("salvaged_scrap_v84",salvageWorldV84.encode())
                .putFloat("clockMinutes",clock.minute()).putInt("clockDay",clock.day())
                .putFloat("aimX",aimX).putFloat("aimY",aimY).apply();
        hasSave=true;
    }
    void menuPause(boolean b){
        if(b){wasPaused=paused;settingsPause=true;paused=true;
            stopWalking();}
        else{settingsPause=false;paused=wasPaused;}
        invalidate();
    }
    void togglePause(){if(!playing)return;paused=!paused;
        if(paused)stopWalking();saveProgress();invalidate();}
    void stopWalking(){stickX=0;stickY=0;moving=false;playerAnimation.reset();}
    boolean debugTeleport(float dx,float dy){
        if(!playing||gameOver)return false;
        cancelPlaceV84();harvestV81.cancel();releaseControls();playerX+=dx;playerY+=dy;
        shots.clear();flashes.clear();sparks.clear();
        saveProgress();invalidate();return true;
    }
    String testStats(){
        return String.format(Locale.US,
          "FPS %.1f | Frame %.1f ms | World (%.0f, %.0f) | Chunk (%d, %d)\\n" +
          "Terrain cache %d/%d | Generated %d | Queued %d | Hits %d | Misses %d",
          1000f/Math.max(1f,smoothedFrameMs),smoothedFrameMs,playerX,playerY,
          WorldChunkModel.chunkIndex(playerX),WorldChunkModel.chunkIndex(playerY),
          terrainChunks.residentCount(),terrainChunks.residentLimit(),
          terrainChunks.generated,terrainChunks.pendingCount(),
          terrainChunks.cacheHits,terrainChunks.cacheMisses);
    }
    void snapAimToWeaponRest(){
        targetAimX=aimX;targetAimY=aimY;
        aimCursorDistance=RadialAimV65.rest(gun,crosshairRestPercent);
        cursorWorldX=playerX+aimX*aimCursorDistance;
        cursorWorldY=playerY-42f+aimY*aimCursorDistance;
        cursorInitialized=true;
    }
    void releaseControls(){stopWalking();firing=false;leftPointer=-1;rightPointer=-1;
        firePointer=-1;fireLeftPointer=-1;editPointer=-1;editControl=-1;panelPointer=-1;
        runHeld=false;crouchHeld=false;aimDeflection=0;
        cursorMoveX=0;cursorMoveY=0;aimStickX=0;aimStickY=0;
        snapAimToWeaponRest();}
    void switchWeapon(){
        if(harvestV81.active)return;
        gun=(gun+1)%12;ammo=MAG[gun];reloadClock=0;
        snapAimToWeaponRest();
        host.prefs.edit().putInt("gun",gun).apply();
    }
    void reload(){
        if(gun==3||gun==11||ammo>=MAG[gun]||reloadClock>0)return;
        if(ammoPacks==0)return;
        ammoPacks--;reloadClock=1.25f;shotClock=0;
    }
    float clamp(float x,float min,float max){return Math.max(min,Math.min(max,x));}
    boolean blocked(float x,float y,float r){
        // V53 unbounded world: collisions are against solid structures, never map borders.
        for(Cover c:covers)if(x+r>c.x&&x-r<c.x+c.w&&y+r>c.y&&y-r<c.y+c.h)return true;
        return false;
    }
    float distance(float x,float y,float xx,float yy){return (float)Math.hypot(x-xx,y-yy);}
    Bandit nearest(float x,float y,float maxRange){
        Bandit best=null;float bestDist=maxRange;
        for(Bandit e:enemies){if(!e.active)continue;float d=distance(x,y,e.x,e.y);
            if(d<bestDist){best=e;bestDist=d;}}
        return best;
    }
    // A bullet's visible launch point is exactly the world-transformed barrel anchor.
    // The same grip pivot, left/right mirror and full semicircle are used by rendering.
    void knifeStrike(){
        if(!playing||paused||knifeCooldown>0||harvestV81.active)return;
        knifeCooldown=MeleeSlashV83.COOLDOWN;knifeDuration=MeleeSlashV83.DURATION;knifeHitPending=true;
        knifeTarget=nearest(playerX,playerY,MeleeSlashV83.REACH);
        float dx=knifeTarget==null?aimX:knifeTarget.x-playerX;
        float dy=knifeTarget==null?aimY:knifeTarget.y-playerY;
        knifeDirection=LegacyControlsV58.quantizeKnife(dx,dy);
        if(LegacyControlsV58.knifeX(knifeDirection)>.01f)face=1;
        else if(LegacyControlsV58.knifeX(knifeDirection)<-.01f)face=-1;
    }
    /** Larger knife component, consistently anchored to the approved weapon hand. */
    void drawKnifeBladeV82(Canvas c,float gx,float gy,float k){
        c.save();
        c.translate(gx,gy);
        c.scale(k,k);
        // Chunky stepped near-black outline, simplified hilt and brighter blade.
        rect(c,-8,-7,28,14,0xff13201f);
        rect(c,-5,-5,22,10,0xff77583e);
        rect(c,-4,-5,7,2,0xffb28d62);
        rect(c,14,-9,5,18,0xff172725);
        rect(c,19,-7,42,13,0xff16272c);
        rect(c,21,-5,33,9,0xff859b98);
        rect(c,23,-4,31,4,0xffc4d3c6);
        rect(c,51,-4,8,4,0xffe3e8dc);
        rect(c,60,-2,5,2,0xff324447);
        c.restore();
    }
    // V84 pointed crescent lies tangential to the blade's rotational cutting path.
    // The same reusable Path is reset each frame; no bitmap or object allocations.
    final Path knifeCutPathV84=new Path();
    void drawShortKnifeTrailV82(Canvas c,float gx,float gy,float s){
        float x=gx+94f*s,y=gy-4f*s;
        knifeCutPathV84.reset();
        knifeCutPathV84.moveTo(x-3*s,y-43*s);
        knifeCutPathV84.quadTo(x+24*s,y-15*s,x+11*s,y+30*s);
        knifeCutPathV84.quadTo(x-4*s,y+16*s,x-14*s,y-1*s);
        knifeCutPathV84.quadTo(x+7*s,y-23*s,x-3*s,y-43*s);
        knifeCutPathV84.close();
        color(0xff285958);c.drawPath(knifeCutPathV84,p);
        knifeCutPathV84.reset();
        knifeCutPathV84.moveTo(x-1*s,y-37*s);
        knifeCutPathV84.quadTo(x+17*s,y-13*s,x+7*s,y+23*s);
        knifeCutPathV84.quadTo(x-2*s,y+11*s,x-9*s,y-1*s);
        knifeCutPathV84.quadTo(x+8*s,y-17*s,x-1*s,y-37*s);
        knifeCutPathV84.close();
        color(0xffe0f7e9);c.drawPath(knifeCutPathV84,p);
    }
    /** Small torso-pivot melee animation with a proper weapon-hand grip. */
    void drawKnifeSwing(Canvas c,float s){
        if(knifeDuration<=0f)return;
        float t=1f-knifeDuration/MeleeSlashV83.DURATION;
        float pivotX=(Ballistics.TORSO_X-70f)*s;
        float pivotY=(Ballistics.TORSO_Y-136f)*s;
        float offsetX=(Ballistics.GRIP_X-MAIN_X[11])*s;
        float offsetY=(Ballistics.GRIP_Y-MAIN_Y[11])*s;
        c.save();
        c.translate(pivotX,pivotY);
        c.rotate(HeadKnifeV82.localBearing(knifeDirection,face)+MeleeSlashV83.angle(t));
        c.translate(-pivotX,-pivotY);
        c.translate(offsetX,offsetY);
        float gx=(MAIN_X[11]-70f)*s,gy=(MAIN_Y[11]-136f)*s;
        if(showWeapons)drawKnifeBladeV82(c,gx,gy,s*HeadKnifeV82.KNIFE_SIZE);
        if(MeleeSlashV83.streakVisible(t)&&showWeapons)drawShortKnifeTrailV82(c,gx,gy,s);
        if(showHands)handAtlas(c,11,2,0,0,s,handScale,0,0);
        c.restore();
    }
    void shoot(float x,float y,float dx,float dy,int weapon,boolean hostile,int facing){
        float length=(float)Math.hypot(dx,dy);
        if(length<.01f){dx=facing;dy=0;length=1;}
        dx/=length;dy/=length;
        if(weapon==3)return; // Flashlight does not fire bullets.
        if(weapon==11){
            if(hostile){if(distance(x,y,playerX,playerY)<92)hurt(POWER[11]);}
            else for(Bandit e:enemies)if(e.active&&distance(x,y,e.x,e.y)<88)damage(e,POWER[11]);
            particles(x+dx*26,y-35,ORANGE,3);
            return;
        }
        float kick=(!hostile&&x==playerX&&y==playerY&&recoilFX)?2.7f:0f;
        float[] muzzle=Ballistics.rigMuzzle(x,y,facing,dx,dy,CharacterCollision.BASE_SCALE*scale,
                MX[weapon],MY[weapon],MAIN_X[weapon],MAIN_Y[weapon],kick);
        final float bx=muzzle[0],by=muzzle[1];
        int pellets=weapon==7?5:1;
        float theta=(float)Math.atan2(dy,dx);
        for(int i=0;i<pellets;i++){
            float jitter=(rng.nextFloat()-.5f)*(weapon==7?.30f:.027f);
            float a=theta+jitter,velocity=Ballistics.SPEED[weapon];
            shots.add(new Shot(bx,by,(float)Math.cos(a)*velocity,
                    (float)Math.sin(a)*velocity,POWER[weapon]/(pellets==5?2f:1f),hostile));
        }
        if(recoilFX){flashes.add(new Flash(bx,by,dx,dy));}
        particles(bx,by,ORANGE,weapon==10?4:2);
    }
    void damage(Bandit enemy,float amount){
        enemy.hp-=amount;enemy.hit=.14f;
        particles(enemy.x,enemy.y-34,RED,2);
        if(enemy.hp<=0&&enemy.active){
            enemy.active=false;kills++;particles(enemy.x,enemy.y-24,ORANGE,7);
            if(lootEnabled){
                int type=kills%7==0?2:kills%3==0?1:0;
                drops.add(new Drop(enemy.x,enemy.y-3,type));
            }
        }
    }
    void hurt(float amount){
        harvestV81.cancel();
        health=Math.max(0,health-amount);shake=.12f;
        particles(playerX,playerY-35,RED,5);
        if(health<=0){gameOver=true;paused=true;saveProgress();}
    }
    void particles(float x,float y,int color,int count){
        for(int i=0;i<count;i++){
            Spark f=new Spark(x,y,(rng.nextFloat()-.5f)*110,(rng.nextFloat()-.5f)*110,color);
            sparks.add(f);
        }
    }
    void update(float dt){
        if(!playing||paused||editControls)return;
        // Clock is real-world-time based and independent of enemy simulation speed.
        clock.advance(Math.min(.04f,dt));
        refreshDaylight();
        dt=Math.min(.04f,dt)*timeSpeed;
        worldTimer+=dt;autSaveClock+=dt;
        gatherFeedbackTime=Math.max(0f,gatherFeedbackTime-dt);
        harvestImpactTimeV81=Math.max(0f,harvestImpactTimeV81-dt);
        if(harvestV81.active){
            ResourceWorldV80.Node target=harvestV81.target;
            SalvageWorldV84.Node rust=harvestV81.salvageTarget;
            boolean salvaging=rust!=null;
            float tx=salvaging?rust.x:target.x,ty=salvaging?rust.y:target.y;
            float dx=tx-playerX,dy=ty-playerY;
            float reach=salvaging?SalvageWorldV84.REACH:ResourceWorldV80.USE_RADIUS;
            boolean depleted=salvaging?
                salvageWorldV84.exhausted(rust.cx,rust.cy,rust.slot):
                harvestWorld.exhausted(target.cx,target.cy,target.slot);
            if((float)Math.hypot(stickX,stickY)>.17f||firing||
               dx*dx+dy*dy>(reach+8f)*(reach+8f)||depleted||
               nearest(playerX,playerY,135f)!=null){
                harvestV81.cancel();
            }else{
                if(harvestV81.advance(dt)){
                    harvestImpactTimeV81=.18f;
                    int color=salvaging?0xffa47e5d:
                        harvestV81.kind==ResourceWorldV80.STONE?0xffa9b3ab:
                        harvestV81.kind==ResourceWorldV80.FIBER?0xff75985d:0xffb38a56;
                    particles(tx,ty-(salvaging?35f:harvestV81.kind==ResourceWorldV80.FIBER?18f:34f),
                        color,6);
                }
                if(harvestV81.finished){
                    if(salvaging){
                        if(harvestV81.canCompleteScrap(playerX,playerY,reach,depleted)&&
                           salvageWorldV84.harvest(rust)){
                            scrap+=rust.quantity();
                            gatherFeedback="SALVAGED SCRAP +"+rust.quantity();
                            gatherFeedbackTime=2.4f;saveProgress();
                        }
                    }else if(harvestV81.canComplete(playerX,playerY,reach,depleted)&&
                             harvestWorld.harvest(target)){
                        switch(target.resource()){
                            case ResourceWorldV80.STONE:stone+=target.quantity();break;
                            case ResourceWorldV80.FIBER:fiber+=target.quantity();break;
                            default:wood+=target.quantity();break;
                        }
                        gatherFeedback="GATHERED "+target.name()+" +"+target.quantity();
                        gatherFeedbackTime=2.3f;saveProgress();
                    }
                    harvestV81.cancel();
                }
            }
        }
        if(autSaveClock>9){saveProgress();autSaveClock=0;}
        shotClock=Math.max(0,shotClock-dt);
        recoil=Math.max(0,recoil-dt*5);
        if(reloadClock>0){
            reloadClock-=dt;if(reloadClock<=0){ammo=MAG[gun];reloadClock=0;}
        }
        float wasX=playerX,wasY=playerY;
        float vx=stickX,vy=stickY;
        float length=(float)Math.hypot(vx,vy);
        if(length>.06f&&!harvestV81.active){
            vx/=Math.max(1,length);vy/=Math.max(1,length);
            float runMultiplier=runHeld&&stamina>0?1.52f:1f;
            float speed=PlayerMovementV77.speed(gun==9?169f:236f,walkSpeedMultiplier,runMultiplier,crouchHeld);
            float nx=playerX+vx*speed*dt;
            float ny=playerY+vy*speed*dt;
            if(!blocked(nx,playerY,20))playerX=nx;
            if(!blocked(playerX,ny,20))playerY=ny;
            // Movement joystick is locomotion ONLY. No facing or aim updates.
        }
        // Animate actual displacement only: releasing the stick or hitting a wall
        // always restores the original neutral idle frame immediately.
        moving=distance(playerX,playerY,wasX,wasY)>.001f;
        // Adjustable extra gait multiplier, auto-synced to movement at 100%.
        playerAnimation.step(moving,dt,
            PlayerMovementV77.gait(walkSpeedMultiplier,runHeld&&stamina>0)*
            walkingAnimationMultiplierV79);
        // V65: the character is the stick/crosshair origin. Only distance
        // increases while the right thumb is active. The heading comes DIRECTLY
        // from the stick, so reversing aims instantly without crossing center.
        // V71 exact V61-style analogue input: each touch event controls the
        // direction directly. No angular interpolation or delayed rotation.
        boolean rightAiming=rightPointer>=0&&aimDeflection>ClassicAimV71.DEADZONE;
        float rest=RadialAimV65.rest(gun,crosshairRestPercent);
        // The crosshair's maximum and the bullet use the identical speed
        // and lifetime values; the muzzle-to-player offset is projected onto
        // the aiming ray to locate the actual bullet endpoint in world space.
        float maxAim=rest;
        if(gun==11)maxAim=Math.max(rest,88f); // axe: collision reach, no bullet
        else if(gun==3)maxAim=Math.max(rest,host.setting("beamReach",490)); // torch: light
        else{
            float[] muzzle=Ballistics.rigMuzzle(playerX,playerY,face,aimX,aimY,
                CharacterCollision.BASE_SCALE*scale,MX[gun],MY[gun],MAIN_X[gun],MAIN_Y[gun],0f);
            float muzzleOffset=(muzzle[0]-playerX)*aimX+
                (muzzle[1]-(playerY-42f))*aimY;
            maxAim=Math.max(rest,Ballistics.unobstructedTravel(gun)+muzzleOffset);
        }
        if(!cursorInitialized){
            aimCursorDistance=rest;cursorInitialized=true;
        }
        // Original proportional joystick: no auto-extension over time.
        // One touch gesture changes aim direction AND marker distance.
        // Keep V66 weapon-specific resting distance but restore V61 short
        // 205px effective travel, rather than chasing a 5000px bullet path.
        aimCursorDistance=rightAiming?
            ClassicAimV71.distance(rest,maxAim,aimDeflection):rest;
        cursorWorldX=playerX+aimX*aimCursorDistance;
        cursorWorldY=playerY-42f+aimY*aimCursorDistance;
        stamina=Math.max(0,Math.min(100,stamina+dt*((moving&&runHeld)?-13f:8f)));
        if(moving){hunger=Math.max(0,hunger-dt*.012f);thirst=Math.max(0,thirst-dt*.023f);}
        fatigue=Math.max(0,Math.min(100,fatigue+dt*(moving&&runHeld?.20f:-.08f)));
        knifeCooldown=Math.max(0,knifeCooldown-dt);
        if(knifeDuration>0){
            knifeDuration=Math.max(0,knifeDuration-dt);
            if(knifeHitPending&&knifeDuration<=MeleeSlashV83.DURATION*.50f){
                knifeHitPending=false;
                if(knifeTarget!=null&&knifeTarget.active&&
                    distance(playerX,playerY,knifeTarget.x,knifeTarget.y)<MeleeSlashV83.REACH+8f)
                    damage(knifeTarget,36);
            }
        }
        // Optional V61-style direction look-ahead, capped to the V69
        // small CIRCULAR radius. Disabled by default in this rollback.
        float panLimit=WeaponCameraV72.distance(gun,Math.round(cameraPanLimit),
            viewW,viewH,Math.max(.01f,zoom));
        float panFactor=ClassicAimV71.panFactor(aimDeflection,lookAheadThreshold);
        float desiredPanX=aimX*panLimit*panFactor;
        float desiredPanY=aimY*panLimit*panFactor;
        if(!rightAiming||!lookAheadEnabled||panLimit==0f){
            cameraLookX=0f;cameraLookY=0f;
        }else{
            cameraLookX+=StableAimV68.panStep(desiredPanX-cameraLookX,dt,
                cameraPanSpeed,lookAheadSmooth);
            cameraLookY+=StableAimV68.panStep(desiredPanY-cameraLookY,dt,
                cameraPanSpeed,lookAheadSmooth);
            float factor=BoundedCameraV69.radialFactor(cameraLookX,cameraLookY,panLimit);
            cameraLookX*=factor;cameraLookY*=factor;
        }
        // Crosshair range remains the actual projectile endpoint, but
        // offscreen reach is clipped to the edge rather than chasing it.
        if(firing&&!harvestV81.active){
            if(aimX>.025f)face=1;else if(aimX<-.025f)face=-1;
            if(shotClock<=0&&reloadClock==0){
                if(ammo>0||gun==11||gun==3){
                    shoot(playerX,playerY,aimX,aimY,gun,false,face);
                    if(gun!=3){shotClock=RATES[gun];ammo=Math.max(0,ammo-1);recoil=recoilFX?1:0;}
                }else reload();
            }
        }
        // Camp NPCs share the exact approved idle/walk state machine. Half stay
        // at their workstations and breathe; half patrol short safe routes.
        for(int i=0;i<campStaff.size();i++){
            Survivor npc=campStaff.get(i);
            if(WorldPerfV55.distantFrom(npc.homeX,npc.homeY,playerX,playerY,
                    npcSleepRadius)){npc.animation.reset();continue;}
            float px=npc.x,py=npc.y;
            if((i&1)==0){
                npc.x=npc.homeX+(float)Math.sin(worldTimer*.41f+i)*18f;
                npc.y=npc.homeY+(float)Math.cos(worldTimer*.41f+i)*11f;
                npc.face=(float)Math.cos(worldTimer*.41f+i)>=0?1:-1;
            }
            npc.animation.step(distance(px,py,npc.x,npc.y)>.001f,dt,7.1f);
        }
        if(moving&&length>.13f){
            followHeadingX=vx;followHeadingY=vy;
        }
        for(int fi=0;fi<friends.size();fi++){
            Survivor friend=friends.get(fi);
            float beforeFriendX=friend.x,beforeFriendY=friend.y;
            friend.cd=Math.max(0,friend.cd-dt);
            float gx=FollowFormationV61.targetX(playerX,followHeadingX,followHeadingY,
                followMode,fi,friends.size(),followSpacing);
            float gy=FollowFormationV61.targetY(playerY,followHeadingX,followHeadingY,
                followMode,fi,friends.size(),followSpacing);
            // Repel overlapping followers even when multiple follow slots coincide
            // with the same obstacle. No teleport or body/rig alterations.
            float repelX=0f,repelY=0f;
            for(int other=0;other<friends.size();other++){
                if(fi==other)continue;
                Survivor neighbor=friends.get(other);
                float rx=friend.x-neighbor.x,ry=friend.y-neighbor.y;
                float dd=rx*rx+ry*ry;
                if(dd<78f*78f){
                    if(dd<1){rx=(fi<other?-1:1)*20f;ry=(fi%2==0?-12:12);dd=rx*rx+ry*ry;}
                    float inv=1f/(float)Math.sqrt(dd);
                    repelX+=rx*inv*(78f-(float)Math.sqrt(dd))*.9f;
                    repelY+=ry*inv*(78f-(float)Math.sqrt(dd))*.9f;
                }
            }
            gx+=repelX;gy+=repelY;
            float d=distance(friend.x,friend.y,gx,gy);
            float travel=FollowerArrivalV78.step(d,dt,
                Math.min(300f,198f+(d>300?76:0)));
            if(travel>0f){
                float ux=(gx-friend.x)/Math.max(1,d),uy=(gy-friend.y)/Math.max(1,d);
                float nx=friend.x+ux*travel,ny=friend.y+uy*travel;
                if(!blocked(nx,friend.y,18))friend.x=nx;
                if(!blocked(friend.x,ny,18))friend.y=ny;
                // Do not flip a companion and both flashlight hands back/forth
                // as small repulsion/arrival corrections cross the desired slot.
                if(FollowerArrivalV78.shouldTurn(gx-beforeFriendX,d))
                    friend.face=ux>=0f?1:-1;
            }
            friend.aimX=friend.face;friend.aimY=0f;
            friend.animation.step(FollowerArrivalV78.visuallyWalking(
                distance(friend.x,friend.y,beforeFriendX,beforeFriendY)),dt,8.5f);
            Bandit target=nearest(friend.x,friend.y,460);
            if(target!=null){
                float dx=target.x-friend.x,dy=target.y-friend.y;
                friend.face=dx>=0?1:-1;
                float aimLen=Math.max(1,(float)Math.hypot(dx,dy));
                friend.aimX=dx/aimLen;friend.aimY=dy/aimLen;
                if(friend.cd<=0){
                    shoot(friend.x,friend.y,dx,dy,friend.gun,false,friend.face);
                    friend.cd=RATES[friend.gun]+.2f;
                }
            }
        }
        if(enemyAI)for(Bandit e:enemies){
            if(!e.active)continue;
            if(WorldPerfV55.distantFrom(e.x,e.y,playerX,playerY,npcSleepRadius)){
                // Combat and HP remain persistent; only distant animation/ticks sleep.
                e.animation.reset();continue;
            }
            float beforeEnemyX=e.x,beforeEnemyY=e.y;
            e.cd-=dt;e.hit=Math.max(0,e.hit-dt);
            float d=distance(e.x,e.y,playerX,playerY);
            if(d<520){
                float dx=(playerX-e.x)/Math.max(1,d),dy=(playerY-e.y)/Math.max(1,d);
                e.face=dx>=0?1:-1;
                if(d>240){
                    float nx=e.x+dx*120*dt,ny=e.y+dy*120*dt;
                    if(!blocked(nx,e.y,18))e.x=nx;
                    if(!blocked(e.x,ny,18))e.y=ny;
                    // Animation is driven by displacement, not historical walking time.
                }else if(e.cd<=0){
                    shoot(e.x,e.y,dx,dy,0,true,e.face);
                    e.cd=1.1f+rng.nextFloat()*.7f;
                }
            }
            e.animation.step(distance(e.x,e.y,beforeEnemyX,beforeEnemyY)>.001f,dt,7.2f);
        }
        if(!enemyAI)for(Bandit e:enemies)e.animation.reset();
        // Continuous collision detection: no tunneling through actors or cover at 4000 px/s.
        for(Iterator<Shot> iter=shots.iterator();iter.hasNext();){
            Shot bullet=iter.next();
            // Do not overshoot the lifespan in the final frame: the
            // crosshair and projectile must share the same exact endpoint.
            float travelDt=Math.min(dt,Math.max(0f,bullet.life));
            float nx=bullet.x+bullet.vx*travelDt,ny=bullet.y+bullet.vy*travelDt;
            bullet.life-=dt;
            float first=Float.POSITIVE_INFINITY;
            Bandit victim=null;
            boolean hitPlayer=false,hitCover=false;
            for(Cover box:covers){
                if(!WorldPerfV55.segmentNearRect(bullet.x,bullet.y,nx,ny,
                        box.x,box.y,box.w,box.h,3f))continue;
                float t=Ballistics.segmentBox(bullet.x,bullet.y,nx,ny,
                        box.x-2,box.y-2,box.x+box.w+2,box.y+box.h+2);
                if(t<first){first=t;victim=null;hitPlayer=false;hitCover=true;}
            }
            if(bullet.hostile){
                float t=WorldPerfV55.segmentNearActor(bullet.x,bullet.y,nx,ny,
                    playerX,playerY,scale)?
                    CharacterCollision.firstHit(bullet.x,bullet.y,nx,ny,
                        playerX,
                        playerY,face,playerAnimation.frame(),
                        playerAnimation.isWalking(),playerAnimation.breathOffset(),scale,
                        playerAnimation.isWalking()?walkMask:bodyMask):
                    Float.POSITIVE_INFINITY;
                if(t<first){first=t;victim=null;hitPlayer=true;hitCover=false;}
            }else{
                for(Bandit e:enemies)if(e.active){
                    if(!WorldPerfV55.segmentNearActor(bullet.x,bullet.y,nx,ny,
                            e.x,e.y,scale))continue;
                    float t=CharacterCollision.firstHit(bullet.x,bullet.y,nx,ny,
                            e.x,
                            e.y,e.face,e.animation.frame(),
                            e.animation.isWalking(),e.animation.breathOffset(),scale,
                            e.animation.isWalking()?walkMask:bodyMask);
                    if(t<first){first=t;victim=e;hitPlayer=false;hitCover=false;}
                }
            }
            if(first<=1f){
                bullet.x+=(nx-bullet.x)*first;
                bullet.y+=(ny-bullet.y)*first;
                if(hitPlayer)hurt(bullet.damage);
                else if(victim!=null)damage(victim,bullet.damage);
                else if(hitCover&&recoilFX)particles(bullet.x,bullet.y,0xffc4b58a,2);
                iter.remove();
            }else if(bullet.life<=0){
                iter.remove();
            }else {bullet.x=nx;bullet.y=ny;}
        }
        for(Iterator<Flash> it=flashes.iterator();it.hasNext();){
            Flash flash=it.next();flash.ttl-=dt;if(flash.ttl<=0)it.remove();
        }
        for(Iterator<Drop> it=drops.iterator();it.hasNext();){
            Drop d=it.next();d.ttl-=dt;
            if(d.ttl<0){it.remove();continue;}
            if(distance(playerX,playerY,d.x,d.y)<51){
                if(d.type==0)ammoPacks++;else if(d.type==1)scrap+=2;else medkits++;
                particles(d.x,d.y,OLIVE,5);it.remove();
            }
        }
        for(Iterator<Spark> iter=sparks.iterator();iter.hasNext();){
            Spark s=iter.next();s.x+=s.vx*dt;s.y+=s.vy*dt;
            s.ttl-=dt;if(s.ttl<=0)iter.remove();
        }
        boolean anyEnemyAlive=false;
        for(Bandit e:enemies)if(e.active){anyEnemyAlive=true;break;}
        if(!anyEnemyAlive){wave++;health=Math.min(100,health+15);spawnWave();}
        if(health<=0){gameOver=true;paused=true;}
    }

    void color(int color){p.setColor(color);p.setStyle(Paint.Style.FILL);p.setStrokeWidth(1);}
    void rect(Canvas c,float x,float y,float w,float h,int color){
        color(color);c.drawRect(x,y,x+w,y+h,p);
    }
    void rounded(Canvas c,float x,float y,float w,float h,float radius,int color){
        color(color);c.drawRoundRect(x,y,x+w,y+h,radius,radius,p);
    }
    void label(Canvas c,String t,float x,float y,int size,int col,boolean bold){
        color(col);p.setTypeface(bold?PIXEL_BOLD:PIXEL_NORMAL);
        p.setTextSize(size);c.drawText(t,x,y,p);
    }
    int hash(int a,int b){int k=a*73856093^b*19349663;k^=k>>>13;k*=0x5bd1e995;return k^(k>>>15);}
    void drawFixtures(Canvas c,boolean emissive){
        // Environmental props are separate from every approved body/weapon asset.
        // Campfires are sorted with characters below; never draw flames
        // in the final emissive pass above every actor again.
        // Road lights are rendered as fixtures, not unexplained ground glows.
        for(float lampX:new float[]{490,1790,2840}){
            if(!emissive){
                rect(c,lampX-3,870,6,52,0xff293a3d);
                rect(c,lampX-11,867,22,10,0xff6d7160);
                rect(c,lampX-7,869,14,4,0xffacae90);
            }else if(night){
                rect(c,lampX-8,866,16,7,0xffffe5a1);
            }
        }
        if(neonEnabled)for(int i=0;i<NEONS.length;i++){
            float[] n=NEONS[i];float x=n[0],y=n[1];int hue=(int)n[2];
            if(!emissive){
                rect(c,x-41,y-7,82,19,0xff18262a);
                rect(c,x-38,y-4,76,12,hue);
                label(c,i%2==0?"MARKET":"MOTEL",x-32,y+6,12,0xff101e28,true);
            }else if(night){
                rect(c,x-39,y-5,78,14,hue);
                label(c,i%2==0?"MARKET":"MOTEL",x-32,y+6,12,0xff0a1b24,true);
            }
        }
    }
    // The fire's entire visual (hearth AND flame) is depth-sorted with
    // actors, so a character IN FRONT occludes fire pixels automatically.
    // Wider V50 fire: 142-world-unit hearth, 124-unit flame front (~3x V49).
    // Pixel-stepped flame silhouettes (no equal-height vertical sound bars).
    void flameTongue(Canvas c,float x,float baseline,float wide,float height,int outer,int core){
        Path outline=new Path();
        outline.moveTo(x-wide/2,baseline);
        outline.lineTo(x-wide*.64f,baseline-height*.18f);
        outline.lineTo(x-wide*.41f,baseline-height*.41f);
        outline.lineTo(x-wide*.24f,baseline-height*.44f);
        outline.lineTo(x-wide*.35f,baseline-height*.69f);
        outline.lineTo(x-wide*.08f,baseline-height*.74f);
        outline.lineTo(x+wide*.13f,baseline-height);
        outline.lineTo(x+wide*.26f,baseline-height*.70f);
        outline.lineTo(x+wide*.13f,baseline-height*.57f);
        outline.lineTo(x+wide*.50f,baseline-height*.30f);
        outline.lineTo(x+wide*.46f,baseline);
        outline.close();color(outer);c.drawPath(outline,p);
        Path inside=new Path();inside.moveTo(x-wide*.26f,baseline);
        inside.lineTo(x-wide*.17f,baseline-height*.30f);
        inside.lineTo(x,baseline-height*.50f);
        inside.lineTo(x+wide*.12f,baseline-height*.66f);
        inside.lineTo(x+wide*.23f,baseline-height*.23f);
        inside.lineTo(x+wide*.25f,baseline);inside.close();
        color(core);c.drawPath(inside,p);
    }
    void drawCampfire(Canvas c,float x,float y,boolean emissive){
        if(!emissive){
            rect(c,x-76,y+6,152,15,0xff242724);
            for(int i=0;i<11;i++){
                float xx=x-75+i*14;
                rect(c,xx,y+9+i%3,16,9,0xff727269);
                rect(c,xx+3,y+10+i%3,7,2,0xffa09d83);
            }
            rect(c,x-62,y+1,125,7,campfiresLit?0xffac4b20:0xff4b3b30);
            for(int i=0;i<8;i++){
                float xx=x-65+i*16;
                rect(c,xx,y-2+i%3*3,31,7,0xff6f4a30);
                rect(c,xx+3,y-1+i%3*3,19,2,0xffab7c4b);
            }
            if(campfiresLit){
                for(int i=0;i<12;i++)rect(c,x-58+i*10,y+1+i%3,5,3,0xffff9845);
            }
        }else if(campfiresLit){
            // Intersecting, asymmetric tongues; stagger heights and tips.
            float sway=(float)Math.sin(worldTimer*6f+x*.014f);
            float wave=(float)Math.sin(worldTimer*9.4f+y*.025f);
            flameTongue(c,x-37+sway*2,y+5,47,50+wave*8,0xffae3a16,0xfff7932e);
            flameTongue(c,x+30-wave*4,y+5,56,66+sway*9,0xffb33e18,0xffffb53b);
            flameTongue(c,x+sway*3,y+4,68,89+wave*10,0xffdb5a20,0xffffc857);
            flameTongue(c,x+8-wave*2,y+3,31,46+sway*7,0xffff9430,0xffffe58a);
            for(int i=0;i<6;i++){
                float t=(worldTimer*(12+i*2f)+i*9f)%65f;
                float xx=x-58+i*23f+(float)Math.sin(worldTimer*3f+i)*5;
                rect(c,xx,y-20-t,3,3,i%2==0?0xffffdc85:0xffff9e43);
            }
        }
    }
    // Flashlight lens color is always tied to the lamp's actual ON/OFF state.
    // Its immutable original artwork is untouched; a small lens-only overlay
    // covers the atlas' baked-in yellow glow both in DAY and in NIGHT.
    void drawFlashlightLens(Canvas c,float s){
        rect(c,(121f-70f)*s,(80f-136f)*s,8*s,17*s,0xff222c30);
        rect(c,(123f-70f)*s,(82f-136f)*s,5*s,13*s,
                lampOn?0xfff1ba53:0xff62696e);
        rect(c,(125f-70f)*s,(85f-136f)*s,2*s,7*s,
                lampOn?0xfffff0b1:0xff434c52);
    }
    void addCharacterShadow(float x,float y){
        if(!WorldPerfV55.nearView(x,y,camX,camY,viewW,viewH,730f))return;
        float s=scale*(CharacterCollision.BASE_SCALE/.76f);
        // Cast from the original on-screen pixel silhouette (three small
        // rectangles, not a large circular aura). Source-facing side remains lit.
        lighting.occludeRect(x-29*s,y-90*s,x+29*s,y-48*s); // head
        lighting.occludeRect(x-21*s,y-48*s,x+21*s,y-16*s); // chest
        lighting.occludeRect(x-22*s,y-17*s,x+22*s,y-2*s); // boots
    }
    void populateLightBlockers(){
        final float edge=730f; // lights can only influence the viewport + reach
        for(Cover b:covers)if(
            b.x+b.w>=camX-edge&&b.x<=camX+viewW+edge&&
            b.y+b.h>=camY-edge&&b.y<=camY+viewH+edge)
            lighting.occludeRect(b.x,b.y,b.x+b.w,b.y+b.h);
        for(int i=0;i<140;i++){
            if(i%7!=0)continue; // tree trunks/crowns, not tiny grass flecks
            int x=(137*i+27*i*i)%3180,y=(211*i+47*i*i)%2170;
            if(y>912&&y<1160)continue;
            if(x>1480&&x<1740)continue;
            if(!WorldPerfV55.nearView(x,y,camX,camY,viewW,viewH,edge))continue;
            lighting.occludeRect(x-8,y-9,x+29,y+31);
        }
        addCharacterShadow(playerX,playerY);
        for(Survivor f:friends)addCharacterShadow(f.x,f.y);
        for(Survivor f:campStaff)addCharacterShadow(f.x,f.y);
        for(Bandit e:enemies)if(e.active)addCharacterShadow(e.x,e.y);
    }
    void applyWorldLighting(Canvas c){
        if(lightAlpha<=0)return;
        long lightStart=System.nanoTime();
        lighting.clear();
        populateLightBlockers();
        if(campfiresLit){
            for(float[] f:FIXED_CAMPFIRES)fireLight(f[0],f[1]);
            for(float[] f:builtCampfires)fireLight(f[0],f[1]);
        }
        if(neonEnabled)for(float[] n:NEONS)
            if(WorldPerfV55.nearView(n[0],n[1],camX,camY,viewW,viewH,215))
                lighting.point(n[0],n[1],202,.77f,(int)n[2]);
        for(CampCraftV83.Structure node:craftV83.objects)
            if(node.kind==CampCraftV83.LIGHT_POST&&
               WorldPerfV55.nearView(node.x,node.y,camX,camY,viewW,viewH,260))
                lighting.point(node.x,node.y-85,185,.83f,0xffffda82);
        // Street lamps offer modest navigation light, not character glow.
        for(float x:new float[]{490,1790,2840})
            if(WorldPerfV55.nearView(x,872,camX,camY,viewW,viewH,185))
                lighting.point(x,872,175,.61f,0xffdbd5a0);
        if(lampOn){
            if(!harvestV81.active&&(gun==3||(dualTorch&&gun>=0&&gun<=2))){
                // Independent off-hand flashlight aims with the same world vector.
                // The player can fire a one-handed gun without interrupting lighting.
                float[] tip=Ballistics.rigMuzzle(playerX,playerY,face,aimX,aimY,
                    CharacterCollision.BASE_SCALE*scale,MX[3],MY[3],MAIN_X[3],MAIN_Y[3],0f);
                lighting.flashlight(tip[0],tip[1],aimX,aimY,flashlightReach);
            }
            int npcFlashlightBudget=2;
            for(Survivor f:friends)if((f.gun==3||(dualTorch&&f.gun<=2))&&
                    npcFlashlightBudget>0&&
                    WorldPerfV55.nearView(f.x,f.y,camX,camY,viewW,viewH,flashlightReach)){
                npcFlashlightBudget--;
                float[] tip=Ballistics.rigMuzzle(f.x,f.y,f.face,f.aimX,f.aimY,
                    CharacterCollision.BASE_SCALE*scale,MX[3],MY[3],MAIN_X[3],MAIN_Y[3],0f);
                lighting.flashlight(tip[0],tip[1],f.aimX,f.aimY,flashlightReach);
            }
            // Camp flashlights face their actual NPC walking/facing direction.
            for(Survivor f:campStaff)if((f.gun==3||(dualTorch&&f.gun<=2))&&
                    npcFlashlightBudget>0&&
                    WorldPerfV55.nearView(f.x,f.y,camX,camY,viewW,viewH,flashlightReach)){
                npcFlashlightBudget--;
                float fx=f.face<0?-1f:1f;
                float[] tip=Ballistics.rigMuzzle(f.x,f.y,f.face,fx,0f,
                        CharacterCollision.BASE_SCALE*scale,MX[3],MY[3],MAIN_X[3],MAIN_Y[3],0f);
                if(WorldPerfV55.nearView(tip[0],tip[1],camX,camY,viewW,viewH,flashlightReach))
                    lighting.flashlight(tip[0],tip[1],fx,0f,flashlightReach);
            }
        }
        for(Flash f:flashes)if(f.ttl>0)
            lighting.point(f.x,f.y,90,Math.min(1f,f.ttl/.065f),0xffffedb3);
        // Actual traveling projectiles cast moving pools of warm illumination.
        // Keep an explicit cap so continuous automatic fire does not overwhelm
        // the mobile CPU lightmap; each pool also respects world occluders.
        int illuminatedBullets=0;
        for(Shot projectile:shots){
            if(illuminatedBullets>=18)break;
            if(projectile.x<camX-85||projectile.x>camX+viewW+85||
               projectile.y<camY-85||projectile.y>camY+viewH+85)continue;
            lighting.point(projectile.x,projectile.y,66,.87f,projectile.color);
            lighting.point(projectile.x-projectile.vx*.009f,
                           projectile.y-projectile.vy*.009f,40,.43f,projectile.color);
            illuminatedBullets++;
        }
        lighting.render(c,camX,camY,viewW,viewH,lightAlpha,covers);
        lightingNs=System.nanoTime()-lightStart;
        // Lamps/neon signage are static architecture; campfire flames were
        // already depth-sorted with characters and are NOT painted over them.
        drawFixtures(c,true);
    }
    void fireLight(float x,float y){
        if(!WorldPerfV55.nearView(x,y,camX,camY,viewW,viewH,225))return;
        float flicker=(float)Math.sin(worldTimer*11f+x*.33f);
        lighting.point(x,y-9,205+flicker*9,.89f+flicker*.07f,LightingV47.WARM);
    }
    void terrain(Canvas c){
        // V54: render cached, asynchronously prepared 16x16-tile chunk textures.
        // Missing chunks use a deterministic immediate fallback (no blank screen).
        terrainChunks.draw(c,camX,camY,viewW,viewH);
        // Landmark road corridors extend through all visible world coordinates.
        rect(c,camX-4,925,viewW+8,225,0xff565b50);
        rect(c,camX-4,940,viewW+8,8,0xff3e493e);
        rect(c,camX-4,1134,viewW+8,7,0xff323f3a);
        int roadX=(int)Math.floor((camX-20)/123f);
        for(int i=roadX;i<roadX+(int)Math.ceil(viewW/123f)+3;i++)
            rect(c,20+i*123,1035,56,6,0xffa1a78d);
        rect(c,1500,camY-4,220,viewH+8,0xff525b50);
        rect(c,1500,camY-4,9,viewH+8,0xff3c473f);
        int roadY=(int)Math.floor(camY/135f);
        for(int i=roadY;i<roadY+(int)Math.ceil(viewH/135f)+3;i++)
            rect(c,1604,i*135+12,7,63,0xffa5aa8e);
        // Bushes and trees are always behind buildings and actors.
        for(int i=0;i<140;i++){
            int x=(137*i+27*i*i)%3180,y=(211*i+47*i*i)%2170;
            if(y>912&&y<1160)continue;
            if(x>1480&&x<1740)continue;
            if(Math.hypot(x-CAMP_X,y-CAMP_Y)<325)continue;
            if(x<camX-55||x>camX+viewW+55||y<camY-55||y>camY+viewH+55)continue;
            if((i%7)==0){
                c.save();
                c.translate(x,y+43f);
                c.scale(1.48f,1.48f);
                c.translate(-x,-y-43f);
                rect(c,x+7,y+19,8,24,0xff243c30);
                rect(c,x-8,y,37,28,0xff172b25);
                rect(c,x-4,y-6,30,27,0xff4e7351);
                rect(c,x+2,y-9,19,13,0xff65845d);
                c.restore();
            }else{
                rect(c,x,y+7,19,8,0xff233c30);
                rect(c,x+3,y,17,11,0xff557253);
                rect(c,x+8,y-4,8,7,0xff647f58);
            }
        }
        drawBiomePropsV74(c);
        drawSalvageWorldV84(c);
        if(placingKindV84>=0){
            rect(c,placingXv84-48,placingYv84-40,96,55,0x6640a688);
            // Reuse the finished structure geometry in transparent placement preview.
            drawCraftStructureV83(c,new CampCraftV83.Structure(
                placingKindV84,placingXv84,placingYv84));
        }
        for(Cover box:covers)
            if(box.x+box.w>=camX-15&&box.x<=camX+viewW+15&&
               box.y+box.h>=camY-15&&box.y<=camY+viewH+15)
                drawCover(c,box);
        drawSpawnCamp(c);
    }
    /** V80 living biome: V74 trees/rocks become harvestable, plus small fiber shrubs. */
    /** Procedural rusted vehicles and scrap heaps, drawn only in visible cells. */
    void drawSalvageWorldV84(Canvas c){
        int cell=SalvageWorldV84.CELL;
        int x0=(int)Math.floor(camX/cell)-1,x1=(int)Math.ceil((camX+viewW)/cell)+1;
        int y0=(int)Math.floor(camY/cell)-1,y1=(int)Math.ceil((camY+viewH)/cell)+1;
        for(int cy=y0;cy<=y1;cy++)for(int cx=x0;cx<=x1;cx++)
        for(int k=0;k<SalvageWorldV84.SLOTS;k++){
            int seed=SalvageWorldV84.seed(cx,cy,k);
            float x=SalvageWorldV84.x(cx,seed),y=SalvageWorldV84.y(cy,seed);
            if(x<camX-170||x>camX+viewW+170||
               y<camY-110||y>camY+viewH+110||
               !SalvageWorldV84.placed(x,y,seed,CAMP_X,CAMP_Y,WORLD_W,WORLD_H))continue;
            int type=Math.floorMod(seed,3);
            boolean depleted=salvageWorldV84.exhausted(cx,cy,k);
            if(depleted&&type!=SalvageWorldV84.CAR)continue;
            boolean shake=harvestImpactTimeV81>0f&&harvestV81.salvageTarget!=null&&
                harvestV81.salvageTarget.cx==cx&&harvestV81.salvageTarget.cy==cy&&
                harvestV81.salvageTarget.slot==k;
            if(shake){c.save();c.translate((float)Math.sin(worldTimer*72f)*3f,0);}
            if(type==SalvageWorldV84.CAR){
                rect(c,x-75,y-35,150,44,0xff172528);
                rect(c,x-70,y-39,140,39,depleted?0xff535952:0xff704c39);
                rect(c,x-37,y-61,75,27,0xff192b2e);
                rect(c,x-31,y-55,60,18,depleted?0xff313b3b:0xff5a7377);
                rect(c,x-25,y-52,20,13,0xff91a09a);
                rect(c,x-72,y-10,144,15,0xff293737);
                rect(c,x-50,y+1,23,17,0xff152025);
                rect(c,x+28,y+1,23,17,0xff152025);
                rect(c,x-44,y+5,11,7,0xff77837d);
                rect(c,x+34,y+5,11,7,0xff77837d);
                if(!depleted){
                    rect(c,x+45,y-28,20,12,0xffaf6a45);
                    rect(c,x-68,y-31,8,9,0xffc9a86b);
                }
            }else if(type==SalvageWorldV84.PILE){
                rect(c,x-53,y-6,106,17,0xff152427);
                rect(c,x-44,y-24,85,28,0xff474c45);
                rect(c,x-33,y-43,63,27,0xff74543d);
                rect(c,x-7,y-56,24,18,0xff293e3e);
                rect(c,x-30,y-33,18,8,0xffab784e);
                rect(c,x+19,y-29,11,15,0xff929a90);
            }else{
                for(int n=0;n<3;n++){
                    float off=n*24-24;
                    rect(c,x+off-10,y-38-(n%2)*9,20,44,0xff142428);
                    rect(c,x+off-7,y-35-(n%2)*9,14,38,0xff81513a);
                    rect(c,x+off-8,y-29-(n%2)*9,16,6,0xffba8155);
                }
            }
            if(shake)c.restore();
        }
    }
    void drawBiomePropsV74(Canvas c){
        final int cell=ResourceWorldV80.CELL;
        int x0=(int)Math.floor(camX/cell)-1,x1=(int)Math.ceil((camX+viewW)/cell)+1;
        int y0=(int)Math.floor(camY/cell)-1,y1=(int)Math.ceil((camY+viewH)/cell)+1;
        // Loop only visible cells; sparse harvest state stays independent of bitmap cache.
        for(int cy=y0;cy<=y1;cy++)for(int cx=x0;cx<=x1;cx++)
            for(int k=0;k<ResourceWorldV80.SLOTS;k++){
                if(harvestWorld.exhausted(cx,cy,k))continue;
                // V80 low-end performance: render world props allocation-free.
                int h=ResourceWorldV80.seed(cx,cy,k);
                float x=ResourceWorldV80.worldX(cx,h);
                float y=ResourceWorldV80.worldY(cy,h);
                if(!ResourceWorldV80.placed(x,y,k,h,
                       CAMP_X,CAMP_Y,WORLD_W,WORLD_H))continue;
                if(x<camX-200||x>camX+viewW+200||
                   y<camY-200||y>camY+viewH+200)continue;
                int kind=k==3?ResourceWorldV80.BUSH:BiomeWorldV74.prop(x,y,h);
                boolean shake=harvestImpactTimeV81>0&&harvestV81.matches(cx,cy,k);
                if(shake){
                    c.save();
                    c.translate((float)Math.sin(harvestImpactTimeV81*73f)*
                        (kind==ResourceWorldV80.BUSH?4f:2.6f),0f);
                }
                if(kind==ResourceWorldV80.BUSH){
                    // Low stepped pixel bush; distinct fiber gathering target.
                    int leaf=BiomeWorldV74.detail(BiomeWorldV74.biome(x,y),h);
                    rect(c,x-21,y-12,42,12,0xff192b24);
                    rect(c,x-27,y-21,54,13,0xff23372b);
                    rect(c,x-17,y-28,35,15,leaf);
                    rect(c,x-7,y-34,14,12,0xff7b9168);
                    if(shake)c.restore();
                    continue;
                }
                float extent=kind==4?72f:kind==5?84f:kind==3?162f:186f;
                if(biomeProps!=null){
                    int size=BiomeWorldV74.CELL;
                    src.set(kind*size,0,(kind+1)*size,size);
                    dest.set(x-extent*.5f,y-extent,x+extent*.5f,y);
                    c.drawBitmap(biomeProps,src,dest,pixel);
                }else{
                    int tint=BiomeWorldV74.detail(BiomeWorldV74.biome(x,y),h);
                    rect(c,x-8,y-14,16,14,0xff24332a);
                    rect(c,x-17,y-28,34,17,tint);
                }
                if(shake)c.restore();
            }
    }
    void drawSpawnCamp(Canvas c){
        if(CAMP_X<camX-520||CAMP_X>camX+viewW+520||
           CAMP_Y<camY-375||CAMP_Y>camY+viewH+375)return;
        if(campStatic==null){
            campStatic=Bitmap.createBitmap(1000,730,Bitmap.Config.ARGB_8888);
            Canvas texture=new Canvas(campStatic);
            texture.translate(-CAMP_TEXTURE_LEFT,-CAMP_TEXTURE_TOP);
            drawSpawnCampDetails(texture);
        }
        c.drawBitmap(campStatic,CAMP_TEXTURE_LEFT,CAMP_TEXTURE_TOP,pixel);
    }
    void drawSpawnCampDetails(Canvas c){
        float x=CAMP_X,y=CAMP_Y;
        rect(c,x-255,y-165,506,355,0x345c7351);
        // Restored simple survivor camp clearing with tents and equipment.
        for(int side:new int[]{-1,1}){
            float tx=x+side*168,ty=y-135;
            rect(c,tx-70,ty-7,140,14,0xff263b32);
            rect(c,tx-62,ty-45,124,39,0xff576c53);
            rect(c,tx-49,ty-70,98,28,0xff71815e);
            rect(c,tx-32,ty-13,64,28,0xff2c3a32);
            rect(c,tx-25,ty-12,50,24,0xff3d483b);
            rect(c,tx-68,ty+22,34,27,0xff634f32);
            rect(c,tx-60,ty+23,18,5,0xffa58b5a);
            rect(c,tx+40,ty+19,31,26,0xff53422c);
        }
        rect(c,x-93,y+108,190,14,0xff493c2b);
        rect(c,x-91,y+112,186,5,0xff87764f);
        for(int i=0;i<5;i++)rect(c,x-86+i*40,y+116,8,10,0xff312e27);
        rect(c,x+212,y-5,9,80,0xff594832);
        rect(c,x+217,y-4,68,22,0xff797a54);
        label(c,"CAMP",x+223,y+12,13,0xffe1dbc2,true);
        // Approved original camp remains. Add deterministic ground-level detail:
        // old-world woodland, scattered stones, wooden supplies and shrubbery.
        for(int k=0;k<38;k++){
            int h=hash(k+203,319-k*7);
            float px=x-400f+Math.floorMod(h,800);
            float py=y-275f+Math.floorMod(h>>>9,560);
            if(Math.abs(px-x)<130&&Math.abs(py-y)<125)continue;
            if((h&3)==0){
                rect(c,px-8,py+4,29,8,0xff364b34);
                rect(c,px-2,py-5,20,17,0xff466946);
                rect(c,px+4,py-11,14,12,0xff66845a);
                if((h&31)==0)rect(c,px+7,py-1,4,4,0xffa76560);
            }else if((h&3)==1){
                rect(c,px-11,py,27,11,0xff3d5148);
                rect(c,px-8,py-6,22,11,0xff758379);
                rect(c,px+1,py-7,6,3,0xff9a9d80);
            }else if((h&3)==2){
                rect(c,px,py,58,11,0xff3c392b);
                rect(c,px,py-8,58,9,0xff775b39);
                rect(c,px+4,py-6,43,3,0xff9a7945);
                rect(c,px+49,py-6,7,7,0xffbda078);
            }else{
                for(int q=0;q<5;q++){
                    float ox=Math.floorMod(hash(k,q*7),28);
                    float oy=Math.floorMod(hash(q,k*9),22);
                    rect(c,px+ox,py+oy,4,3,q%2==0?0xffa39c66:0xff6f864f);
                }
            }
        }
    }
    void drawCover(Canvas c,Cover box){
        if(box.kind==3)return; // V83 player-built barricades are depth-sorted.
        float x=box.x,y=box.y,w=box.w,h=box.h;
        if(box.kind==0){
            rect(c,x+5,y+9,w,h,0xff142b29);
            rect(c,x,y,w,h,0xff626b5c);
            rect(c,x+8,y+7,w-16,h-20,0xff424f4d);
            rect(c,x,y,w,12,0xff1d3032);
            for(int i=18;i<w-8;i+=34)rect(c,x+i,y+19,4,h-42,0xff53645b);
            rect(c,x+16,y+h-44,55,24,0xff172a2e);
            rect(c,x+w-75,y+22,46,34,0xff172b2e);
            rect(c,x+8,y+h-13,w-16,10,0xff252f2e);
        }else{
            rect(c,x+5,y+6,w,h,0xff142528);
            rect(c,x,y,w,h-7,0xff655e4e);
            for(int i=5;i<w-7;i+=20)rect(c,x+i,y+5,13,h-19,i%3==0?0xff967d59:0xff847357);
        }
    }
    // Render the LOCKED atlas frames; all weapon, off-hand and main-hand slices are independent.
    void atlas(Canvas c,Bitmap bmp,int sx,int sy,float x,float y,float size){
        if(bmp==null)return;
        src.set(sx,sy,sx+260,sy+160);
        dest.set(x-70*size,y-136*size,x+190*size,y+24*size);
        c.drawBitmap(bmp,src,dest,pixel);
    }
    // V52: Original V40/V50 idle is immutable. Walking still uses V51's
    // approved role/color atlas and its four animation frames.
    static final int APPROVED_PLANTED_IDLE_FRAME=2;
    static final int IDLE_HEAD_BODY_SPLIT=92;
    static final int IDLE_HEAD_OVERLAP=101;
    /**
     * Exact V40/V56 head pixels only (atlas x24..109, y20..91).
     * Pivot at the neckline, no edits to the torso, legs, face or idle atlas.
     */
    void drawScaledHeadV82(Canvas c,Bitmap atlas,int sx,int sy,float s,float breath){
        float bob=breath*s;
        src.set(sx+HeadKnifeV82.HEAD_LEFT,sy+HeadKnifeV82.HEAD_TOP,
                sx+HeadKnifeV82.HEAD_RIGHT,sy+HeadKnifeV82.HEAD_BOTTOM);
        dest.set(HeadKnifeV82.headLeft(s,headScaleV82),
                 HeadKnifeV82.headTop(s,headScaleV82,bob),
                 HeadKnifeV82.headRight(s,headScaleV82),
                 HeadKnifeV82.headBottom(s,bob));
        c.drawBitmap(atlas,src,dest,pixel);
    }
    void stablePose(Canvas c,Bitmap walkingAtlas,int variant,int frame,float s,float breath){
        if(breath==Float.POSITIVE_INFINITY){
            if(walkingAtlas==null)return;
            if(!HeadKnifeV82.defaultHead(headScaleV82)){
                int row=Math.max(0,variant)*160;
                int f=Math.max(0,Math.min(3,frame));
                src.set(f*260,row+110,f*260+260,row+160);
                dest.set(-70*s,(110-136)*s,190*s,24*s);
                c.drawBitmap(walkingAtlas,src,dest,pixel);
                boolean npc=variant>=0;
                Bitmap locked=npc?npcIdleV56:body;
                if(locked==null)return;
                int sx=npc?0:APPROVED_PLANTED_IDLE_FRAME*260;
                int sy=npc?Math.min(11,variant)*160:0;
                // The original shirt starts on row 92.
                src.set(sx,sy+HeadKnifeV82.HEAD_BOTTOM,sx+260,sy+110);
                dest.set(-70*s,(HeadKnifeV82.HEAD_BOTTOM-136)*s,190*s,(110-136)*s);
                c.drawBitmap(locked,src,dest,pixel);
                drawScaledHeadV82(c,locked,sx,sy,s,0f);
                return;
            }
            int row=Math.max(0,variant)*160;
            int f=Math.max(0,Math.min(3,frame));
            // V59 locked identity compositor: use the approved walking frame
            // only below the upper-body split. Face, hair, eyes, chest colors
            // and their near-black outlines are taken from the SAME approved
            // idle frame for every walk step. No source image is modified.
            final int split=110;
            src.set(f*260,row+split,f*260+260,row+160);
            dest.set(-70*s,(split-136)*s,190*s,24*s);
            c.drawBitmap(walkingAtlas,src,dest,pixel);
            final boolean npc=variant>=0;
            Bitmap locked=npc?npcIdleV56:body;
            if(locked==null)return;
            int sx=npc?0:APPROVED_PLANTED_IDLE_FRAME*260;
            int sy=npc?Math.min(11,variant)*160:0;
            src.set(sx,sy,sx+260,sy+split);
            dest.set(-70*s,-136*s,190*s,(split-136)*s);
            c.drawBitmap(locked,src,dest,pixel);
            return;
        }
        // Original planted idle source, NOT a walking pose reconstructed in V51.
        // Approved NPC role colors are applied to an otherwise identical silhouette.
        final boolean npc=variant>=0;
        Bitmap idleSource=npc?npcIdleV56:body;
        if(idleSource==null)return;
        int sx=npc?0:APPROVED_PLANTED_IDLE_FRAME*260;
        int sy=npc?Math.min(11,variant)*160:0;
        if(!HeadKnifeV82.defaultHead(headScaleV82)){
            src.set(sx,sy+HeadKnifeV82.HEAD_BOTTOM,sx+260,sy+160);
            dest.set(-70*s,(HeadKnifeV82.HEAD_BOTTOM-136)*s,190*s,24*s);
            c.drawBitmap(idleSource,src,dest,pixel);
            drawScaledHeadV82(c,idleSource,sx,sy,s,breath);
            return;
        }
        src.set(sx,sy+IDLE_HEAD_BODY_SPLIT,sx+260,sy+160);
        dest.set(-70*s,(IDLE_HEAD_BODY_SPLIT-136)*s,190*s,24*s);
        c.drawBitmap(idleSource,src,dest,pixel);
        // Exact V40 breathing: stationary legs/torso; head-only 0/-4px.
        float headBob=breath*s;
        src.set(sx,sy,sx+260,sy+IDLE_HEAD_OVERLAP);
        dest.set(-70*s,-136*s+headBob,190*s,
                (IDLE_HEAD_OVERLAP-136)*s+headBob);
        c.drawBitmap(idleSource,src,dest,pixel);
    }
    void handAtlas(Canvas c,int weapon,int row,float x,float y,float s,float size,float reach,float vertical){
        float px=row==2?MAIN_X[weapon]:OFF_X[weapon];
        float py=row==2?MAIN_Y[weapon]:OFF_Y[weapon];
        if(px==0)return;
        c.save();
        c.translate((px-70+reach)*s,(py-136+(row==1?vertical:0f))*s);
        c.scale(size,size);
        c.translate(-(px-70)*s,-(py-136)*s);
        atlas(c,gear,weapon*260,row*160,x,y,s);
        c.restore();
    }
    void drawApprovedAxe(Canvas c,float pivotX,float pivotY,float scale){
        if(approvedAxe==null)return;
        // Cropped from the user's approved V29 weapon presentation image, not redrawn.
        // Grip at image coordinate (29,138), anchored to the approved main-hand pivot.
        float k=.58f*scale;
        dest.set(pivotX-29*k,pivotY-138*k,
                pivotX+(approvedAxe.getWidth()-29)*k,
                pivotY+(approvedAxe.getHeight()-138)*k);
        c.drawBitmap(approvedAxe,null,dest,pixel);
    }
    /** V81 original chunky pixel pickaxe generated once at scene initialization. */
    Bitmap makePixelPickaxeV81(){
        Bitmap bm=Bitmap.createBitmap(76,100,Bitmap.Config.ARGB_8888);
        Canvas tool=new Canvas(bm);
        Paint ink=new Paint();ink.setAntiAlias(false);
        // Wooden handle with a thick near-black outline, visible grain and grip.
        ink.setColor(0xff121c1c);tool.drawRect(34,19,46,96,ink);
        ink.setColor(0xff806242);tool.drawRect(37,22,43,92,ink);
        ink.setColor(0xffb18b57);tool.drawRect(37,30,39,81,ink);
        ink.setColor(0xff473a2d);tool.drawRect(42,48,44,88,ink);
        ink.setColor(0xff1d282a);tool.drawRect(11,12,68,29,ink);
        ink.setColor(0xff566b6b);tool.drawRect(17,15,63,25,ink);
        ink.setColor(0xff98a9a4);tool.drawRect(20,16,53,19,ink);
        ink.setColor(0xff394d50);tool.drawRect(8,17,17,23,ink);
        ink.setColor(0xff182527);tool.drawRect(3,19,11,23,ink);
        ink.setColor(0xff111d1f);tool.drawRect(0,22,7,25,ink);
        // Stepped downward beak tip, distinct from an axe silhouette.
        ink.setColor(0xff141e21);tool.drawRect(62,23,72,35,ink);
        ink.setColor(0xff27383b);tool.drawRect(68,32,75,44,ink);
        ink.setColor(0xffb5bcb4);tool.drawRect(65,26,68,35,ink);
        ink.setColor(0xff8a996e);tool.drawRect(36,23,44,27,ink);
        return bm;
    }
    /** One shared torso pivot drives tool, approved V29 fist, and handle. */
    void drawHarvestRigV81(Canvas c,float s){
        int kind=harvestV81.kind;
        float pivotX=(Ballistics.TORSO_X-70f)*s;
        float pivotY=(Ballistics.TORSO_Y-136f)*s;
        float offsetX=(Ballistics.GRIP_X-MAIN_X[11])*s;
        float offsetY=(Ballistics.GRIP_Y-MAIN_Y[11])*s;
        c.save();
        c.translate(pivotX,pivotY);
        c.rotate(harvestV81.swingDegrees());
        c.translate(-pivotX,-pivotY);
        c.translate(offsetX,offsetY);
        float gx=(MAIN_X[11]-70f)*s,gy=(MAIN_Y[11]-136f)*s;
        if(showWeapons){
            if(kind==ResourceWorldV80.WOOD&&approvedAxe!=null){
                drawApprovedAxe(c,gx,gy,scale*(CharacterCollision.BASE_SCALE/.76f));
            }else if(kind==ResourceWorldV80.STONE&&pickaxeV81!=null){
                float k=s*.91f;
                dest.set(gx-40*k,gy-78*k,gx+36*k,gy+22*k);
                c.drawBitmap(pickaxeV81,null,dest,pixel);
            }else if(kind==ResourceWorldV80.FIBER){
                drawKnifeBladeV82(c,gx,gy,s*HeadKnifeV82.KNIFE_SIZE);
                if(harvestV81.phase()==HarvestActionV81.STRIKE)
                    drawShortKnifeTrailV82(c,gx,gy,s);
            }else if(kind==HarvestActionV81.SCRAP){
                // Dedicated hooked crowbar with black outline and oxidized shaft.
                c.save();c.translate(gx,gy);c.scale(s,s);
                rect(c,-7,-78,16,103,0xff162426);
                rect(c,-3,-75,8,90,0xff8b5345);
                rect(c,0,-69,3,72,0xffc08b69);
                rect(c,-22,-85,32,12,0xff142529);
                rect(c,-18,-82,26,7,0xff8b9c98);
                rect(c,-25,-83,8,14,0xff4b6769);
                rect(c,6,15,10,12,0xff142326);
                c.restore();
            }
        }
        if(showHands)handAtlas(c,11,2,0,0,s,handScale,0,0);
        c.restore();
    }
    void character(Canvas c,float x,float y,int weapon,int facing,int frame,float breath,float aimAng,float kick,
                   boolean player,boolean bandit,int npcVariant){
        float s=CharacterCollision.BASE_SCALE*scale;
        c.save();c.translate(x,y);if(facing<0)c.scale(-1,1);
        color(0x670b1a18);c.drawOval(-26*s,-7*s,26*s,7*s,p);
        // V58 rear-layer hand torch. Draw BEFORE the immutable original body:
        // its silhouette cannot cover the head, eyes, or facial outline.
        if(!bandit&&!(player&&harvestV81.active)&&dualTorch&&lampOn&&weapon>=0&&weapon<=2&&showWeapons){
            c.save();
            c.translate(-30*s,-33*s);
            c.rotate(aimRotation?aimAng*180f/(float)Math.PI:0f);
            c.scale(.50f,.50f);
            atlas(c,gear,3*260,0,0,0,s);
            drawFlashlightLens(c,s);
            if(showHands)handAtlas(c,3,2,0,0,s,handScale,0,0);
            c.restore();
        }
        Bitmap atlas=npcVariant>=0?npcWalkV56:approvedWalkColors;
        stablePose(c,atlas,npcVariant<0?0:npcVariant,frame,s,breath);
        if(player&&harvestV81.active)drawHarvestRigV81(c,s);
        else if(player&&knifeDuration>0f)drawKnifeSwing(c,s);
        else if(!bandit){
            c.save();
            // Keep the accepted V36 torso-centered weapon/hand rig stationary.
            // Parent pivot is the CHARACTER'S torso center (constant across all weapons).
            // The approved weapon, main hand and support hand remain rigid sibling
            // sprites: one translation to an in-reach chest grip, then one shared rotation.
            final float pivotX=(Ballistics.TORSO_X-70f)*s;
            final float pivotY=(Ballistics.TORSO_Y-136f)*s;
            final float offsetX=(Ballistics.GRIP_X-MAIN_X[weapon])*s;
            final float offsetY=(Ballistics.GRIP_Y-MAIN_Y[weapon])*s;
            c.translate(pivotX-kick,pivotY);
            c.rotate(aimRotation?aimAng*180f/(float)Math.PI:0f);
            c.translate(-pivotX,-pivotY);
            c.translate(offsetX,offsetY);
            if(showWeapons){
                if(weapon==11&&approvedAxe!=null)
                    drawApprovedAxe(c,(MAIN_X[weapon]-70f)*s,(MAIN_Y[weapon]-136f)*s,scale*(CharacterCollision.BASE_SCALE/.76f));
                else atlas(c,gear,weapon*260,0,0,0,s);
                if(weapon==3)drawFlashlightLens(c,s);
            }
            if(showHands){
                handAtlas(c,weapon,2,0,0,s,handScale,0,0);
                handAtlas(c,weapon,1,0,0,s,handScale,support,supportVertical);
            }
            if(anchors){
                // Debug the torso parent + the attached contact points separately.
                rect(c,pivotX-offsetX-3,pivotY-offsetY-3,6,6,0xff6ccde1);
                rect(c,(MAIN_X[weapon]-70f)*s-3,(MAIN_Y[weapon]-136f)*s-3,6,6,0xffb9e9cf);
                if(OFF_X[weapon]>0)rect(c,(OFF_X[weapon]-70f+support)*s-3,
                    (OFF_Y[weapon]-136f+supportVertical)*s-3,6,6,0xffe9cc8c);
            }
            c.restore();
        }else{
            // Bandit overlay is NEW independent art. Body pixels are not changed.
            rect(c,-16*s,-100*s,27*s,5*s,RED);
            rect(c,-16*s,-90*s,12*s,5*s,0xffad5b52);
        }
        if(hitboxes){
            // Debug rectangles track the original atlas head and body areas,
            // including the breathing offset; no oversized arbitrary circle.
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.2f);
            color(RED);
            float hb=breath==Float.POSITIVE_INFINITY?0:breath*s;
            c.drawRect((15-70)*s,(19-136)*s+hb,(112-70)*s,(100-136)*s+hb,p);
            color(OLIVE);
            c.drawRect((15-70)*s,(92-136)*s,(113-70)*s,(138-136)*s,p);
            p.setStyle(Paint.Style.FILL);
        }
        c.restore();
    }
    void drawWorld(Canvas c){
        c.save();c.translate(-camX,-camY);
        terrain(c);
        drawFixtures(c,false);
        for(Drop d:drops){
            if(!WorldPerfV55.nearView(d.x,d.y,camX,camY,viewW,viewH,24))continue;
            float bob=(float)Math.sin(worldTimer*5+d.x)*2;
            rect(c,d.x-9,d.y-13+bob,18,16,DK);
            rect(c,d.x-7,d.y-11+bob,14,12,d.type==2?0xffd7e2d7:d.type==1?0xff8e9b9d:ORANGE);
            if(d.type==2){rect(c,d.x-1,d.y-9+bob,3,9,RED);rect(c,d.x-5,d.y-6+bob,11,3,RED);}
        }
        ArrayList<DrawEntity> order=new ArrayList<>();
        lastVisibleNpcs=0;lastCulledNpcs=0;
        for(float[] fire:FIXED_CAMPFIRES){
            if(!WorldPerfV55.nearView(fire[0],fire[1],camX,camY,viewW,viewH,155))continue;
            final float fx=fire[0],fy=fire[1];
            order.add(new DrawEntity(fy,()->{
                drawCampfire(c,fx,fy,false);
                drawCampfire(c,fx,fy,true);
            }));
        }
        for(float[] fire:builtCampfires){
            if(!WorldPerfV55.nearView(fire[0],fire[1],camX,camY,viewW,viewH,155))continue;
            final float fx=fire[0],fy=fire[1];
            order.add(new DrawEntity(fy,()->{
                drawCampfire(c,fx,fy,false);
                drawCampfire(c,fx,fy,true);
            }));
        }
        for(CampCraftV83.Structure node:craftV83.objects){
            if(!WorldPerfV55.nearView(node.x,node.y,camX,camY,viewW,viewH,140))continue;
            order.add(new DrawEntity(node.y,()->drawCraftStructureV83(c,node)));
        }
        for(Bandit e:enemies)if(e.active){
            if(!WorldPerfV55.nearView(e.x,e.y,camX,camY,viewW,viewH,180)){
                lastCulledNpcs++;continue;
            }
            lastVisibleNpcs++;
            order.add(new DrawEntity(e.y,()->{
            character(c,e.x,e.y,0,e.face,e.animation.frame(),
                    e.animation.isWalking()?Float.POSITIVE_INFINITY:e.animation.breathOffset(),
                    0,0,false,true,e.variant);
            rect(c,e.x-23,e.y-114,46,5,DK);rect(c,e.x-22,e.y-113,44*clamp(e.hp/78,0,1),3,RED);
        }));
        }
        for(Survivor f:friends){
            if(!WorldPerfV55.nearView(f.x,f.y,camX,camY,viewW,viewH,180)){
                lastCulledNpcs++;continue;
            }
            lastVisibleNpcs++;
            order.add(new DrawEntity(f.y,()->{
            character(c,f.x,f.y,f.gun,f.face,f.animation.frame(),
                    f.animation.isWalking()?Float.POSITIVE_INFINITY:f.animation.breathOffset(),
                    Ballistics.angle(f.aimX,f.aimY,f.face),0,false,false,f.variant);
            rect(c,f.x-5,f.y-117,10,4,OLIVE);
        }));
        }
        for(Survivor npc:campStaff){
            if(!WorldPerfV55.nearView(npc.x,npc.y,camX,camY,viewW,viewH,180)){
                lastCulledNpcs++;continue;
            }
            lastVisibleNpcs++;
            order.add(new DrawEntity(npc.y,()->{
            character(c,npc.x,npc.y,npc.gun,npc.face,npc.animation.frame(),
                npc.animation.isWalking()?Float.POSITIVE_INFINITY:npc.animation.breathOffset(),
                0,0,false,false,npc.variant);
        }));
        }
        order.add(new DrawEntity(playerY,()->{
            float angle=Ballistics.angle(aimX,aimY,face);
            character(c,playerX,playerY,gun,face,playerAnimation.frame(),
                    playerAnimation.isWalking()?Float.POSITIVE_INFINITY:playerAnimation.breathOffset(),
                    angle,recoil*2.7f,true,false,-1);
        }));
        order.sort((a,b)->Float.compare(a.y,b.y));
        for(DrawEntity e:order)e.draw.run();
        // Melee knife is drawn with the player at the correct world depth.
        for(Shot projectile:shots){
            if(!WorldPerfV55.nearView(projectile.x,projectile.y,
                    camX,camY,viewW,viewH,25))continue;
            // Short, subtle tracer instead of slow glowing projectile blocks.
            float inv=1f/Math.max(1f,(float)Math.hypot(projectile.vx,projectile.vy));
            float vx=projectile.vx*inv,vy=projectile.vy*inv;
            color(projectile.color);p.setStrokeWidth(1.6f);
            c.drawLine(projectile.x-vx*19,projectile.y-vy*19,
                    projectile.x,projectile.y,p);
            rect(c,projectile.x-1,projectile.y-1,3,3,WHITE);
        }
        for(Flash flash:flashes){
            if(!WorldPerfV55.nearView(flash.x,flash.y,camX,camY,viewW,viewH,32))continue;
            float alpha=clamp(flash.ttl/.065f,0,1),length=18*alpha;
            color(0xffffdf95);p.setStrokeWidth(Math.max(1.5f,3f*alpha));
            c.drawLine(flash.x,flash.y,flash.x+flash.dx*length,
                    flash.y+flash.dy*length,p);
            rect(c,flash.x-2,flash.y-2,4,4,0xfffff7cf);
        }
        for(Spark s:sparks)if(
            WorldPerfV55.nearView(s.x,s.y,camX,camY,viewW,viewH,10))
                rect(c,s.x,s.y,4,4,s.color);
        // Last pass darkens the *entire* world, including all characters,
        // equipment, projectiles and props; real lights punch through this mask.
        if(lightAlpha>0)applyWorldLighting(c);else drawFixtures(c,true);
        if(showChunkGrid)drawChunkGrid(c);
        c.restore();
    }
    void drawChunkGrid(Canvas c){
        final int unit=WorldChunkModel.CHUNK_SIZE;
        int x0=WorldChunkModel.chunkIndex(camX),y0=WorldChunkModel.chunkIndex(camY);
        int x1=WorldChunkModel.chunkIndex(camX+viewW)+1;
        int y1=WorldChunkModel.chunkIndex(camY+viewH)+1;
        color(0x99c8efbb);
        p.setStrokeWidth(2f);
        for(int x=x0;x<=x1;x++)c.drawLine(x*(float)unit,camY,x*(float)unit,camY+viewH,p);
        for(int y=y0;y<=y1;y++)c.drawLine(camX,y*(float)unit,camX+viewW,y*(float)unit,p);
        for(int y=y0;y<y1;y++)for(int x=x0;x<x1;x++)
            label(c,"("+x+","+y+")",x*unit+12f,y*unit+24f,15,0xffbde5c8,false);
    }
    static class DrawEntity {float y;Runnable draw;DrawEntity(float y,Runnable r){this.y=y;draw=r;}}
    void btn(Canvas c,float x,float y,float w,float h,String label,int fill){
        rounded(c,x,y,w,h,9,fill);
        label(c,label,x+12,y+h*.66f,14,WHITE,true);
    }
    float uiSize(int id){return host.setting("uiSize"+id,LegacyControlsV58.defaultScale(id))/100f;}
    float uiWidth(int id){return LegacyControlsV58.defaultW(id)*uiSize(id);}
    float uiHeight(int id){return LegacyControlsV58.defaultH(id)*uiSize(id);}
    float uiX(int id){
        int delta=editPointer>=0&&editControl==id?editX:
            host.setting("uiX"+id,0);
        return LegacyControlsV58.defaultX(id,viewW)+delta;
    }
    float uiY(int id){
        int delta=editPointer>=0&&editControl==id?editY:
            host.setting("uiY"+id,0);
        return LegacyControlsV58.defaultY(id,viewH)+delta;
    }
    boolean uiEnabled(int id){return host.option("uiEnabled"+id,LegacyControlsV58.defaultEnabled(id));}
    int actionAt(float x,float y){
        for(int i=0;i<LegacyControlsV58.COUNT;i++)
            if((uiEnabled(i)||editControls)&&
                LegacyControlsV58.hit(x,y,uiX(i),uiY(i),uiWidth(i),uiHeight(i)))
                return i;
        return -1;
    }
    float padBaseX(boolean right){return right?viewW-190f:Math.max(165f,viewW*.122f);}
    float padBaseY(boolean right){return viewH-(right?145f:153f);}
    float padCenterX(boolean right){
        int id=right?AIM_PAD:MOVE_PAD;
        return padBaseX(right)+(editPointer>=0&&editControl==id?editX:host.setting("uiX"+id,0));
    }
    float padCenterY(boolean right){
        int id=right?AIM_PAD:MOVE_PAD;
        return padBaseY(right)+(editPointer>=0&&editControl==id?editY:host.setting("uiY"+id,0));
    }
    String controlName(int id){return id==MOVE_PAD?"MOVE JOYSTICK":id==AIM_PAD?"AIM JOYSTICK":
        id==HOTBAR?"QUICK ACCESS BAR":LegacyControlsV58.NAMES[id];}
    String controlSizeKey(int id){return id==MOVE_PAD?"movePadSize":id==AIM_PAD?"aimPadSize":"uiSize"+id;}
    int stickEditorAt(float x,float y){
        for(int id=MOVE_PAD;id<=AIM_PAD;id++){
            boolean right=id==AIM_PAD;
            float cx=padCenterX(right),cy=padCenterY(right);
            float radius=(right?82*aimPadScale:86*movePadScale);
            if(Math.hypot(x-cx,y-cy)<radius+20)return id;
        }
        return -1;
    }
    void drawAction(Canvas c,int id){
        if(!uiEnabled(id)&&!editControls)return;
        float x=uiX(id),y=uiY(id),w=uiWidth(id),h=uiHeight(id);
        int opacity=host.setting("uiAlpha"+id,100);
        int alpha=Math.max(36,Math.min(255,opacity*255/100));
        int fill=(LegacyControlsV58.isFire(id)?0x735148:
            LegacyControlsV58.isMelee(id)?0x4e5145:0x345354);
        if(editControls&&id==editControl)fill=0x367665;
        btn(c,x,y,w,h,LegacyControlsV58.LABELS[id],(alpha<<24)|fill);
        if(editControls){
            color(uiEnabled(id)?0xffc4dcbb:0xffe29b80);
            p.setStrokeWidth(2f);p.setStyle(Paint.Style.STROKE);
            c.drawRect(x,y,x+w,y+h,p);p.setStyle(Paint.Style.FILL);
        }
    }
    void drawStatusBar(Canvas c,String title,float value,float x,float y,int fill){
        float v=Math.max(0f,Math.min(100f,value));
        label(c,title,x,y+12,12,WHITE,true);
        rect(c,x+63,y,146,16,0xbb132623);
        rect(c,x+65,y+2,142*v/100f,12,fill);
        label(c,Integer.toString(Math.round(v)),x+213,y+12,12,WHITE,true);
    }
    float hotbarLeft(){
        return viewW*.5f-6*47f*hotbarScale*.5f+
            (editPointer>=0&&editControl==HOTBAR?editX:host.setting("uiX"+HOTBAR,-17));
    }
    float hotbarTop(){
        return viewH-103f+
            (editPointer>=0&&editControl==HOTBAR?editY:host.setting("uiY"+HOTBAR,0));
    }
    int hotbarAt(float x,float y){
        float l=hotbarLeft(),top=hotbarTop(),size=47f*hotbarScale;
        if(y<top||y>top+size||x<l||x>=l+6*size)return -1;
        return Math.min(5,(int)((x-l)/size));
    }
    static String hotbarLabel(int item){
        if(item<0||item>=HOTBAR_TYPES.length)return "?";
        return HOTBAR_TYPES[item];
    }
    int hotbarQuantity(int item){
        if(item==1)return medkits;
        if(item==2)return ammoPacks;
        if(item==6)return foodCount;
        if(item==7)return waterCount;
        if(item==9)return craftV83.stock[0];
        if(item==10)return craftV83.stock[1];
        return 0;
    }
    void setHotbarItem(int slot,int item){
        if(slot<0||slot>=hotbar.length||item<0||item>=HOTBAR_TYPES.length)return;
        hotbar[slot]=item;
        host.prefs.edit().putInt("hotbar"+slot,item).apply();
    }
    void useHotbar(int slot){
        if(slot<0||slot>=6||!playing||paused)return;
        selectedHotbar=slot;int item=hotbar[slot];
        if(item==1&&medkits>0&&health<100){
            medkits--;health=Math.min(100,health+40);
        }else if(item==2&&ammoPacks>0&&ammo<MAG[gun]){
            ammoPacks--;ammo=MAG[gun];
        }else if(item==3||item==4||item==5){
            int weapon=item==3?0:item==4?7:2;
            gun=weapon;ammo=Math.min(ammo,MAG[gun]);
            host.prefs.edit().putInt("gun",weapon).apply();
        }else if(item==6&&foodCount>0){
            foodCount--;hunger=Math.min(100f,hunger+30);
        }else if(item==7&&waterCount>0){
            waterCount--;thirst=Math.min(100f,thirst+35);
        }else if(item==8){
            toggleLamp();
        }else if(item==9||item==10){
            selectPlaceItemV84(item-9);
        }
        saveProgress();invalidate();
    }
    void drawHotbar(Canvas c){
        float x=hotbarLeft(),y=hotbarTop(),size=47f*hotbarScale;
        for(int i=0;i<6;i++){
            int item=hotbar[i],alpha=Math.round(255f*hotbarOpacity/100f);
            int bg=((Math.max(35,alpha)&255)<<24)|(i==selectedHotbar?0x0067573c:0x002e3938);
            rounded(c,x+i*size+1,y+1,size-3,size-3,5,bg);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(i==selectedHotbar?2.4f:1f);
            color(i==selectedHotbar?0xffe5bb6e:0xff8b8270);
            c.drawRect(x+i*size+3,y+3,x+(i+1)*size-4,y+size-4,p);
            p.setStyle(Paint.Style.FILL);
            label(c,Integer.toString(i+1),x+i*size+5,y+12,9,0xffc2c5ad,true);
            String name=hotbarLabel(item);
            itemIconsV84.draw(c,ItemIconsV84.hotbarType(item),
                x+i*size+size*.5f-11f,y+size*.24f,22f);
            label(c,name.length()>6?name.substring(0,6):name,x+i*size+5,y+size-7,
                    8,0xffe7e1c7,true);
            if(item==1||item==2||item==6||item==7||item==9||item==10)
                label(c,Integer.toString(hotbarQuantity(item)),x+(i+1)*size-14,
                      y+size-6,10,0xffe6d4aa,true);
        }
        if(editControls){
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);
            color(0xffe6bc71);
            c.drawRect(x,y,x+size*6,y+size,p);
            p.setStyle(Paint.Style.FILL);
        }
    }
    float hudEditorLeft(){return viewW*.5f-350f+panelX;}
    void drawHudEditorOverlay(Canvas c){
        float left=hudEditorLeft(),top=panelY;
        c.save();c.translate(left,top);c.scale(panelScale,panelScale);
        rounded(c,0,0,700,113,10,0xf2203436);
        int i=Math.max(0,Math.min(EDITOR_ITEMS-1,selectedHudControl));
        label(c,"MOVE PANEL: drag header    "+controlName(i)+
             "   SIZE "+host.setting(controlSizeKey(i),100)+"%",10,17,12,WHITE,true);
        btn(c,610,0,42,20,"-",0xff456961);
        btn(c,657,0,42,20,"+",0xff456961);
        String[] names={"PREV","NEXT","SIZE -","SIZE +","ALPHA -","ALPHA +","HIDE"};
        for(int j=0;j<names.length;j++)
            btn(c,5+j*99,22,94,36,names[j],0xff34565a);
        String[] positions={"LEFT","RIGHT","UP","DOWN","RESET","DONE"};
        for(int j=0;j<positions.length;j++)
            btn(c,8+j*115,65,110,35,positions[j],0xff395653);
        c.restore();
    }
    boolean hudEditorTouch(float x,float y){
        if(!editControls)return false;
        float left=hudEditorLeft(),top=panelY;
        if(!within(x,y,left,top,700*panelScale,113*panelScale))return false;
        float u=(x-left)/panelScale,v=(y-top)/panelScale;
        int i=Math.max(0,Math.min(EDITOR_ITEMS-1,selectedHudControl));
        if(v<20){
            if(u>=608){
                panelScale=clamp(panelScale+(u<655?-.10f:.10f),.65f,1.5f);
                host.prefs.edit().putInt("hudPanelSize",Math.round(panelScale*100f)).apply();
            }else{
                panelPointer=-2;panelGrabX=x-left;panelGrabY=y-top;
            }
            return true;
        }
        if(v>=22&&v<=58){
            int j=(int)((u-5)/99);
            if(j>=0&&j<7){
                if(j==0||j==1){
                    selectedHudControl=Math.floorMod(i+(j==0?-1:1),EDITOR_ITEMS);
                    host.prefs.edit().putInt("selectedButton",selectedHudControl).apply();
                }else if(j==6){
                    if(i<LegacyControlsV58.COUNT)
                        host.prefs.edit().putBoolean("uiEnabled"+i,!uiEnabled(i)).apply();
                }else{
                    String key=j==2||j==3?controlSizeKey(i):"uiAlpha"+i;
                    int min=j<=3?(i>=MOVE_PAD?70:60):30;
                    int current=host.setting(key,100);
                    int next=Math.round(clamp(current+(j%2==0?-10:10),min,j<=3?180:100));
                    host.prefs.edit().putInt(key,next).apply();
                    if(i==HOTBAR||(i>=MOVE_PAD&&j<=3))reloadSettings();
                }
                invalidate();return true;
            }
        }
        if(v>=65&&v<=102){
            int j=(int)((u-8)/115);
            if(j>=0&&j<6){
                if(j==5){
                    editControls=false;
                    host.prefs.edit().putBoolean("editControls",false).apply();
                }else if(j==4){
                    android.content.SharedPreferences.Editor reset=host.prefs.edit()
                        .remove("uiX"+i).remove("uiY"+i).remove("uiAlpha"+i)
                        .remove("uiEnabled"+i);
                    reset.remove(controlSizeKey(i)).apply();
                    reloadSettings();
                }else{
                    String key=(j<=1?"uiX":"uiY")+i;
                    int shift=(j==0||j==2)?-10:10;
                    host.prefs.edit().putInt(key,host.setting(key,0)+shift).apply();
                }
                invalidate();return true;
            }
        }
        return true; // never accidentally touches underlying gameplay objects
    }
    // HUD-pass world marker: must be painted AFTER darkening the entire world.
    // World space aiming marker is rendered AFTER lighting and above HUD darkness.
    void drawBrightCrosshair(Canvas c){
        if(!playing||!showCrosshair||crosshairReticle==null)return;
        // Screen bounds only affect RENDER distance along the aim ray.
        // They never feed back into the actual aim direction, and the
        // crosshair always remains on the character-to-stick ray.
        float half=21f*reticleSize;
        float originX=(playerX-camX)*zoom,originY=(playerY-42f-camY)*zoom;
        float available=aimCursorDistance*zoom;
        if(aimX>.0001f)available=Math.min(available,
            (viewW-half-5f-originX)/aimX);
        else if(aimX<-.0001f)available=Math.min(available,
            (half+5f-originX)/aimX);
        if(aimY>.0001f)available=Math.min(available,
            (viewH-48f-half-originY)/aimY);
        else if(aimY<-.0001f)available=Math.min(available,
            (59f+half-originY)/aimY);
        available=Math.max(0f,available);
        float x=originX+aimX*available,y=originY+aimY*available;
        dest.set(x-half,y-half,x+half,y+half);
        c.drawBitmap(crosshairReticle,null,dest,reticlePaint);
    }
    void topHudButton(Canvas c,int id,String title,boolean active){
        float x=TopHudV76.x(id,viewW),width=TopHudV76.buttonWidth(id,viewW);
        int alpha=Math.round(topButtonOpacityV76*255f/100f);
        if(alpha>0)rounded(c,x,TopHudV76.Y,width,TopHudV76.HEIGHT,5,
            (alpha<<24)|(active?0x003b665b:0x0010262b));
        int size=TopHudV76.scale(viewW)<.8f?10:12;
        p.setTypeface(PIXEL_BOLD);p.setTextSize(size);
        float textX=x+(width-p.measureText(title))*.5f;
        label(c,title,textX+1f,TopHudV76.Y+21f,size,0xff142526,true);
        label(c,title,textX,TopHudV76.Y+20f,size,WHITE,true);
    }
    void hud(Canvas c){
        // Entire interface fades together; world and targeting reticle are
        // outside this composited HUD layer and stay fully readable.
        // Avoid allocating an offscreen HUD layer at the 100% default.
        int hudLayer=hudOpacityV73<100?
            c.saveLayerAlpha(0f,0f,viewW,viewH,CameraHudV73.alpha(hudOpacityV73)):0;
        // No opaque top or bottom bars: the world fills the entire screen.
        label(c,"SURVIVAL PARADISE",13,17,15,0xff142326,true);
        label(c,"SURVIVAL PARADISE",12,16,15,WHITE,true);
        String meta="HP "+(int)health+"  AMMO "+ammo+"/"+MAG[gun]+"  WAVE "+wave+"  KILLS "+kills;
        label(c,meta,13,35,11,0xff142326,false);
        label(c,meta,12,34,11,OLIVE,false);
        topHudButton(c,TopHudV76.FORM,"FORM",false);
        topHudButton(c,TopHudV76.EDIT,editControls?"DONE":"EDIT",editControls);
        topHudButton(c,TopHudV76.DAY,lightAlpha>nightDarkness*.5f?"NOON":"NIGHT",false);
        topHudButton(c,TopHudV76.CAMP,"CAMP",false);
        topHudButton(c,TopHudV76.LAMP,lampOn?"LAMP ON":"LAMP OFF",lampOn);
        topHudButton(c,TopHudV76.BAG,"BAG",false);
        topHudButton(c,TopHudV76.PAUSE,paused?"RESUME":"PAUSE",paused);
        topHudButton(c,TopHudV76.SET,"SET",false);
        String footer="SCRAP "+scrap+"  WOOD "+wood+"  STONE "+stone+
            "  FIBER "+fiber+"  MED "+medkits+"  AMMO "+ammoPacks+
            "   "+MainActivity.LOADOUTS[gun]+"  "+clock.display()+
            (automaticDayNight?" [AUTO]":" [MANUAL]");
        label(c,footer,14,viewH-15,13,0xff182521,true);
        label(c,footer,13,viewH-16,13,ORANGE,true);
        if(harvestV81.active){
            label(c,harvestV81.actionName()+"  "+harvestV81.hitsDone+
                "/"+harvestV81.hitsRequired,14,viewH-53,13,0xffd3e4a7,true);
            rect(c,14,viewH-45,152,5,0xaa112520);
            rect(c,15,viewH-44,150*harvestV81.totalProgress(),3,0xffc2b58c);
        }else if(gatherFeedbackTime>0)
            label(c,gatherFeedback,14,viewH-54,13,0xffd3e4a7,true);
        else{
            ResourceWorldV80.Node near=harvestWorld.nearest(playerX,playerY,
                ResourceWorldV80.USE_RADIUS,CAMP_X,CAMP_Y,WORLD_W,WORLD_H);
            if(near!=null)
                label(c,"USE: GATHER "+near.name(),14,viewH-54,12,0xffd3e4a7,true);
        }
        // Original two virtual sticks, with per-stick size/sensitivity tests.
        float jy=padCenterY(false),rx=padCenterX(true),ry=padCenterY(true);
        float lx=padCenterX(false);
        float leftRadius=86*movePadScale,rightRadius=82*aimPadScale;
        int alpha=Math.round(255f*Math.max(25,Math.min(100,controlOpacity))/100f);
        int leftAlpha=alpha*host.setting("uiAlpha"+MOVE_PAD,100)/100;
        int rightAlpha=alpha*host.setting("uiAlpha"+AIM_PAD,100)/100;
        color((leftAlpha*0x66/255<<24)|0x003e625a);
        c.drawCircle(lx,jy,leftRadius,p);
        color((leftAlpha*0x9b/255<<24)|0x0096b8a5);
        c.drawCircle(lx+stickX*46*movePadScale,jy+stickY*46*movePadScale,31*movePadScale,p);
        color((rightAlpha*0x66/255<<24)|0x005b6f61);
        c.drawCircle(rx,ry,rightRadius,p);
        color((rightAlpha*0xaa/255<<24)|0x00aa9d71);
        c.drawCircle(rx,ry,52*aimPadScale,p);
        color((rightAlpha<<24)|0x00f2deb0);
        // Restored MOVING thumb: pad center when released, slides radially
        // with touch distance instead of orbiting at a fixed 39px radius.
        c.drawCircle(rx+aimStickX*59*aimPadScale,
            ry+aimStickY*59*aimPadScale,13*aimPadScale,p);
        label(c,"AIM",rx-20,ry+6,17,WHITE,true);
        for(int ui=0;ui<LegacyControlsV58.COUNT;ui++)drawAction(c,ui);
        drawHotbar(c);
        if(showStatusBars){
            drawStatusBar(c,"HP",health,12,145,0xffc76b65);
            drawStatusBar(c,"STA",stamina,12,165,0xff64ad80);
            drawStatusBar(c,"HUN TEST",hunger,12,185,0xffb5a06b);
            drawStatusBar(c,"THR TEST",thirst,12,205,0xff608dad);
            drawStatusBar(c,"FAT TEST",fatigue,12,225,0xffa18eaf);
            float enc=Math.min(100f,scrap*.8f+ammoPacks*5f+medkits*7f);
            drawStatusBar(c,"ENC TEST",enc,12,245,0xffbca36e);
        }
        label(c,"MOVE",lx-39,jy+105,12,0xffb8d4c5,true);
        if(reloadClock>0)label(c,"RELOADING...",viewW-235,viewH-227,17,ORANGE,true);
        if(showPerf){
            if(host.option("compactDebugV76",true)){
                label(c,String.format(Locale.US,"FPS %.1f | %.1fms | NPC %d | CHUNK %d,%d",
                    1000f/Math.max(1f,smoothedFrameMs),smoothedFrameMs,lastVisibleNpcs,
                    WorldChunkModel.chunkIndex(playerX),WorldChunkModel.chunkIndex(playerY)),
                    13,55,12,WHITE,true);
            }else{
                rounded(c,10,46,348,87,8,0x761a3033);
                label(c,String.format(Locale.US,"FPS %.1f  %.1fms  NPC %d",
                    1000f/Math.max(1f,smoothedFrameMs),smoothedFrameMs,lastVisibleNpcs),
                    18,66,14,WHITE,true);
                label(c,String.format(Locale.US,"CHUNK %d,%d   CACHE %d/%d  JOBS %d",
                    WorldChunkModel.chunkIndex(playerX),WorldChunkModel.chunkIndex(playerY),
                    terrainChunks.residentCount(),terrainChunks.residentLimit(),
                    terrainChunks.pendingCount()),18,86,13,OLIVE,false);
                label(c,String.format(Locale.US,"WORLD %.0f, %.0f | CULLED %d",
                    playerX,playerY,lastCulledNpcs),18,104,12,ORANGE,false);
                label(c,String.format(Locale.US,"CPU UPDATE %.1f  DRAW %.1f  LIGHT %.1f ms",
                    updateNs/1e6f,worldNs/1e6f,lightingNs/1e6f),18,122,11,OLIVE,false);
            }
        }
        if(placingKindV84>=0){
            label(c,"PLACE "+(placingKindV84==0?"BARRICADE":"LIGHT POST")+
                " • DRAG / RELEASE ON GROUND",viewW*.5f-205f,66,13,0xfff4d5a1,true);
            label(c,"Tap BAG to cancel placement",viewW*.5f-117f,86,11,0xffdfd6c2,false);
        }
        if(hudLayer!=0)c.restoreToCount(hudLayer);
        // Keep on-screen edit handles opaque at any HUD opacity.
        if(editControls)drawHudEditorOverlay(c);
    }
    void menu(Canvas c){
        rounded(c,viewW/2-300,viewH/2-200,600,398,20,0xef14272b);
        label(c,"SURVIVAL PARADISE",viewW/2-254,viewH/2-115,34,WHITE,true);
        label(c,"NATIVE ANDROID SURVIVAL SHOOTER  •  ALPHA 57 HYBRID",
                viewW/2-254,viewH/2-80,15,OLIVE,true);
        label(c,"Move left. Aim right. FIRE with independent button.",viewW/2-254,viewH/2-40,15,WHITE,false);
        label(c,"Explore the world, fight bandits, and collect supplies.",viewW/2-254,viewH/2-15,15,WHITE,false);
        btn(c,viewW/2-254,viewH/2+18,245,60,"NEW GAME",0xff396c5d);
        btn(c,viewW/2+8,viewH/2+18,245,60,hasSave?"CONTINUE":"NO SAVE",hasSave?0xff416b5f:0xff334441);
        btn(c,viewW/2-254,viewH/2+92,507,55,"GAME SETTINGS",0xff2d5055);
        label(c,"Approved V31 character and weapons • offline • no WebView",
                viewW/2-254,viewH/2+173,13,ORANGE,false);
    }
    void pauseOverlay(Canvas c){
        rect(c,0,0,viewW,viewH,0xaa07171d);
        rounded(c,viewW/2-195,viewH/2-130,390,250,16,0xff20353b);
        label(c,gameOver?"YOU DIED":"GAME PAUSED",viewW/2-155,viewH/2-66,27,WHITE,true);
        btn(c,viewW/2-150,viewH/2-38,300,50,gameOver?"NEW GAME":"RESUME",0xff376a5e);
        btn(c,viewW/2-150,viewH/2+28,300,50,"SETTINGS",0xff344952);
    }
    @Override protected void onDetachedFromWindow(){
        terrainChunks.release();
        lighting.release();
        if(campStatic!=null){campStatic.recycle();campStatic=null;}
        itemIconsV84.release();
        if(pickaxeV81!=null){pickaxeV81.recycle();pickaxeV81=null;}
        if(crosshairReticle!=null){crosshairReticle.recycle();crosshairReticle=null;}
        super.onDetachedFromWindow();
    }
    @Override protected void onDraw(Canvas canvas){
        super.onDraw(canvas);
        long now=System.nanoTime();float dt=lastFrame==0?0:(now-lastFrame)/1e9f;lastFrame=now;
        if(dt>0&&dt<.5f){
            float rawMs=dt*1000f;
            smoothedFrameMs=drawFrames==0?rawMs:smoothedFrameMs*.92f+rawMs*.08f;
            drawFrames++;
        }
        drawScale=Math.max(.1f,getHeight()/H);
        viewW=getWidth()/drawScale;viewH=H;
        long updateStart=System.nanoTime();
        update(dt);
        updateNs=System.nanoTime()-updateStart;
        float effectiveZoom=zoom;
        // Camera follow and clamping in world coordinates.
        camX=playerX-viewW/(2*effectiveZoom)+cameraLookX;
        camY=playerY-viewH/(2*effectiveZoom)+cameraLookY;
        canvas.drawColor(0xff101f24);
        canvas.save();canvas.scale(drawScale,drawScale);
        canvas.save();canvas.scale(effectiveZoom,effectiveZoom);
        float drawW=viewW/effectiveZoom,drawH=viewH/effectiveZoom;
        float oldW=viewW,oldH=viewH;
        viewW=drawW;viewH=drawH;
        long renderStart=System.nanoTime();
        if(lightAlpha<=0)lightingNs=0;
        drawWorld(canvas);
        worldNs=System.nanoTime()-renderStart;
        viewW=oldW;viewH=oldH;
        canvas.restore();
        if(playing){
            drawBrightCrosshair(canvas);
            hud(canvas);
            if(paused&&!settingsPause)pauseOverlay(canvas);
        }else menu(canvas);
        canvas.restore();
        // Schedule at the next display vsync, never add a fixed 16ms delay ON TOP
        // of CPU draw time. The old loop capped real FPS below panel refresh.
        postInvalidateOnAnimation();
    }
    byte[] capturePNG(){
        Bitmap image=Bitmap.createBitmap(Math.max(1,getWidth()),Math.max(1,getHeight()),Bitmap.Config.ARGB_8888);
        Canvas canvas=new Canvas(image);
        long save=lastFrame;lastFrame=System.nanoTime();drawSnapshot(canvas);lastFrame=save;
        ByteArrayOutputStream buf=new ByteArrayOutputStream();image.compress(Bitmap.CompressFormat.PNG,100,buf);
        image.recycle();return buf.toByteArray();
    }
    // Snapshot renderer without the infinite game invalidation loop.
    private void drawSnapshot(Canvas canvas){
        float s=Math.max(.1f,getHeight()/H);
        viewW=getWidth()/s;viewH=H;drawScale=s;
        camX=playerX-viewW/2;
        camY=playerY-viewH/2;
        canvas.drawColor(0xff101f24);canvas.save();canvas.scale(s,s);
        if(playing){drawWorld(canvas);drawBrightCrosshair(canvas);hud(canvas);}else menu(canvas);
        canvas.restore();
    }
    void updateStick(float x,float y,boolean right){
        float cx=padCenterX(right),cy=padCenterY(right);
        float padSize=right?aimPadScale:movePadScale;
        float sensitivity=right?aimSensitivity:moveSensitivity;
        float dx=(x-cx)/(74*padSize)*sensitivity;
        float dy=(y-cy)/(74*padSize)*sensitivity;
        float length=(float)Math.hypot(dx,dy);
        if(length>1){dx/=length;dy/=length;length=1f;}
        if(right){
            // V61 directly maps thumb position to heading and distance.
            // Position is clamped to the joystick rim, not angular-only.
            aimStickX=dx;aimStickY=dy;
            aimDeflection=length;
            if(length>ClassicAimV71.DEADZONE){
                float heading=Math.max(.001f,(float)Math.hypot(dx,dy));
                aimX=ClassicAimV71.heading(dx,heading,aimX);
                aimY=ClassicAimV71.heading(dy,heading,aimY);
                targetAimX=aimX;targetAimY=aimY;
                face=aimX<-.025f?-1:aimX>.025f?1:face;
            }
            // Update immediately on a touch event; NO frame-accumulated speed.
            float rest=RadialAimV65.rest(gun,crosshairRestPercent);
            aimCursorDistance=rest+ClassicAimV71.TRAVEL*
                Math.max(0f,Math.min(1f,length));
            cursorInitialized=true;
            cursorWorldX=playerX+aimX*aimCursorDistance;
            cursorWorldY=playerY-42f+aimY*aimCursorDistance;
        }else {stickX=dx;stickY=dy;}
    }
    float fireWidth(){return 105f*fireButtonSize;}
    float fireHeight(){return 47f*fireButtonSize;}
    float fireLeft(){return viewW-352f+fireButtonX;}
    float fireTop(){return viewH-268f+fireButtonY;}
    boolean within(float x,float y,float left,float top,float width,float height){
        return x>=left&&x<=left+width&&y>=top&&y<=top+height;
    }
    void tap(float x,float y){
        if(!playing){
            if(within(x,y,viewW/2-254,viewH/2+18,245,60)){newGame();return;}
            if(within(x,y,viewW/2+8,viewH/2+18,245,60)){if(hasSave)continueGame();return;}
            if(within(x,y,viewW/2-254,viewH/2+92,507,55)){host.settings();return;}
            return;
        }
        if(paused&&!settingsPause){
            if(within(x,y,viewW/2-150,viewH/2-38,300,50)){if(gameOver)newGame();else togglePause();return;}
            if(within(x,y,viewW/2-150,viewH/2+28,300,50)){host.settings();return;}
        }
        switch(TopHudV76.hit(x,y,viewW)){
            case TopHudV76.FORM:
                followMode=(followMode+1)%FollowFormationV61.NAMES.length;
                host.prefs.edit().putInt("followMode",followMode).apply();
                host.runOnUiThread(()->android.widget.Toast.makeText(host,
                    "FORMATION: "+FollowFormationV61.NAMES[followMode],
                    android.widget.Toast.LENGTH_SHORT).show());return;
            case TopHudV76.EDIT:
                editControls=!editControls;releaseControls();
                host.prefs.edit().putBoolean("editControls",editControls).apply();
                invalidate();return;
            case TopHudV76.SET:host.settings();return;
            case TopHudV76.PAUSE:togglePause();return;
            case TopHudV76.LAMP:toggleLamp();return;
            case TopHudV76.CAMP:placeCampfire();return;
            case TopHudV76.DAY:toggleNight();return;
            case TopHudV76.BAG:host.inventory();return;
            default:break;
        }
        if(paused)return;
        // HUD action buttons are dispatched through LegacyControlsV58 so all
        // visible and touch regions always use the same configurable geometry.
        if(x<viewW*.37f&&y>viewH*.45f)return;
        if(x>viewW*.61f&&y>viewH*.42f)return;
    }
    /** Existing USE keeps loot priority, but harvesting is now an animation. */
    boolean gatherNearestV80(){
        if(harvestV81.active||firing||!playing||paused||gameOver)return false;
        if(nearest(playerX,playerY,135f)!=null)return false;
        ResourceWorldV80.Node node=harvestWorld.nearest(playerX,playerY,
            ResourceWorldV80.USE_RADIUS,CAMP_X,CAMP_Y,WORLD_W,WORLD_H);
        SalvageWorldV84.Node salvage=salvageWorldV84.nearest(playerX,playerY,
            SalvageWorldV84.REACH,CAMP_X,CAMP_Y,WORLD_W,WORLD_H);
        if(node==null&&salvage==null)return false;
        boolean useScrap=salvage!=null&&(node==null||
            distance(playerX,playerY,salvage.x,salvage.y)<
            distance(playerX,playerY,node.x,node.y));
        if(useScrap){
            if(!harvestV81.beginScrap(salvage))return false;
            face=salvage.x>=playerX?1:-1;
        }else{
            if(!harvestV81.begin(node))return false;
            face=node.x>=playerX?1:-1;
        }
        stopWalking();knifeDuration=0f;knifeHitPending=false;
        gatherFeedbackTime=0f;harvestImpactTimeV81=0f;
        return true;
    }
    void activateButton(int ui,int pointer){
        // No second attack/use while tool strikes are underway.
        if(harvestV81.active)return;
        if(LegacyControlsV58.isFire(ui)){
            if(ui==LegacyControlsV58.FIRE_L)fireLeftPointer=pointer;
            else firePointer=pointer;
            firing=true;
        }else if(LegacyControlsV58.isMelee(ui))knifeStrike();
        else if(ui==LegacyControlsV58.RUN)runHeld=!runHeld;
        else if(ui==LegacyControlsV58.CROUCH)crouchHeld=!crouchHeld;
        else if(ui==LegacyControlsV58.SWAP)switchWeapon();
        else if(ui==LegacyControlsV58.RELOAD)reload();
        else if(ui==LegacyControlsV58.ZOOM_IN||ui==LegacyControlsV58.ZOOM_OUT){
            float delta=ui==LegacyControlsV58.ZOOM_IN?.12f:-.12f;
            zoom=clamp(zoom+delta,.45f,1.8f);
            host.prefs.edit().putInt("cameraZoom",Math.round(zoom*100f)).apply();
        }else if(ui==LegacyControlsV58.USE){
            for(Iterator<Drop> it=drops.iterator();it.hasNext();){
                Drop drop=it.next();
                if(distance(playerX,playerY,drop.x,drop.y)<100f){
                    if(drop.type==0)ammoPacks++;else if(drop.type==1)scrap+=2;
                    else medkits++;it.remove();saveProgress();return;
                }
            }
            gatherNearestV80();
        }
    }
    @Override public boolean onTouchEvent(MotionEvent e){
        int action=e.getActionMasked(),i=e.getActionIndex(),id=e.getPointerId(i);
        float x=e.getX(i)/Math.max(.01f,drawScale),y=e.getY(i)/Math.max(.01f,drawScale);
        switch(action){
            case MotionEvent.ACTION_DOWN:
            case MotionEvent.ACTION_POINTER_DOWN:
                if(!playing||paused||TopHudV76.hit(x,y,viewW)>=0){tap(x,y);return true;}
                if(editControls&&hudEditorTouch(x,y)){
                    if(panelPointer==-2)panelPointer=id;
                    return true;
                }
                int hotSlot=hotbarAt(x,y);
                if(hotSlot>=0){
                    if(editControls){
                        editPointer=id;editControl=HOTBAR;selectedHudControl=HOTBAR;
                        editX=host.setting("uiX"+HOTBAR,-17);
                        editY=host.setting("uiY"+HOTBAR,0);
                        editGrabX=x-hotbarLeft();editGrabY=y-hotbarTop();
                        host.prefs.edit().putInt("selectedButton",HOTBAR).apply();
                    }else useHotbar(hotSlot);
                    return true;
                }
                int target=actionAt(x,y);
                if(target>=0){
                    if(editControls){
                        editPointer=id;editControl=target;
                        selectedHudControl=target;
                        host.prefs.edit().putInt("selectedButton",target).apply();
                        editX=host.setting("uiX"+target,0);
                        editY=host.setting("uiY"+target,0);
                        editGrabX=x-uiX(target);
                        editGrabY=y-uiY(target);
                    }else activateButton(target,id);
                    return true;
                }
                if(editControls){
                    int stickTarget=stickEditorAt(x,y);
                    if(stickTarget>=0){
                        editPointer=id;editControl=stickTarget;selectedHudControl=stickTarget;
                        host.prefs.edit().putInt("selectedButton",stickTarget).apply();
                        editX=host.setting("uiX"+stickTarget,0);
                        editY=host.setting("uiY"+stickTarget,0);
                        editGrabX=x-padCenterX(stickTarget==AIM_PAD);
                        editGrabY=y-padCenterY(stickTarget==AIM_PAD);
                    }
                    return true;
                }
                if(placingKindV84>=0&&!editControls){
                    placingPointerV84=id;
                    placingXv84=camX+x/Math.max(.01f,zoom);
                    placingYv84=camY+y/Math.max(.01f,zoom);
                    invalidate();return true;
                }
                // Joystick hit tests follow their EDITED positions; the old
                // fixed screen zones broke input after moving the controls.
                float moveDistance=(float)Math.hypot(x-padCenterX(false),y-padCenterY(false));
                float aimDistance=(float)Math.hypot(x-padCenterX(true),y-padCenterY(true));
                float moveReach=100f*movePadScale,aimReach=100f*aimPadScale;
                if(leftPointer<0&&moveDistance<moveReach&&moveDistance<=aimDistance){
                    leftPointer=id;updateStick(x,y,false);return true;
                }
                if(rightPointer<0&&aimDistance<aimReach){
                    rightPointer=id;updateStick(x,y,true);return true;
                }
                tap(x,y);return true;
            case MotionEvent.ACTION_MOVE:
                for(int j=0;j<e.getPointerCount();j++){
                    int pointer=e.getPointerId(j);
                    float px=e.getX(j)/Math.max(.01f,drawScale);
                    float py=e.getY(j)/Math.max(.01f,drawScale);
                    if(pointer==placingPointerV84){
                        placingXv84=camX+px/Math.max(.01f,zoom);
                        placingYv84=camY+py/Math.max(.01f,zoom);
                        invalidate();
                    }
                    if(pointer==leftPointer)updateStick(px,py,false);
                    if(pointer==rightPointer)updateStick(px,py,true);
                    if(pointer==panelPointer){
                        panelX=clamp(px-panelGrabX-(viewW*.5f-350f),
                                     -viewW*.5f+355f,viewW*.5f-350f);
                        panelY=clamp(py-panelGrabY,55f,viewH-75f);
                    }
                    if(pointer==editPointer&&editControl>=0){
                        editX=Math.round(px-editGrabX-
                                (editControl==HOTBAR?viewW*.5f-6*47f*hotbarScale*.5f:
                                 editControl<LegacyControlsV58.COUNT?
                                 LegacyControlsV58.defaultX(editControl,viewW):
                                 padBaseX(editControl==AIM_PAD)));
                        editY=Math.round(py-editGrabY-
                                (editControl==HOTBAR?viewH-103f:
                                 editControl<LegacyControlsV58.COUNT?
                                 LegacyControlsV58.defaultY(editControl,viewH):
                                 padBaseY(editControl==AIM_PAD)));
                        if(editControl<LegacyControlsV58.COUNT){
                            editX=Math.round(clamp(editX,-LegacyControlsV58.defaultX(editControl,viewW),
                                  viewW-uiWidth(editControl)-LegacyControlsV58.defaultX(editControl,viewW)));
                            editY=Math.round(clamp(editY,-LegacyControlsV58.defaultY(editControl,viewH),
                                  viewH-uiHeight(editControl)-LegacyControlsV58.defaultY(editControl,viewH)));
                        }else if(editControl==HOTBAR){
                            float width=6*47f*hotbarScale;
                            editX=Math.round(clamp(editX,-viewW*.5f+width*.5f+5,
                                      viewW*.5f-width*.5f-5));
                            editY=Math.round(clamp(editY,65-(viewH-103f),
                                      viewH-55-(viewH-103f)));
                        }else{
                            editX=Math.round(clamp(editX,70-padBaseX(editControl==AIM_PAD),
                                  viewW-70-padBaseX(editControl==AIM_PAD)));
                            editY=Math.round(clamp(editY,90-padBaseY(editControl==AIM_PAD),
                                  viewH-70-padBaseY(editControl==AIM_PAD)));
                        }
                        invalidate();
                    }
                }return true;
            case MotionEvent.ACTION_POINTER_UP:
            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_CANCEL:
                if(id==placingPointerV84){
                    placingPointerV84=-1;
                    if(action!=MotionEvent.ACTION_CANCEL)
                        placeAtV84(camX+x/Math.max(.01f,zoom),
                            camY+y/Math.max(.01f,zoom));
                    invalidate();return true;
                }
                if(id==leftPointer||action==MotionEvent.ACTION_CANCEL){
                    leftPointer=-1;stopWalking();
                }
                if(id==rightPointer||action==MotionEvent.ACTION_CANCEL){
                    rightPointer=-1;aimDeflection=0f;
                    cursorMoveX=0f;cursorMoveY=0f;
                    aimStickX=0f;aimStickY=0f;snapAimToWeaponRest();
                }
                if(id==firePointer||action==MotionEvent.ACTION_CANCEL)firePointer=-1;
                if(id==fireLeftPointer||action==MotionEvent.ACTION_CANCEL)fireLeftPointer=-1;
                firing=firePointer>=0||fireLeftPointer>=0;
                if(id==panelPointer||action==MotionEvent.ACTION_CANCEL){
                    panelPointer=-1;
                    host.prefs.edit().putInt("hudPanelX",Math.round(panelX))
                         .putInt("hudPanelY",Math.round(panelY)).apply();
                }
                if((id==editPointer||action==MotionEvent.ACTION_CANCEL)&&editControl>=0){
                    host.prefs.edit().putInt("uiX"+editControl,editX)
                        .putInt("uiY"+editControl,editY).apply();
                    editPointer=-1;editControl=-1;
                }
                return true;
        }
        return true;
    }
}