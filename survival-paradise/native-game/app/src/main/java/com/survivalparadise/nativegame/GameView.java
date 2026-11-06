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
    // V108 head-fitting controls: neutral settings preserve every V98 pixel.
    int fitHeadXV108=0,fitHeadYV108=0,fitIdleBreathV108=4,fitWalkFpsV108=0;
    float idleBreathingTempoV110=1f;
    // V117: independent player and world-NPC gun/hand rotation-axis fitting.
    int playerGunPivotXV117=0,playerGunPivotYV117=0;
    int npcGunPivotXV117=0,npcGunPivotYV117=0;
    int playerHeadSizeV113=100,npcHeadSizeV113=100;
    int playerTorsoWidthV114=100,npcTorsoWidthV114=100;
    int playerPelvisWidthV115=100,npcPelvisWidthV115=100;
    int npcHeadFitXV113=0,npcHeadFitYV113=0,npcBreathPixelsV113=4,npcWalkFpsV113=0;
    int npcHeadAimMaxDegreesV113=10;
    float npcBreathingTempoV113=1f,npcWalkingAnimationTempoV113=1f;
    int headAimMaxDegreesV111=HeadAimV111.DEFAULT_MAX_DEGREES;
    float playerHeadTiltV111=0f;
    boolean showHands=true,showWeapons=true,anchors=false,hitboxes=false,enemyAI=true,
            aimRotation=true,recoilFX=true,lootEnabled=true,night=true;
    boolean playing=false,paused=false,settingsPause=false,wasPaused=false,hasSave=false,gameOver=false;
    boolean lampOn=true,neonEnabled=true,campfiresLit=true;
    int nightDarkness=211,flashlightReach=490;
    final LightingV47 lighting=new LightingV47();
    final WorldChunkCache terrainChunks=new WorldChunkCache((int)CAMP_X,(int)CAMP_Y);
    // V128: the original camp, NPCs, and all six V74 outdoor biomes remain.
    // The industrial biome now occupies a seed-stable connected region east
    // of the original world; no second world mode or teleport is required.
    final boolean industrialModeV123=false;
    final boolean stitchedIndustrialV128=true;
    final IndustrialArtV123 industrialArtV123=new IndustrialArtV123();
    final IndustrialYardV123 industrialYardV123=new IndustrialYardV123();
    static final int INDUSTRIAL_SITE_V123=99123;
    int industrialSeedV123=14901;
    IndustrialWorldV123.District industrialSiteV123=IndustrialWorldV123.district(0,0,14901);
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
    final GroundPickupsV85 groundPickupsV85=new GroundPickupsV85();
    final BanditLootV87 banditLootV87=new BanditLootV87();
    final FieldFindsV91 fieldFindsV91=new FieldFindsV91();
    final GearLootV95 gearLootV95=new GearLootV95();
    final WardrobeV92 wardrobeV92=new WardrobeV92();
    final WearableArtV96 wearableArtV96=new WearableArtV96();
    CharacterSkinsV109 characterSkinsV109; // exact 200 approved head/body sources + V5 fittings
    int playerSkinV109=124;
    final TorsoRecolorV98 torsoRecolorV98=new TorsoRecolorV98();
    int backpackStyleV96=0,headgearStyleV96=0;
    // Previously authored gear source images, normalized via transparent ROIs.
    // No modification is performed on the locked body/head animation atlas.
    final Bitmap[] approvedGearV93=new Bitmap[3];
    final Rect[] approvedGearBoundsV93=new Rect[3];
    void loadApprovedGearV93(){
        String[] names={"backpack.png","headgear.png","vest.png"};
        for(int i=0;i<names.length;i++){
            try(InputStream in=getResources().getAssets().open("pixel_gear_v95/"+names[i])){
                Bitmap bitmap=BitmapFactory.decodeStream(in);
                if(bitmap==null||bitmap.getWidth()>2048||bitmap.getHeight()>2048)continue;
                int left=bitmap.getWidth(),top=bitmap.getHeight(),right=0,bottom=0;
                for(int y=0;y<bitmap.getHeight();y++)for(int x=0;x<bitmap.getWidth();x++){
                    if((bitmap.getPixel(x,y)>>>24)<48)continue;
                    if(x<left)left=x;if(x>right)right=x;
                    if(y<top)top=y;if(y>bottom)bottom=y;
                }
                if(left>right||top>bottom){bitmap.recycle();continue;}
                approvedGearV93[i]=bitmap;
                approvedGearBoundsV93[i]=new Rect(left,top,right+1,bottom+1);
            }catch(Exception ignored){approvedGearV93[i]=null;}
        }
    }
    void drawApprovedGearV93(Canvas c,int index,float left,float top,
        float right,float bottom,float scale){
        if(index<0||index>=approvedGearV93.length||
            approvedGearV93[index]==null||approvedGearBoundsV93[index]==null)return;
        // Preserve native-pixel silhouette; scale through nearest-neighbor.
        RectF frame=new RectF(left*scale,top*scale,right*scale,bottom*scale);
        c.drawBitmap(approvedGearV93[index],approvedGearBoundsV93[index],frame,pixel);
    }
    final NPCRelationshipsV92 relationshipsV92=new NPCRelationshipsV92();
    final int[] bagOrderV92=new int[40];
    boolean bagOrderInitializedV92=false;
    float campGuardCooldownV92=0f;
    int activeSiteV91=-1; // -1 outdoors, 1 original clinic, all others separate indoor maps
    boolean sitesInitializedV88=false;
    ClinicInteriorV89 clinicInteriorV89=new ClinicInteriorV89();
    ClinicActorsV90 clinicActorsV90=new ClinicActorsV90(clinicInteriorV89);
    final ClinicVisionV90 clinicVisionV90=new ClinicVisionV90();
    ClinicNavV90 clinicNavV90=new ClinicNavV90(clinicInteriorV89);
    final ArrayList<float[]> clinicFriendWaypointsV90=new ArrayList<>();
    final Path clinicVisionPathV90=new Path();
    final ArrayList<float[]> outdoorCompanionPositionsV90=new ArrayList<>();
    float indoorShotCooldownV90=0f;
    float indoorCompanionNavClockV90=0f;
    boolean insideClinicV89=false;
    float outsideDoorXv89=0f,outsideDoorYv89=0f;
    final java.util.HashMap<Long,Float> stationUsedV88=new java.util.HashMap<>();
    final ItemIconsV84 itemIconsV84=new ItemIconsV84();
    int placingKindV84=-1,placingPointerV84=-1;
    float placingXv84,placingYv84;
    final ResourceWorldV80 harvestWorld=new ResourceWorldV80();
    final HarvestActionV81 harvestV81=new HarvestActionV81();
    float harvestImpactTimeV81=0f;
    float playerX=1000,playerY=1060,health=100,stamina=100,shotClock=0,reloadClock=0,recoil=0;
    float aimX=1,aimY=0,stickX=0,stickY=0;
    int face=1,gun=0,ammo=12,kills=0,wave=1,scrap=0,medkits=0,ammoPacks=0,enemyCount=0;
    int wood=0,stone=0,fiber=0,bandagesV88=0,energyV88=0;
    String gatherFeedback="";float gatherFeedbackTime=0f;
    float worldTimer=0,autSaveClock=0,shake=0;
    long lastFrame=0;
    float viewW=1200,viewH=660,drawScale=1,camX=0,camY=0;
    float renderZoomV90=1f;
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
    // Append new controls after all existing saved IDs: no HUD migration.
    static final int HOTBAR=HUD_ITEMS,BAG_EDITOR=HOTBAR+1,TALK_EDITOR=BAG_EDITOR+1,
        TOP_FORM_EDITOR=TALK_EDITOR+1,TOP_EDIT_EDITOR=TOP_FORM_EDITOR+1,
        TOP_DAY_EDITOR=TOP_EDIT_EDITOR+1,TOP_CAMP_EDITOR=TOP_DAY_EDITOR+1,
        TOP_LAMP_EDITOR=TOP_CAMP_EDITOR+1,TOP_PAUSE_EDITOR=TOP_LAMP_EDITOR+1,
        TOP_SET_EDITOR=TOP_PAUSE_EDITOR+1,STATUS_EDITOR=TOP_SET_EDITOR+1,
        HEADER_EDITOR=STATUS_EDITOR+1,FOOTER_EDITOR=HEADER_EDITOR+1,
        PERF_EDITOR=FOOTER_EDITOR+1,COMMAND_EDITOR=PERF_EDITOR+1,
        ENTER_EDITOR=COMMAND_EDITOR+1,EDITOR_ITEMS=ENTER_EDITOR+1;
    static final String[] HOTBAR_TYPES={
        "EMPTY","MEDKIT","AMMO","PISTOL","SHOTGUN","UZI","FOOD","WATER","TORCH",
        "BARRICADE","LIGHT POST","WATER COLLECTOR","FIELD SHELTER",
        "BANDAGE","ENERGY RATION"};
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
    final DroppedItemsV129 droppedItemsV129=new DroppedItemsV129();
    float droppedExpiryClockV129=0f;
    // V122 interior damage is intentionally V90 hitscan, but every actual
    // NPC/player gunshot generates a matching transient traveling bullet.
    final ArrayList<IndoorRoundV122> indoorRoundsV122=new ArrayList<>();

    final ArrayList<Cover> covers=new ArrayList<>();
    int allySetting=1,allyCurrent=1;
    int followMode=FollowFormationV61.SCATTER,followSpacing=125;
    boolean companionStayV118=false,companionHoldFireV118=false;
    float axeSwingTimeV118=0f;
    float followHeadingX=1f,followHeadingY=0f;
    final Rect src=new Rect();
    final RectF dest=new RectF();
    final float PAD=46;
    static class Bandit {float x,y,hp=78,cd,hit,homeX,homeY,patrolClock,aimX=1f,aimY=0f;int face=1,skinV109;boolean active=true;
        final AnimationCycle animation=new AnimationCycle();
        int variant;
        Bandit(float a,float b,int variant){x=a;y=b;homeX=a;homeY=b;patrolClock=variant*2.3f;cd=.7f;this.variant=variant;
            skinV109=1+Math.floorMod(Math.round(a*11f+b*17f+variant*73f),200);}}
    static class Survivor {float x,y,homeX,homeY,cd,aimX=1,aimY=0;int gun,face=1,variant,skinV109;
        final AnimationCycle animation=new AnimationCycle();
        Survivor(float a,float b,int g,int variant){x=a;y=b;homeX=a;homeY=b;gun=g;this.variant=variant;
            skinV109=1+Math.floorMod(Math.round(a*13f+b*19f+variant*41f),200);}}
    static class Shot {float x,y,vx,vy,life,damage;boolean hostile;int color;
        Shot(float x,float y,float vx,float vy,float damage,boolean enemy){
            this.x=x;this.y=y;this.vx=vx;this.vy=vy;this.damage=damage;this.life=Ballistics.PROJECTILE_LIFE;
            this.hostile=enemy;this.color=enemy?0xffffa88a:0xffeada9e;
        }}
    static class Flash {
        float x,y,dx,dy,ttl=GunEffectsV119.FLASH_SECONDS;
        Flash(float x,float y,float dx,float dy){
            this.x=x;this.y=y;this.dx=dx;this.dy=dy;
        }
    }
    static class IndoorRoundV122 {
        float x,y,vx,vy,life;boolean hostile;
        IndoorRoundV122(float x,float y,float vx,float vy,float life,boolean hostile){
            this.x=x;this.y=y;this.vx=vx;this.vy=vy;
            this.life=life;this.hostile=hostile;
        }
    }
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
        try{characterSkinsV109=new CharacterSkinsV109(activity);}catch(Exception v109Error){
            android.util.Log.e("SP-V109","Source-locked character pack failed to load",v109Error);
            characterSkinsV109=null; // legacy renderer only if source fails validation
        }
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
        loadApprovedGearV93();
        initCovers();reloadSettings();hasSave=host.prefs.getBoolean("hasSave",false);
        if(industrialModeV123||stitchedIndustrialV128)
            industrialArtV123.load(host.getAssets());
    }
    void initCovers(){
        // Four formerly solid cover buildings have real enterable POI exteriors
        // now; do not leave a second invisible collision hull at those spots.
        covers.add(new Cover(1300,850,95,37,1));
        covers.add(new Cover(1920,1020,110,48,1));
        covers.add(new Cover(2100,710,120,36,1));
        covers.add(new Cover(650,1160,100,38,1));
        covers.add(new Cover(1360,1570,110,40,1));
        covers.add(new Cover(2520,1760,110,40,1));
        // The ten fixed facilities are physical solid buildings; loot is
        // reachable from the cache parked outside each entrance.
        for(ExpeditionSitesV88.Site s:ExpeditionSitesV88.SITES){
            if(s.kind==ExpeditionSitesV88.CLINIC)
                covers.add(new Cover(s.x-175,s.y-140,350,255,4));
            else covers.add(new Cover(s.x-68,s.y-56,136,120,4));
        }
    }
    /** Load one independent indoor instance. V90 clinic saves are migrated unchanged. */
    String currentSiteNameV91(){
        if(activeSiteV91==INDUSTRIAL_SITE_V123)
            return industrialSiteV123.name;
        if(activeSiteV91>=0&&activeSiteV91<ExpeditionSitesV88.SITES.length)
            return ExpeditionSitesV88.SITES[activeSiteV91].name;
        return activeSiteV91>=ExpeditionSitesV88.SITES.length?"FIELD SHELTER":"FIELD CLINIC";
    }
    void configureInteriorV91(int site){
        if((industrialModeV123||stitchedIndustrialV128)&&
                site==INDUSTRIAL_SITE_V123){
            activeSiteV91=site;
            clinicInteriorV89=new IndustrialInteriorV123(industrialSiteV123);
            clinicActorsV90=new ClinicActorsV90(clinicInteriorV89);
            clinicNavV90=new ClinicNavV90(clinicInteriorV89);
            String key=IndustrialWorldV123.saveNamespace(industrialSeedV123)+"_"+
                       industrialSiteV123.id.replace(',','_');
            clinicInteriorV89.decode(host.prefs.getString(key+"_loot",""));
            clinicActorsV90.decode(host.prefs.getString(key+"_actors",""),clinicInteriorV89);
            clinicFriendWaypointsV90.clear();return;
        }
        int builtIndex=site-ExpeditionSitesV88.SITES.length;
        boolean shelter=site>=ExpeditionSitesV88.SITES.length&&builtIndex>=0&&
            builtIndex<craftV83.objects.size()&&
            craftV83.objects.get(builtIndex).kind==CampCraftV83.FIELD_SHELTER;
        if(site<0||(site>=ExpeditionSitesV88.SITES.length&&!shelter))site=1;
        activeSiteV91=site;
        ExpeditionSitesV88.Site loc=site<ExpeditionSitesV88.SITES.length?
            ExpeditionSitesV88.SITES[site]:
            new ExpeditionSitesV88.Site(ExpeditionSitesV88.CABIN,
                craftV83.objects.get(site-ExpeditionSitesV88.SITES.length).x,
                craftV83.objects.get(site-ExpeditionSitesV88.SITES.length).y,
                "FIELD SHELTER",true);
        clinicInteriorV89=site==1?new ClinicInteriorV89():
            new ExpeditionInteriorV91(loc);
        clinicActorsV90=new ClinicActorsV90(clinicInteriorV89);
        clinicNavV90=new ClinicNavV90(clinicInteriorV89);
        String loot=host.prefs.getString("site_containers_v91_"+site,
            site==1?host.prefs.getString("clinic_containers_v89",""):"");
        String actors=host.prefs.getString("site_actors_v91_"+site,
            site==1?host.prefs.getString("clinic_actors_v90",""):"");
        clinicInteriorV89.decode(loot);
        clinicActorsV90.decode(actors,clinicInteriorV89);
        clinicFriendWaypointsV90.clear();
    }
    void persistCurrentInteriorV91(){
        if(activeSiteV91==INDUSTRIAL_SITE_V123){
            String key=IndustrialWorldV123.saveNamespace(industrialSeedV123)+"_"+
                       industrialSiteV123.id.replace(',','_');
            host.prefs.edit().putString(key+"_loot",clinicInteriorV89.encode())
                .putString(key+"_actors",clinicActorsV90.encode()).apply();
            return;
        }
        if(activeSiteV91<0||activeSiteV91>=ExpeditionSitesV88.SITES.length+
            CampCraftV83.MAX)return;
        android.content.SharedPreferences.Editor edit=host.prefs.edit()
            .putString("site_containers_v91_"+activeSiteV91,clinicInteriorV89.encode())
            .putString("site_actors_v91_"+activeSiteV91,clinicActorsV90.encode());
        if(activeSiteV91==1)edit.putString("clinic_containers_v89",clinicInteriorV89.encode())
            .putString("clinic_actors_v90",clinicActorsV90.encode());
        edit.apply();
    }
    /** Allow a gear-only case to be searched after ordinary supplies are depleted. */
    ClinicInteriorV89.Storage nearestAnyInteriorStorageV91(float x,float y,float reach){
        ClinicInteriorV89.Storage best=null;float min=reach*reach;
        for(int i=0;i<clinicInteriorV89.storages.length;i++){
            ClinicInteriorV89.Storage box=clinicInteriorV89.storages[i];
            if(box.empty()&&!gearLootV95.hasLoot(activeSiteV91,i,
                fieldFindsV91.searched(activeSiteV91,i)))continue;
            float dx=box.x-x,dy=box.y-y,dist=dx*dx+dy*dy;
            if(dist<min){min=dist;best=box;}
        }
        return best;
    }
    int storageIndexV91(ClinicInteriorV89.Storage s){
        for(int i=0;i<clinicInteriorV89.storages.length;i++)
            if(clinicInteriorV89.storages[i]==s)return i;
        return -1;
    }
    int remainingGearV95(ClinicInteriorV89.Storage box,int gearType){
        int id=storageIndexV91(box);
        return id<0?0:gearLootV95.available(activeSiteV91,id,gearType,
            fieldFindsV91.searched(activeSiteV91,id))?1:0;
    }
    int playerGearQuantityV95(int type){
        if(type<0||type>=GearLootV95.TYPES)return 0;
        if(type<3)return fieldFindsV91.bags[type];
        int slot=(type-3)/3,variant=(type-3)%3;
        return wardrobeV92.found[slot][variant];
    }
    int lootClinicGearV95(ClinicInteriorV89.Storage box,int type){
        if(!insideClinicV89||!playing||!clinicInteriorV89.contains(box)||
            distance(playerX,playerY,box.x,box.y)>ClinicInteriorV89.USE_RADIUS+12f)return 0;
        int id=storageIndexV91(box);
        if(!gearLootV95.transfer(activeSiteV91,id,type,
            fieldFindsV91.searched(activeSiteV91,id),fieldFindsV91,wardrobeV92))
            return 0;
        gatherFeedback="FOUND "+GearLootV95.NAMES[type];
        gatherFeedbackTime=2f;saveProgress();invalidate();
        return 1;
    }
    int lootClinicAllGearV95(ClinicInteriorV89.Storage box){
        int taken=0;
        for(int type=0;type<GearLootV95.TYPES;type++)
            taken+=lootClinicGearV95(box,type);
        return taken;
    }
    String lootGearV91(ClinicInteriorV89.Storage box){
        int id=storageIndexV91(box);
        if(!insideClinicV89||!playing||id<0||
            distance(playerX,playerY,box.x,box.y)>ClinicInteriorV89.USE_RADIUS+12f)return "";
        String found=fieldFindsV91.scavenge(activeSiteV91,id);
        if(!found.isEmpty()){
            String clothing=wardrobeV92.scavenge(activeSiteV91,id);
            if(!clothing.isEmpty())found+=" • "+clothing;
            gatherFeedback="GEAR: "+found;gatherFeedbackTime=3.5f;
            saveProgress();invalidate();
        }
        return found;
    }
    float encumbranceV91(){
        float load=0f;
        for(int i=0;i<InventoryCatalogV131.COUNT;i++)
            load+=InventoryCatalogV131.weight(i)*inventoryQuantityV92(i);
        return Math.min(100f,Math.max(0f,(load-fieldFindsV91.capacity())*1.7f));
    }
    float carrySpeedV91(){return Math.max(.54f,1f-encumbranceV91()*.0046f);}
    boolean isPlaying(){return playing;}
    void reloadSettings(){
        scale=host.setting("scale",100)/100f;
        playerSkinV109=Math.max(1,Math.min(200,host.setting("playerSkinV109",124)));
        playerGunPivotXV117=WeaponPivotV117.clamp(host.setting("weaponPivotXV117",0));
        playerGunPivotYV117=WeaponPivotV117.clamp(host.setting("weaponPivotYV117",0));
        npcGunPivotXV117=WeaponPivotV117.clamp(host.setting("weaponPivotXV117NpcV113",0));
        npcGunPivotYV117=WeaponPivotV117.clamp(host.setting("weaponPivotYV117NpcV113",0));
        playerHeadSizeV113=CharacterScopeV113.percent(host.setting("headSizeV82",100),75,160);
        playerTorsoWidthV114=TorsoWidthV114.percent(host.setting("bodyWidthV114",100));
        npcTorsoWidthV114=TorsoWidthV114.percent(host.setting("bodyWidthV114NpcV113",100));
        playerPelvisWidthV115=PelvisWidthV115.percent(host.setting("pelvisWidthV115",100));
        npcPelvisWidthV115=PelvisWidthV115.percent(host.setting("pelvisWidthV115NpcV113",100));
        npcHeadSizeV113=CharacterScopeV113.percent(host.setting("headSizeV82NpcV113",100),75,160);
        npcHeadFitXV113=HeadFitOffsetsV112.clampOffset(host.setting("fitHeadXV108NpcV113",0));
        npcHeadFitYV113=HeadFitOffsetsV112.clampOffset(host.setting("fitHeadYV108NpcV113",0));
        npcBreathPixelsV113=CharacterScopeV113.percent(host.setting("fitIdleBreathV108NpcV113",4),0,12);
        npcWalkFpsV113=CharacterScopeV113.percent(host.setting("fitWalkFpsV108NpcV113",0),0,12);
        npcHeadAimMaxDegreesV113=HeadAimV111.limit(host.setting("headAimTiltV111NpcV113",10));
        npcBreathingTempoV113=CharacterAnimationV110.breathingMultiplier(host.setting("idleBreathingSpeedV110NpcV113",100));
        npcWalkingAnimationTempoV113=WalkingAnimationV79.multiplier(host.setting("walkingAnimationSpeedV79NpcV113",100));
        headAimMaxDegreesV111=HeadAimV111.limit(
            host.setting("headAimTiltV111",HeadAimV111.DEFAULT_MAX_DEGREES));
        headScaleV82=HeadKnifeV82.headMultiplier(host.setting("headSizeV82",HeadKnifeV82.HEAD_DEFAULT));
        fitHeadXV108=CharacterFitV108.headX(host.prefs);
        fitHeadYV108=CharacterFitV108.headY(host.prefs);
        fitIdleBreathV108=CharacterFitV108.breathPixels(host.prefs);
        idleBreathingTempoV110=CharacterAnimationV110.breathingMultiplier(
            host.setting("idleBreathingSpeedV110",CharacterAnimationV110.BREATH_DEFAULT_PERCENT));
        fitWalkFpsV108=CharacterFitV108.walkFps(host.prefs);
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
        panelScale=host.setting("hudPanelSize",120)/100f;
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
        followSpacing=CompanionOrdersV118.spacing(host.setting("followSpacing",125));
        companionStayV118=host.option("companionStayV118",false);
        companionHoldFireV118=host.option("companionHoldFireV118",false);
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
    int equippedReserveV131(int type){
        int slot=InventoryCatalogV131.equipmentSlot(type);
        if(slot<0)return 0;
        if(slot==5)return fieldFindsV91.equipped==type-24?1:0;
        if(slot==0||slot==2||slot==3||slot==4){
            int clothing=slot==0?0:slot==2?1:slot==3?2:3;
            return wardrobeV92.equipped[clothing]==(type-27)%3?1:0;
        }
        return 0;
    }
    /** Inventory totals include worn gear, bag quantities intentionally exclude it. */
    int availableInventoryV131(int type){
        return type<0||type>=InventoryCatalogV131.COUNT?0:
            Math.max(0,inventoryQuantityV92(type)-equippedReserveV131(type));
    }
    boolean equipInventoryItemV131(int type,int targetSlot){
        if(!InventoryCatalogV131.compatible(type,targetSlot)||
           availableInventoryV131(type)<1)return false;
        boolean done=targetSlot==5?fieldFindsV91.equip(type-24):
            wardrobeV92.equip(targetSlot==0?0:targetSlot==2?1:
                targetSlot==3?2:3,(type-27)%3);
        if(done){organizeBagV131(0);saveProgress();invalidate();}
        return done;
    }
    boolean unequipInventorySlotV131(int slot){
        if(slot==5){fieldFindsV91.unequip();}
        else if(slot==0||slot==2||slot==3||slot==4){
            int clothing=slot==0?0:slot==2?1:slot==3?2:3;
            wardrobeV92.equip(clothing,-1);
        }else return false;
        organizeBagV131(0);saveProgress();invalidate();return true;
    }
    /** Sort never alters the underlying quantities. Split portions move as a unit. */
    void organizeBagV131(int mode){
        reconcileBagSplitsV130();
        Integer[] places=new Integer[40];
        int[] count=new int[40],firstIndex=new int[40];
        java.util.Arrays.fill(firstIndex,40);
        for(int i=0;i<40;i++){
            places[i]=i;count[i]=bagSlotQuantityV130(i);
            if(count[i]>0)
                firstIndex[bagOrderV92[i]]=Math.min(firstIndex[bagOrderV92[i]],i);
        }
        java.util.Arrays.sort(places,(a,b)->{
            if((count[a]>0)!=(count[b]>0))return count[a]>0?-1:1;
            if(count[a]==0)return Integer.compare(a,b);
            int t=bagOrderV92[a],u=bagOrderV92[b];
            int cmp=mode==0?
                Integer.compare(firstIndex[t],firstIndex[u]):
                InventoryCatalogV131.compare(t,u,mode,INVENTORY_NAMES_V92);
            return cmp!=0?cmp:Integer.compare(a,b);
        });
        int[] order=new int[40],splits=new int[40],originals=new int[40];
        for(int i=0;i<40;i++){
            int j=places[i];order[i]=bagOrderV92[j];
            splits[i]=bagSplitAmountV130[j];
            originals[i]=bagSplitOriginalV130[j];
        }
        System.arraycopy(order,0,bagOrderV92,0,40);
        System.arraycopy(splits,0,bagSplitAmountV130,0,40);
        System.arraycopy(originals,0,bagSplitOriginalV130,0,40);
        saveProgress();
    }
    float itemMassV131(int kind){return InventoryCatalogV131.weight(kind);}
    int inventoryQuantityV92(int idx){
        switch(idx){
            case 0:return scrap;case 1:return medkits;case 2:return ammoPacks;
            case 3:return foodCount;case 4:return waterCount;case 5:return wood;
            case 6:return stone;case 7:return fiber;
            case 8:case 9:case 10:case 11:return craftV83.stock[idx-8];
            case 12:return bandagesV88;case 13:return energyV88;
            default:
                if(idx>=14&&idx<24)return fieldFindsV91.items[idx-14];
                if(idx>=24&&idx<39)return playerGearQuantityV95(idx-24);
                return 0;
        }
    }

    String droppedSceneV129(){
        if(!insideClinicV89)return "world";
        if(activeSiteV91==INDUSTRIAL_SITE_V123)
            return "industrial:"+industrialSeedV123+":"+industrialSiteV123.sx+
                ":"+industrialSiteV123.sy;
        return "site:"+activeSiteV91;
    }
    float gameTimeV129(){return DroppedItemsV129.time(clock.day(),clock.minute());}
    boolean changeInventoryV129(int idx,int delta){
        if(idx<0||idx>=39||delta==0)return false;
        int current=inventoryQuantityV92(idx);
        int equippedReserved=equippedReserveV131(idx);
        if(delta<0&&current+delta<equippedReserved)return false;
        long next=(long)current+delta;
        if(next<0||next>(idx>=24?99:9999))return false;
        int value=(int)next;
        switch(idx){
            case 0:scrap=value;break;case 1:medkits=value;break;
            case 2:ammoPacks=value;break;case 3:foodCount=value;break;
            case 4:waterCount=value;break;case 5:wood=value;break;
            case 6:stone=value;break;case 7:fiber=value;break;
            case 8:case 9:case 10:case 11:craftV83.stock[idx-8]=value;break;
            case 12:bandagesV88=value;break;case 13:energyV88=value;break;
            default:
                if(idx>=14&&idx<24){fieldFindsV91.items[idx-14]=value;break;}
                int gear=idx-24;
                if(gear<0||gear>=GearLootV95.TYPES)return false;
                if(gear<3){
                    fieldFindsV91.bags[gear]=value;
                    if(value==0&&fieldFindsV91.equipped==gear)
                        fieldFindsV91.unequip();
                }else{
                    int slot=(gear-3)/3,style=(gear-3)%3;
                    wardrobeV92.found[slot][style]=value;
                    if(value==0&&wardrobeV92.equipped[slot]==style)
                        wardrobeV92.equip(slot,-1);
                }
        }
        return true;
    }
    /** Save stack before changing the inventory, so failed placement loses nothing. */
    boolean dropInventoryV129(int kind,int quantity){
        if(!playing||gameOver||kind<0||kind>=39||quantity<=0||
           availableInventoryV131(kind)<quantity)return false;
        float x=playerX+aimX*44f,y=playerY+aimY*44f;
        if(insideClinicV89){
            if(clinicInteriorV89.blocked(x,y,16f)){x=playerX;y=playerY;}
        }else if(blocked(x,y,16f)){x=playerX;y=playerY;}
        DroppedItemsV129.Stack stack=droppedItemsV129.drop(kind,quantity,x,y,
            droppedSceneV129(),gameTimeV129(),host.setting("groundDropDaysV129",2));
        if(stack==null)return false;
        if(!changeInventoryV129(kind,-quantity)){
            droppedItemsV129.take(stack);return false;
        }
        gatherFeedback="DROPPED "+INVENTORY_NAMES_V92[kind]+" ×"+quantity;
        gatherFeedbackTime=2.2f;saveProgress();invalidate();return true;
    }
    DroppedItemsV129.Stack nearbyDroppedV129(){
        if(!playing||gameOver)return null;
        return droppedItemsV129.nearest(playerX,playerY,
            droppedSceneV129(),DroppedItemsV129.USE_RADIUS);
    }
    boolean takeDroppedV129(DroppedItemsV129.Stack stack){
        if(stack==null||!droppedItemsV129.contains(stack)||
           !stack.scene.equals(droppedSceneV129())||
           distance(playerX,playerY,stack.x,stack.y)>DroppedItemsV129.USE_RADIUS+8f)
            return false;
        if(!changeInventoryV129(stack.type,stack.quantity))return false;
        droppedItemsV129.take(stack);
        gatherFeedback="RECOVERED "+INVENTORY_NAMES_V92[stack.type]+" ×"+stack.quantity;
        gatherFeedbackTime=2f;saveProgress();invalidate();return true;
    }
    void drawDroppedItemsV129(Canvas c){
        String scene=droppedSceneV129();
        if(insideClinicV89){c.save();c.clipPath(clinicVisionPathV90);}
        for(DroppedItemsV129.Stack stack:droppedItemsV129.stacks){
            if(!scene.equals(stack.scene)||!WorldPerfV55.nearView(
                    stack.x,stack.y,camX,camY,viewW,viewH,50f))continue;
            float x=stack.x,y=stack.y;
            color(0x8c151e1d);c.drawOval(x-26,y-8,x+26,y+9,p);
            rect(c,x-23,y-19,46,22,0xff283a39);
            rect(c,x-20,y-22,40,20,0xff796348);
            rect(c,x-16,y-18,32,12,0xffa28d63);
            rect(c,x-14,y-14,28,3,0xff453f35);
            rect(c,x+12,y-16,5,13,0xff243f3e);
            label(c,INVENTORY_NAMES_V92[stack.type]+" ×"+stack.quantity,
                x-24,y-31,10,0xffe2c58f,true);
        }
        if(insideClinicV89)c.restore();
    }
    static final String[] INVENTORY_NAMES_V92={"SCRAP","MEDKIT","AMMO",
        "FOOD","WATER","WOOD","STONE","FIBER","BARRICADE","LIGHT POST",
        "WATER COLLECTOR","FIELD SHELTER","BANDAGE","ENERGY RATION",
        "CLOTH","BATTERY","WIRING","ANTISEPTIC","FUEL","WATER FILTER",
        "SEEDS","TOOLKIT","ROPE","SPARE PARTS",
        "DAYPACK","HIKING PACK","TACTICAL PACK",
        "CANVAS CAP","SUN-BRIM FIELD HAT","BALLISTIC HELMET",
        "CANVAS WORK JACKET","WEATHERPROOF FIELD COAT","PLATE CARRIER VEST",
        "UTILITY CARGO TROUSERS","RIPSTOP FIELD TROUSERS","REINFORCED TACTICAL PANTS",
        "STEEL-TOE WORK BOOTS","LEATHER TRAIL BOOTS","TACTICAL COMBAT BOOTS","EMPTY"};
    // Stack-aware bag extension. The underlying totals remain the original
    // save counters; reserved portions are separate draggable inventory stacks.
    final int[] bagSplitAmountV130=new int[40];
    final int[] bagSplitOriginalV130=new int[40];
    int bagSlotQuantityV130(int position){
        if(position<0||position>=40)return 0;
        int kind=bagOrderV92[position];
        if(kind<0||kind>=39)return 0;
        int total=availableInventoryV131(kind);
        if(bagSplitAmountV130[position]>0)
            return Math.min(total,bagSplitAmountV130[position]);
        int reserved=0;
        for(int i=0;i<40;i++)
            if(i!=position&&bagOrderV92[i]==kind&&bagSplitAmountV130[i]>0)
                reserved+=bagSplitAmountV130[i];
        return Math.max(0,total-reserved);
    }
    void clearBagSplitsV130(){
        java.util.Arrays.fill(bagSplitAmountV130,0);
        java.util.Arrays.fill(bagSplitOriginalV130,-1);
    }
    void reconcileBagSplitsV130(){
        for(int position=0;position<40;position++){
            if(bagSplitAmountV130[position]<=0)continue;
            int kind=bagOrderV92[position];
            int original=bagSplitOriginalV130[position];
            if(kind<0||kind>=39||original<0||original>=40){
                bagSplitAmountV130[position]=0;continue;
            }
            // A newly obtained item takes priority over a placeholder slot.
            if(availableInventoryV131(original)>0){
                bagOrderV92[position]=original;
                bagSplitAmountV130[position]=0;
                bagSplitOriginalV130[position]=-1;continue;
            }
            int total=availableInventoryV131(kind),reserved=0;
            for(int i=0;i<position;i++)
                if(bagOrderV92[i]==kind)reserved+=bagSplitAmountV130[i];
            bagSplitAmountV130[position]=Math.max(0,
                Math.min(bagSplitAmountV130[position],total-reserved));
            if(bagSplitAmountV130[position]==0){
                bagOrderV92[position]=original;
                bagSplitOriginalV130[position]=-1;
            }
        }
    }
    boolean splitBagSlotV130(int source,int quantity){
        reconcileBagSplitsV130();
        if(source<0||source>=40||quantity<1||
           quantity>=bagSlotQuantityV130(source))return false;
        int target=-1;
        for(int i=39;i>=0;i--){
            if(i==source||bagSplitAmountV130[i]>0)continue;
            if(availableInventoryV131(bagOrderV92[i])==0){
                target=i;break;
            }
        }
        if(target<0)return false;
        int kind=bagOrderV92[source],displaced=bagOrderV92[target];
        bagOrderV92[target]=kind;
        bagSplitAmountV130[target]=quantity;
        bagSplitOriginalV130[target]=displaced;
        if(bagSplitAmountV130[source]>0)bagSplitAmountV130[source]-=quantity;
        saveProgress();invalidate();return true;
    }
    boolean dropBagSlotV130(int position,int quantity){
        reconcileBagSplitsV130();
        if(position<0||position>=40||quantity<1||
           quantity>bagSlotQuantityV130(position))return false;
        int type=bagOrderV92[position];
        if(!dropInventoryV129(type,quantity))return false;
        if(bagSplitAmountV130[position]>0)
            bagSplitAmountV130[position]-=quantity;
        reconcileBagSplitsV130();saveProgress();return true;
    }
    String encodeBagSplitsV130(){
        StringBuilder sb=new StringBuilder();
        for(int i=0;i<40;i++){
            if(i>0)sb.append(',');
            sb.append(bagOrderV92[i]).append(':')
                .append(bagSplitAmountV130[i]).append(':')
                .append(bagSplitOriginalV130[i]);
        }
        return sb.toString();
    }
    void restoreBagSplitsV130(String raw){
        clearBagSplitsV130();
        if(raw==null||raw.isEmpty())return;
        String[] fields=raw.split(",",-1);
        if(fields.length!=40)return;
        int[] order=new int[40],pieces=new int[40],originals=new int[40];
        try{
            for(int i=0;i<40;i++){
                String[] parts=fields[i].split(":",-1);
                if(parts.length!=3)return;
                order[i]=Integer.parseInt(parts[0]);
                pieces[i]=Integer.parseInt(parts[1]);
                originals[i]=Integer.parseInt(parts[2]);
                if(order[i]<0||order[i]>=40||pieces[i]<0||pieces[i]>9999||
                   originals[i]<-1||originals[i]>=40)return;
                if((pieces[i]>0)!=(originals[i]>=0))return;
            }
            System.arraycopy(order,0,bagOrderV92,0,40);
            System.arraycopy(pieces,0,bagSplitAmountV130,0,40);
            System.arraycopy(originals,0,bagSplitOriginalV130,0,40);
            reconcileBagSplitsV130();
        }catch(NumberFormatException ignored){clearBagSplitsV130();}
    }
    void initInventoryOrderV92(){
        clearBagSplitsV130();
        int count=0;
        for(int i=0;i<bagOrderV92.length;i++)
            if(availableInventoryV131(i)>0)bagOrderV92[count++]=i;
        for(int i=0;i<bagOrderV92.length;i++)
            if(availableInventoryV131(i)==0)bagOrderV92[count++]=i;
        bagOrderInitializedV92=true;
    }
    void restoreBagOrderV92(String raw){
        initInventoryOrderV92();
        if(raw==null||raw.isEmpty())return;
        String[] fields=raw.split(",");
        // Preserve V92-V94 24-cell player order, append 15 new gear stacks.
        if(fields.length!=24&&fields.length!=40)return;
        int[] restored=new int[40];boolean[] seen=new boolean[40];
        int index=0;
        try{
            for(String value:fields){
                int n=Integer.parseInt(value);
                if(n<0||n>=40||seen[n])return;
                restored[index++]=n;seen[n]=true;
            }
            for(int i=0;i<40;i++)if(!seen[i])restored[index++]=i;
            System.arraycopy(restored,0,bagOrderV92,0,40);
        }catch(NumberFormatException ignored){}
    }
    String encodeBagOrderV92(){
        StringBuilder b=new StringBuilder();
        for(int i=0;i<bagOrderV92.length;i++){
            if(i>0)b.append(',');
            b.append(bagOrderV92[i]);
        }
        return b.toString();
    }
    boolean moveBagSlotV92(int source,int dest){
        if(source<0||dest<0||source>=bagOrderV92.length||dest>=bagOrderV92.length||source==dest)return false;
        int type=bagOrderV92[source];
        int split=bagSplitAmountV130[source],original=bagSplitOriginalV130[source];
        int from=Math.min(source,dest)+(source<dest?1:0);
        int to=Math.min(source,dest)+(source<dest?0:1);
        int length=Math.abs(source-dest);
        System.arraycopy(bagOrderV92,from,bagOrderV92,to,length);
        System.arraycopy(bagSplitAmountV130,from,bagSplitAmountV130,to,length);
        System.arraycopy(bagSplitOriginalV130,from,bagSplitOriginalV130,to,length);
        bagOrderV92[dest]=type;
        bagSplitAmountV130[dest]=split;bagSplitOriginalV130[dest]=original;
        saveProgress();return true;
    }
    void newGame(){
        industrialSeedV123=host.prefs.getInt(IndustrialWorldV123.SEED_PREF,14901);
        industrialSiteV123=IndustrialWorldV123.district(0,0,industrialSeedV123);
        industrialYardV123.clear();
        playerX=industrialModeV123?industrialSiteV123.doorX:CAMP_X;
        playerY=industrialModeV123?industrialSiteV123.doorY+112f:CAMP_Y;health=100;stamina=100;
        hunger=100;thirst=100;fatigue=0;foodCount=2;waterCount=2;
        knifeDuration=0;knifeCooldown=0;
        cameraLookX=0;cameraLookY=0;aimDeflection=0;
        cursorInitialized=false;cursorMoveX=0;cursorMoveY=0;
        playerAnimation.reset();moving=false;stickX=0;stickY=0;shotClock=0;
        gun=Math.max(0,Math.min(11,host.setting("gun",0)));ammo=MAG[gun];
        kills=0;wave=1;scrap=0;medkits=1;ammoPacks=2;
        wood=0;stone=0;fiber=0;bandagesV88=0;energyV88=0;harvestWorld.clear();salvageWorldV84.clear();groundPickupsV85.clear();
        placingKindV84=-1;placingPointerV84=-1;harvestV81.cancel();
        harvestImpactTimeV81=0;gatherFeedback="";gatherFeedbackTime=0;
        worldTimer=0;autSaveClock=0;playerHeadTiltV111=0f;
        clock.setClock(industrialModeV123?12*60f:(night?21*60f:12*60f),1);
        face=1;aimX=1;aimY=0;refreshDaylight();
        enemies.clear();friends.clear();campStaff.clear();shots.clear();drops.clear();sparks.clear();flashes.clear();indoorRoundsV122.clear();builtCampfires.clear();
        craftV83.clear();banditLootV87.clear();removeBarricadeCoverV83();
        droppedItemsV129.clear();
        sitesInitializedV88=false;stationUsedV88.clear();
        clinicInteriorV89=new ClinicInteriorV89();
        clinicActorsV90=new ClinicActorsV90(clinicInteriorV89);
        clinicNavV90=new ClinicNavV90(clinicInteriorV89);
        insideClinicV89=false;activeSiteV91=-1;fieldFindsV91.clear();
        wardrobeV92.clear();gearLootV95.clear();relationshipsV92.decode("");
        backpackStyleV96=0;headgearStyleV96=0;
        // Starting clothes are modular overlays, never edits to the locked
        // original character frames. Additional sets are found inside cases.
        for(int slot=1;slot<4;slot++){
            wardrobeV92.found[slot][0]=1;
            wardrobeV92.equip(slot,0);
        }
        bagOrderInitializedV92=false;campGuardCooldownV92=0f;
        android.content.SharedPreferences.Editor sitesClear=host.prefs.edit();
        for(int i=0;i<ExpeditionSitesV88.SITES.length+CampCraftV83.MAX;i++)
            {sitesClear.remove("site_containers_v91_"+i)
                .remove("site_actors_v91_"+i)
                .remove("indoor_corpse_v129_site:"+i);}
        // Fresh world of this seed: clear ALL industrial sites. The V127
        // isolated test's persistent per-facility and per-seed keys are reused.
        String industryPrefix=IndustrialWorldV123.saveNamespace(industrialSeedV123)+"_";
        for(int sy=IndustrialBiomeBridgeV128.INDUSTRIAL_MIN_SY;
                sy<IndustrialBiomeBridgeV128.INDUSTRIAL_MAX_SY;sy++)
            for(int sx=IndustrialBiomeBridgeV128.INDUSTRIAL_MIN_SX;
                    sx<IndustrialBiomeBridgeV128.INDUSTRIAL_MAX_SX;sx++){
                String key=industryPrefix+sx+"_"+sy;
                sitesClear.remove(key+"_loot").remove(key+"_actors")
                    .remove("indoor_corpse_v129_industrial:"+industrialSeedV123+
                        ":"+sx+":"+sy);
            }
        sitesClear.remove("industrial_yard_v123_"+industrialSeedV123);
        sitesClear.apply();
        clinicActorsV90.reset(clinicInteriorV89);
        outdoorCompanionPositionsV90.clear();
        clinicFriendWaypointsV90.clear();
        indoorShotCooldownV90=0f;indoorCompanionNavClockV90=0f;
        outsideDoorXv89=0f;outsideDoorYv89=0f;
        seedExpeditionCachesV88();
        initInventoryOrderV92();
        initCampStaff();
        playing=true;paused=false;settingsPause=false;gameOver=false;
        adjustFriends();spawnWave();
        saveProgress();invalidate();
    }
    void continueGame(){
        if(!hasSave){newGame();return;}
        industrialSeedV123=host.prefs.getInt(IndustrialWorldV123.SEED_PREF,14901);
        industrialSiteV123=IndustrialWorldV123.district(
            host.prefs.getInt("industrial_sx_v123",0),
            host.prefs.getInt("industrial_sy_v123",0),industrialSeedV123);
        industrialYardV123.decode(host.prefs.getString("industrial_yard_v123_"+industrialSeedV123,""));
        playerAnimation.reset();moving=false;stickX=0;stickY=0;
        clock.setClock(host.prefs.getFloat("clockMinutes",night?21*60f:12*60f),
            host.setting("clockDay",1));
        aimX=host.prefs.getFloat("aimX",1f);aimY=host.prefs.getFloat("aimY",0f);
        float lengthAim=(float)Math.hypot(aimX,aimY);
        if(lengthAim<.01f){aimX=1;aimY=0;}else{aimX/=lengthAim;aimY/=lengthAim;}
        face=aimX<-.025f?-1:1;
        refreshDaylight();
        playerX=host.prefs.getFloat("px",1000);playerY=host.prefs.getFloat("py",1060);
        // A save imported from the isolated V123-V127 test has local
        // industrial coordinates; general-world saves remain world-native.
        boolean importedIndustrialV128=stitchedIndustrialV128&&
            host.prefs.contains("industrial_sx_v123")&&
            !host.prefs.getBoolean("v128_world_coords",false);
        if(importedIndustrialV128&&!host.prefs.getBoolean("inside_clinic_v89",false)){
            playerX=IndustrialBiomeBridgeV128.worldX(playerX);
            playerY=IndustrialBiomeBridgeV128.worldY(playerY);
        }
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
        bandagesV88=host.setting("bandagesV88",0);energyV88=host.setting("energyV88",0);
        harvestWorld.decode(host.prefs.getString("depleted_resources_v80",""));
        harvestV81.cancel();harvestImpactTimeV81=0f;
        gatherFeedback="";gatherFeedbackTime=0;
        gun=Math.max(0,Math.min(11,host.setting("gun",0)));
        ammo=Math.max(0,Math.min(MAG[gun],host.setting("ammo",MAG[gun])));
        enemies.clear();friends.clear();shots.clear();drops.clear();sparks.clear();flashes.clear();indoorRoundsV122.clear();
        restoreCampfires();
        craftV83.decode(host.prefs.getString("camp_buildings_v83",""));
        craftV83.decodeStock(host.prefs.getString("camp_stock_v84",""));
        salvageWorldV84.decode(host.prefs.getString("salvaged_scrap_v84",""));
        groundPickupsV85.decode(host.prefs.getString("loose_pickups_v85",""));
        banditLootV87.decode(host.prefs.getString("bandit_loot_bags_v87",""));
        droppedItemsV129.decode(host.prefs.getString("ground_drops_v129",""));
        droppedItemsV129.expire(gameTimeV129());
        sitesInitializedV88=host.prefs.getBoolean("sitesInitializedV88",false);
        if(!sitesInitializedV88)seedExpeditionCachesV88();
        decodeFacilityCooldownV88(host.prefs.getString("facilityCooldownV88",""));
        fieldFindsV91.decode(host.prefs.getString("field_finds_v91",""));
        wardrobeV92.decode(host.prefs.getString("wardrobe_v92",""));
        backpackStyleV96=Math.floorMod(host.prefs.getInt("backpackStyleV96",0),20);
        headgearStyleV96=Math.floorMod(host.prefs.getInt("headgearStyleV96",0),4);
        gearLootV95.decode(host.prefs.getString("gear_loot_v95",""));
        relationshipsV92.decode(host.prefs.getString("npc_relations_v92",""));
        restoreBagOrderV92(host.prefs.getString("bag_order_v92",""));
        restoreBagSplitsV130(host.prefs.getString("bag_splits_v130",""));
        insideClinicV89=host.prefs.getBoolean("inside_clinic_v89",false);
        int savedSiteV91=host.prefs.getInt("active_site_v91",1);
        if(insideClinicV89)configureInteriorV91(savedSiteV91);
        else {
            activeSiteV91=-1;
            clinicInteriorV89=new ClinicInteriorV89();
            clinicActorsV90=new ClinicActorsV90(clinicInteriorV89);
            clinicNavV90=new ClinicNavV90(clinicInteriorV89);
        }
        // V89 indoor saves used a 1600x1120 world. Migrate position once.
        if(insideClinicV89&&!host.prefs.getBoolean("clinic_scaled_v90",false)){
            playerX*=ClinicInteriorV89.EXPANSION_V90;
            playerY*=ClinicInteriorV89.EXPANSION_V90;
        }
        outsideDoorXv89=host.prefs.getFloat("clinic_return_x_v89",
            ExpeditionSitesV88.SITES[1].x);
        outsideDoorYv89=host.prefs.getFloat("clinic_return_y_v89",
            ExpeditionSitesV88.SITES[1].y+165f);
        if(importedIndustrialV128){
            outsideDoorXv89=IndustrialBiomeBridgeV128.worldX(outsideDoorXv89);
            outsideDoorYv89=IndustrialBiomeBridgeV128.worldY(outsideDoorYv89);
        }
        if(!insideClinicV89&&blocked(playerX,playerY,21f)){
            float[] safe=WorldSafetyV92.resolveExit(this::blocked,playerX,playerY);
            playerX=safe[0];playerY=safe[1];
        }
        if(insideClinicV89){
            playerX=clamp(playerX,40,ClinicInteriorV89.WIDTH-40);
            playerY=clamp(playerY,45,ClinicInteriorV89.HEIGHT-40);
            if(clinicInteriorV89.blocked(playerX,playerY,19f)){
                playerX=ClinicInteriorV89.ENTRANCE_X;
                playerY=ClinicInteriorV89.ENTRANCE_Y;
            }
        }
        placingKindV84=-1;placingPointerV84=-1;
        removeBarricadeCoverV83();restoreBarricadeCoverV83();
        campStaff.clear();initCampStaff();
        playing=true;paused=false;gameOver=false;
        // Companion spawn anchors stay outdoors even if Continue loads indoors.
        if(insideClinicV89){
            float localX=playerX,localY=playerY;
            playerX=outsideDoorXv89;playerY=outsideDoorYv89;
            adjustFriends();
            playerX=localX;playerY=localY;
            bringFriendsInsideV90();
            enemies.clear();
        }else{
            adjustFriends();spawnWave();
        }
        invalidate();
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
    /** Two utility recipes produce usable inventory items, not instant effects. */
    boolean craftConsumableV88(int type){
        if(!playing||gameOver)return false;
        if(type==0){
            if(fiber<2||scrap<1||bandagesV88>=99)return false;
            fiber-=2;scrap-=1;bandagesV88++;
            gatherFeedback="CRAFTED BANDAGE";
        }else if(type==1){
            if(foodCount<1||waterCount<1||energyV88>=99)return false;
            foodCount--;waterCount--;energyV88++;
            gatherFeedback="CRAFTED ENERGY RATION";
        }else return false;
        gatherFeedbackTime=2f;saveProgress();invalidate();return true;
    }
    static String craftNameV88(int kind){
        switch(kind){
            case CampCraftV83.BARRICADE:return "BARRICADE";
            case CampCraftV83.LIGHT_POST:return "LIGHT POST";
            case CampCraftV83.WATER_COLLECTOR:return "RAIN COLLECTOR";
            case CampCraftV83.FIELD_SHELTER:return "FIELD SHELTER";
            default:return "UNKNOWN";
        }
    }
    long facilityKeyV88(float x,float y){
        return (((long)Math.round(x))<<32)|((long)Math.round(y)&0xffffffffL);
    }
    String encodeFacilityCooldownV88(){
        StringBuilder sb=new StringBuilder();
        for(java.util.Map.Entry<Long,Float> e:stationUsedV88.entrySet()){
            if(sb.length()>0)sb.append(';');
            sb.append(e.getKey()).append(',').append(e.getValue());
        }
        return sb.toString();
    }
    void decodeFacilityCooldownV88(String raw){
        stationUsedV88.clear();if(raw==null||raw.isEmpty())return;
        for(String token:raw.split(";")){
            String[] part=token.split(",");if(part.length!=2)continue;
            try{
                long k=Long.parseLong(part[0]);float time=Float.parseFloat(part[1]);
                if(Float.isFinite(time)&&time>=0&&time<2000000000f)
                    stationUsedV88.put(k,time);
            }catch(NumberFormatException ignored){}
        }
    }
    /** Return true when USE interacts with a utility instead of harvesting. */
    boolean useFacilityV88(){
        for(CampCraftV83.Structure s:craftV83.objects){
            if(s.kind!=CampCraftV83.WATER_COLLECTOR&&
               s.kind!=CampCraftV83.FIELD_SHELTER)continue;
            if(distance(playerX,playerY,s.x,s.y)>135f)continue;
            float now=clock.day()*1440f+clock.minute();
            long k=facilityKeyV88(s.x,s.y);
            float last=stationUsedV88.containsKey(k)?stationUsedV88.get(k):-10000f;
            float required=s.kind==CampCraftV83.WATER_COLLECTOR?360f:180f;
            if(now-last<required){
                gatherFeedback="STATION RECOVERING";gatherFeedbackTime=1.8f;
                return true;
            }
            stationUsedV88.put(k,now);
            if(s.kind==CampCraftV83.WATER_COLLECTOR){
                waterCount+=2;gatherFeedback="COLLECTED WATER +2";
            }else{
                stamina=100f;fatigue=Math.max(0,fatigue-30f);
                gatherFeedback="RESTED • STAMINA RECOVERED";
            }
            gatherFeedbackTime=2.5f;saveProgress();return true;
        }
        return false;
    }
    /** Crafting yields a storable backpack item; no immediate construction. */
    boolean craftIntoBagV84(int kind){
        if(!playing||gameOver){craftV83.error="Start a game first";return false;}
        int[] resources={wood,stone,fiber,scrap};
        if(!craftV83.craftToBag(kind,resources))return false;
        wood=resources[0];stone=resources[1];fiber=resources[2];scrap=resources[3];
        gatherFeedback="CRAFTED "+craftNameV88(kind)+" (BAG)";
        gatherFeedbackTime=2.2f;saveProgress();invalidate();return true;
    }
    boolean selectPlaceItemV84(int kind){
        if(!playing||gameOver||insideClinicV89||kind<0||
            kind>=CampCraftV83.COST.length||craftV83.stock[kind]<1){
            craftV83.error="No crafted item in backpack";return false;
        }
        placingKindV84=kind;placingPointerV84=-1;
        updatePlacementTargetV86();
        invalidate();return true;
    }
    void cancelPlaceV84(){placingKindV84=-1;placingPointerV84=-1;}
    /** Placement consumes one finished item only when valid. */
    boolean placeAtV84(float x,float y){
        if(placingKindV84<0||!playing||paused||editControls||insideClinicV89)return false;
        updatePlacementTargetV86();
        x=placingXv84;y=placingYv84;
        if(distance(x,y,playerX,playerY)>420f){
            craftV83.error="Move closer to build";return false;
        }
        if(blocked(x,y,48f)){craftV83.error="Clear ground needed";return false;}
        for(float[] f:activeCampfiresV125())if(distance(x,y,f[0],f[1])<115f){
            craftV83.error="Too close to campfire";return false;
        }
        for(float[] f:builtCampfires)if(distance(x,y,f[0],f[1])<115f){
            craftV83.error="Too close to campfire";return false;
        }
        int kind=placingKindV84;
        if(!craftV83.placeFromBag(kind,x,y))return false;
        if(kind==CampCraftV83.BARRICADE)
            covers.add(new Cover(x-39,y-15,78,27,3));
        gatherFeedback=craftNameV88(kind)+" PLACED";
        gatherFeedbackTime=2.7f;cancelPlaceV84();saveProgress();invalidate();return true;
    }
    /** Legacy direct placement, not exposed by V84 UI. */
    boolean craftPlaceV83(int kind){
        if(!playing||gameOver){craftV83.error="Start a game first";return false;}
        if(harvestV81.active){craftV83.error="Finish harvesting first";return false;}
        float x=playerX+face*110f,y=playerY+28f;
        if(blocked(x,y,43)){craftV83.error="Find clear ground";return false;}
        for(float[] fire:activeCampfiresV125())if(distance(x,y,fire[0],fire[1])<110){
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
        }else if(node.kind==CampCraftV83.LIGHT_POST){
            rect(c,x-10,y-92,20,94,0xff16241f);
            rect(c,x-5,y-88,10,86,0xff786043);
            rect(c,x-21,y-99,42,12,0xff2a3f39);
            rect(c,x-17,y-95,34,6,0xff978356);
            rect(c,x-13,y-87,26,13,0xffd5ae69);
            rect(c,x-8,y-83,16,8,0xffffdf8f);
            rect(c,x-9,y-3,18,6,0xff394d40);
        }else if(node.kind==CampCraftV83.WATER_COLLECTOR){
            // Low covered rain / condensation barrel; interact with USE for water.
            rect(c,x-35,y-41,71,50,0xff17282a);
            rect(c,x-31,y-37,63,43,0xff477584);
            rect(c,x-37,y-44,75,12,0xff1a3031);
            rect(c,x-33,y-41,67,7,0xffa0b6a6);
            rect(c,x-19,y-29,41,6,0xff7eaba6);
            rect(c,x-26,y-15,54,5,0xff213d47);
            rect(c,x+26,y-24,8,20,0xff6e5140);
        }else{
            // Canvas field shelter with timber frame, narrow entrance.
            rect(c,x-66,y-35,132,45,0xff172625);
            rect(c,x-60,y-63,121,56,0xff435b46);
            rect(c,x-40,y-77,81,26,0xff688165);
            rect(c,x-21,y-43,42,49,0xff192a26);
            rect(c,x-16,y-40,32,42,0xff8b7957);
            rect(c,x-8,y-36,16,36,0xff25342b);
            rect(c,x-69,y+2,139,11,0xff675844);
            rect(c,x-64,y-36,9,44,0xffb49b6b);
            rect(c,x+55,y-36,9,44,0xffb49b6b);
            label(c,"ENTER",x-21,y+33,11,0xfff4ddac,true);
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
    float[][] activeCampfiresV125(){
        return industrialModeV123?IndustrialCampV125.FIRES:FIXED_CAMPFIRES;
    }
    void initCampStaff(){
        // Character sprite and role identities are unchanged from V122.
        if(industrialModeV123){
            int[] guns={3,3,3,2,3};
            int[] roles={ROLE_TRADER,ROLE_MEDIC+1,ROLE_MECHANIC,
                         ROLE_GUARD+1,ROLE_CIVILIAN};
            for(int i=0;i<roles.length;i++){
                float[] home=IndustrialCampV125.home(i,industrialSeedV123);
                campStaff.add(new Survivor(home[0],home[1],guns[i],roles[i]));
            }
            return;
        }
        campStaff.add(new Survivor(CAMP_X-175,CAMP_Y-75,3,ROLE_TRADER));
        campStaff.add(new Survivor(CAMP_X-126,CAMP_Y-78,3,ROLE_MEDIC+1));
        campStaff.add(new Survivor(CAMP_X+179,CAMP_Y-67,3,ROLE_MECHANIC));
        campStaff.add(new Survivor(CAMP_X+156,CAMP_Y+84,2,ROLE_GUARD+1));
        campStaff.add(new Survivor(CAMP_X-180,CAMP_Y+96,3,ROLE_CIVILIAN));
    }
    /** Seed ten permanent scavenging caches once per save, never again after looting. */
    void seedExpeditionCachesV88(){
        if(sitesInitializedV88)return;
        for(int i=0;i<ExpeditionSitesV88.SITES.length;i++){
            ExpeditionSitesV88.Site s=ExpeditionSitesV88.SITES[i];
            BanditLootV87.Bag bag=banditLootV87.spawn(s.x+115,s.y+91,i+3,wave,i%2);
            if(bag==null)continue;
            int[] items=ExpeditionSitesV88.supplies(i);
            System.arraycopy(items,0,bag.count,0,BanditLootV87.ITEMS);
        }
        sitesInitializedV88=true;
    }
    /** 10 visitable silhouettes: each contains distinct features and real loot cache. */
    void drawExpeditionSitesV88(Canvas c){
        for(ExpeditionSitesV88.Site s:ExpeditionSitesV88.SITES){
            if(!WorldPerfV55.nearView(s.x,s.y,camX,camY,viewW,viewH,630))continue;
            if(s.kind==ExpeditionSitesV88.CLINIC){
                drawFieldClinicExteriorV89(c,s);continue;
            }
            float x=s.x,y=s.y;
            // Scale the old structure and its authored decoration together,
            // around the unchanged world-space interaction doorway.
            float zoom=ExteriorFootprintV130.scale(s);
            float pivotY=y+ExteriorFootprintV130.anchor(s);
            c.save();c.translate(x,pivotY);c.scale(zoom,zoom);
            c.translate(-x,-pivotY);
            // Dirt lot and entrance path ensure readable traversal.
            rect(c,x-105,y-79,210,186,0xff44544a);
            rect(c,x-97,y-73,194,156,0xff54574b);
            rect(c,x-10,y+72,20,58,0xff79765d);
            int roof=s.kind==ExpeditionSitesV88.CLINIC?0xffa2afa2:
                s.kind==ExpeditionSitesV88.RELAY?0xff456771:
                s.kind==ExpeditionSitesV88.FARM?0xff886548:
                s.kind==ExpeditionSitesV88.CHECKPOINT?0xff4a5555:
                s.kind==ExpeditionSitesV88.GARAGE?0xff786352:0xff656f61;
            if(s.kind==ExpeditionSitesV88.RELAY||s.kind==ExpeditionSitesV88.TOWER){
                rect(c,x-52,y-57,104,120,0xff182628);
                rect(c,x-46,y-53,92,111,0xff565e51);
                rect(c,x-29,y-80,58,50,0xff253e3e);
                rect(c,x-6,y-146,12,67,0xff172729);
                rect(c,x-3,y-140,6,55,0xff9ba79c);
                rect(c,x-34,y-119,69,7,0xff263b3e);
                rect(c,x-20,y-106,42,4,0xffb6baa0);
                rect(c,x-19,y+38,38,19,0xff172a2b);
            }else{
                rect(c,x-78,y-66,160,145,0xff142626);
                rect(c,x-71,y-60,145,130,roof);
                rect(c,x-64,y-54,130,20,0xffa19b7a);
                rect(c,x-63,y-29,125,80,0xff4a5b51);
                rect(c,x-15,y+44,31,30,0xff172d2c);
                rect(c,x-61,y-19,27,24,0xff142f32);
                rect(c,x+32,y-19,27,24,0xff142f32);
                rect(c,x-57,y-16,19,15,0xff8d9f9c);
                rect(c,x+36,y-16,19,15,0xff8d9f9c);
                if(s.kind==ExpeditionSitesV88.GARAGE||s.kind==ExpeditionSitesV88.WORKSHOP){
                    rect(c,x-65,y+7,54,55,0xff1a2a2a);
                    rect(c,x-60,y+12,44,46,0xff876a4b);
                    for(int q=0;q<3;q++)rect(c,x-57,y+16+q*13,38,3,0xff263637);
                }else if(s.kind==ExpeditionSitesV88.CLINIC){
                    rect(c,x-8,y-52,16,27,0xffb94845);
                    rect(c,x-17,y-44,34,11,0xffb94845);
                }else if(s.kind==ExpeditionSitesV88.FARM){
                    rect(c,x-93,y+45,50,10,0xff2d4c36);
                    rect(c,x-91,y+55,49,13,0xff72905c);
                }else if(s.kind==ExpeditionSitesV88.MOTEL){
                    rect(c,x-62,y+26,30,26,0xff29373b);
                    rect(c,x+35,y+26,25,26,0xff29373b);
                }
            }
            rect(c,x-84,y-82,168,19,0xff1b2b2b);
            rect(c,x-81,y-78,162,12,0xffa2a18a);
            label(c,s.name,x-75,y-68,11,0xff1c2928,true);
            // Stenciled crate near entry; remaining loot bag is drawn separately.
            rect(c,x+91,y+73,44,30,0xff1a2926);
            rect(c,x+96,y+77,35,22,0xff94714b);
            rect(c,x+100,y+80,27,6,0xffc4a373);
            rect(c,x+110,y+78,5,20,0xff4b4937);
            rect(c,x-13,y+66,26,11,0xff111d1c);
            label(c,"ENTER",x-24,y+108,10,0xffe9d49d,true);
            c.restore();
        }
    }
    /** Avoid player-built and fixed cover when shooting, independent of FPS. */
    boolean banditHasLineOfSightV88(float x,float y,float tx,float ty){
        for(Cover c:covers){
            if(Ballistics.segmentBox(x,y,tx,ty,
                c.x-3,c.y-3,c.x+c.w+3,c.y+c.h+3)<=1f)return false;
        }
        return true;
    }
    boolean banditNearCoverV88(float x,float y){
        for(Cover c:covers){
            float nx=clamp(x,c.x,c.x+c.w),ny=clamp(y,c.y,c.y+c.h);
            float dx=x-nx,dy=y-ny;
            if(dx*dx+dy*dy<145f*145f)return true;
        }
        return false;
    }
    /** Canonical hit test for both the door indicator and its action.
     * Keep all V91/V128 entrance radii and world landing positions unchanged.
     */
    static final class DoorV132 {
        final int site;final float x,y;final String name;
        final IndustrialWorldV123.District district;
        DoorV132(int site,float x,float y,String name,
                 IndustrialWorldV123.District district){
            this.site=site;this.x=x;this.y=y;this.name=name;this.district=district;
        }
    }
    DoorV132 nearbyDoorV132(){
        if(!playing||gameOver)return null;
        if(insideClinicV89){
            return ContextualDoorV132.indoorExit(
                playerX,playerY,ClinicInteriorV89.EXIT_X,ClinicInteriorV89.EXIT_Y)?
                new DoorV132(-2,0f,0f,"EXIT BUILDING",null):null;
        }
        if(industrialModeV123||stitchedIndustrialV128){
            IndustrialWorldV123.District district=stitchedIndustrialV128?
                IndustrialBiomeBridgeV128.nearestEntrance(
                    playerX,playerY,ContextualDoorV132.INDUSTRIAL_RADIUS,industrialSeedV123):
                IndustrialOpenWorldV124.nearestEntrance(
                    playerX,playerY,ContextualDoorV132.INDUSTRIAL_RADIUS,industrialSeedV123);
            if(district!=null){
                float x=stitchedIndustrialV128?
                    IndustrialBiomeBridgeV128.worldX(district.doorX):
                    district.doorX;
                float y=stitchedIndustrialV128?
                    IndustrialBiomeBridgeV128.worldY(district.doorY+35f):
                    district.doorY+35f;
                return new DoorV132(INDUSTRIAL_SITE_V123,x,y,district.name,district);
            }
            if(industrialModeV123)return null;
        }
        for(int i=0;i<ExpeditionSitesV88.SITES.length;i++){
            ExpeditionSitesV88.Site site=ExpeditionSitesV88.SITES[i];
            float doorY=site.y+(site.kind==ExpeditionSitesV88.CLINIC?154f:90f);
            if(ContextualDoorV132.fixedDoor(playerX,playerY,
                site.x,site.y,site.kind==ExpeditionSitesV88.CLINIC))
                return new DoorV132(i,site.x,doorY+20f,site.name,null);
        }
        for(int i=0;i<craftV83.objects.size();i++){
            CampCraftV83.Structure shelter=craftV83.objects.get(i);
            if(shelter.kind==CampCraftV83.FIELD_SHELTER&&
               ContextualDoorV132.shelterDoor(
                   playerX,playerY,shelter.x,shelter.y))
                return new DoorV132(ExpeditionSitesV88.SITES.length+i,
                    shelter.x,shelter.y+67f,"FIELD SHELTER",null);
        }
        return null;
    }
    boolean enterDoorV132(){
        if(!playing||paused||gameOver)return false;
        DoorV132 door=nearbyDoorV132();
        if(door==null)return false;
        if(door.site==-2){exitClinicV89();return true;}
        if(door.district!=null)industrialSiteV123=door.district;
        return enterIndoorSiteV91(door.site,door.x,door.y,door.name);
    }
    /** Historical method retained, called by ENTER only. */
    boolean enterClinicFromWorldV89(){
        if(insideClinicV89)return false;
        return enterDoorV132();
    }
    boolean enterIndoorSiteV91(int site,float worldX,float worldY,String name){
        float[] landing=WorldSafetyV92.resolveExit(this::blocked,worldX,worldY);
        outsideDoorXv89=landing[0];
        outsideDoorYv89=landing[1];
        configureInteriorV91(site);
        insideClinicV89=true;
        playerX=ClinicInteriorV89.ENTRANCE_X;
        playerY=ClinicInteriorV89.ENTRANCE_Y;
        bringFriendsInsideV90();
        harvestV81.cancel();cancelPlaceV84();
        releaseControls();shots.clear();sparks.clear();flashes.clear();indoorRoundsV122.clear();
        cameraLookX=0;cameraLookY=0;
        gatherFeedback=name+"  •  EXPLORE AND SCAVENGE";
        gatherFeedbackTime=3.5f;
        saveProgress();invalidate();return true;
    }
    void exitClinicV89(){
        if(!insideClinicV89)return;
        String place=currentSiteNameV91();
        persistCurrentInteriorV91();
        insideClinicV89=false;activeSiteV91=-1;
        float[] landingV92=WorldSafetyV92.resolveExit(this::blocked,
            outsideDoorXv89,outsideDoorYv89);
        playerX=landingV92[0];playerY=landingV92[1];
        returnFriendsOutsideV90();
        releaseControls();shots.clear();sparks.clear();flashes.clear();indoorRoundsV122.clear();
        cameraLookX=0;cameraLookY=0;
        gatherFeedback="RETURNED TO "+place;
        gatherFeedbackTime=2.5f;
        spawnWave();saveProgress();invalidate();
    }
    /** Non-hostile NPCs have affiliations, dialogue, trading and recruitment. */
    /** The closest friendly NPC owns the contextual TALK button. */
    int nearbyNPCInteractionV92(){
        int role=-1;
        float nearest=148f;
        if(insideClinicV89){
            for(ClinicActorsV90.Actor npc:clinicActorsV90.actors){
                if(!npc.active||npc.hostile())continue;
                float d=distance(playerX,playerY,npc.x,npc.y);
                if(d>=nearest)continue;
                nearest=d;
                role=npc.type==ClinicActorsV90.MEDIC?1:4;
            }
            return role;
        }
        for(Survivor npc:campStaff){
            float d=distance(playerX,playerY,npc.x,npc.y);
            if(d>=nearest)continue;
            nearest=d;
            role=npc.variant==ROLE_TRADER?0:
                npc.variant==ROLE_MEDIC||npc.variant==ROLE_MEDIC+1?1:
                npc.variant==ROLE_GUARD||npc.variant==ROLE_GUARD+1?2:
                npc.variant==ROLE_MECHANIC||npc.variant==ROLE_MECHANIC+1?3:4;
        }
        return role;
    }
    boolean interactNearbyNPCV92(){
        int role=nearbyNPCInteractionV92();
        if(role<0)return false;
        host.runOnUiThread(()->host.npcInteractionV92(role));
        return true;
    }
    boolean tradeNPCV92(int choice){
        if(nearbyNPCInteractionV92()<0||!playing||gameOver)return false;
        switch(choice){
            case 0:if(scrap<2)return false;scrap-=2;medkits++;break;
            case 1:if(scrap<1)return false;scrap--;foodCount+=2;break;
            case 2:if(scrap<1)return false;scrap--;waterCount+=2;break;
            case 3:
                if(scrap<4||!relationshipsV92.canRecruit()||friends.size()>=6)return false;
                scrap-=4;
                Survivor ally=new Survivor(playerX+60,playerY+52,2,
                    ROLE_GUARD+friends.size()%2);
                if(insideClinicV89){
                    if(clinicInteriorV89.blocked(ally.x,ally.y,17)){
                        ally.x=ClinicInteriorV89.ENTRANCE_X;
                        ally.y=ClinicInteriorV89.ENTRANCE_Y;
                    }
                    outdoorCompanionPositionsV90.add(new float[]{outsideDoorXv89+60,
                        outsideDoorYv89+52});
                }
                friends.add(ally);
                allySetting=friends.size()+1;
                host.prefs.edit().putInt("survivors",allySetting).apply();
                break;
            default:return false;
        }
        relationshipsV92.trade();
        gatherFeedback=choice==3?"SURVIVOR RECRUITED":"TRADE COMPLETE • RELATIONSHIP IMPROVED";
        gatherFeedbackTime=3f;saveProgress();invalidate();
        return true;
    }
    /** A real inventory transfer to the addressed non-hostile nearby NPC.
     * No synthetic stock; resources leave the player's actual saved counters.
     */
    boolean giveNPCV97(int choice){
        int role=nearbyNPCInteractionV92();
        if(role<0||!playing||gameOver)return false;
        switch(choice){
            case 0: if(foodCount<1)return false;foodCount--;break;
            case 1: if(waterCount<1)return false;waterCount--;break;
            case 2: if(medkits<1)return false;medkits--;break;
            case 3: if(scrap<2)return false;scrap-=2;break;
            case 4: if(bandagesV88<1)return false;bandagesV88--;break;
            default:return false;
        }
        relationshipsV92.helped();
        gatherFeedback="SUPPLIES GIVEN • TRUST +2";
        gatherFeedbackTime=3f;
        saveProgress();invalidate();
        return true;
    }
    void interactClinicV89(){
        if(!insideClinicV89)return;
        // INTERACT handles containers and corpses; contextual ENTER / EXIT
        // exclusively handles doorway transitions.
        ClinicInteriorV89.Storage found=nearestAnyInteriorStorageV91(
            playerX,playerY,ClinicInteriorV89.USE_RADIUS);
        if(found!=null){
            host.runOnUiThread(()->host.lootClinicStorageV89(found));
        }else if(nearestIndoorCorpseV129()>=0){
            int corpse=nearestIndoorCorpseV129();
            host.runOnUiThread(()->host.searchIndoorCorpseDialogV129(corpse));
        }else{
            gatherFeedback="SEARCH CLOSE TO A CASE OR FALLEN NPC";
            gatherFeedbackTime=1.5f;
        }
    }
    int lootClinicStackV89(ClinicInteriorV89.Storage box,int kind){
        if(!insideClinicV89||!playing||!clinicInteriorV89.contains(box)||
           distance(playerX,playerY,box.x,box.y)>ClinicInteriorV89.USE_RADIUS+12f)
            return 0;
        int amount=clinicInteriorV89.take(box,kind);
        if(amount>0){
            addBanditLootV87(kind,amount); // same item inventories, no duplicate type.
            gatherFeedback="SCAVENGED "+BanditLootV87.NAMES[kind]+" +"+amount;
            gatherFeedbackTime=2f;saveProgress();invalidate();
        }
        return amount;
    }
    int lootClinicAllV89(ClinicInteriorV89.Storage box){
        if(!insideClinicV89||!playing||!clinicInteriorV89.contains(box)||
           distance(playerX,playerY,box.x,box.y)>ClinicInteriorV89.USE_RADIUS+12f)
            return 0;
        int[] taken=clinicInteriorV89.takeAll(box);
        int total=0;
        for(int i=0;i<taken.length;i++){
            total+=taken[i];addBanditLootV87(i,taken[i]);
        }
        total+=lootClinicAllGearV95(box);
        if(total>0){
            gatherFeedback="SCAVENGED "+total+" SUPPLIES AND GEAR";
            gatherFeedbackTime=2f;saveProgress();invalidate();
        }
        return total;
    }
    void bringFriendsInsideV90(){
        outdoorCompanionPositionsV90.clear();
        clinicFriendWaypointsV90.clear();
        for(int i=0;i<friends.size();i++){
            Survivor friend=friends.get(i);
            outdoorCompanionPositionsV90.add(new float[]{friend.x,friend.y});
            float x=playerX+(i%2==0?-48f:48f),y=playerY-56f-25f*i;
            if(clinicInteriorV89.blocked(x,y,19f)){
                x=playerX+(i%2==0?-34:34);y=playerY-35;
            }
            friend.x=x;friend.y=y;
            clinicFriendWaypointsV90.add(new float[]{x,y});
        }
    }
    void returnFriendsOutsideV90(){
        for(int i=0;i<friends.size();i++){
            Survivor friend=friends.get(i);
            float[] prev=i<outdoorCompanionPositionsV90.size()?
                outdoorCompanionPositionsV90.get(i):null;
            friend.x=prev==null?playerX+(i%2==0?-35:35):
                prev[0];
            friend.y=prev==null?playerY+38:prev[1];
        }
        outdoorCompanionPositionsV90.clear();
        clinicFriendWaypointsV90.clear();
    }
    float indoorHitXV131=0f,indoorHitYV131=0f;
    /** No feet-anchored target line: the actual visible head and torso count. */
    ClinicActorsV90.Actor indoorTargetV131(float reach){
        float startX=playerX,startY=playerY-27f;
        float endX=startX+aimX*reach,endY=startY+aimY*reach;
        float best=Float.POSITIVE_INFINITY;
        ClinicActorsV90.Actor choice=null;
        for(ClinicActorsV90.Actor actor:clinicActorsV90.actors){
            if(!actor.active||!actor.hostile())continue;
            float body=Ballistics.segmentBox(startX,startY,endX,endY,
                actor.x-(actor.type==ClinicActorsV90.FERAL?33f:22f),
                actor.y-(actor.type==ClinicActorsV90.FERAL?44f:90f),
                actor.x+(actor.type==ClinicActorsV90.FERAL?41f:22f),actor.y+5f);
            float head=actor.type==ClinicActorsV90.FERAL?
                Float.POSITIVE_INFINITY:firstHeadImpactV131(
                    startX,startY,endX,endY,actor.x,actor.y,
                    aimX<0?-1:1,
                    1+Math.floorMod(actor.type*31+37,200),
                    false,0f,false);
            float impact=Math.min(body,head);
            if(!Float.isFinite(impact)||impact<0f||impact>=best||impact>1f)continue;
            float x=startX+(endX-startX)*impact,y=startY+(endY-startY)*impact;
            if(!ClinicActorsV90.lineOfSight(clinicInteriorV89,startX,startY,x,y))
                continue;
            choice=actor;best=impact;indoorHitXV131=x;indoorHitYV131=y;
        }
        return choice;
    }
    void updateClinicFriendsV90(float dt){
        indoorCompanionNavClockV90-=dt;
        boolean updatePath=indoorCompanionNavClockV90<=0f;
        if(updatePath)indoorCompanionNavClockV90=.34f;
        for(int i=0;i<friends.size();i++){
            Survivor friend=friends.get(i);
            while(clinicFriendWaypointsV90.size()<=i)
                clinicFriendWaypointsV90.add(new float[]{friend.x,friend.y});
            float tx=playerX+(i%2==0?-45f:45f),
                ty=playerY+58f+(i/2)*44f;
            if(clinicInteriorV89.blocked(tx,ty,18)){
                tx=playerX;ty=playerY;
            }
            float[] wp=clinicFriendWaypointsV90.get(i);
            if(updatePath||Math.hypot(wp[0]-friend.x,wp[1]-friend.y)<25f){
                float[] next=ClinicActorsV90.lineOfSight(clinicInteriorV89,
                    friend.x,friend.y,tx,ty)?
                    new float[]{tx,ty}:clinicNavV90.next(friend.x,friend.y,tx,ty);
                wp[0]=next[0];wp[1]=next[1];
            }
            float dx=wp[0]-friend.x,dy=wp[1]-friend.y;
            float d=(float)Math.hypot(dx,dy);
            boolean walked=false;
            if(d>21f&&!companionStayV118){
                float nx=friend.x+dx/Math.max(1,d)*170f*dt,
                      ny=friend.y+dy/Math.max(1,d)*170f*dt;
                if(!clinicInteriorV89.blocked(nx,friend.y,16)){friend.x=nx;walked=true;}
                if(!clinicInteriorV89.blocked(friend.x,ny,16)){friend.y=ny;walked=true;}
                friend.face=dx>=0?1:-1;
            }
            friend.animation.step(walked,dt,CharacterFitV108.rate(7.8f,fitWalkFpsV108));
            friend.cd=Math.max(0f,friend.cd-dt);
            ClinicActorsV90.Actor chosen=null;
            float nearestDistance=300f;
            for(ClinicActorsV90.Actor a:clinicActorsV90.actors){
                if(!a.active||!a.hostile())continue;
                float distance=distance(friend.x,friend.y,a.x,a.y);
                if(distance>=nearestDistance)continue;
                if(!ClinicActorsV90.lineOfSight(clinicInteriorV89,
                    friend.x,friend.y,a.x,a.y))continue;
                chosen=a;nearestDistance=distance;
            }
            float wantX=NpcAimV122.scanX(worldTimer,i+71);
            float wantY=NpcAimV122.scanY(worldTimer,i+71);
            if(chosen!=null){
                float[] to=NpcAimV122.toward(
                    friend.x,friend.y,chosen.x,chosen.y);
                wantX=to[0];wantY=to[1];
            }
            float[] heading=NpcAimV122.turn(friend.aimX,friend.aimY,
                wantX,wantY,dt);
            friend.aimX=heading[0];friend.aimY=heading[1];
            friend.face=NpcAimV122.facing(friend.aimX,friend.face);
            if(chosen!=null&&friend.cd<=0&&!companionHoldFireV118&&
                NpcGunfireV122.firearm(friend.gun)&&
                NpcAimV122.aligned(friend.aimX,friend.aimY,wantX,wantY)){
                clinicActorsV90.hit(chosen,17f);
                hitBloodV129(chosen.x,chosen.y-42f,friend.aimX,friend.aimY,5);
                spawnIndoorGunfireV122(friend.x,friend.y,friend.gun,
                    friend.face,friend.aimX,friend.aimY,
                    chosen.x,chosen.y,false,false);
                friend.cd=.9f+(i%3)*.17f;
            }
        }
    }
    /** Indoor movement uses the approved character gait and the original sticks. */
    void updateClinicV89(float dt){
        gatherFeedbackTime=Math.max(0f,gatherFeedbackTime-dt);
        shotClock=Math.max(0f,shotClock-dt);
        recoil=Math.max(0f,recoil-dt*5f);
        indoorShotCooldownV90=Math.max(0f,indoorShotCooldownV90-dt);
        axeSwingTimeV118=Math.max(0f,axeSwingTimeV118-dt);
        updateGunEffectsV119(dt);
        updateIndoorRoundsV122(dt);
        if(reloadClock>0f){
            reloadClock-=dt;
            if(reloadClock<=0f){ammo=MAG[gun];reloadClock=0f;}
        }
        float vx=stickX,vy=stickY;
        float oldX=playerX,oldY=playerY;
        float len=(float)Math.hypot(vx,vy);
        if(len>.06f){
            vx/=Math.max(1f,len);vy/=Math.max(1f,len);
            float run=runHeld&&stamina>0?1.52f:1f;
            float speed=PlayerMovementV77.speed(gun==9?169f:236f,
                walkSpeedMultiplier,run,crouchHeld)*carrySpeedV91();
            float nx=playerX+vx*speed*dt,ny=playerY+vy*speed*dt;
            if(!clinicInteriorV89.blocked(nx,playerY,19f))playerX=nx;
            if(!clinicInteriorV89.blocked(playerX,ny,19f))playerY=ny;
        }
        moving=distance(playerX,playerY,oldX,oldY)>.001f;
        playerAnimation.step(moving,dt,CharacterFitV108.rate(
            PlayerMovementV77.gait(walkSpeedMultiplier,runHeld&&stamina>0)*
            walkingAnimationMultiplierV79,fitWalkFpsV108));
        float rest=RadialAimV65.rest(gun,crosshairRestPercent);
        boolean aim=rightPointer>=0&&aimDeflection>ClassicAimV71.DEADZONE;
        aimCursorDistance=aim?ClassicAimV71.distance(rest,
            Math.max(rest,340f),aimDeflection):rest;
        cursorWorldX=playerX+aimX*aimCursorDistance;
        cursorWorldY=playerY-42f+aimY*aimCursorDistance;
        stamina=clamp(stamina+dt*((moving&&runHeld)?-13f:8f),0,100);
        if(moving){
            hunger=Math.max(0,hunger-dt*.012f);
            thirst=Math.max(0,thirst-dt*.023f);
        }
        fatigue=clamp(fatigue+dt*(moving&&runHeld?.20f:-.08f),0,100);
        knifeCooldown=Math.max(0,knifeCooldown-dt);
        knifeDuration=Math.max(0,knifeDuration-dt);
        updateClinicFriendsV90(dt);
        float raiderBeforeV122=Float.POSITIVE_INFINITY;
        for(ClinicActorsV90.Actor a:clinicActorsV90.actors){
            if(a.active&&a.type==ClinicActorsV90.RAIDER)
                raiderBeforeV122=a.cooldown;
        }
        float threat=clinicActorsV90.tick(dt,playerX,playerY,clinicInteriorV89);
        // Only actual V90 raider gun hits create visible indoor bullets.
        // Zombies and animals remain melee-only; no fake firing effects.
        for(ClinicActorsV90.Actor a:clinicActorsV90.actors){
            if(!a.active||a.type!=ClinicActorsV90.RAIDER)continue;
            if(raiderBeforeV122<=dt+.0001f&&a.cooldown>=1.64f&&
                distance(a.x,a.y,playerX,playerY)<245f&&
                ClinicActorsV90.lineOfSight(clinicInteriorV89,
                    a.x,a.y,playerX,playerY)){
                float[] direction=NpcAimV122.toward(a.x,a.y,playerX,playerY);
                int facing=NpcAimV122.facing(direction[0],1);
                spawnIndoorGunfireV122(a.x,a.y,0,facing,
                    direction[0],direction[1],playerX,playerY,true,false);
            }
        }
        // Actors never despawn when colliding with allies. Separate their
        // footprints instead of hiding overlapping sprites or mutating 'active'.
        for(ClinicActorsV90.Actor actor:clinicActorsV90.actors)if(actor.active)
            for(Survivor friend:friends){
                float dx=actor.x-friend.x,dy=actor.y-friend.y;
                float d=(float)Math.hypot(dx,dy);
                if(d>=65f)continue;
                if(d<.1f){dx=17f;dy=-19f;d=25.5f;}
                float nx=actor.x+dx/d*(65f-d),ny=actor.y+dy/d*(65f-d);
                if(!clinicInteriorV89.blocked(nx,actor.y,15f))actor.x=nx;
                if(!clinicInteriorV89.blocked(actor.x,ny,15f))actor.y=ny;
            }
        if(threat>0f){
            ClinicActorsV90.Actor attacker=null;float distance=Float.POSITIVE_INFINITY;
            for(ClinicActorsV90.Actor actor:clinicActorsV90.actors){
                if(!actor.active||!actor.hostile())continue;
                float d=distance(playerX,playerY,actor.x,actor.y);
                if(d<distance){distance=d;attacker=actor;}
            }
            if(attacker!=null)hurtDirectionalV129(threat,
                playerX-attacker.x,playerY-attacker.y);
            else hurt(threat);
        }
        if(firing&&indoorShotCooldownV90<=0f&&reloadClock<=0f&&
            gun!=3&&gun!=11&&!gameOver){
            if(ammo>0){
                ammo--;
                ClinicActorsV90.Actor target=indoorTargetV131(
                    Math.min(700f,Ballistics.unobstructedTravel(gun)));
                if(target!=null){
                    clinicActorsV90.hit(target,gun==0?24f:gun==4?41f:32f);
                    hitBloodV129(target.x,target.y-39f,aimX,aimY,6);
                }
                recoil=recoilFX?1:0;
                if(GunEffectsV118.firearm(gun)){
                    float sc=CharacterCollision.BASE_SCALE*scale;
                    float[] mx=Ballistics.rigMuzzle(playerX,playerY,face,aimX,aimY,
                        sc,MX[gun],MY[gun],MAIN_X[gun],MAIN_Y[gun],0f);
                    WeaponPivotV117.relocateMuzzle(mx,face,sc,
                        playerGunPivotXV117,playerGunPivotYV117);
                    spawnIndoorGunfireV122(playerX,playerY,gun,face,
                        aimX,aimY,
                        target!=null?indoorHitXV131:mx[0]+aimX*420f,
                        target!=null?indoorHitYV131:mx[1]+aimY*420f,
                        false,true);
                }
                indoorShotCooldownV90=Math.max(.13f,RATES[gun]);
                saveProgress();
            }else if(ammoPacks>0){
                ammoPacks--;ammo=MAG[gun];
                indoorShotCooldownV90=1.1f;
            }else indoorShotCooldownV90=.4f;
        }
        cameraLookX=0;cameraLookY=0;
    }
    /** Exterior is substantially larger than V88. Entrance remains physically reachable. */
    void drawFieldClinicExteriorV89(Canvas c,ExpeditionSitesV88.Site site){
        float x=site.x,y=site.y;
        float zoom=ExteriorFootprintV130.scale(site);
        float pivotY=y+ExteriorFootprintV130.anchor(site);
        c.save();c.translate(x,pivotY);c.scale(zoom,zoom);
        c.translate(-x,-pivotY);
        rect(c,x-210,y-174,420,365,0xff3c4b43);
        rect(c,x-204,y-167,408,342,0xff52584b);
        // Pixelated roof and concrete foundation.
        rect(c,x-194,y-159,388,292,0xff102122);
        rect(c,x-184,y-151,368,277,0xff7f9591);
        rect(c,x-174,y-145,348,267,0xffa4b2aa);
        for(int i=0;i<6;i++){
            rect(c,x-166+i*56,y-141,45,12,i%2==0?0xff829b99:0xff78918e);
            rect(c,x-162+i*56,y+102,43,9,0xff4a6c6a);
        }
        // Distinct crossed ambulance insignia and emergency awning.
        rect(c,x-21,y-106,43,71,0xffa1433d);
        rect(c,x-42,y-84,85,26,0xffa1433d);
        rect(c,x-10,y-97,20,55,0xffe8e3c9);
        rect(c,x-31,y-75,62,9,0xffe8e3c9);
        rect(c,x-84,y+119,168,14,0xff142826);
        rect(c,x-78,y+125,156,10,0xff9e7961);
        rect(c,x-52,y+134,104,17,0xff243533);
        rect(c,x-25,y+137,50,8,0xff9ab1af);
        rect(c,x-24,y+147,48,27,0xff1b3031);
        rect(c,x-2,y+145,5,28,0xff8daca5);
        // Empty landing strip guides USE interaction.
        rect(c,x-63,y+171,126,13,0xff968e75);
        rect(c,x-54,y+183,108,4,0xffb9ae89);
        label(c,"FIELD CLINIC",x-92,y-155,17,0xffe3ebe1,true);
        label(c,"ENTER AT THE DOOR",x-48,y+205,13,0xffe1d4a3,true);
        // Door furniture, vents, rust and water damage are distinct from V88.
        rect(c,x-166,y-24,49,59,0xff425d59);
        rect(c,x+117,y-24,49,59,0xff425d59);
        for(int i=0;i<4;i++){
            rect(c,x-159,y-17+i*12,34,5,0xffa1b7ae);
            rect(c,x+124,y-17+i*12,34,5,0xffa1b7ae);
        }
        rect(c,x-172,y+42,83,34,0xff405e5d);
        rect(c,x+90,y+43,82,31,0xff405e5d);
        rect(c,x-164,y+49,69,7,0xff658d88);
        rect(c,x+98,y+49,67,7,0xff658d88);
        c.restore();
    }
    /** Furniture uses only reusable rectangle primitives, never generated bitmaps. */
    void drawClinicFurnitureV89(Canvas c,float[] item){
        int kind=(int)item[0];
        float x=item[1],y=item[2],w=item[3],h=item[4];
        int fill=kind==0?0xff697d6f:kind==1?0xff647781:
            kind==2?0xff806b54:kind==3?0xff9f9e87:
            kind==4?0xff587b7a:0xff697c61;
        rect(c,x-3,y-3,w+6,h+6,0xff152a2b);
        rect(c,x,y,w,h,fill);
        if(kind==0){
            rect(c,x+7,y+7,w-14,25,0xffd2d8bd);
            rect(c,x+8,y+35,w-16,h-43,0xff8eada1);
            rect(c,x+12,y+42,w-24,5,0xffe1e7d6);
            rect(c,x+3,y+h-13,w-6,8,0xff425b50);
        }else if(kind==1||kind==5){
            for(int i=0;i<3;i++){
                float top=y+6+i*(h-12)/3f;
                rect(c,x+5,top,w-10,2,0xffb3b8a5);
                rect(c,x+w*.55f,top+4,5,5,0xff203c3e);
            }
        }else if(kind==2){
            rect(c,x+8,y+7,w-16,h-14,0xffb49b77);
            rect(c,x+w*.35f,y+10,w*.32f,18,0xff2b494c);
            rect(c,x+w*.4f,y+12,w*.22f,11,0xff85b6b1);
        }else if(kind==3){
            rect(c,x+8,y+8,w-16,h-16,0xffd2c5a2);
            rect(c,x+14,y+15,w-28,9,0xff889e98);
        }else{
            rect(c,x+8,y+7,w-16,h-14,0xff2a5156);
            rect(c,x+12,y+12,w-24,6,0xffa0c5b9);
            rect(c,x+16,y+29,9,10,0xffe0bf79);
        }
    }
    void drawClinicStorageV89(Canvas c,ClinicInteriorV89.Storage box){
        float x=box.x,y=box.y;
        boolean empty=box.empty();
        rect(c,x-23,y-17,47,34,0xff152b2c);
        rect(c,x-19,y-14,39,27,empty?0xff4b5d59:0xff867c64);
        rect(c,x-14,y-10,29,10,empty?0xff55645b:0xffc1b18c);
        rect(c,x+3,y+3,6,5,0xff243d3d);
        if(!empty){
            rect(c,x-22,y-20,44,5,0xffd2c18e);
            if(distance(playerX,playerY,x,y)<148)
                label(c,"INTERACT  "+box.label,x-51,y-28,10,0xffe8ddad,true);
        }
    }
    /** Indoor render path does not call terrain(), drawWorld(), NPCs or outdoor lights. */
    /** Actual indoor world coordinates, V122 player/companion/NPC rigs and shooting. */
    void drawIndustrialInteriorV123(Canvas c){
        c.save();c.translate(-camX,-camY);
        IndustrialSceneV123.indoors(c,p,(IndustrialInteriorV123)clinicInteriorV89);
        industrialArtV123.indoors(c,(IndustrialInteriorV123)clinicInteriorV89);
        IndustrialInteriorArtV125.details(c,p,(IndustrialInteriorV123)clinicInteriorV89);
        for(ClinicInteriorV89.Storage box:clinicInteriorV89.storages){
            if(!WorldPerfV55.nearView(box.x,box.y,camX,camY,viewW,viewH,80))continue;
            if(!box.empty()&&distance(playerX,playerY,box.x,box.y)<145f)
                label(c,"INTERACT "+box.label,box.x-45,box.y-29,12,0xfff3d9a1,true);
        }
        rect(c,1237,1828,245,31,0xff243638);
        label(c,"EXIT",1308,1847,20,0xffebd5a3,true);
        drawClinicVisionV90(c);
        drawIndoorMuzzleLightV129(c);
        drawDroppedItemsV129(c);
        drawIndoorCorpsesV129(c);
        ArrayList<DrawEntity> sorted=new ArrayList<>();
        for(ClinicActorsV90.Actor actor:clinicActorsV90.actors){
            if(!actor.active||!WorldPerfV55.nearView(actor.x,actor.y,camX,camY,viewW,viewH,155)||
                    !indoorCharacterVisibleV127(actor.x,actor.y))
                continue;
            sorted.add(new DrawEntity(actor.y,()->drawIndoorVisibleEntityV127(c,
                ()->drawClinicActorV90(c,actor))));
        }
        for(Survivor friend:friends){
            if(!WorldPerfV55.nearView(friend.x,friend.y,camX,camY,viewW,viewH,145)||
                    !indoorCharacterVisibleV127(friend.x,friend.y))
                continue;
            sorted.add(new DrawEntity(friend.y,()->drawIndoorVisibleEntityV127(c,
                ()->character(c,friend.x,friend.y,
                friend.gun,friend.face,friend.animation.frame(),
                friend.animation.isWalking()?Float.POSITIVE_INFINITY:
                    friend.animation.breathOffset(),
                Ballistics.angle(friend.aimX,friend.aimY,friend.face),
                0,false,false,friend.variant,friend.skinV109))));
        }
        sorted.add(new DrawEntity(playerY,()->character(c,playerX,playerY,gun,face,
            playerAnimation.frame(),
            playerAnimation.isWalking()?Float.POSITIVE_INFINITY:
                playerAnimation.breathOffset(),
            Ballistics.angle(aimX,aimY,face),recoil*2.7f,true,false,-1)));
        sorted.sort((a,b)->Float.compare(a.y,b.y));
        for(DrawEntity item:sorted)item.draw.run();
        drawGunEffectsV119(c);
        drawIndoorRoundsV122(c);
        drawIndoorSpeechAfterLightingV93(c);
        c.restore();
    }

    void drawClinicInteriorV89(Canvas c){
        if(clinicInteriorV89 instanceof IndustrialInteriorV123){
            drawIndustrialInteriorV123(c);return;
        }
        c.save();c.translate(-camX,-camY);
        int siteKindV91=activeSiteV91>=0&&activeSiteV91<ExpeditionSitesV88.SITES.length?
            ExpeditionSitesV88.SITES[activeSiteV91].kind:ExpeditionSitesV88.CABIN;
        boolean nonClinicV91=clinicInteriorV89 instanceof ExpeditionInteriorV91;
        rect(c,0,0,ClinicInteriorV89.WIDTH,ClinicInteriorV89.HEIGHT,
            nonClinicV91?0xff292c2a:0xff182f31);
        // Base layout can be rendered at the same proportions as its V89 art.
        // Physical model, entrances, rooms, furniture and actor positions use
        // expanded actual coordinates, while locked pixel size stays unchanged.
        c.save();
        c.scale(ClinicInteriorV89.EXPANSION_V90,
            ClinicInteriorV89.EXPANSION_V90);
        rect(c,23,23,1554,1072,0xff747d70);
        // Six departments have differentiated tile/palette, connected by hall.
        int[] north=nonClinicV91?new int[]{0xff777667,0xff767a71,0xff7c766b}:
            new int[]{0xff70837e,0xff858a81,0xff6a8987};
        int[] south=nonClinicV91?new int[]{0xff8c8978,0xff838a7a,0xff776e60}:
            new int[]{0xff7b8b78,0xff9a927d,0xff778579};
        for(int i=0;i<3;i++){
            int sx=23+i*526;int width=(i==2?502:506);
            rect(c,sx,44,width,442,north[i]);
            rect(c,sx,642,width,428,south[i]);
        }
        rect(c,23,508,1554,112,0xff93998a);
        // Checker-style grouting with no dynamic bitmaps, loops <160 lines.
        for(int x=44;x<1575;x+=72)
            rect(c,x,43,2,1028,0x32404c46);
        for(int y=45;y<1080;y+=72)
            rect(c,24,y,1551,2,0x37455851);
        float inv=1f/ClinicInteriorV89.EXPANSION_V90;
        drawIndoorFloorIlluminationV93(c);
        for(float[] wall:nonClinicV91?
            ((ExpeditionInteriorV91)clinicInteriorV89).sceneWalls():ClinicInteriorV89.WALLS){
            float wx=wall[0]*inv,wy=wall[1]*inv,
                ww=wall[2]*inv,wh=wall[3]*inv;
            rect(c,wx-2,wy-2,ww+4,wh+4,0xff162e30);
            rect(c,wx,wy,ww,wh,0xff425d59);
            rect(c,wx+2,wy+2,Math.max(2,ww-4),5,0xff90a39b);
        }
        // Door portal frames face the central corridor.
        for(float[] door:ClinicInteriorV89.DOOR_SIGNS){
            float dx=door[0]*inv,dy=door[1]*inv;
            rect(c,dx-47,dy,94,9,0xff283e40);
            rect(c,dx-44,dy+3,88,4,0xffddc7a2);
        }
        for(int i=0;i<ClinicInteriorV89.ROOM_LABELS.length;i++){
            float x=ClinicInteriorV89.ROOM_LABELS[i][0]*inv;
            float y=ClinicInteriorV89.ROOM_LABELS[i][1]*inv;
            String[] roomsV91=nonClinicV91?
                ((ExpeditionInteriorV91)clinicInteriorV89).roomNames():ClinicInteriorV89.ROOMS;
            label(c,roomsV91[i],x,y,13,0xff213b3b,true);
        }
        label(c,"MAIN CORRIDOR  •  "+currentSiteNameV91(),
            550,559,14,0xff253e3a,true);
        c.restore();
        for(float[] obj:nonClinicV91?
            ((ExpeditionInteriorV91)clinicInteriorV89).sceneFurniture():ClinicInteriorV89.FURNITURE){
            if(!WorldPerfV55.nearView(obj[1],obj[2],camX,camY,
                viewW,viewH,Math.max(obj[3],obj[4])+30))continue;
            drawClinicFurnitureV89(c,obj);
        }
        for(ClinicInteriorV89.Storage storage:clinicInteriorV89.storages){
            if(!WorldPerfV55.nearView(storage.x,storage.y,camX,camY,viewW,viewH,80))
                continue;
            drawClinicStorageV89(c,storage);
        }
        // Real departure point at bottom entrance; not a map-teleport hotspot.
        float s=ClinicInteriorV89.EXPANSION_V90;
        rect(c,757*s,1070*s,86*s,30*s,0xff122a29);
        rect(c,762*s,1074*s,76*s,21*s,0xff9d8c68);
        rect(c,780*s,1074*s,39*s,18*s,0xff284448);
        label(c,"EXIT",777*s,1064*s,22,0xffe9d8af,true);
        if(distance(playerX,playerY,ClinicInteriorV89.EXIT_X,
           ClinicInteriorV89.EXIT_Y)<125f)
            label(c,"EXIT AT THE DOOR",691*s,1020*s,18,0xfff0e5bf,true);
        drawIndoorLightFixturesV93(c);
        drawClinicVisionV90(c);
        drawIndoorMuzzleLightV129(c);
        drawDroppedItemsV129(c);
        drawIndoorCorpsesV129(c);
        // Actual world-Y depth sort. NPCs cannot visually disappear beneath
        // accompanying survivors merely because companions render last.
        ArrayList<DrawEntity> indoorOrderV92=new ArrayList<>();
        for(ClinicActorsV90.Actor actor:clinicActorsV90.actors){
            if(!actor.active)continue;
            if(!WorldPerfV55.nearView(actor.x,actor.y,camX,camY,viewW,viewH,160)||
                    !indoorCharacterVisibleV127(actor.x,actor.y))
                continue;
            indoorOrderV92.add(new DrawEntity(actor.y,
                ()->drawIndoorVisibleEntityV127(c,()->drawClinicActorV90(c,actor))));
        }
        for(Survivor friend:friends){
            if(!WorldPerfV55.nearView(friend.x,friend.y,camX,camY,viewW,viewH,145)||
                    !indoorCharacterVisibleV127(friend.x,friend.y))
                continue;
            indoorOrderV92.add(new DrawEntity(friend.y,()->drawIndoorVisibleEntityV127(c,()->{
                float friendAim=Ballistics.angle(friend.aimX,friend.aimY,friend.face);
                character(c,friend.x,friend.y,friend.gun,friend.face,
                    friend.animation.frame(),
                    friend.animation.isWalking()?Float.POSITIVE_INFINITY:
                    friend.animation.breathOffset(),friendAim,0,false,false,
                    friend.variant,friend.skinV109);
                rect(c,friend.x-6,friend.y-117,13,4,OLIVE);
                
            })));
        }
        indoorOrderV92.add(new DrawEntity(playerY,()->{
            float angle=Ballistics.angle(aimX,aimY,face);
            character(c,playerX,playerY,gun,face,playerAnimation.frame(),
                playerAnimation.isWalking()?Float.POSITIVE_INFINITY:
                playerAnimation.breathOffset(),angle,recoil*2.7f,true,false,-1);
        }));
        indoorOrderV92.sort((a,b)->Float.compare(a.y,b.y));
        for(DrawEntity entity:indoorOrderV92)entity.draw.run();
        drawGunEffectsV119(c);
        drawIndoorRoundsV122(c);
        drawIndoorSpeechAfterLightingV93(c);
        c.restore();
    }
    void drawClinicActorV90(Canvas c,ClinicActorsV90.Actor a){
        if(a.type==ClinicActorsV90.FERAL){
            // Side-view infected canine: recognizable muzzle, ears and tail.
            rect(c,a.x-28,a.y-28,55,21,0xff172925);
            rect(c,a.x-23,a.y-34,41,19,0xff665e47);
            rect(c,a.x+12,a.y-43,20,20,0xff263d34);
            rect(c,a.x+15,a.y-41,14,13,0xff8c7c53);
            rect(c,a.x+27,a.y-30,14,9,0xff7f674c);
            rect(c,a.x+23,a.y-35,4,4,0xffda9b6b);
            rect(c,a.x-22,a.y-7,8,13,0xff222e28);
            rect(c,a.x+13,a.y-7,8,13,0xff222e28);
            rect(c,a.x-37,a.y-29,12,5,0xff665e47);
            return;
        }
        boolean hostile=a.hostile();
        int variant=a.type==ClinicActorsV90.MEDIC?ROLE_MEDIC:
            a.type==ClinicActorsV90.SURVIVOR?ROLE_CIVILIAN:0;
        float lookX=NpcAimV122.scanX(worldTimer,a.type+85);
        float lookY=NpcAimV122.scanY(worldTimer,a.type+85);
        if(hostile&&distance(a.x,a.y,playerX,playerY)<500f){
            float[] toward=NpcAimV122.toward(a.x,a.y,playerX,playerY);
            lookX=toward[0];lookY=toward[1];
        }
        int facing=NpcAimV122.facing(lookX,1);
        character(c,a.x,a.y,hostile?0:3,facing,0,
            (float)Math.sin(worldTimer*2+a.type)*.22f,
            Ballistics.angle(lookX,lookY,facing),0,
            false,hostile,variant,1+Math.floorMod(a.type*31+37,200));
        if(a.type==ClinicActorsV90.ZOMBIE){
            // Greenish face + torn sleeves over original character atlas.
            rect(c,a.x-9,a.y-103,17,8,0xff718361);
            rect(c,a.x-6,a.y-101,4,3,0xffac4a44);
            rect(c,a.x+3,a.y-101,4,3,0xffac4a44);
            rect(c,a.x-17,a.y-56,6,11,0xff44563e);
        }else if(a.type==ClinicActorsV90.RAIDER)
            rect(c,a.x-9,a.y-107,18,5,0xff9d514c);
        else if(!hostile)
            rect(c,a.x-6,a.y-118,12,4,0xff7cc9b0);
        
        if(hostile){
            rect(c,a.x-21,a.y-126,42,4,0xff172827);
            rect(c,a.x-20,a.y-125,40*a.hp/85f,3,
                a.type==ClinicActorsV90.ZOMBIE?0xff77955c:0xffa66b58);
        }
    }
    /** All non-player indoor actors obey the existing vision and walls. */
    boolean indoorCharacterVisibleV127(float x,float feetY){
        return IndoorCharacterVisionV127.visible(clinicVisionV90,clinicInteriorV89,
            playerX,playerY-35f,aimX,aimY,x,feetY);
    }
    /** Clip character art, hair and weapons precisely to the traced cone. */
    void drawIndoorVisibleEntityV127(Canvas c,Runnable entityDraw){
        c.save();
        c.clipPath(clinicVisionPathV90);
        entityDraw.run();
        c.restore();
    }
    void drawClinicVisionV90(Canvas c){
        float ox=playerX,oy=playerY-35;
        clinicVisionV90.trace(ox,oy,aimX,aimY,clinicInteriorV89);
        clinicVisionPathV90.reset();
        clinicVisionPathV90.moveTo(ox,oy);
        for(int i=0;i<ClinicVisionV90.RAYS;i++)
            clinicVisionPathV90.lineTo(clinicVisionV90.xs[i],
                clinicVisionV90.ys[i]);
        clinicVisionPathV90.close();
        c.save();
        c.clipPath(clinicVisionPathV90,android.graphics.Region.Op.DIFFERENCE);
        rect(c,camX-10,camY-10,viewW+20,viewH+20,0xb9071516);
        c.restore();
    }
    void spawnWave(){
        if(industrialModeV123){enemies.clear();enemyCount=0;return;}
        enemies.clear();enemyCount=5+Math.min(17,wave*2);
        for(int i=0;i<enemyCount;i++){
            // Camp is an actual protected settlement, never a bandit spawn or patrol target.
            boolean spawned=false;
            for(int retry=0;retry<80;retry++){
                float a=(float)(rng.nextDouble()*Math.PI*2);
                float distance=830+rng.nextInt(480);
                float x=playerX+(float)Math.cos(a)*distance;
                float y=playerY+(float)Math.sin(a)*distance;
                if(!WorldSafetyV92.hostileAllowed(x,y,CAMP_X,CAMP_Y)||
                    blocked(x,y,28f))continue;
                enemies.add(new Bandit(x,y,i%2));spawned=true;break;
            }
            if(!spawned)enemyCount--;
        }
    }
    void saveProgress(){
        if(industrialModeV123||stitchedIndustrialV128){
            host.prefs.edit().putInt(IndustrialWorldV123.SEED_PREF,industrialSeedV123)
                .putInt("industrial_sx_v123",industrialSiteV123.sx)
                .putInt("industrial_sy_v123",industrialSiteV123.sy)
                .putString("industrial_yard_v123_"+industrialSeedV123,
                    industrialYardV123.encode()).apply();
        }
        if(!playing||gameOver)return;
        if(insideClinicV89)persistCurrentInteriorV91();
        host.prefs.edit().putBoolean("hasSave",true)
                .putBoolean("v128_world_coords",true).putFloat("px",playerX).putFloat("py",playerY)
                .putFloat("hp",health).putFloat("stamina",stamina)
                .putFloat("hunger",hunger).putFloat("thirst",thirst)
                .putFloat("fatigue",fatigue).putInt("foodCount",foodCount)
                .putInt("waterCount",waterCount).putInt("kills",kills).putInt("wave",wave)
                .putInt("scrap",scrap).putInt("medkits",medkits)
                .putInt("ammoPacks",ammoPacks).putInt("ammo",ammo)
                .putInt("woodV80",wood).putInt("stoneV80",stone).putInt("fiberV80",fiber)
                .putInt("bandagesV88",bandagesV88).putInt("energyV88",energyV88)
                .putString("depleted_resources_v80",harvestWorld.encode())
                .putString("campfire_locations",encodeCampfires())
                .putString("camp_buildings_v83",craftV83.encode())
                .putString("camp_stock_v84",craftV83.encodeStock())
                .putString("salvaged_scrap_v84",salvageWorldV84.encode())
                .putString("loose_pickups_v85",groundPickupsV85.encode())
                .putString("bandit_loot_bags_v87",banditLootV87.encode())
                .putString("ground_drops_v129",droppedItemsV129.encode())
                .putBoolean("sitesInitializedV88",sitesInitializedV88)
                .putString("facilityCooldownV88",encodeFacilityCooldownV88())
                .putInt("active_site_v91",insideClinicV89?activeSiteV91:-1)
                .putString("field_finds_v91",fieldFindsV91.encode())
                .putString("wardrobe_v92",wardrobeV92.encode())
                .putInt("backpackStyleV96",backpackStyleV96)
                .putInt("headgearStyleV96",headgearStyleV96)
                .putString("gear_loot_v95",gearLootV95.encode())
                .putString("npc_relations_v92",relationshipsV92.encode())
                .putString("bag_order_v92",encodeBagOrderV92())
                .putString("bag_splits_v130",encodeBagSplitsV130())
                .putBoolean("inside_clinic_v89",insideClinicV89)
                .putFloat("clinic_return_x_v89",outsideDoorXv89)
                .putFloat("clinic_return_y_v89",outsideDoorYv89)
                .putString("clinic_containers_v89",activeSiteV91==1?
                    clinicInteriorV89.encode():host.prefs.getString("clinic_containers_v89",""))
                .putString("clinic_actors_v90",activeSiteV91==1?
                    clinicActorsV90.encode():host.prefs.getString("clinic_actors_v90",""))
                .putBoolean("clinic_scaled_v90",true)
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
        shots.clear();flashes.clear();indoorRoundsV122.clear();sparks.clear();
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
        if(stitchedIndustrialV128&&
            IndustrialBiomeBridgeV128.blocked(x,y,r,industrialSeedV123))
            return true;
        if(industrialModeV123)return IndustrialOpenWorldV124.blocked(
            x,y,r,industrialSeedV123);
        // V130 collision matches the expanded painted roof only, preserving
        // the original southern doorway and normal NPC navigation lanes.
        for(ExpeditionSitesV88.Site site:ExpeditionSitesV88.SITES)
            if(ExteriorFootprintV130.blocked(site,x,y,r))return true;
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
        if(insideClinicV89){
            knifeHitPending=false;knifeTarget=null;
            knifeDirection=LegacyControlsV58.quantizeKnife(aimX,aimY);
            ClinicActorsV90.Actor target=clinicActorsV90.target(
                playerX,playerY-27,aimX,aimY,MeleeSlashV83.REACH,
                clinicInteriorV89);
            if(target!=null){
                clinicActorsV90.hit(target,40f);
                hitBloodV129(target.x,target.y-40f,aimX,aimY,4);
                particles(target.x,target.y-28,0xffa45146,6);
                saveProgress();
            }
            return;
        }
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
        c.translate(WeaponPivotV117.localX(playerGunPivotXV117,s),
                    WeaponPivotV117.localY(playerGunPivotYV117,s));
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
    void shoot(float x,float y,float dx,float dy,int weapon,boolean hostile,int facing,
               boolean playerShooter){
        float length=(float)Math.hypot(dx,dy);
        if(length<.01f){dx=facing;dy=0;length=1;}
        dx/=length;dy/=length;
        if(weapon==3)return; // Flashlight does not fire bullets.
        if(weapon==11){
            if(playerShooter)axeSwingTimeV118=.25f;
            if(hostile){if(distance(x,y,playerX,playerY)<92)hurt(POWER[11]);}
            else for(Bandit e:enemies)if(e.active&&distance(x,y,e.x,e.y)<88)damage(e,POWER[11]);
            particles(x+dx*26,y-35,ORANGE,3);
            return;
        }
        float kick=(!hostile&&x==playerX&&y==playerY&&recoilFX)?2.7f:0f;
        float gunScale=CharacterCollision.BASE_SCALE*scale;
        float[] muzzle=Ballistics.rigMuzzle(x,y,facing,dx,dy,gunScale,
                MX[weapon],MY[weapon],MAIN_X[weapon],MAIN_Y[weapon],kick);
        WeaponPivotV117.relocateMuzzle(muzzle,facing,gunScale,
            playerShooter?playerGunPivotXV117:npcGunPivotXV117,
            playerShooter?playerGunPivotYV117:npcGunPivotYV117);
        final float bx=muzzle[0],by=muzzle[1];
        int pellets=weapon==7?5:1;
        float theta=(float)Math.atan2(dy,dx);
        for(int i=0;i<pellets;i++){
            float jitter=(rng.nextFloat()-.5f)*(weapon==7?.30f:.027f);
            float a=theta+jitter,velocity=Ballistics.SPEED[weapon];
            shots.add(new Shot(bx,by,(float)Math.cos(a)*velocity,
                    (float)Math.sin(a)*velocity,POWER[weapon]/(pellets==5?2f:1f),hostile));
        }
        emitGunEffectsV119(bx,by,dx,dy,weapon);
        particles(bx,by,ORANGE,weapon==10?4:2);
    }
    /** Add only a brief, small gun muzzle flash at the V117-fitted muzzle.
     * Unlike V118, no synthetic tracers are generated independently of bullets.
     */
    void emitGunEffectsV119(float x,float y,float dx,float dy,int weapon){
        if(!GunEffectsV119.firearm(weapon)||!host.option("gunMuzzleV119",true))return;
        float length=Math.max(.001f,(float)Math.hypot(dx,dy));
        float nx=dx/length,ny=dy/length;
        if(flashes.size()>=48)flashes.remove(0);
        flashes.add(new Flash(x,y,nx,ny));
    }

    /** Visualizes an actual V90 indoor hitscan shot as a tiny moving
     * physical-looking round, with matching V119 muzzle source. The existing
     * combat damage/collision is unchanged and applied only once.
     */
    void spawnIndoorGunfireV122(float x,float y,int weapon,int facing,
        float aimX,float aimY,float targetX,float targetY,
        boolean hostile,boolean playerShooter){
        if(!NpcGunfireV122.firearm(weapon))return;
        float size=CharacterCollision.BASE_SCALE*scale;
        float[] muzzle=Ballistics.rigMuzzle(x,y,facing,aimX,aimY,
            size,MX[weapon],MY[weapon],MAIN_X[weapon],MAIN_Y[weapon],0f);
        WeaponPivotV117.relocateMuzzle(muzzle,facing,size,
            playerShooter?playerGunPivotXV117:npcGunPivotXV117,
            playerShooter?playerGunPivotYV117:npcGunPivotYV117);
        emitGunEffectsV119(muzzle[0],muzzle[1],aimX,aimY,weapon);
        if(!host.option("gunTrailV119",true))return;
        float[] velocity=NpcGunfireV122.velocity(
            muzzle[0],muzzle[1],targetX,targetY);
        float life=NpcGunfireV122.life(muzzle[0],muzzle[1],targetX,targetY);
        if(indoorRoundsV122.size()>=75)indoorRoundsV122.remove(0);
        indoorRoundsV122.add(new IndoorRoundV122(
            muzzle[0],muzzle[1],velocity[0],velocity[1],life,hostile));
    }
    void updateIndoorRoundsV122(float dt){
        for(Iterator<IndoorRoundV122> it=indoorRoundsV122.iterator();it.hasNext();){
            IndoorRoundV122 round=it.next();
            float delta=Math.min(dt,round.life);
            round.x+=round.vx*delta;round.y+=round.vy*delta;
            round.life-=dt;
            if(round.life<=0f)it.remove();
        }
    }
    void drawIndoorRoundsV122(Canvas c){
        if(!host.option("gunTrailV119",true))return;
        for(IndoorRoundV122 round:indoorRoundsV122){
            if(!WorldPerfV55.nearView(round.x,round.y,camX,camY,
                viewW,viewH,24f))continue;
            float m=Math.max(.001f,(float)Math.hypot(round.vx,round.vy));
            float dx=round.vx/m,dy=round.vy/m;
            color(GunEffectsV119.bulletColor(round.hostile));
            p.setStrokeWidth(1.8f);
            c.drawLine(round.x-dx*GunEffectsV119.BULLET_TRAIL_LENGTH,
                round.y-dy*GunEffectsV119.BULLET_TRAIL_LENGTH,
                round.x,round.y,p);
            rect(c,round.x-1.5f,round.y-1.5f,3f,3f,
                GunEffectsV119.bulletColor(round.hostile));
        }
    }

    void updateGunEffectsV119(float dt){
        for(Iterator<Flash> it=flashes.iterator();it.hasNext();){
            Flash flash=it.next();flash.ttl-=dt;
            if(flash.ttl<=0f)it.remove();
        }
    }

    void drawWorldMuzzleBloomV130(Canvas c){
        if(!host.option("gunMuzzleV119",true))return;
        for(Flash f:flashes){
            if(f.ttl<=0f||!WorldPerfV55.nearView(
                    f.x,f.y,camX,camY,viewW,viewH,245f))continue;
            int alpha=Math.round(155f*GunEffectsV119.alpha(f.ttl));
            p.setShader(new android.graphics.RadialGradient(f.x,f.y,190f,
                new int[]{(alpha<<24)|0x00ffe0ae,
                    ((alpha/3)<<24)|0x00dba66b,0},
                new float[]{0f,.33f,1f},android.graphics.Shader.TileMode.CLAMP));
            c.drawCircle(f.x,f.y,190f,p);p.setShader(null);
        }
    }
    /** Real traveling bullets and restrained muzzle tip after the night pass.
     * No large glowing streak, fake traveling projectile, laser or starburst.
     * Never invoked for the axe (ID 11) or flashlight (ID 3).
     */
    void drawGunEffectsV119(Canvas c){
        if(host.option("gunTrailV119",true)){
            for(Shot bullet:shots){
                if(!WorldPerfV55.nearView(bullet.x,bullet.y,camX,camY,
                    viewW,viewH,24f))continue;
                float speed=Math.max(1f,(float)Math.hypot(bullet.vx,bullet.vy));
                float dx=bullet.vx/speed,dy=bullet.vy/speed;
                color(GunEffectsV119.bulletColor(bullet.hostile));
                p.setStrokeWidth(1.8f);
                c.drawLine(bullet.x-dx*GunEffectsV119.BULLET_TRAIL_LENGTH,
                    bullet.y-dy*GunEffectsV119.BULLET_TRAIL_LENGTH,
                    bullet.x,bullet.y,p);
                rect(c,bullet.x-1.5f,bullet.y-1.5f,3f,3f,
                    GunEffectsV119.bulletColor(bullet.hostile));
            }
        }
        if(!host.option("gunMuzzleV119",true))return;
        for(Flash f:flashes){
            if(!WorldPerfV55.nearView(f.x,f.y,camX,camY,viewW,viewH,20f))continue;
            float a=GunEffectsV119.alpha(f.ttl);
            if(a<=0f)continue;
            float len=GunEffectsV119.muzzleLength(a,0);
            float spread=GunEffectsV119.muzzleHalfWidth(a);
            float px=-f.dy,py=f.dx;
            // A tiny tapered, warm muzzle cone: 1 short center dash and
            // two narrow edges. Not a glowing cross or a static giant streak.
            color(0xffdfbc77);
            p.setStrokeWidth(2.1f);
            c.drawLine(f.x,f.y,f.x+f.dx*len,f.y+f.dy*len,p);
            color(0xffc98d50);
            p.setStrokeWidth(1.5f);
            c.drawLine(f.x+px*spread*.7f,f.y+py*spread*.7f,
                f.x+f.dx*len*.88f,f.y+f.dy*len*.88f,p);
            c.drawLine(f.x-px*spread*.7f,f.y-py*spread*.7f,
                f.x+f.dx*len*.88f,f.y+f.dy*len*.88f,p);
        }
    }

    /** Small directional hit flecks, spawned at the actual damage point. */
    void hitBloodV129(float x,float y,float impulseX,float impulseY,int amount){
        float length=Math.max(.001f,(float)Math.hypot(impulseX,impulseY));
        float dx=impulseX/length,dy=impulseY/length;
        for(int i=0;i<Math.max(2,Math.min(9,amount));i++){
            float speed=30f+rng.nextFloat()*115f;
            float sway=(rng.nextFloat()-.5f)*.85f;
            Spark drop=new Spark(x,y,
                (dx-dy*sway)*speed,(dy+dx*sway)*speed,
                (i&1)==0?0xffa33b37:0xff741e21);
            drop.ttl=.18f+rng.nextFloat()*.28f;
            sparks.add(drop);
        }
    }
    void damageDirectionalV129(Bandit enemy,float amount,float dx,float dy){
        if(enemy==null||!enemy.active)return;
        hitBloodV129(enemy.x,enemy.y-47,dx,dy,6);
        damage(enemy,amount);
    }
    void hurtDirectionalV129(float amount,float dx,float dy){
        hitBloodV129(playerX,playerY-47,dx,dy,6);
        hurt(amount);
    }
    /** Brief muzzle illumination of actual indoor floors, never of hidden walls. */
    void drawIndoorMuzzleLightV129(Canvas c){
        if(!host.option("gunMuzzleV119",true)||flashes.isEmpty())return;
        c.save();c.clipPath(clinicVisionPathV90);
        for(Flash f:flashes){
            if(f.ttl<=0||!WorldPerfV55.nearView(f.x,f.y,camX,camY,
                    viewW,viewH,170f))continue;
            float strength=GunEffectsV119.alpha(f.ttl);
            int alpha=Math.round(strength*205f);
            p.setStyle(Paint.Style.FILL);
            p.setShader(new android.graphics.RadialGradient(f.x,f.y,235f,
                new int[]{(alpha<<24)|0x00ffd3a1,
                          ((alpha/3)<<24)|0x00db9f55,0},
                new float[]{0f,.38f,1f},
                android.graphics.Shader.TileMode.CLAMP));
            c.drawCircle(f.x,f.y,235f,p);
            p.setShader(null);
        }
        c.restore();
    }
    /** V131: head damage uses the exact V5-fitted 200-character art, not V31. */
    float firstHeadImpactV131(float x0,float y0,float x1,float y1,
            float actorX,float actorY,int facing,int skin,boolean walking,
            float tilt,boolean player){
        if(characterSkinsV109==null||!characterSkinsV109.ready())
            return Float.POSITIVE_INFINITY;
        float[] local=characterSkinsV109.headBoundsLocalV131(
            skin,CharacterCollision.BASE_SCALE*scale,
            player?fitHeadXV108:npcHeadFitXV113,
            player?fitHeadYV108:npcHeadFitYV113,
            player?playerHeadSizeV113:npcHeadSizeV113,
            player?fitIdleBreathV108:npcBreathPixelsV113,
            player?idleBreathingTempoV110:npcBreathingTempoV113,
            worldTimer,walking);
        if(local==null)return Float.POSITIVE_INFINITY;
        float[] bounds=HeadCollisionV131.worldBounds(
            actorX,actorY,facing,local[0],local[1],local[2],local[3],tilt);
        return HeadCollisionV131.firstHit(x0,y0,x1,y1,bounds);
    }
    void damage(Bandit enemy,float amount){
        enemy.hp-=amount;enemy.hit=.14f;
        particles(enemy.x,enemy.y-34,RED,2);
        if(enemy.hp<=0&&enemy.active){
            enemy.active=false;kills++;particles(enemy.x,enemy.y-24,ORANGE,7);
            BanditLootV87.Bag remains=banditLootV87.spawnCorpse(
                enemy.x,enemy.y-3,kills,wave,enemy.variant,enemy.face,
                enemy.skinV109);
            if(remains!=null&&!lootEnabled)
                java.util.Arrays.fill(remains.count,0);
            saveProgress(); // The body persists even with loot drops disabled.
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
        droppedExpiryClockV129+=dt;
        if(droppedExpiryClockV129>=1f){
            droppedExpiryClockV129=0f;
            int before=droppedItemsV129.stacks.size();
            droppedItemsV129.expire(gameTimeV129());
            if(before!=droppedItemsV129.stacks.size())saveProgress();
        }
        refreshDaylight();
        dt=Math.min(.04f,dt)*timeSpeed;
        worldTimer+=dt;autSaveClock+=dt;
        // Head alone gently follows aim pitch, same in the world and interiors.
        // Never alter ballistic angle, aim stick, weapon/hands or character body.
        playerHeadTiltV111=HeadAimV111.follow(playerHeadTiltV111,
            HeadAimV111.targetDegrees(Ballistics.angle(aimX,aimY,face),
                headAimMaxDegreesV111),dt);
        if(insideClinicV89){
            updateClinicV89(dt);
            if(autSaveClock>9f){saveProgress();autSaveClock=0f;}
            return; // No outdoor world physics, hostile NPCs, spawn or lighting.
        }
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
            float speed=PlayerMovementV77.speed(gun==9?169f:236f,walkSpeedMultiplier,runMultiplier,crouchHeld)*carrySpeedV91();
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
        playerAnimation.step(moving,dt,CharacterFitV108.rate(
            PlayerMovementV77.gait(walkSpeedMultiplier,runHeld&&stamina>0)*
            walkingAnimationMultiplierV79,fitWalkFpsV108));
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
            float rigScale=CharacterCollision.BASE_SCALE*scale;
            float[] muzzle=Ballistics.rigMuzzle(playerX,playerY,face,aimX,aimY,
                rigScale,MX[gun],MY[gun],MAIN_X[gun],MAIN_Y[gun],0f);
            WeaponPivotV117.relocateMuzzle(muzzle,face,rigScale,
                playerGunPivotXV117,playerGunPivotYV117);
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
                    shoot(playerX,playerY,aimX,aimY,gun,false,face,true);
                    if(gun!=3){
                        shotClock=RATES[gun];
                        if(GunEffectsV118.firearm(gun))ammo=Math.max(0,ammo-1);
                        recoil=GunEffectsV118.firearm(gun)&&recoilFX?1:0;
                    }
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
                float tryX=npc.homeX+(float)Math.sin(worldTimer*.41f+i)*18f;
                float tryY=npc.homeY+(float)Math.cos(worldTimer*.41f+i)*11f;
                if(!industrialModeV123||IndustrialCampV125.patrolAllowed(
                    tryX,tryY,industrialSeedV123)){npc.x=tryX;npc.y=tryY;}
                else {npc.x=npc.homeX;npc.y=npc.homeY;}
            }
            // All camp roles scan a full circle instead of holding a
            // horizontal weapon. Noncombatant NPCs still never fire guns.
            float desireX=NpcAimV122.scanX(worldTimer,i+4);
            float desireY=NpcAimV122.scanY(worldTimer,i+4);
            Bandit threat=nearest(npc.x,npc.y,500f);
            if(threat!=null) {
                float[] toward=NpcAimV122.toward(
                    npc.x,npc.y,threat.x,threat.y);
                desireX=toward[0];desireY=toward[1];
            }
            float[] look=NpcAimV122.turn(npc.aimX,npc.aimY,
                desireX,desireY,dt);
            npc.aimX=look[0];npc.aimY=look[1];
            npc.face=NpcAimV122.facing(npc.aimX,npc.face);
            // The existing armed camp guard now actually shoots: no more
            // invisible magic hits on raiders. Use the same physical Shot
            // bullets and restrained V119 muzzle effects as the player.
            if(npc.gun!=3&&threat!=null&&npc.cd<=0f&&
                NpcAimV122.aligned(npc.aimX,npc.aimY,desireX,desireY)&&
                banditHasLineOfSightV88(npc.x,npc.y-30f,threat.x,threat.y-30f)){
                shoot(npc.x,npc.y,npc.aimX,npc.aimY,npc.gun,false,npc.face,false);
                npc.cd=RATES[npc.gun]+.28f;
            }
            npc.cd=Math.max(0f,npc.cd-dt);
            npc.animation.step(distance(px,py,npc.x,npc.y)>.001f,dt,
                CharacterFitV108.rate(7.1f,fitWalkFpsV108));
        }
        if(moving&&length>.13f){
            followHeadingX=vx;followHeadingY=vy;
        }
        for(int fi=0;fi<friends.size();fi++){
            Survivor friend=friends.get(fi);
            float beforeFriendX=friend.x,beforeFriendY=friend.y;
            friend.cd=Math.max(0,friend.cd-dt);
            float gx=CompanionOrdersV118.targetX(playerX,followHeadingX,followHeadingY,
                followMode,fi,friends.size(),followSpacing);
            float gy=CompanionOrdersV118.targetY(playerY,followHeadingX,followHeadingY,
                followMode,fi,friends.size(),followSpacing);
            if(companionStayV118){gx=friend.x;gy=friend.y;}
            // Repel overlapping followers even when multiple follow slots coincide
            // with the same obstacle. No teleport or body/rig alterations.
            float repelX=0f,repelY=0f;
            for(int other=0;other<friends.size()&&!companionStayV118;other++){
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
            friend.animation.step(FollowerArrivalV78.visuallyWalking(
                distance(friend.x,friend.y,beforeFriendX,beforeFriendY)),dt,
                CharacterFitV108.rate(8.5f,fitWalkFpsV108));
            Bandit target=nearest(friend.x,friend.y,460);
            float wantX=NpcAimV122.scanX(worldTimer,fi+17);
            float wantY=NpcAimV122.scanY(worldTimer,fi+17);
            if(target!=null){
                float[] desired=NpcAimV122.toward(
                    friend.x,friend.y,target.x,target.y);
                wantX=desired[0];wantY=desired[1];
            }
            float[] heading=NpcAimV122.turn(friend.aimX,friend.aimY,
                wantX,wantY,dt);
            friend.aimX=heading[0];friend.aimY=heading[1];
            friend.face=NpcAimV122.facing(friend.aimX,friend.face);
            if(target!=null&&friend.cd<=0f&&!companionHoldFireV118&&
                NpcGunfireV122.firearm(friend.gun)&&
                NpcAimV122.aligned(friend.aimX,friend.aimY,wantX,wantY)&&
                banditHasLineOfSightV88(friend.x,friend.y-30f,target.x,target.y-30f)){
                shoot(friend.x,friend.y,friend.aimX,friend.aimY,
                    friend.gun,false,friend.face,false);
                friend.cd=RATES[friend.gun]+.2f;
            }
        }
        if(enemyAI)for(Bandit e:enemies){
            if(!e.active)continue;
            if(WorldPerfV55.distantFrom(e.x,e.y,playerX,playerY,npcSleepRadius)){
                e.animation.reset();continue; // dormant actors stay off simulation
            }
            float oldX=e.x,oldY=e.y;
            e.cd-=dt;e.hit=Math.max(0,e.hit-dt);e.patrolClock+=dt;
            float d=distance(e.x,e.y,playerX,playerY);
            float dx=(playerX-e.x)/Math.max(1,d),dy=(playerY-e.y)/Math.max(1,d);
            if(!WorldSafetyV92.hostileAllowed(e.x,e.y,CAMP_X,CAMP_Y)){
                float rx=e.x-CAMP_X,ry=e.y-CAMP_Y,rl=(float)Math.hypot(rx,ry);
                float heading=(float)(e.variant*2.39996323);
                if(rl<1f){rx=(float)Math.cos(heading);ry=(float)Math.sin(heading);rl=1;}
                float safeDist=WorldSafetyV92.CAMP_SAFE_RADIUS+30f;
                e.x=CAMP_X+rx/rl*safeDist;e.y=CAMP_Y+ry/rl*safeDist;
                e.animation.reset();continue;
            }
            // V122 guard defense uses visible physical shots and muzzle
            // flashes in the campStaff loop, not invisible damage.
            boolean clear=banditHasLineOfSightV88(e.x,e.y-30,playerX,playerY-32);
            int state=BanditBrainV88.state(d,e.hp,banditNearCoverV88(e.x,e.y));
            if(!clear&&state==BanditBrainV88.GUARD)state=BanditBrainV88.STRAFE;
            int side=(e.variant%2==0?1:-1);
            float mx=BanditBrainV88.moveX(state,dx,dy,side),
                my=BanditBrainV88.moveY(state,dx,dy,side);
            if(state==BanditBrainV88.PATROL){
                // Wanders a short arc near its original spawn, instead of freezing.
                float homeDistance=distance(e.x,e.y,e.homeX,e.homeY);
                if(homeDistance>125){
                    float heading=(float)Math.atan2(e.homeY-e.y,e.homeX-e.x);
                    mx=(float)Math.cos(heading);my=(float)Math.sin(heading);
                }else{
                    mx=(float)Math.cos(e.patrolClock*.68f+e.variant*2.3f);
                    my=(float)Math.sin(e.patrolClock*.68f+e.variant*2.3f);
                }
            }
            // Obstacle-aware slide is stable at different render frame rates.
            float speed=BanditBrainV88.speed(state)*dt;
            float nx=e.x+mx*speed,ny=e.y+my*speed;
            if(WorldSafetyV92.hostileAllowed(nx,e.y,CAMP_X,CAMP_Y)&&
                !blocked(nx,e.y,18))e.x=nx;
            else if(WorldSafetyV92.hostileAllowed(e.x-my*speed,e.y,CAMP_X,CAMP_Y)&&
                !blocked(e.x-my*speed,e.y,18))e.x-=my*speed;
            if(WorldSafetyV92.hostileAllowed(e.x,ny,CAMP_X,CAMP_Y)&&
                !blocked(e.x,ny,18))e.y=ny;
            else if(WorldSafetyV92.hostileAllowed(e.x,e.y+mx*speed,CAMP_X,CAMP_Y)&&
                !blocked(e.x,e.y+mx*speed,18))e.y+=mx*speed;
            float scanX=NpcAimV122.scanX(worldTimer,e.variant+32);
            float scanY=NpcAimV122.scanY(worldTimer,e.variant+32);
            boolean tracking=d<BanditBrainV88.ALERT_RANGE&&clear;
            float desireX=tracking?dx:scanX,desireY=tracking?dy:scanY;
            float[] facingAim=NpcAimV122.turn(e.aimX,e.aimY,
                desireX,desireY,dt);
            e.aimX=facingAim[0];e.aimY=facingAim[1];
            e.face=NpcAimV122.facing(e.aimX,e.face);
            if(WorldSafetyV92.hostileAllowed(playerX,playerY,CAMP_X,CAMP_Y)&&
                BanditBrainV88.shouldShoot(state,d,e.cd,clear)&&
                NpcAimV122.aligned(e.aimX,e.aimY,dx,dy)){
                shoot(e.x,e.y,e.aimX,e.aimY,0,true,e.face,false);
                e.cd=.95f+(e.variant%3)*.19f;
            }
            e.animation.step(distance(e.x,e.y,oldX,oldY)>.001f,dt,
                CharacterFitV108.rate(state==BanditBrainV88.CHASE?8.5f:6.6f,fitWalkFpsV108));
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
                float headT=firstHeadImpactV131(bullet.x,bullet.y,nx,ny,
                    playerX,playerY,face,playerSkinV109,
                    playerAnimation.isWalking(),playerHeadTiltV111,true);
                float oldBodyT=WorldPerfV55.segmentNearActor(bullet.x,bullet.y,nx,ny,
                    playerX,playerY,scale)?
                    CharacterCollision.firstHit(bullet.x,bullet.y,nx,ny,
                        playerX,playerY,face,playerAnimation.frame(),
                        playerAnimation.isWalking(),playerAnimation.breathOffset(),scale,
                        playerAnimation.isWalking()?walkMask:bodyMask):
                    Float.POSITIVE_INFINITY;
                float t=Math.min(headT,oldBodyT);
                if(t<first){first=t;victim=null;hitPlayer=true;hitCover=false;}
            }else{
                for(Bandit e:enemies)if(e.active){
                    float tilt=HeadAimV111.targetDegrees(
                        Ballistics.angle(e.aimX,e.aimY,e.face),
                        npcHeadAimMaxDegreesV113);
                    float headT=firstHeadImpactV131(bullet.x,bullet.y,nx,ny,
                        e.x,e.y,e.face,e.skinV109,e.animation.isWalking(),
                        tilt,false);
                    float bodyT=WorldPerfV55.segmentNearActor(
                            bullet.x,bullet.y,nx,ny,e.x,e.y,scale)?
                        CharacterCollision.firstHit(bullet.x,bullet.y,nx,ny,
                            e.x,e.y,e.face,e.animation.frame(),
                            e.animation.isWalking(),e.animation.breathOffset(),scale,
                            e.animation.isWalking()?walkMask:bodyMask):
                        Float.POSITIVE_INFINITY;
                    float t=Math.min(headT,bodyT);
                    if(t<first){first=t;victim=e;hitPlayer=false;hitCover=false;}
                }
            }
            if(first<=1f){
                bullet.x+=(nx-bullet.x)*first;
                bullet.y+=(ny-bullet.y)*first;
                if(hitPlayer)hurtDirectionalV129(bullet.damage,bullet.vx,bullet.vy);
                else if(victim!=null)damageDirectionalV129(victim,bullet.damage,
                    bullet.vx,bullet.vy);
                else if(hitCover&&recoilFX)particles(bullet.x,bullet.y,0xffc4b58a,2);
                iter.remove();
            }else if(bullet.life<=0){
                iter.remove();
            }else {bullet.x=nx;bullet.y=ny;}
        }
        updateGunEffectsV119(dt);
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
        if(industrialModeV123)return;
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
            for(float[] f:activeCampfiresV125())fireLight(f[0],f[1]);
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
                WeaponPivotV117.relocateMuzzle(tip,face,CharacterCollision.BASE_SCALE*scale,
                    playerGunPivotXV117,playerGunPivotYV117);
                lighting.flashlight(tip[0],tip[1],aimX,aimY,flashlightReach);
            }
            int npcFlashlightBudget=2;
            for(Survivor f:friends)if((f.gun==3||(dualTorch&&f.gun<=2))&&
                    npcFlashlightBudget>0&&
                    WorldPerfV55.nearView(f.x,f.y,camX,camY,viewW,viewH,flashlightReach)){
                npcFlashlightBudget--;
                float[] tip=Ballistics.rigMuzzle(f.x,f.y,f.face,f.aimX,f.aimY,
                    CharacterCollision.BASE_SCALE*scale,MX[3],MY[3],MAIN_X[3],MAIN_Y[3],0f);
                WeaponPivotV117.relocateMuzzle(tip,f.face,CharacterCollision.BASE_SCALE*scale,
                    npcGunPivotXV117,npcGunPivotYV117);
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
                WeaponPivotV117.relocateMuzzle(tip,f.face,CharacterCollision.BASE_SCALE*scale,
                    npcGunPivotXV117,npcGunPivotYV117);
                if(WorldPerfV55.nearView(tip[0],tip[1],camX,camY,viewW,viewH,flashlightReach))
                    lighting.flashlight(tip[0],tip[1],fx,0f,flashlightReach);
            }
        }
        // V119 small gunbarrel glint, not V118 90px muzzle light circles or
        // 66px glowing pools around every individual bullet.
        // Bullets remain visible in their own short post-lighting draw pass.
        if(host.option("gunMuzzleV119",true))
            for(Flash f:flashes)if(f.ttl>0f)
                lighting.point(f.x,f.y,240f,
                    .98f*GunEffectsV119.alpha(f.ttl),0xffffd591);
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
        if(industrialModeV123){
            IndustrialSceneV124.outdoors(c,p,camX,camY,viewW,viewH,industrialSeedV123);
            industrialArtV123.outdoors(c,camX,camY,viewW,viewH,industrialSeedV123);
            return;
        }
        boolean industrialCoreV128=stitchedIndustrialV128&&
            IndustrialBiomeBridgeV128.viewportCore(camX,camY,viewW,viewH);
        // Deep inside industry the old biome chunks would be fully covered.
        // Do not stream or paint thousands of invisible woodland tiles there.
        if(!industrialCoreV128){
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
        drawExpeditionSitesV88(c);
        drawSalvageWorldV84(c);
        drawLooseGroundPickupsV85(c);
        }
        // One world, no portal: render the industrial terrain into its world
        // coordinates over the old streamed biome. Render before structures,
        // characters and effects so their depth/aiming systems remain intact.
        if(stitchedIndustrialV128)IndustrialBiomeSceneV128.draw(c,p,
            industrialArtV123,camX,camY,viewW,viewH,industrialSeedV123);
        if(placingKindV84>=0){
            updatePlacementTargetV86();
            c.saveLayerAlpha(placingXv84-72,placingYv84-115,
                placingXv84+72,placingYv84+50,164);
            drawCraftStructureV83(c,new CampCraftV83.Structure(
                placingKindV84,placingXv84,placingYv84));
            c.restore();
            color(0xffdfbe7e);p.setStyle(Paint.Style.STROKE);
            p.setStrokeWidth(2.4f);c.drawCircle(placingXv84,placingYv84,15,p);
            p.setStyle(Paint.Style.FILL);
        }
        for(Cover box:covers)
            if(box.x+box.w>=camX-15&&box.x<=camX+viewW+15&&
               box.y+box.h>=camY-15&&box.y<=camY+viewH+15)
                drawCover(c,box);
        drawSpawnCamp(c);
    }
    /** V80 living biome: V74 trees/rocks become harvestable, plus small fiber shrubs. */
    /** Three small, discoverable pickups, no heavy atlas or bitmap regeneration. */
    void drawLooseGroundPickupsV85(Canvas c){
        int cell=GroundPickupsV85.CELL;
        int x0=(int)Math.floor(camX/cell)-1,x1=(int)Math.ceil((camX+viewW)/cell)+1;
        int y0=(int)Math.floor(camY/cell)-1,y1=(int)Math.ceil((camY+viewH)/cell)+1;
        for(int cy=y0;cy<=y1;cy++)for(int cx=x0;cx<=x1;cx++)
        for(int kind=0;kind<GroundPickupsV85.SLOTS;kind++){
            if(groundPickupsV85.collected(cx,cy,kind))continue;
            int seed=GroundPickupsV85.seed(cx,cy,kind);
            float x=GroundPickupsV85.worldX(cx,seed),y=GroundPickupsV85.worldY(cy,seed);
            if(x<camX-60||x>camX+viewW+60||y<camY-60||y>camY+viewH+60||
               !GroundPickupsV85.placed(kind,seed,x,y,CAMP_X,CAMP_Y))continue;
            // V86 irregular ground silhouettes; never draw framed inventory icons.
            color(0x99101c1a);c.drawOval(x-18,y-8,x+18,y+5,p);
            if(kind==GroundPickupsV85.STONE){
                rect(c,x-17,y-11,30,13,0xff182628);
                rect(c,x-12,y-17,23,15,0xff516a70);
                rect(c,x-5,y-22,10,7,0xffa3b0a7);
                rect(c,x-15,y-6,10,6,0xff384d4f);
                rect(c,x+5,y-14,7,8,0xff83988e);
            }else if(kind==GroundPickupsV85.WOOD){
                rect(c,x-24,y-10,47,15,0xff15251f);
                rect(c,x-21,y-8,42,11,0xff6d5139);
                rect(c,x-16,y-7,29,3,0xffb48e58);
                rect(c,x+14,y-7,5,10,0xffcfaa71);
                rect(c,x-4,y-15,7,10,0xff293627);
                rect(c,x-2,y-12,4,7,0xffa47a4e);
            }else{
                rect(c,x-20,y-11,42,16,0xff17272a);
                rect(c,x-17,y-12,30,11,0xff865740);
                rect(c,x-14,y-10,22,3,0xffb48154);
                rect(c,x+10,y-20,10,20,0xff2b4042);
                rect(c,x+13,y-17,5,12,0xffa5b3a8);
                rect(c,x-13,y-7,4,4,0xffc0ab80);
                rect(c,x+3,y-6,4,4,0xff44595d);
            }
        }
    }
    /** USE immediately picks up small items, unlike axe/pick/crowbar resources. */
    boolean collectIndustrialYardV123(){
        if((!industrialModeV123&&!stitchedIndustrialV128)||insideClinicV89||
                !playing||paused)return false;
        if(stitchedIndustrialV128&&
           !IndustrialBiomeBridgeV128.hasIndustrialLoot(
                playerX,playerY,industrialSeedV123))return false;
        IndustrialYardV123.Stock found=industrialYardV123.nearest(
            stitchedIndustrialV128?IndustrialBiomeBridgeV128.localX(playerX):playerX,
            stitchedIndustrialV128?IndustrialBiomeBridgeV128.localY(playerY):playerY,
            industrialSeedV123);
        if(found!=null&&stitchedIndustrialV128&&
           !IndustrialBiomeBridgeV128.industrialPlot(found.district.sx,
                                                      found.district.sy))return false;
        if(found==null||!industrialYardV123.collect(found))return false;
        int n=found.quantity();
        if(found.slot==2)fieldFindsV91.items[2]+=n;
        else if(found.slot==3)fieldFindsV91.items[9]+=n;
        else scrap+=n;
        gatherFeedback="SALVAGED "+found.name()+" +"+n;
        gatherFeedbackTime=2.8f;
        saveProgress();invalidate();return true;
    }
    boolean pickupGroundV85(){
        GroundPickupsV85.Item item=groundPickupsV85.nearest(playerX,playerY,
            GroundPickupsV85.REACH,CAMP_X,CAMP_Y);
        if(item==null||!groundPickupsV85.collect(item))return false;
        if(item.slot==GroundPickupsV85.STONE)stone+=item.quantity();
        else if(item.slot==GroundPickupsV85.WOOD)wood+=item.quantity();
        else scrap+=item.quantity();
        gatherFeedback="PICKED UP "+item.label()+" +"+item.quantity();
        gatherFeedbackTime=2f;saveProgress();return true;
    }
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
                int kind=k==3?ResourceWorldV80.BUSH:k==2&&
                    x>=0&&x<=WORLD_W&&y>=0&&y<=WORLD_H?4:BiomeWorldV74.prop(x,y,h);
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
        if(box.kind==3||box.kind==4)return; // player builds and authored V88 POIs drawn in their own passes.
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
        // Fit is applied to the head crop only; torso and planted feet never shift.
        float bob=CharacterFitV108.breath(breath,fitIdleBreathV108)*s;
        float dx=fitHeadXV108*s,dy=fitHeadYV108*s;
        src.set(sx+HeadKnifeV82.HEAD_LEFT,sy+HeadKnifeV82.HEAD_TOP,
                sx+HeadKnifeV82.HEAD_RIGHT,sy+HeadKnifeV82.HEAD_BOTTOM);
        dest.set(HeadKnifeV82.headLeft(s,headScaleV82)+dx,
                 HeadKnifeV82.headTop(s,headScaleV82,bob)+dy,
                 HeadKnifeV82.headRight(s,headScaleV82)+dx,
                 HeadKnifeV82.headBottom(s,bob)+dy);
        c.drawBitmap(atlas,src,dest,pixel);
    }
    void stablePose(Canvas c,Bitmap walkingAtlas,int variant,int frame,float s,float breath,int torsoVariant){
        final boolean isNpc=variant>=0;
        final Bitmap baseIdle=isNpc?npcIdleV56:body;
        final Bitmap approvedTorso=torsoVariant>=0?
            torsoRecolorV98.frame(baseIdle,npcIdleV56,variant,torsoVariant):null;
        final int idleX=approvedTorso!=null?0:(isNpc?0:APPROVED_PLANTED_IDLE_FRAME*260);
        final int idleY=approvedTorso!=null?0:(isNpc?Math.min(11,variant)*160:0);
        final Bitmap selectedIdle=approvedTorso!=null?approvedTorso:baseIdle;
        if(breath==Float.POSITIVE_INFINITY){
            if(walkingAtlas==null)return;
            if(CharacterFitV108.separateHead(headScaleV82,fitHeadXV108,fitHeadYV108,fitIdleBreathV108)){
                int row=Math.max(0,variant)*160;
                int f=Math.max(0,Math.min(3,frame));
                src.set(f*260,row+110,f*260+260,row+160);
                dest.set(-70*s,(110-136)*s,190*s,24*s);
                c.drawBitmap(walkingAtlas,src,dest,pixel);
                boolean npc=variant>=0;
                Bitmap locked=selectedIdle;
                if(locked==null)return;
                int sx=idleX;
                int sy=idleY;
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
            Bitmap locked=selectedIdle;
            if(locked==null)return;
            int sx=idleX;
            int sy=idleY;
            src.set(sx,sy,sx+260,sy+split);
            dest.set(-70*s,-136*s,190*s,(split-136)*s);
            c.drawBitmap(locked,src,dest,pixel);
            return;
        }
        // Original planted idle source, NOT a walking pose reconstructed in V51.
        // Approved NPC role colors are applied to an otherwise identical silhouette.
        final boolean npc=variant>=0;
        Bitmap idleSource=selectedIdle;
        if(idleSource==null)return;
        int sx=idleX;
        int sy=idleY;
        if(CharacterFitV108.separateHead(headScaleV82,fitHeadXV108,fitHeadYV108,fitIdleBreathV108)){
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
        character(c,x,y,weapon,facing,frame,breath,aimAng,kick,player,bandit,npcVariant,
            player?playerSkinV109:1+Math.floorMod(npcVariant*17+37,200));
    }
    void character(Canvas c,float x,float y,int weapon,int facing,int frame,float breath,float aimAng,float kick,
                   boolean player,boolean bandit,int npcVariant,int skinIdV109){
        float s=CharacterCollision.BASE_SCALE*scale;
        c.save();c.translate(x,y);if(facing<0)c.scale(-1,1);
        color(0x670b1a18);c.drawOval(-26*s,-7*s,26*s,7*s,p);
        // V96: approved backpack-only pixels behind the immutable body atlas.
        if(characterSkinsV109==null){ // legacy equipment is hidden in the 200-character test
            if(player&&fieldFindsV91.equipped>=0)
                wearableArtV96.drawPack(c,backpackStyleV96,s,pixel);
            else if(!player&&npcVariant>=0&&(npcVariant%3)!=0)
                wearableArtV96.drawPack(c,Math.floorMod(npcVariant*7+11,20),s,pixel);
        }
        // V58 rear-layer hand torch. Draw BEFORE the immutable original body:
        // its silhouette cannot cover the head, eyes, or facial outline.
        if(!bandit&&!(player&&harvestV81.active)&&dualTorch&&lampOn&&weapon>=0&&weapon<=2&&showWeapons){
            c.save();
            int lightFitX=player?playerGunPivotXV117:npcGunPivotXV117;
            int lightFitY=player?playerGunPivotYV117:npcGunPivotYV117;
            c.translate(-30*s+WeaponPivotV117.localX(lightFitX,s),
                -33*s+WeaponPivotV117.localY(lightFitY,s));
            c.rotate(aimRotation?aimAng*180f/(float)Math.PI:0f);
            c.scale(.50f,.50f);
            atlas(c,gear,3*260,0,0,0,s);
            drawFlashlightLens(c,s);
            if(showHands)handAtlas(c,3,2,0,0,s,handScale,0,0);
            c.restore();
        }
        if(characterSkinsV109!=null&&characterSkinsV109.ready()){
            characterSkinsV109.draw(c,skinIdV109,
                !renderingCorpseV130&&breath==Float.POSITIVE_INFINITY,
                renderingCorpseV130?0:frame,
                renderingCorpseV130?0f:worldTimer,s,pixel,
                player?walkingAnimationMultiplierV79:npcWalkingAnimationTempoV113,
                player?idleBreathingTempoV110:npcBreathingTempoV113,
                player?fitWalkFpsV108:npcWalkFpsV113,
                renderingCorpseV130?0:(player?fitIdleBreathV108:npcBreathPixelsV113),
                renderingCorpseV130?0:(player?playerHeadTiltV111:
                    HeadAimV111.targetDegrees(aimAng,npcHeadAimMaxDegreesV113)),
                player?fitHeadXV108:npcHeadFitXV113,
                player?fitHeadYV108:npcHeadFitYV113,
                player?playerHeadSizeV113:npcHeadSizeV113,
                player?playerTorsoWidthV114:npcTorsoWidthV114,
                player?playerPelvisWidthV115:npcPelvisWidthV115);
        }else{
            Bitmap atlas=npcVariant>=0?npcWalkV56:approvedWalkColors;
            int torsoVariant=player?wardrobeV92.equipped[1]:
                WardrobeV92.npcOutfit(Math.max(0,npcVariant),1);
            stablePose(c,atlas,npcVariant,frame,s,breath,torsoVariant);
            drawWardrobeV92(c,s,breath,player,bandit,npcVariant);
        }
        if(renderingCorpseV130){c.restore();return;}
        if(player&&harvestV81.active)drawHarvestRigV81(c,s);
        else if(player&&knifeDuration>0f)drawKnifeSwing(c,s);
        else if(characterSkinsV109!=null||!bandit){
            c.save();
            // Keep the accepted V36 torso-centered weapon/hand rig stationary.
            // Parent pivot is the CHARACTER'S torso center (constant across all weapons).
            // The approved weapon, main hand and support hand remain rigid sibling
            // sprites: one translation to an in-reach chest grip, then one shared rotation.
            final float pivotX=(Ballistics.TORSO_X-70f)*s;
            final float pivotY=(Ballistics.TORSO_Y-136f)*s;
            final float offsetX=(Ballistics.GRIP_X-MAIN_X[weapon])*s;
            final float offsetY=(Ballistics.GRIP_Y-MAIN_Y[weapon])*s;
            // Relocate the entire rotation axis and its weapon/two-hand rig.
            // Both hands retain original contact points; recoil and aim unchanged.
            int actorFitX=player?playerGunPivotXV117:npcGunPivotXV117;
            int actorFitY=player?playerGunPivotYV117:npcGunPivotYV117;
            c.translate(pivotX-kick+WeaponPivotV117.localX(actorFitX,s),
                pivotY+WeaponPivotV117.localY(actorFitY,s));
            float displayedAngleV118=aimRotation?aimAng*180f/(float)Math.PI:0f;
            if(player&&weapon==11&&axeSwingTimeV118>0f){
                float phase=1f-axeSwingTimeV118/.25f;
                displayedAngleV118+=-35f+75f*(float)Math.sin(Math.PI*phase);
            }
            c.rotate(displayedAngleV118);
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
        }else if(characterSkinsV109==null){
            // Legacy-only bandit body decoration, hidden in V109 test mode.
            rect(c,-16*s,-100*s,27*s,5*s,RED);
            rect(c,-16*s,-90*s,12*s,5*s,0xffad5b52);
        }
        if(hitboxes&&characterSkinsV109!=null&&characterSkinsV109.ready()){
            int id=player?playerSkinV109:skinIdV109;
            float[] hbox=characterSkinsV109.headBoundsLocalV131(
                id,CharacterCollision.BASE_SCALE*scale,
                player?fitHeadXV108:npcHeadFitXV113,
                player?fitHeadYV108:npcHeadFitYV113,
                player?playerHeadSizeV113:npcHeadSizeV113,
                player?fitIdleBreathV108:npcBreathPixelsV113,
                player?idleBreathingTempoV110:npcBreathingTempoV113,
                worldTimer,breath==Float.POSITIVE_INFINITY);
            if(hbox!=null){
                p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.3f);
                color(0xffebc779);
                c.drawRect(hbox[0]-3f,hbox[1]-3f,hbox[2]+3f,hbox[3]+3f,p);
                p.setStyle(Paint.Style.FILL);
            }
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
    /** Separate rear-layer pixel silhouette, attached to player pose, no body atlas edits. */
    /** Retained compatibility entry point; draws authored gear, not rectangles. */
    void drawEquippedPackV91(Canvas c,float size,int kind){
        if(kind>=0)wearableArtV96.drawPack(c,backpackStyleV96,size,pixel);
    }
    /** Gear-only layers from prior authored art, never procedural replacements. */
    void drawWardrobeV92(Canvas c,float size,float breath,boolean player,boolean bandit,int variant){
        int role=variant<0?0:variant;
        int head=player?wardrobeV92.equipped[0]:WardrobeV92.npcOutfit(role,0);
        int torso=player?wardrobeV92.equipped[1]:WardrobeV92.npcOutfit(role,1);
        int legs=player?wardrobeV92.equipped[2]:WardrobeV92.npcOutfit(role,2);
        int boots=player?wardrobeV92.equipped[3]:WardrobeV92.npcOutfit(role,3);
        if(head>=0){
            int artwork=player?headgearStyleV96:Math.floorMod(role*5+1,4);
            float bob=breath==Float.POSITIVE_INFINITY?0f:
                CharacterFitV108.breath(breath,fitIdleBreathV108)*size;
            c.save();
            c.translate(fitHeadXV108*size,fitHeadYV108*size);
            wearableArtV96.drawHead(c,artwork,size,bob,headScaleV82,pixel);
            c.restore();
        }
        // V98: normal jackets recolor original torso interior inside stablePose.
        // There must be NO external torso/vest bitmap overlay.
        // Approved character's leg/boot pixels stay immutable until correctly
        // registered animation-specific gear sheets are available.
        // Equipping pants or boots still updates inventory and save data.
    }
    void drawSpeechV92(Canvas c,float x,float y,int code,int attitude,boolean threat){
        if(distance(playerX,playerY,x,y)>445f)return;
        float phase=(worldTimer+code*2.13f)%11.7f;
        if(phase>3.5f)return;
        String message=relationshipsV92.speech(attitude,
            ((int)(worldTimer/11.7f)+code),threat);
        float width=19f+message.length()*7.1f;
        float left=x-width*.5f,top=y-165f;
        rounded(c,left,top,width,27f,5f,0xdd152a29);
        label(c,message,left+9,top+18,12,
            attitude==NPCRelationshipsV92.HOSTILE?0xffef9e91:0xffe6e3c4,true);
    }
    /** Each luminaire illuminates the FLOOR, not the characters or equipment.
      * Clip by individual rooms so falloff cannot shine through interior walls. */
    void drawIndoorFloorIlluminationV93(Canvas c){
        final int[][] lamps={{260,225},{790,225},{1310,225},
            {260,845},{790,845},{1310,845},{800,562}};
        boolean electric=activeSiteV91==1||(activeSiteV91>=0&&
            activeSiteV91<ExpeditionSitesV88.SITES.length&&
            (ExpeditionSitesV88.SITES[activeSiteV91].kind==ExpeditionSitesV88.RELAY||
             ExpeditionSitesV88.SITES[activeSiteV91].kind==ExpeditionSitesV88.MOTEL));
        int tint=electric?0x226b9c9d:0x267d6044;
        for(int i=0;i<lamps.length;i++){
            float x=lamps[i][0],y=lamps[i][1];
            if(!WorldPerfV55.nearView(x*ClinicInteriorV89.EXPANSION_V90,
                y*ClinicInteriorV89.EXPANSION_V90,
                camX,camY,viewW,viewH,530f))continue;
            float x0=i==6?23f:(i%3==0?23f:i%3==1?551f:1071f);
            float x1=i==6?1577f:(i%3==0?530f:i%3==1?1050f:1577f);
            float y0=i==6?508f:i<3?44f:642f;
            float y1=i==6?620f:i<3?486f:1070f;
            c.save();c.clipRect(x0,y0,x1,y1);
            float range=i==6?125f:260f;
            p.setColor(0xffffffff);
            p.setShader(new android.graphics.RadialGradient(x,y,range,
                new int[]{tint,electric?0x126c9196:0x12796346,0x00000000},
                new float[]{0f,.45f,1f},android.graphics.Shader.TileMode.CLAMP));
            c.drawCircle(x,y,range,p);
            p.setShader(null);
            c.restore();
        }
    }
    /** Scene fixture is a solid object, NOT an additive circle rendered over actors. */
    void drawIndoorLightFixturesV93(Canvas c){
        float z=ClinicInteriorV89.EXPANSION_V90;
        final int[][] lamps={{260,225},{790,225},{1310,225},
            {260,845},{790,845},{1310,845},{800,562}};
        boolean electric=activeSiteV91==1||(activeSiteV91>=0&&
            activeSiteV91<ExpeditionSitesV88.SITES.length&&
            (ExpeditionSitesV88.SITES[activeSiteV91].kind==ExpeditionSitesV88.RELAY||
             ExpeditionSitesV88.SITES[activeSiteV91].kind==ExpeditionSitesV88.MOTEL));
        for(int[] l:lamps){
            float x=l[0]*z,y=l[1]*z;
            if(!WorldPerfV55.nearView(x,y,camX,camY,viewW,viewH,50f))continue;
            rect(c,x-15,y-9,30,18,0xff172c2c);
            rect(c,x-12,y-6,24,12,electric?0xff5d9296:0xff795c3e);
            rect(c,x-9,y-4,18,8,electric?0xffb2d8d1:0xffd4ad76);
            rect(c,x-3,y-2,6,4,electric?0xffe3faed:0xffffdda0);
        }
    }
    /** All speech draws after terrain light masks, indoor vision, and actors. */
    void drawIndoorSpeechAfterLightingV93(Canvas c){
        // Dialogue indicators must not reveal unseen NPCs through walls or fog.
        c.save();
        c.clipPath(clinicVisionPathV90);
        for(ClinicActorsV90.Actor a:clinicActorsV90.actors){
            if(!a.active||a.type==ClinicActorsV90.FERAL||
                    !indoorCharacterVisibleV127(a.x,a.y))continue;
            drawSpeechV92(c,a.x,a.y,a.type,
                a.hostile()?NPCRelationshipsV92.HOSTILE:NPCRelationshipsV92.FRIENDLY,
                distance(playerX,playerY,a.x,a.y)<255f);
        }
        for(Survivor f:friends){
            if(!indoorCharacterVisibleV127(f.x,f.y))continue;
            drawSpeechV92(c,f.x,f.y,f.variant+30,NPCRelationshipsV92.FRIENDLY,false);
        }
        c.restore();
    }
    void drawOutdoorSpeechAfterLightingV93(Canvas c){
        for(Bandit e:enemies)if(e.active)drawSpeechV92(c,e.x,e.y,
            e.variant+20,NPCRelationshipsV92.HOSTILE,
            distance(e.x,e.y,playerX,playerY)<420f);
        for(Survivor f:friends)drawSpeechV92(c,f.x,f.y,f.variant+30,
            NPCRelationshipsV92.FRIENDLY,nearest(f.x,f.y,430f)!=null);
        for(Survivor npc:campStaff)drawSpeechV92(c,npc.x,npc.y,npc.variant,
            npc.variant==ROLE_GUARD+1?NPCRelationshipsV92.FRIENDLY:
            NPCRelationshipsV92.NEUTRAL,nearest(npc.x,npc.y,400f)!=null);
    }

    /** Fallen sprites are frozen: no animation clock, head movement or breathing. */
    boolean renderingCorpseV130=false;
    void drawFallenAnimalV130(Canvas c,float x,float y){
        // Feral dogs keep their animal form after death, rather than inheriting
        // the generic human rig. All pieces are static and remain near the ground.
        color(0x865a2020);c.drawOval(x-32,y-10,x+34,y+9,p);
        rect(c,x-28,y-24,53,16,0xff172925);
        rect(c,x-25,y-28,47,15,0xff665e47);
        rect(c,x+15,y-37,20,19,0xff263d34);
        rect(c,x+19,y-34,14,13,0xff8c7c53);
        rect(c,x+30,y-23,14,7,0xff7f674c);
        rect(c,x-37,y-24,13,5,0xff665e47);
        rect(c,x-18,y-10,8,6,0xff222e28);
        rect(c,x+12,y-10,8,6,0xff222e28);
    }
    /** A fallen body is itself the searchable object; approved pixels preserved. */
    void drawFallenBodyV129(Canvas c,float x,float y,int variant,int skin,int facing){
        color(0x7c592021);c.drawOval(x-34,y-19,x+35,y+10,p);
        color(0x9b742427);c.drawOval(x-22,y-14,x+18,y+4,p);
        c.save();c.rotate(facing<0?-85f:85f,x,y-47f);
        renderingCorpseV130=true;
        try {
            character(c,x,y,0,facing,0,0f,0f,0f,false,true,variant,skin);
        }finally{renderingCorpseV130=false;c.restore();}
    }
    void drawIndoorCorpsesV129(Canvas c){
        for(ClinicActorsV90.Actor actor:clinicActorsV90.actors){
            if(actor.active||!WorldPerfV55.nearView(actor.x,actor.y,
                camX,camY,viewW,viewH,150f)||
                !indoorCharacterVisibleV127(actor.x,actor.y))continue;
            int skin=1+Math.floorMod(actor.type*31+37,200);
            if(actor.type==ClinicActorsV90.FERAL)
                drawIndoorVisibleEntityV127(c,()->drawFallenAnimalV130(c,
                    actor.x,actor.y));
            else{
                int appearance=actor.type==ClinicActorsV90.MEDIC?ROLE_MEDIC:
                    actor.type==ClinicActorsV90.SURVIVOR?ROLE_CIVILIAN:0;
                drawIndoorVisibleEntityV127(c,()->drawFallenBodyV129(c,
                    actor.x,actor.y,appearance,skin,(actor.type&1)==0?1:-1));
            }
        }
    }
    int nearestIndoorCorpseV129(){
        if(!insideClinicV89)return -1;
        float closest=120f*120f;int found=-1;
        for(int i=0;i<clinicActorsV90.actors.length;i++){
            ClinicActorsV90.Actor actor=clinicActorsV90.actors[i];
            if(actor.active)continue;
            float dx=actor.x-playerX,dy=actor.y-playerY;
            float distance=dx*dx+dy*dy;
            if(distance<closest){closest=distance;found=i;}
        }
        return found;
    }
    String indoorCorpseKeyV129(){return "indoor_corpse_v129_"+droppedSceneV129();}
    boolean indoorCorpseSearchedV129(int index){
        return index<0||index>=clinicActorsV90.actors.length||
            (host.prefs.getInt(indoorCorpseKeyV129(),0)&(1<<index))!=0;
    }
    String indoorCorpseContentsV129(int index){
        if(index<0||index>=clinicActorsV90.actors.length)return "";
        switch(clinicActorsV90.actors[index].type){
            case ClinicActorsV90.RAIDER:return "Ammo ×2, Scrap ×2";
            case ClinicActorsV90.MEDIC:return "Medkit ×1, Water ×1";
            case ClinicActorsV90.SURVIVOR:return "Food ×1, Scrap ×1";
            case ClinicActorsV90.ZOMBIE:return "Scrap ×1";
            default:return "No usable possessions";
        }
    }
    boolean searchIndoorCorpseV129(int index){
        if(!insideClinicV89||!playing||index<0||
            index>=clinicActorsV90.actors.length||
            indoorCorpseSearchedV129(index))return false;
        ClinicActorsV90.Actor actor=clinicActorsV90.actors[index];
        if(actor.active||distance(playerX,playerY,actor.x,actor.y)>128f)
            return false;
        switch(actor.type){
            case ClinicActorsV90.RAIDER:ammoPacks+=2;scrap+=2;break;
            case ClinicActorsV90.MEDIC:medkits++;waterCount++;break;
            case ClinicActorsV90.SURVIVOR:foodCount++;scrap++;break;
            case ClinicActorsV90.ZOMBIE:scrap++;break;
            default:break;
        }
        int old=host.prefs.getInt(indoorCorpseKeyV129(),0);
        host.prefs.edit().putInt(indoorCorpseKeyV129(),old|(1<<index)).apply();
        gatherFeedback="SEARCHED FALLEN NPC";gatherFeedbackTime=2f;
        saveProgress();invalidate();return true;
    }
    /** A grounded pixel-art dropped backpack with zipper, straps and loot count. */
    void drawBanditBagV87(Canvas c,BanditLootV87.Bag bag){
        float x=bag.x,y=bag.y;
        if(bag.corpse){
            int skin=bag.skinV109>=1&&bag.skinV109<=200?
                bag.skinV109:
                1+Math.floorMod(Math.round(x*11f+(y+3f)*17f+
                    bag.variant*73f),200);
            drawFallenBodyV129(c,x,y,bag.variant,skin,bag.face);
            if(!bag.empty())label(c,"SEARCH",x-15,y-86,11,0xffe6c99a,true);
            return;
        }
        color(0x990f1a17);c.drawOval(x-23,y-6,x+23,y+8,p);
        rect(c,x-20,y-21,40,26,0xff142522);
        rect(c,x-16,y-23,32,25,0xff565b43);
        rect(c,x-13,y-27,26,8,0xff1e3028);
        rect(c,x-9,y-25,18,5,0xff8b7955);
        rect(c,x-13,y-16,26,11,0xff787558);
        rect(c,x-8,y-14,16,7,0xffaaa078);
        rect(c,x+12,y-16,5,18,0xff24352b);
        rect(c,x-17,y-16,5,18,0xff24352b);
        rect(c,x-2,y-13,5,5,0xffd5ba7e);
        label(c,"x"+bag.total(),x+14,y-26,10,0xffecd3a4,true);
    }
    /** Only a nearby bandit bag can be inspected or transferred to player. */
    BanditLootV87.Bag nearbyBanditBagV87(){
        if(!playing||gameOver||insideClinicV89)return null;
        return banditLootV87.nearest(playerX,playerY,BanditLootV87.USE_RADIUS);
    }
    /** Maps all loot icon types to the existing live inventory counters. */
    void addBanditLootV87(int type,int count){
        if(count<=0)return;
        switch(type){
            case BanditLootV87.SCRAP:scrap+=count;break;
            case BanditLootV87.MEDKIT:medkits+=count;break;
            case BanditLootV87.AMMO:ammoPacks+=count;break;
            case BanditLootV87.FOOD:foodCount+=count;break;
            case BanditLootV87.WATER:waterCount+=count;break;
            case BanditLootV87.WOOD:wood+=count;break;
            case BanditLootV87.STONE:stone+=count;break;
            case BanditLootV87.FIBER:fiber+=count;break;
        }
    }
    int lootBanditStackV87(BanditLootV87.Bag bag,int kind){
        if(!playing||!banditLootV87.contains(bag)||
            distance(playerX,playerY,bag.x,bag.y)>BanditLootV87.USE_RADIUS+7f)return 0;
        int count=banditLootV87.take(bag,kind);
        if(count>0){
            addBanditLootV87(kind,count);
            gatherFeedback="LOOTED "+BanditLootV87.NAMES[kind]+" +"+count;
            gatherFeedbackTime=2.2f;
            saveProgress();invalidate();
        }
        return count;
    }
    int lootAllBanditV87(BanditLootV87.Bag bag){
        if(!playing||!banditLootV87.contains(bag)||
            distance(playerX,playerY,bag.x,bag.y)>BanditLootV87.USE_RADIUS+7f)return 0;
        int[] taken=banditLootV87.takeAll(bag);
        int count=0;
        for(int i=0;i<taken.length;i++){
            addBanditLootV87(i,taken[i]);count+=taken[i];
        }
        if(count>0){
            gatherFeedback="LOOTED "+count+" ITEMS";gatherFeedbackTime=2.2f;
            saveProgress();invalidate();
        }
        return count;
    }
    void drawWorld(Canvas c){
        if(insideClinicV89){drawClinicInteriorV89(c);return;}
        c.save();c.translate(-camX,-camY);
        terrain(c);
        drawDroppedItemsV129(c);
        drawFixtures(c,false);
        for(BanditLootV87.Bag bag:banditLootV87.bags){
            if(!WorldPerfV55.nearView(bag.x,bag.y,camX,camY,viewW,viewH,70))continue;
            drawBanditBagV87(c,bag);
        }
        for(Drop d:drops){
            if(!WorldPerfV55.nearView(d.x,d.y,camX,camY,viewW,viewH,24))continue;
            float bob=(float)Math.sin(worldTimer*5+d.x)*2;
            rect(c,d.x-9,d.y-13+bob,18,16,DK);
            rect(c,d.x-7,d.y-11+bob,14,12,d.type==2?0xffd7e2d7:d.type==1?0xff8e9b9d:ORANGE);
            if(d.type==2){rect(c,d.x-1,d.y-9+bob,3,9,RED);rect(c,d.x-5,d.y-6+bob,11,3,RED);}
        }
        ArrayList<DrawEntity> order=new ArrayList<>();
        lastVisibleNpcs=0;lastCulledNpcs=0;
        for(float[] fire:activeCampfiresV125()){
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
                    Ballistics.angle(e.aimX,e.aimY,e.face),
                    0,false,true,e.variant,e.skinV109);
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
                    Ballistics.angle(f.aimX,f.aimY,f.face),0,false,false,f.variant,f.skinV109);
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
                Ballistics.angle(npc.aimX,npc.aimY,npc.face),
                0,false,false,npc.variant,npc.skinV109);
            
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
        // Bullets + subtle muzzle flashes are drawn ONCE after lighting
        // in drawGunEffectsV119, using actual projectile positions.
        for(Spark s:sparks)if(
            WorldPerfV55.nearView(s.x,s.y,camX,camY,viewW,viewH,10))
                rect(c,s.x,s.y,4,4,s.color);
        // Last pass darkens the *entire* world, including all characters,
        // equipment, projectiles and props; real lights punch through this mask.
        if(lightAlpha>0)applyWorldLighting(c);else drawFixtures(c,true);
        drawWorldMuzzleBloomV130(c);
        drawGunEffectsV119(c);
        if(showChunkGrid)drawChunkGrid(c);
        drawOutdoorSpeechAfterLightingV93(c);
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
    float uiWidth(int id){
        if(id==ENTER_EDITOR)return enterWidthV132();
        if(id==TALK_EDITOR)return talkWidthV94();
        return LegacyControlsV58.defaultW(id)*uiSize(id);
    }
    float uiHeight(int id){
        if(id==ENTER_EDITOR)return enterHeightV132();
        if(id==TALK_EDITOR)return talkHeightV94();
        return LegacyControlsV58.defaultH(id)*uiSize(id);
    }
    float uiX(int id){
        // TALK is NOT a LegacyControlsV58 action. Never send its ID through
        // defaultX/defaultY (throws IllegalArgumentException on drag).
        if(id==TALK_EDITOR)return talkLeftV94();
        if(id==ENTER_EDITOR)return enterLeftV132();
        if(id>=TOP_FORM_EDITOR&&id<ENTER_EDITOR)return hudExtraXV118(id);
        if(id==BAG_EDITOR)return bagXv87();
        if(id==HOTBAR)return hotbarLeft();
        if(id==MOVE_PAD||id==AIM_PAD)return padCenterX(id==AIM_PAD);
        if(id<0||id>=LegacyControlsV58.COUNT)return 0f;
        int delta=editPointer>=0&&editControl==id?editX:
            host.setting("uiX"+id,0);
        return LegacyControlsV58.defaultX(id,viewW)+delta;
    }
    float uiY(int id){
        if(id==TALK_EDITOR)return talkTopV94();
        if(id==ENTER_EDITOR)return enterTopV132();
        if(id>=TOP_FORM_EDITOR&&id<ENTER_EDITOR)return hudExtraYV118(id);
        if(id==BAG_EDITOR)return bagYv87();
        if(id==HOTBAR)return hotbarTop();
        if(id==MOVE_PAD||id==AIM_PAD)return padCenterY(id==AIM_PAD);
        if(id<0||id>=LegacyControlsV58.COUNT)return 0f;
        int delta=editPointer>=0&&editControl==id?editY:
            host.setting("uiY"+id,0);
        return LegacyControlsV58.defaultY(id,viewH)+delta;
    }
    boolean uiEnabled(int id){
        return host.option("uiEnabled"+id,id>=LegacyControlsV58.COUNT||
            LegacyControlsV58.defaultEnabled(id));
    }
    float talkDefaultX(){return Math.round(viewW*.64f);}
    float talkDefaultY(){return Math.round(viewH*.28f);}
    float talkSizeV94(){return host.setting("uiSize"+TALK_EDITOR,100)/100f;}
    float talkLeftV94(){
        return talkDefaultX()+(editPointer>=0&&editControl==TALK_EDITOR?
            editX:host.setting("uiX"+TALK_EDITOR,0));
    }
    float talkTopV94(){
        return talkDefaultY()+(editPointer>=0&&editControl==TALK_EDITOR?
            editY:host.setting("uiY"+TALK_EDITOR,0));
    }
    float talkWidthV94(){return 105f*talkSizeV94();}
    float talkHeightV94(){return 44f*talkSizeV94();}
    boolean talkVisibleV94(){
        // Deliberately visible in editor without requiring an NPC nearby.
        return ContextualTalkV94.visible(editControls,playing,paused,gameOver,
            uiEnabled(TALK_EDITOR),nearbyNPCInteractionV92());
    }
    boolean talkButtonAtV94(float x,float y){
        return talkVisibleV94()&&
            LegacyControlsV58.hit(x,y,talkLeftV94(),talkTopV94(),
                talkWidthV94(),talkHeightV94());
    }
    float enterDefaultX(){return Math.round(viewW*.64f);}
    float enterDefaultY(){return Math.round(viewH*.37f);}
    float enterSizeV132(){
        return Math.max(.6f,Math.min(1.8f,
            host.setting("uiSize"+ENTER_EDITOR,100)/100f));
    }
    float enterLeftV132(){
        return enterDefaultX()+(editPointer>=0&&editControl==ENTER_EDITOR?
            editX:host.setting("uiX"+ENTER_EDITOR,0));
    }
    float enterTopV132(){
        return enterDefaultY()+(editPointer>=0&&editControl==ENTER_EDITOR?
            editY:host.setting("uiY"+ENTER_EDITOR,0));
    }
    float enterWidthV132(){return 105f*enterSizeV132();}
    float enterHeightV132(){return 44f*enterSizeV132();}
    boolean enterVisibleV132(){
        if(editControls)return true;
        return ContextualDoorV132.visible(editControls,playing,paused,
            gameOver,uiEnabled(ENTER_EDITOR),nearbyDoorV132()!=null);
    }
    boolean enterButtonAtV132(float x,float y){
        return enterVisibleV132()&&
            LegacyControlsV58.hit(x,y,enterLeftV132(),enterTopV132(),
                enterWidthV132(),enterHeightV132());
    }
    void drawEnterButtonV132(Canvas c){
        if(!enterVisibleV132())return;
        float x=enterLeftV132(),y=enterTopV132(),
            w=enterWidthV132(),h=enterHeightV132();
        int alpha=Math.max(36,Math.min(255,
            host.setting("uiAlpha"+ENTER_EDITOR,100)*255/100));
        btn(c,x,y,w,h,insideClinicV89?"EXIT":"ENTER",
            (alpha<<24)|0x00436b60);
        if(editControls){
            color(uiEnabled(ENTER_EDITOR)?0xffc4dcbb:0xffe29b80);
            p.setStrokeWidth(2f);p.setStyle(Paint.Style.STROKE);
            c.drawRect(x,y,x+w,y+h,p);p.setStyle(Paint.Style.FILL);
        }
    }
    int actionAt(float x,float y){
        if(enterButtonAtV132(x,y))return ENTER_EDITOR;
        if(talkButtonAtV94(x,y))return TALK_EDITOR;
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
    String controlName(int id){
        if(id==ENTER_EDITOR)return "ENTER / EXIT BUTTON";
        if(id==TALK_EDITOR)return "TALK BUTTON";
        if(id==BAG_EDITOR)return "BAG BUTTON";
        if(id==MOVE_PAD)return "MOVE JOYSTICK";
        if(id==AIM_PAD)return "AIM JOYSTICK";
        if(id==HOTBAR)return "QUICK ACCESS BAR";
        if(id>=TOP_FORM_EDITOR){
            String[] labels={"FORM BUTTON","HUD EDIT BUTTON","DAY / NIGHT BUTTON",
                "CAMP BUTTON","LAMP BUTTON","PAUSE BUTTON","SETTINGS BUTTON",
                "STATUS BARS WINDOW","TOP INFORMATION WINDOW",
                "BOTTOM RESOURCE WINDOW","FPS STATUS WINDOW","COMPANION COMMAND BUTTON"};
            return labels[Math.max(0,Math.min(labels.length-1,id-TOP_FORM_EDITOR))];
        }
        return LegacyControlsV58.NAMES[id];
    }
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
    void drawTalkButtonV94(Canvas c){
        if(!talkVisibleV94())return;
        float x=talkLeftV94(),y=talkTopV94(),
            w=talkWidthV94(),h=talkHeightV94();
        int alpha=Math.max(36,Math.min(255,
            host.setting("uiAlpha"+TALK_EDITOR,100)*255/100));
        btn(c,x,y,w,h,"TALK",(alpha<<24)|0x00426a59);
        if(editControls){
            color(uiEnabled(TALK_EDITOR)?0xffc4dcbb:0xffe29b80);
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
        if(!editControls&&!uiEnabled(HOTBAR))return -1;
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
        if(item==11)return craftV83.stock[2];
        if(item==12)return craftV83.stock[3];
        if(item==13)return bandagesV88;
        if(item==14)return energyV88;
        return 0;
    }
    void setHotbarItem(int slot,int item){
        if(slot<0||slot>=hotbar.length||item<0||item>=HOTBAR_TYPES.length)return;
        hotbar[slot]=item;
        host.prefs.edit().putInt("hotbar"+slot,item).apply();
    }
    /** Inventory consumes directly while its dialog pauses the world simulation. */
    boolean useBackpackV88(int item){
        if(!playing||gameOver)return false;
        boolean used=false;
        if(item==1&&medkits>0&&health<100f){
            medkits--;health=Math.min(100f,health+40f);used=true;
        }else if(item==2&&ammoPacks>0&&ammo<MAG[gun]){
            ammoPacks--;ammo=MAG[gun];used=true;
        }else if(item==6&&foodCount>0&&hunger<100f){
            foodCount--;hunger=Math.min(100f,hunger+30f);used=true;
        }else if(item==7&&waterCount>0&&thirst<100f){
            waterCount--;thirst=Math.min(100f,thirst+35f);used=true;
        }else if(item==13&&bandagesV88>0&&health<100f){
            bandagesV88--;health=Math.min(100f,health+24f);used=true;
        }else if(item==14&&energyV88>0&&(stamina<100f||fatigue>0f)){
            energyV88--;stamina=Math.min(100f,stamina+50f);
            fatigue=Math.max(0f,fatigue-20f);used=true;
        }
        if(used){saveProgress();invalidate();}
        return used;
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
        }else if(item>=9&&item<=12){
            selectPlaceItemV84(item-9);
        }else if(item==13&&bandagesV88>0&&health<100f){
            bandagesV88--;health=Math.min(100f,health+24f);
        }else if(item==14&&energyV88>0&&stamina<100f){
            energyV88--;stamina=Math.min(100f,stamina+50f);
            fatigue=Math.max(0f,fatigue-20f);
        }
        saveProgress();invalidate();
    }
    void drawHotbar(Canvas c){
        if(!uiEnabled(HOTBAR)&&!editControls)return;
        float x=hotbarLeft(),y=hotbarTop(),size=47f*hotbarScale;
        int hotbarAlpha=Math.max(25,Math.min(100,
            host.setting("uiAlpha"+HOTBAR,100)));
        int hotbarLayer=hotbarAlpha<100?c.saveLayerAlpha(
            x,y,x+6*size,y+size,Math.round(hotbarAlpha*255f/100f)):0;
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
                x+i*size+size*.5f-16f,y+size*.13f,32f);
            label(c,name.length()>6?name.substring(0,6):name,x+i*size+4,y+size-3,
                    8,0xffe7e1c7,true);
            if(item==1||item==2||item==6||item==7||(item>=9&&item<=14))
                label(c,Integer.toString(hotbarQuantity(item)),x+(i+1)*size-14,
                      y+size-6,10,0xffe6d4aa,true);
        }
        if(hotbarLayer!=0)c.restoreToCount(hotbarLayer);
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
                    if(i<LegacyControlsV58.COUNT||i==BAG_EDITOR||
                       i==TALK_EDITOR||i>=TOP_FORM_EDITOR)
                        host.prefs.edit().putBoolean("uiEnabled"+i,
                            !host.option("uiEnabled"+i,true)).apply();
                }else{
                    String key=j==2||j==3?controlSizeKey(i):"uiAlpha"+i;
                    int min=j<=3?(i>=MOVE_PAD?70:60):30;
                    int current=host.setting(key,100);
                    int next=Math.round(clamp(current+(j%2==0?-10:10),min,j<=3?180:100));
                    host.prefs.edit().putInt(key,next).apply();
                    if(i==HOTBAR||i==BAG_EDITOR||i>=TOP_FORM_EDITOR||
                       (i>=MOVE_PAD&&j<=3))reloadSettings();
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
        float originX=(playerX-camX)*renderZoomV90,
            originY=(playerY-42f-camY)*renderZoomV90;
        float available=aimCursorDistance*renderZoomV90;
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
    /** Larger BAG control directly over right aim stick. */
    float bagScaleV87(){return host.setting("uiSize"+BAG_EDITOR,100)/100f;}
    float bagXv87(){
        return WorldUiV86.bagX(viewW)+
            (editPointer>=0&&editControl==BAG_EDITOR?editX:host.setting("uiX"+BAG_EDITOR,0));
    }
    float bagYv87(){
        return WorldUiV86.bagY(viewH)+
            (editPointer>=0&&editControl==BAG_EDITOR?editY:host.setting("uiY"+BAG_EDITOR,0));
    }
    boolean bagHitV87(float x,float y){
        if(!editControls&&!host.option("uiEnabled"+BAG_EDITOR,true))return false;
        return within(x,y,bagXv87(),bagYv87(),
            WorldUiV86.BAG_W*bagScaleV87(),WorldUiV86.BAG_H*bagScaleV87());
    }
    void drawFloatingBagV86(Canvas c){
        if(!editControls&&!host.option("uiEnabled"+BAG_EDITOR,true))return;
        float x=bagXv87(),y=bagYv87(),s=bagScaleV87();
        int alpha=host.setting("uiAlpha"+BAG_EDITOR,100);
        c.save();c.translate(x,y);c.scale(s,s);
        int fade=alpha<100?c.saveLayerAlpha(0,0,WorldUiV86.BAG_W,
            WorldUiV86.BAG_H,Math.round(Math.max(30,alpha)*2.55f)):0;
        x=0;y=0;
        rounded(c,x,y,WorldUiV86.BAG_W,WorldUiV86.BAG_H,9,0xd020403b);
        p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2f);
        color(0xffd6b27b);
        c.drawRoundRect(x+1,y+1,x+WorldUiV86.BAG_W-1,
            y+WorldUiV86.BAG_H-1,9,9,p);
        p.setStyle(Paint.Style.FILL);
        // Distinct backpack silhouette (not a barricade/structure icon).
        rect(c,x+13,y+10,30,33,0xff152522);
        rect(c,x+17,y+6,22,10,0xff172d29);
        rect(c,x+20,y+10,16,5,0xffa88c61);
        rect(c,x+16,y+14,24,25,0xff685b42);
        rect(c,x+20,y+18,17,12,0xff8f7954);
        rect(c,x+23,y+31,11,5,0xffc0a77d);
        rect(c,x+18,y+16,4,21,0xff243a32);
        label(c,"BAG",x+49,y+34,17,0xfff4ebd5,true);
        if(editControls){
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);
            color(0xffebc279);c.drawRect(1,1,WorldUiV86.BAG_W-1,WorldUiV86.BAG_H-1,p);
            p.setStyle(Paint.Style.FILL);
        }
        if(fade!=0)c.restoreToCount(fade);
        c.restore();
    }
    /** Aim direction determines ghost location; use the unchanged aim stick. */
    void updatePlacementTargetV86(){
        if(placingKindV84<0)return;
        placingXv84=WorldUiV86.targetX(playerX,aimX,aimCursorDistance);
        placingYv84=WorldUiV86.targetY(playerY,aimY,aimCursorDistance);
    }
    /** V118 complete editor geometry: top row, status windows and squad HUD. */
    static final int[] TOP_EDIT_CONTROLS_V118={
        TopHudV76.FORM,TopHudV76.EDIT,TopHudV76.DAY,TopHudV76.CAMP,
        TopHudV76.LAMP,TopHudV76.PAUSE,TopHudV76.SET
    };
    int topEditorV118(int topButton){
        for(int i=0;i<TOP_EDIT_CONTROLS_V118.length;i++)
            if(TOP_EDIT_CONTROLS_V118[i]==topButton)return TOP_FORM_EDITOR+i;
        return -1;
    }
    int topButtonV118(int editor){
        int i=editor-TOP_FORM_EDITOR;
        return i>=0&&i<TOP_EDIT_CONTROLS_V118.length?
            TOP_EDIT_CONTROLS_V118[i]:-1;
    }
    float hudExtraScaleV118(int id){
        return Math.max(.6f,Math.min(1.8f,
            host.setting("uiSize"+id,100)/100f));
    }
    float hudBaseXV118(int id){
        int top=topButtonV118(id);
        if(top>=0)return TopHudV76.x(top,viewW);
        switch(id){
            case STATUS_EDITOR:return 12f;
            case HEADER_EDITOR:return 12f;
            case FOOTER_EDITOR:return 13f;
            case PERF_EDITOR:return 10f;
            case COMMAND_EDITOR:return viewW-195f;
            default:return 0f;
        }
    }
    float hudBaseYV118(int id){
        if(topButtonV118(id)>=0)return TopHudV76.Y;
        switch(id){
            case STATUS_EDITOR:return 145f;
            case HEADER_EDITOR:return 0f;
            case FOOTER_EDITOR:return viewH-37f;
            case PERF_EDITOR:return 46f;
            case COMMAND_EDITOR:return 58f;
            default:return 0f;
        }
    }
    float hudExtraXV118(int id){
        return hudBaseXV118(id)+(editPointer>=0&&editControl==id?
            editX:host.setting("uiX"+id,0));
    }
    float hudExtraYV118(int id){
        return hudBaseYV118(id)+(editPointer>=0&&editControl==id?
            editY:host.setting("uiY"+id,0));
    }
    float hudExtraWidthV118(int id){
        int top=topButtonV118(id);
        float base=top>=0?TopHudV76.buttonWidth(top,viewW):
            id==STATUS_EDITOR?244f:id==HEADER_EDITOR?370f:
            id==FOOTER_EDITOR?650f:id==PERF_EDITOR?348f:
            id==COMMAND_EDITOR?142f:100f;
        return base*hudExtraScaleV118(id);
    }
    float hudExtraHeightV118(int id){
        float base=topButtonV118(id)>=0?TopHudV76.HEIGHT:
            id==STATUS_EDITOR?120f:id==HEADER_EDITOR?42f:
            id==FOOTER_EDITOR?28f:id==PERF_EDITOR?92f:
            id==COMMAND_EDITOR?42f:36f;
        return base*hudExtraScaleV118(id);
    }
    int hudExtraAtV118(float x,float y){
        // Reverse order gives small top buttons precedence over large panels.
        for(int id=COMMAND_EDITOR;id>=TOP_FORM_EDITOR;id--){
            if(!editControls&&!uiEnabled(id))continue;
            if(within(x,y,hudExtraXV118(id),hudExtraYV118(id),
                hudExtraWidthV118(id),hudExtraHeightV118(id)))return id;
        }
        return -1;
    }
    int topHudHitV118(float x,float y){
        for(int i=0;i<TOP_EDIT_CONTROLS_V118.length;i++){
            int id=TOP_FORM_EDITOR+i;
            if(uiEnabled(id)&&within(x,y,hudExtraXV118(id),hudExtraYV118(id),
                hudExtraWidthV118(id),hudExtraHeightV118(id)))
                return TOP_EDIT_CONTROLS_V118[i];
        }
        return -1;
    }
    void hudSelectionBorderV118(Canvas c,int id){
        if(!editControls)return;
        float x=hudExtraXV118(id),y=hudExtraYV118(id),
              w=hudExtraWidthV118(id),h=hudExtraHeightV118(id);
        color(uiEnabled(id)?0xffc5e2c4:0xffdc9579);
        p.setStrokeWidth(1.9f);p.setStyle(Paint.Style.STROKE);
        c.drawRect(x,y,x+w,y+h,p);p.setStyle(Paint.Style.FILL);
    }
    void topHudButton(Canvas c,int id,String title,boolean active){
        int editor=topEditorV118(id);
        if(editor<0)return;
        if(!uiEnabled(editor)&&!editControls)return;
        float x=hudExtraXV118(editor),y=hudExtraYV118(editor),
              width=hudExtraWidthV118(editor),height=hudExtraHeightV118(editor);
        int opacity=Math.max(30,Math.min(100,host.setting("uiAlpha"+editor,100)));
        int layer=opacity<100?c.saveLayerAlpha(x,y,x+width,y+height,
            Math.round(255f*opacity/100f)):0;
        int fillAlpha=Math.round(topButtonOpacityV76*255f/100f);
        if(fillAlpha>0)rounded(c,x,y,width,height,5,
            (fillAlpha<<24)|(active?0x003b665b:0x0010262b));
        int size=TopHudV76.scale(viewW)<.8f?10:12;
        size=Math.max(8,Math.round(size*hudExtraScaleV118(editor)));
        p.setTypeface(PIXEL_BOLD);p.setTextSize(size);
        float textX=x+(width-p.measureText(title))*.5f;
        label(c,title,textX+1f,y+height*.68f+1f,size,0xff142526,true);
        label(c,title,textX,y+height*.68f,size,WHITE,true);
        if(layer!=0)c.restoreToCount(layer);
        hudSelectionBorderV118(c,editor);
    }
    /** Editable and always accessible companion command button. */
    void drawSquadButtonV118(Canvas c){
        if(!uiEnabled(COMMAND_EDITOR)&&!editControls)return;
        float x=hudExtraXV118(COMMAND_EDITOR),y=hudExtraYV118(COMMAND_EDITOR),
              w=hudExtraWidthV118(COMMAND_EDITOR),h=hudExtraHeightV118(COMMAND_EDITOR);
        int alpha=Math.max(25,Math.min(100,
            host.setting("uiAlpha"+COMMAND_EDITOR,100)));
        int layer=alpha<100?c.saveLayerAlpha(x,y,x+w,y+h,
            Math.round(255f*alpha/100f)):0;
        btn(c,x,y,w,h,"SQUAD"+(companionStayV118?" [STAY]":""),
            0x99425a50);
        if(layer!=0)c.restoreToCount(layer);
        hudSelectionBorderV118(c,COMMAND_EDITOR);
    }
    void drawStatusWindowV118(Canvas c){
        if(!showStatusBars&&!editControls)return;
        if(!uiEnabled(STATUS_EDITOR)&&!editControls)return;
        int id=STATUS_EDITOR,opacity=Math.max(25,Math.min(100,
            host.setting("uiAlpha"+id,100)));
        c.save();
        c.translate(hudExtraXV118(id),hudExtraYV118(id));
        c.scale(hudExtraScaleV118(id),hudExtraScaleV118(id));
        int layer=opacity<100?c.saveLayerAlpha(0,0,244,120,
            Math.round(255f*opacity/100f)):0;
        drawStatusBar(c,"HP",health,0,0,0xffc76b65);
        drawStatusBar(c,"STA",stamina,0,20,0xff64ad80);
        drawStatusBar(c,"HUN TEST",hunger,0,40,0xffb5a06b);
        drawStatusBar(c,"THR TEST",thirst,0,60,0xff608dad);
        drawStatusBar(c,"FAT TEST",fatigue,0,80,0xffa18eaf);
        drawStatusBar(c,"ENC TEST",encumbranceV91(),0,100,0xffbca36e);
        if(layer!=0)c.restoreToCount(layer);
        c.restore();
        hudSelectionBorderV118(c,id);
    }
    void hud(Canvas c){
        // Entire interface fades together; world and targeting reticle are
        // outside this composited HUD layer and stay fully readable.
        // Avoid allocating an offscreen HUD layer at the 100% default.
        int hudLayer=hudOpacityV73<100?
            c.saveLayerAlpha(0f,0f,viewW,viewH,CameraHudV73.alpha(hudOpacityV73)):0;
        // No opaque top or bottom bars: the world fills the entire screen.
        if(uiEnabled(HEADER_EDITOR)||editControls){
            int id=HEADER_EDITOR,alpha=host.setting("uiAlpha"+id,100);
            c.save();c.translate(hudExtraXV118(id),hudExtraYV118(id));
            c.scale(hudExtraScaleV118(id),hudExtraScaleV118(id));
            int layer=alpha<100?c.saveLayerAlpha(0,0,370,42,alpha*255/100):0;
            label(c,"SURVIVAL PARADISE",1,17,15,0xff142326,true);
            label(c,"SURVIVAL PARADISE",0,16,15,WHITE,true);
            String meta="HP "+(int)health+"  AMMO "+ammo+"/"+MAG[gun]+
                "  WAVE "+wave+"  KILLS "+kills;
            label(c,meta,1,35,11,0xff142326,false);
            label(c,meta,0,34,11,OLIVE,false);
            if(layer!=0)c.restoreToCount(layer);c.restore();
            hudSelectionBorderV118(c,id);
        }
        topHudButton(c,TopHudV76.FORM,"FORM",false);
        topHudButton(c,TopHudV76.EDIT,editControls?"DONE":"EDIT",editControls);
        topHudButton(c,TopHudV76.DAY,lightAlpha>nightDarkness*.5f?"NOON":"NIGHT",false);
        topHudButton(c,TopHudV76.CAMP,"CAMP",false);
        topHudButton(c,TopHudV76.LAMP,lampOn?"LAMP ON":"LAMP OFF",lampOn);
        drawFloatingBagV86(c);
        topHudButton(c,TopHudV76.PAUSE,paused?"RESUME":"PAUSE",paused);
        topHudButton(c,TopHudV76.SET,"SET",false);
        drawSquadButtonV118(c);
        String footer="SCRAP "+scrap+"  WOOD "+wood+"  STONE "+stone+
            "  FIBER "+fiber+"  MED "+medkits+"  AMMO "+ammoPacks+
            "   "+MainActivity.LOADOUTS[gun]+"  "+clock.display()+
            (automaticDayNight?" [AUTO]":" [MANUAL]");
        if(uiEnabled(FOOTER_EDITOR)||editControls){
            int id=FOOTER_EDITOR,alpha=host.setting("uiAlpha"+id,100);
            c.save();c.translate(hudExtraXV118(id),hudExtraYV118(id));
            c.scale(hudExtraScaleV118(id),hudExtraScaleV118(id));
            int layer=alpha<100?c.saveLayerAlpha(0,0,650,28,alpha*255/100):0;
            label(c,footer,1,22,13,0xff182521,true);
            label(c,footer,0,21,13,ORANGE,true);
            if(layer!=0)c.restoreToCount(layer);c.restore();
            hudSelectionBorderV118(c,id);
        }
        if(harvestV81.active){
            label(c,harvestV81.actionName()+"  "+harvestV81.hitsDone+
                "/"+harvestV81.hitsRequired,14,viewH-53,13,0xffd3e4a7,true);
            rect(c,14,viewH-45,152,5,0xaa112520);
            rect(c,15,viewH-44,150*harvestV81.totalProgress(),3,0xffc2b58c);
        }else if(gatherFeedbackTime>0)
            label(c,gatherFeedback,14,viewH-54,13,0xffd3e4a7,true);
        else if((industrialModeV123||stitchedIndustrialV128)&&!insideClinicV89&&
                (!stitchedIndustrialV128||
                IndustrialBiomeBridgeV128.hasIndustrialLoot(
                    playerX,playerY,industrialSeedV123))){
            IndustrialYardV123.Stock stock=industrialYardV123.nearest(
                stitchedIndustrialV128?IndustrialBiomeBridgeV128.localX(playerX):playerX,
                stitchedIndustrialV128?IndustrialBiomeBridgeV128.localY(playerY):playerY,
                industrialSeedV123);
            if(stock!=null)label(c,"INTERACT: SALVAGE "+stock.name(),
                14,viewH-54,12,0xffd3e4a7,true);
        }else{
            ResourceWorldV80.Node near=harvestWorld.nearest(playerX,playerY,
                ResourceWorldV80.USE_RADIUS,CAMP_X,CAMP_Y,WORLD_W,WORLD_H);
            if(near!=null)
                label(c,"INTERACT: GATHER "+near.name(),14,viewH-54,12,0xffd3e4a7,true);
        }
        // Original two virtual sticks, with per-stick size/sensitivity tests.
        float jy=padCenterY(false),rx=padCenterX(true),ry=padCenterY(true);
        float lx=padCenterX(false);
        float leftRadius=86*movePadScale,rightRadius=82*aimPadScale;
        int alpha=Math.round(255f*Math.max(25,Math.min(100,controlOpacity))/100f);
        int leftAlpha=(uiEnabled(MOVE_PAD)||editControls)?
            alpha*host.setting("uiAlpha"+MOVE_PAD,100)/100:0;
        int rightAlpha=(uiEnabled(AIM_PAD)||editControls)?
            alpha*host.setting("uiAlpha"+AIM_PAD,100)/100:0;
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
        drawTalkButtonV94(c);
        drawEnterButtonV132(c);
        drawHotbar(c);
        drawStatusWindowV118(c);
        if(uiEnabled(MOVE_PAD)||editControls)
            label(c,"MOVE",lx-39,jy+105,12,0xffb8d4c5,true);
        if(reloadClock>0)label(c,"RELOADING...",viewW-235,viewH-227,17,ORANGE,true);
        if((showPerf||editControls)&&(uiEnabled(PERF_EDITOR)||editControls)){
            int perfId=PERF_EDITOR,opacity=host.setting("uiAlpha"+perfId,100);
            c.save();
            c.translate(hudExtraXV118(perfId)-10f,hudExtraYV118(perfId)-46f);
            c.scale(hudExtraScaleV118(perfId),hudExtraScaleV118(perfId),10f,46f);
            int perfLayer=opacity<100?c.saveLayerAlpha(10,46,360,138,
                Math.round(opacity*255f/100f)):0;
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
            if(perfLayer!=0)c.restoreToCount(perfLayer);
            c.restore();
            hudSelectionBorderV118(c,PERF_EDITOR);
        }
        if(playing&&!gameOver&&!insideClinicV89){
            ExpeditionSitesV88.Site nearby=null;
            float nearestDistance=1450f;
            for(ExpeditionSitesV88.Site site:ExpeditionSitesV88.SITES){
                float d=distance(playerX,playerY,site.x,site.y);
                if(d<nearestDistance){nearestDistance=d;nearby=site;}
            }
            if(nearby!=null){
                float dx=nearby.x-playerX,dy=nearby.y-playerY;
                String heading=Math.abs(dx)>Math.abs(dy)?
                    (dx>=0?"E":"W"):(dy>=0?"S":"N");
                label(c,"EXPLORE "+heading+"  "+nearby.name+
                    "   "+Math.round(nearestDistance)+"m",
                    14,viewH-84,12,0xffd9c9a0,true);
            }
        }
        if(placingKindV84>=0){
            label(c,"AIM "+craftNameV88(placingKindV84)+
                "  •  PRESS INTERACT TO PLACE",viewW*.5f-205f,66,13,0xfff4d5a1,true);
            label(c,"Tap BAG to cancel placement",viewW*.5f-117f,86,11,0xffdfd6c2,false);
        }
        if(hudLayer!=0)c.restoreToCount(hudLayer);
        // Keep on-screen edit handles opaque at any HUD opacity.
        if(editControls)drawHudEditorOverlay(c);
    }
    void menu(Canvas c){
        rounded(c,viewW/2-300,viewH/2-200,600,398,20,0xef14272b);
        label(c,"SURVIVAL PARADISE V124",viewW/2-254,viewH/2-115,32,WHITE,true);
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
    float pauseMenuTopV131(){
        return gameOver?viewH/2f-130f:54f;
    }
    void pauseOverlay(Canvas c){
        rect(c,0,0,viewW,viewH,0xaa07171d);
        float top=pauseMenuTopV131();
        rounded(c,viewW/2-195,top,390,215,16,0xff20353b);
        label(c,gameOver?"YOU DIED":"GAME PAUSED",viewW/2-155,top+52,27,WHITE,true);
        btn(c,viewW/2-150,top+77,300,50,gameOver?"NEW GAME":"RESUME",0xff376a5e);
        btn(c,viewW/2-150,top+143,300,50,"SETTINGS",0xff344952);
    }
    @Override protected void onDetachedFromWindow(){
        terrainChunks.release();
        industrialArtV123.release();
        lighting.release();
        if(campStatic!=null){campStatic.recycle();campStatic=null;}
        itemIconsV84.release();
        for(Bitmap b:approvedGearV93)if(b!=null&&!b.isRecycled())b.recycle();
        if(pickaxeV81!=null){pickaxeV81.recycle();pickaxeV81=null;}
        if(crosshairReticle!=null){crosshairReticle.recycle();crosshairReticle=null;}
        super.onDetachedFromWindow();
    }
    @Override protected void onSizeChanged(int width,int height,
                                           int oldWidth,int oldHeight){
        super.onSizeChanged(width,height,oldWidth,oldHeight);
        // The screenshot is 1480x720 physical; gameplay draws in logical
        // 660px-height coordinates. Initialize only after Android supplies
        // the actual usable display bounds. Preserve explicit user edits.
        if(width>0&&height>0&&!host.prefs.getBoolean(
                ScreenshotSettingsV121.HUD_MARKER,false)){
            float logicalWidth=width*(H/(float)height);
            ScreenshotSettingsV121.applyHud(host.prefs,logicalWidth,false);
            reloadSettings();
        }
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
        // Prevent empty margins when a player zooms out inside a finite room
        // map. Outdoor zoom values remain unchanged.
        float effectiveZoom=insideClinicV89?
            Math.max(zoom,Math.max(viewW/ClinicInteriorV89.WIDTH,
                viewH/ClinicInteriorV89.HEIGHT)):zoom;
        renderZoomV90=effectiveZoom;
        // Camera follow and clamping in world coordinates.
        if(insideClinicV89){
            float frameW=viewW/effectiveZoom,frameH=viewH/effectiveZoom;
            camX=clamp(playerX-frameW*.5f,0f,
                Math.max(0f,ClinicInteriorV89.WIDTH-frameW));
            camY=clamp(playerY-frameH*.5f,0f,
                Math.max(0f,ClinicInteriorV89.HEIGHT-frameH));
        }else{
            camX=playerX-viewW/(2*effectiveZoom)+cameraLookX;
            camY=playerY-viewH/(2*effectiveZoom)+cameraLookY;
        }
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
        camX=insideClinicV89?Math.max(0,playerX-viewW/2):playerX-viewW/2;
        camY=insideClinicV89?Math.max(0,playerY-viewH/2):playerY-viewH/2;
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
            updatePlacementTargetV86();
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
            if(within(x,y,viewW/2-150,pauseMenuTopV131()+77,300,50)){
                if(gameOver)newGame();else togglePause();return;
            }
            if(within(x,y,viewW/2-150,pauseMenuTopV131()+143,300,50)){
                host.settings();return;
            }
        }
        if(!editControls&&bagHitV87(x,y)){
            cancelPlaceV84();host.inventory();return;
        }
        if(uiEnabled(COMMAND_EDITOR)&&!editControls&&
           within(x,y,hudExtraXV118(COMMAND_EDITOR),hudExtraYV118(COMMAND_EDITOR),
               hudExtraWidthV118(COMMAND_EDITOR),hudExtraHeightV118(COMMAND_EDITOR))){
            host.companionCommandsV118();return;
        }
        switch(topHudHitV118(x,y)){
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
            case TopHudV76.BAG:return; // top BAG moved above aiming stick
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
        }else if(ui==ENTER_EDITOR){
            if(!editControls&&enterVisibleV132())enterDoorV132();
        }else if(ui==TALK_EDITOR){
            // TALK is separate from INTERACT and ENTER.
            if(ContextualTalkV94.canTalk(editControls,playing,paused,gameOver,
                    uiEnabled(TALK_EDITOR),nearbyNPCInteractionV92()))
                interactNearbyNPCV92();
        }else if(ui==LegacyControlsV58.USE){
            if(placingKindV84>=0){
                if(!placeAtV84(placingXv84,placingYv84)){
                    gatherFeedback=craftV83.error;gatherFeedbackTime=1.8f;
                }
                invalidate();return;
            }
            if(insideClinicV89){
                DroppedItemsV129.Stack pile=nearbyDroppedV129();
                if(pile!=null){host.runOnUiThread(()->host.recoverDroppedV129(pile));return;}
                interactClinicV89();return;
            }
            // Building entrances are controlled only by ENTER.
            DroppedItemsV129.Stack pileV129=nearbyDroppedV129();
            if(pileV129!=null){
                host.runOnUiThread(()->host.recoverDroppedV129(pileV129));return;
            }
            if(industrialModeV123){
                collectIndustrialYardV123();return;
            }
            if(stitchedIndustrialV128&&collectIndustrialYardV123())return;
            if(useFacilityV88())return;
            BanditLootV87.Bag banditBag=nearbyBanditBagV87();
            if(banditBag!=null){
                host.runOnUiThread(()->host.lootBanditBagV87(banditBag));
                return;
            }
            for(Iterator<Drop> it=drops.iterator();it.hasNext();){
                Drop drop=it.next();
                if(distance(playerX,playerY,drop.x,drop.y)<100f){
                    if(drop.type==0)ammoPacks++;else if(drop.type==1)scrap+=2;
                    else medkits++;it.remove();saveProgress();return;
                }
            }
            if(!pickupGroundV85())gatherNearestV80();
        }
    }
    @Override public boolean onTouchEvent(MotionEvent e){
        int action=e.getActionMasked(),i=e.getActionIndex(),id=e.getPointerId(i);
        float x=e.getX(i)/Math.max(.01f,drawScale),y=e.getY(i)/Math.max(.01f,drawScale);
        switch(action){
            case MotionEvent.ACTION_DOWN:
            case MotionEvent.ACTION_POINTER_DOWN:
                if(!playing||paused){tap(x,y);return true;}
                if(editControls&&hudEditorTouch(x,y)){
                    if(panelPointer==-2)panelPointer=id;
                    return true;
                }
                if(editControls){
                    int extra=hudExtraAtV118(x,y);
                    if(extra>=TOP_FORM_EDITOR){
                        editPointer=id;editControl=extra;selectedHudControl=extra;
                        editX=host.setting("uiX"+extra,0);
                        editY=host.setting("uiY"+extra,0);
                        editGrabX=x-hudExtraXV118(extra);
                        editGrabY=y-hudExtraYV118(extra);
                        host.prefs.edit().putInt("selectedButton",extra).apply();
                        return true;
                    }
                }else if(topHudHitV118(x,y)>=0||
                         bagHitV87(x,y)||
                         (uiEnabled(COMMAND_EDITOR)&&within(x,y,
                            hudExtraXV118(COMMAND_EDITOR),hudExtraYV118(COMMAND_EDITOR),
                            hudExtraWidthV118(COMMAND_EDITOR),hudExtraHeightV118(COMMAND_EDITOR)))){
                    tap(x,y);return true;
                }
                if(editControls&&bagHitV87(x,y)){
                    editPointer=id;editControl=BAG_EDITOR;
                    selectedHudControl=BAG_EDITOR;
                    editX=host.setting("uiX"+BAG_EDITOR,0);
                    editY=host.setting("uiY"+BAG_EDITOR,0);
                    editGrabX=x-bagXv87();editGrabY=y-bagYv87();
                    host.prefs.edit().putInt("selectedButton",BAG_EDITOR).apply();
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
                        // Contextual ENTER/TALK controls use their own positions.
                        editGrabX=HudDragV119.grabOffset(x,uiX(target));
                        editGrabY=HudDragV119.grabOffset(y,uiY(target));
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
                // Aim-stick placement does not capture ordinary world touches.
                // Joystick hit tests follow their EDITED positions; the old
                // fixed screen zones broke input after moving the controls.
                float moveDistance=(float)Math.hypot(x-padCenterX(false),y-padCenterY(false));
                float aimDistance=(float)Math.hypot(x-padCenterX(true),y-padCenterY(true));
                float moveReach=100f*movePadScale,aimReach=100f*aimPadScale;
                if(leftPointer<0&&uiEnabled(MOVE_PAD)&&moveDistance<moveReach&&moveDistance<=aimDistance){
                    leftPointer=id;updateStick(x,y,false);return true;
                }
                if(rightPointer<0&&uiEnabled(AIM_PAD)&&aimDistance<aimReach){
                    rightPointer=id;updateStick(x,y,true);return true;
                }
                tap(x,y);return true;
            case MotionEvent.ACTION_MOVE:
                for(int j=0;j<e.getPointerCount();j++){
                    int pointer=e.getPointerId(j);
                    float px=e.getX(j)/Math.max(.01f,drawScale);
                    float py=e.getY(j)/Math.max(.01f,drawScale);
                    // Preview follows right thumbstick, never arbitrary finger drags.
                    if(pointer==leftPointer)updateStick(px,py,false);
                    if(pointer==rightPointer)updateStick(px,py,true);
                    if(pointer==panelPointer){
                        panelX=clamp(px-panelGrabX-(viewW*.5f-350f),
                                     -viewW*.5f+355f,viewW*.5f-350f);
                        panelY=clamp(py-panelGrabY,55f,viewH-75f);
                    }
                    if(pointer==editPointer&&editControl>=TOP_FORM_EDITOR&&
                       editControl<ENTER_EDITOR){
                        editX=Math.round(clamp(px-editGrabX-hudBaseXV118(editControl),
                            -hudBaseXV118(editControl),
                            viewW-hudExtraWidthV118(editControl)-hudBaseXV118(editControl)));
                        editY=Math.round(clamp(py-editGrabY-hudBaseYV118(editControl),
                            -hudBaseYV118(editControl),
                            viewH-hudExtraHeightV118(editControl)-hudBaseYV118(editControl)));
                        invalidate();
                    }else if(pointer==editPointer&&editControl==ENTER_EDITOR){
                        editX=HudDragV119.horizontalOffset(px,editGrabX,
                            enterDefaultX(),enterWidthV132(),viewW);
                        editY=HudDragV119.verticalOffset(py,editGrabY,
                            enterDefaultY(),enterHeightV132(),viewH);
                        invalidate();
                    }else if(pointer==editPointer&&editControl==TALK_EDITOR){
                        // V119: the TALK button is contextual; its ID is outside
                        // LegacyControlsV58 and must never be sent to defaultX/Y.
                        // Preserve its exact finger grab point, square size and
                        // independent X/Y save overrides while dragging.
                        editX=HudDragV119.horizontalOffset(px,editGrabX,
                            talkDefaultX(),talkWidthV94(),viewW);
                        editY=HudDragV119.verticalOffset(py,editGrabY,
                            talkDefaultY(),talkHeightV94(),viewH);
                        invalidate();
                    }else if(pointer==editPointer&&editControl>=0){
                        editX=Math.round(px-editGrabX-
                                (editControl==BAG_EDITOR?WorldUiV86.bagX(viewW):
                                 editControl==HOTBAR?viewW*.5f-6*47f*hotbarScale*.5f:
                                 editControl==TALK_EDITOR?talkDefaultX():
                                 editControl<LegacyControlsV58.COUNT?
                                 LegacyControlsV58.defaultX(editControl,viewW):
                                 padBaseX(editControl==AIM_PAD)));
                        editY=Math.round(py-editGrabY-
                                (editControl==BAG_EDITOR?WorldUiV86.bagY(viewH):
                                 editControl==HOTBAR?viewH-103f:
                                 editControl==TALK_EDITOR?talkDefaultY():
                                 editControl<LegacyControlsV58.COUNT?
                                 LegacyControlsV58.defaultY(editControl,viewH):
                                 padBaseY(editControl==AIM_PAD)));
                        if(editControl==BAG_EDITOR){
                            editX=Math.round(clamp(editX,-WorldUiV86.bagX(viewW),
                                viewW-WorldUiV86.BAG_W*bagScaleV87()-WorldUiV86.bagX(viewW)));
                            editY=Math.round(clamp(editY,60-WorldUiV86.bagY(viewH),
                                viewH-WorldUiV86.BAG_H*bagScaleV87()-WorldUiV86.bagY(viewH)));
                        }else if(editControl==TALK_EDITOR){
                            editX=Math.round(clamp(editX,-talkDefaultX(),
                                viewW-talkWidthV94()-talkDefaultX()));
                            editY=Math.round(clamp(editY,42-talkDefaultY(),
                                viewH-talkHeightV94()-talkDefaultY()));
                        }else if(editControl<LegacyControlsV58.COUNT){
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
                // Lifting a finger does not place anything; INTERACT confirms placement.
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