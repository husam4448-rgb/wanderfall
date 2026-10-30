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
    final Paint pixel=new Paint(Paint.ANTI_ALIAS_FLAG==0?0:0);
    Bitmap body,approvedWalkColors,stableBody,npcRoleAtlas,gear,approvedAxe;
    static final int ROLE_BANDIT=0,ROLE_GUARD=2,ROLE_MEDIC=4,ROLE_MECHANIC=6,
                     ROLE_TRADER=8,ROLE_CIVILIAN=10;
    static final float CAMP_X=1080,CAMP_Y=710;
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

    float scale=1,handScale=1,support=0,supportVertical=0,timeSpeed=1,zoom=1;
    boolean showHands=true,showWeapons=true,anchors=false,hitboxes=false,enemyAI=true,
            aimRotation=true,recoilFX=true,lootEnabled=true,night=true;
    boolean playing=false,paused=false,settingsPause=false,wasPaused=false,hasSave=false,gameOver=false;
    boolean lampOn=true,neonEnabled=true,campfiresLit=true;
    int nightDarkness=211,flashlightReach=490;
    final LightingV47 lighting=new LightingV47();
    // V47: solar clock advances during gameplay, including smooth dawn/dusk.
    final GameClockV47 clock=new GameClockV47(21*60f);
    boolean automaticDayNight=true;
    int lightAlpha=210;
    static final float[][] FIXED_CAMPFIRES={{1170,805},{2140,1550},{300,780}};
    static final float[][] NEONS={
       {465,321,LightingV47.NEON_BLUE},{1775,343,LightingV47.NEON_PINK},
       {2455,1170,LightingV47.NEON_BLUE},{857,1710,LightingV47.NEON_PINK}};
    final ArrayList<float[]> builtCampfires=new ArrayList<>();
    float playerX=1000,playerY=1060,health=100,stamina=100,shotClock=0,reloadClock=0,recoil=0;
    float aimX=1,aimY=0,stickX=0,stickY=0;
    int face=1,gun=0,ammo=12,kills=0,wave=1,scrap=0,medkits=0,ammoPacks=0,enemyCount=0;
    float worldTimer=0,autSaveClock=0,shake=0;
    long lastFrame=0;
    float viewW=1200,viewH=660,drawScale=1,camX=0,camY=0;
    int leftPointer=-1,rightPointer=-1;
    boolean firing=false,moving=false;
    final AnimationCycle playerAnimation=new AnimationCycle();
    // Keep projectile collision against the exact approved atlas alpha, not an
    // unrelated circle near the characters' feet.
    final CharacterCollision.PixelMask bodyMask=(x,y)->stableBody!=null &&
            x>=0&&y>=0&&x<stableBody.getWidth()&&y<stableBody.getHeight() &&
            (stableBody.getPixel(x,y)>>>24)!=0;
    final CharacterCollision.PixelMask walkMask=(x,y)->stableBody!=null &&
            x>=0&&y>=0&&x<stableBody.getWidth()&&y<stableBody.getHeight() &&
            (stableBody.getPixel(x,y)>>>24)!=0;
    final ArrayList<Bandit> enemies=new ArrayList<>();
    final ArrayList<Survivor> friends=new ArrayList<>();
    final ArrayList<Survivor> campStaff=new ArrayList<>();
    final ArrayList<Shot> shots=new ArrayList<>();
    final ArrayList<Drop> drops=new ArrayList<>();
    final ArrayList<Spark> sparks=new ArrayList<>();
    final ArrayList<Flash> flashes=new ArrayList<>();
    final ArrayList<Cover> covers=new ArrayList<>();
    int allySetting=1,allyCurrent=1;
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
            this.x=x;this.y=y;this.vx=vx;this.vy=vy;this.damage=damage;this.life=1.3f;
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
            try(InputStream axe=getResources().getAssets().open("approved_v29_axe.png")){
                approvedAxe=BitmapFactory.decodeStream(axe);
            }
        }catch(Exception e){body=null;gear=null;}
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
        handScale=host.setting("hand",100)/100f;
        support=host.setting("support",0);
        supportVertical=host.setting("supportY",0);
        timeSpeed=host.setting("speed",100)/100f;
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
        playerX=CAMP_X;playerY=CAMP_Y;health=100;stamina=100;playerAnimation.reset();moving=false;stickX=0;stickY=0;shotClock=0;
        gun=Math.max(0,Math.min(11,host.setting("gun",0)));ammo=MAG[gun];
        kills=0;wave=1;scrap=0;medkits=1;ammoPacks=2;worldTimer=0;autSaveClock=0;
        clock.setClock(night?21*60f:12*60f,1);
        face=1;aimX=1;aimY=0;refreshDaylight();
        enemies.clear();friends.clear();campStaff.clear();shots.clear();drops.clear();sparks.clear();flashes.clear();builtCampfires.clear();
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
        health=host.prefs.getFloat("hp",100);kills=host.setting("kills",0);
        wave=Math.max(1,host.setting("wave",1));
        scrap=host.setting("scrap",0);medkits=host.setting("medkits",1);ammoPacks=host.setting("ammoPacks",2);
        gun=Math.max(0,Math.min(11,host.setting("gun",0)));
        ammo=Math.max(0,Math.min(MAG[gun],host.setting("ammo",MAG[gun])));
        enemies.clear();friends.clear();shots.clear();drops.clear();sparks.clear();flashes.clear();
        restoreCampfires();
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
                if(x>=30&&x<=WORLD_W-30&&y>=30&&y<=WORLD_H-30&&builtCampfires.size()<16)
                    builtCampfires.add(new float[]{x,y});
            }catch(NumberFormatException ignored){}
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
            float x=clamp(playerX+(float)Math.cos(a)*distance,85,WORLD_W-85);
            float y=clamp(playerY+(float)Math.sin(a)*distance,100,WORLD_H-90);
            if(blocked(x,y,22)){x=clamp(x+140,90,WORLD_W-100);y=clamp(y+130,90,WORLD_H-100);}
            // Prevent hostile wave placement in the protected spawn clearing.
            if(distance(x,y,CAMP_X,CAMP_Y)<450){x=clamp(x+520,90,WORLD_W-90);}
            enemies.add(new Bandit(x,y,i%2));
        }
    }
    void saveProgress(){
        if(!playing||gameOver)return;
        host.prefs.edit().putBoolean("hasSave",true).putFloat("px",playerX).putFloat("py",playerY)
                .putFloat("hp",health).putInt("kills",kills).putInt("wave",wave)
                .putInt("scrap",scrap).putInt("medkits",medkits)
                .putInt("ammoPacks",ammoPacks).putInt("ammo",ammo)
                .putString("campfire_locations",encodeCampfires())
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
    void releaseControls(){stopWalking();firing=false;leftPointer=-1;rightPointer=-1;}
    void switchWeapon(){
        gun=(gun+1)%12;ammo=MAG[gun];reloadClock=0;
        host.prefs.edit().putInt("gun",gun).apply();
    }
    void reload(){
        if(gun==3||gun==11||ammo>=MAG[gun]||reloadClock>0)return;
        if(ammoPacks==0)return;
        ammoPacks--;reloadClock=1.25f;shotClock=0;
    }
    float clamp(float x,float min,float max){return Math.max(min,Math.min(max,x));}
    boolean blocked(float x,float y,float r){
        if(x<32||y<40||x>WORLD_W-32||y>WORLD_H-32)return true;
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
        float[] muzzle=Ballistics.rigMuzzle(x,y,facing,dx,dy,.76f*scale,
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
        if(!playing||paused)return;
        // Clock is real-world-time based and independent of enemy simulation speed.
        clock.advance(Math.min(.04f,dt));
        refreshDaylight();
        dt=Math.min(.04f,dt)*timeSpeed;
        worldTimer+=dt;autSaveClock+=dt;
        if(autSaveClock>9){saveProgress();autSaveClock=0;}
        shotClock=Math.max(0,shotClock-dt);
        recoil=Math.max(0,recoil-dt*5);
        if(reloadClock>0){
            reloadClock-=dt;if(reloadClock<=0){ammo=MAG[gun];reloadClock=0;}
        }
        float wasX=playerX,wasY=playerY;
        float vx=stickX,vy=stickY;
        float length=(float)Math.hypot(vx,vy);
        if(length>.06f){
            vx/=Math.max(1,length);vy/=Math.max(1,length);
            float speed=gun==9?147:207;
            float nx=clamp(playerX+vx*speed*dt,35,WORLD_W-40);
            float ny=clamp(playerY+vy*speed*dt,50,WORLD_H-40);
            if(!blocked(nx,playerY,20))playerX=nx;
            if(!blocked(playerX,ny,20))playerY=ny;
            // Movement joystick is locomotion ONLY. No facing or aim updates.
        }
        // Animate actual displacement only: releasing the stick or hitting a wall
        // always restores the original neutral idle frame immediately.
        moving=distance(playerX,playerY,wasX,wasY)>.001f;
        playerAnimation.step(moving,dt,7f);
        if(firing){
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
            float px=npc.x,py=npc.y;
            if((i&1)==0){
                npc.x=npc.homeX+(float)Math.sin(worldTimer*.34f+i)*18f;
                npc.y=npc.homeY+(float)Math.cos(worldTimer*.34f+i)*11f;
                npc.face=(float)Math.cos(worldTimer*.34f+i)>=0?1:-1;
            }
            npc.animation.step(distance(px,py,npc.x,npc.y)>.001f,dt,6f);
        }
        for(Survivor friend:friends){
            float beforeFriendX=friend.x,beforeFriendY=friend.y;
            friend.cd=Math.max(0,friend.cd-dt);
            float d=distance(friend.x,friend.y,playerX,playerY);
            if(d>80){
                float ux=(playerX-friend.x)/Math.max(1,d),uy=(playerY-friend.y)/Math.max(1,d);
                float nx=friend.x+ux*170*dt,ny=friend.y+uy*170*dt;
                if(!blocked(nx,friend.y,18))friend.x=nx;
                if(!blocked(friend.x,ny,18))friend.y=ny;
                friend.face=ux>=0?1:-1;
            }
            friend.animation.step(distance(friend.x,friend.y,beforeFriendX,beforeFriendY)>.001f,dt,7f);
            Bandit target=nearest(friend.x,friend.y,460);
            if(target!=null&&friend.cd<=0){
                float dx=target.x-friend.x,dy=target.y-friend.y;
                friend.face=dx>=0?1:-1;
                float aimLen=Math.max(1,(float)Math.hypot(dx,dy));
                friend.aimX=dx/aimLen;friend.aimY=dy/aimLen;
                shoot(friend.x,friend.y,dx,dy,friend.gun,false,friend.face);
                friend.cd=RATES[friend.gun]+.2f;
            }
        }
        if(enemyAI)for(Bandit e:enemies){
            if(!e.active)continue;
            float beforeEnemyX=e.x,beforeEnemyY=e.y;
            e.cd-=dt;e.hit=Math.max(0,e.hit-dt);
            float d=distance(e.x,e.y,playerX,playerY);
            if(d<520){
                float dx=(playerX-e.x)/Math.max(1,d),dy=(playerY-e.y)/Math.max(1,d);
                e.face=dx>=0?1:-1;
                if(d>240){
                    float nx=e.x+dx*105*dt,ny=e.y+dy*105*dt;
                    if(!blocked(nx,e.y,18))e.x=nx;
                    if(!blocked(e.x,ny,18))e.y=ny;
                    // Animation is driven by displacement, not historical walking time.
                }else if(e.cd<=0){
                    shoot(e.x,e.y,dx,dy,0,true,e.face);
                    e.cd=1.1f+rng.nextFloat()*.7f;
                }
            }
            e.animation.step(distance(e.x,e.y,beforeEnemyX,beforeEnemyY)>.001f,dt,6f);
        }
        if(!enemyAI)for(Bandit e:enemies)e.animation.reset();
        // Continuous collision detection: no tunneling through actors or cover at 4000 px/s.
        for(Iterator<Shot> iter=shots.iterator();iter.hasNext();){
            Shot bullet=iter.next();
            float nx=bullet.x+bullet.vx*dt,ny=bullet.y+bullet.vy*dt;
            bullet.life-=dt;
            float first=Float.POSITIVE_INFINITY;
            Bandit victim=null;
            boolean hitPlayer=false,hitCover=false;
            for(Cover box:covers){
                float t=Ballistics.segmentBox(bullet.x,bullet.y,nx,ny,
                        box.x-2,box.y-2,box.x+box.w+2,box.y+box.h+2);
                if(t<first){first=t;victim=null;hitPlayer=false;hitCover=true;}
            }
            if(bullet.hostile){
                float t=CharacterCollision.firstHit(bullet.x,bullet.y,nx,ny,
                        playerX,
                        playerY,face,playerAnimation.frame(),
                        playerAnimation.isWalking(),playerAnimation.breathOffset(),scale,
                        playerAnimation.isWalking()?walkMask:bodyMask);
                if(t<first){first=t;victim=null;hitPlayer=true;hitCover=false;}
            }else{
                for(Bandit e:enemies)if(e.active){
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
            }else if(bullet.life<=0||nx<0||ny<0||nx>WORLD_W||ny>WORLD_H){
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
        if(enemies.stream().noneMatch(e->e.active)){wave++;health=Math.min(100,health+15);spawnWave();}
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
        color(col);p.setTypeface(bold?android.graphics.Typeface.create("monospace",1):
                android.graphics.Typeface.create("monospace",0));
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
        float s=scale;
        // Cast from the original on-screen pixel silhouette (three small
        // rectangles, not a large circular aura). Source-facing side remains lit.
        lighting.occludeRect(x-29*s,y-90*s,x+29*s,y-48*s); // head
        lighting.occludeRect(x-21*s,y-48*s,x+21*s,y-16*s); // chest
        lighting.occludeRect(x-22*s,y-17*s,x+22*s,y-2*s); // boots
    }
    void populateLightBlockers(){
        for(Cover b:covers)lighting.occludeRect(b.x,b.y,b.x+b.w,b.y+b.h);
        for(int i=0;i<140;i++){
            if(i%7!=0)continue; // tree trunks/crowns, not tiny grass flecks
            int x=(137*i+27*i*i)%3180,y=(211*i+47*i*i)%2170;
            if(y>912&&y<1160)continue;
            if(x>1480&&x<1740)continue;
            lighting.occludeRect(x-8,y-9,x+29,y+31);
        }
        addCharacterShadow(playerX,playerY);
        for(Survivor f:friends)addCharacterShadow(f.x,f.y);
        for(Survivor f:campStaff)addCharacterShadow(f.x,f.y);
        for(Bandit e:enemies)if(e.active)addCharacterShadow(e.x,e.y);
    }
    void applyWorldLighting(Canvas c){
        if(lightAlpha<=0)return;
        lighting.clear();
        populateLightBlockers();
        if(campfiresLit){
            for(float[] f:FIXED_CAMPFIRES)fireLight(f[0],f[1]);
            for(float[] f:builtCampfires)fireLight(f[0],f[1]);
        }
        if(neonEnabled)for(float[] n:NEONS){
            lighting.point(n[0],n[1],202,.77f,(int)n[2]);
        }
        // Street lamps offer modest navigation light, not character glow.
        for(float x:new float[]{490,1790,2840})
            lighting.point(x,872,175,.61f,0xffdbd5a0);
        if(lampOn){
            if(gun==3){
                float[] tip=Ballistics.rigMuzzle(playerX,playerY,face,aimX,aimY,
                    .76f*scale,MX[3],MY[3],MAIN_X[3],MAIN_Y[3],0f);
                lighting.flashlight(tip[0],tip[1],aimX,aimY,flashlightReach);
            }
            for(Survivor f:friends)if(f.gun==3){
                float[] tip=Ballistics.rigMuzzle(f.x,f.y,f.face,f.aimX,f.aimY,
                    .76f*scale,MX[3],MY[3],MAIN_X[3],MAIN_Y[3],0f);
                lighting.flashlight(tip[0],tip[1],f.aimX,f.aimY,flashlightReach);
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
        // Lamps/neon signage are static architecture; campfire flames were
        // already depth-sorted with characters and are NOT painted over them.
        drawFixtures(c,true);
    }
    void fireLight(float x,float y){
        float flicker=(float)Math.sin(worldTimer*11f+x*.33f);
        lighting.point(x,y-9,205+flicker*9,.89f+flicker*.07f,LightingV47.WARM);
    }
    void terrain(Canvas c){
        // Deterministic, streaming visible world: foliage, asphalt, debris, and vegetation.
        rect(c,camX-4,camY-4,viewW+8,viewH+8,0xff354c40);
        int tile=72;
        int x0=(int)Math.floor(camX/tile)-1,x1=(int)Math.ceil((camX+viewW)/tile)+1;
        int y0=(int)Math.floor(camY/tile)-1,y1=(int)Math.ceil((camY+viewH)/tile)+1;
        for(int gy=y0;gy<=y1;gy++)for(int gx=x0;gx<=x1;gx++){
            if(gx<0||gy<0||gx>WORLD_W/tile||gy>WORLD_H/tile)continue;
            int h=hash(gx,gy);
            float x=gx*tile,y=gy*tile;
            // Streaming deterministic 5x5-tile procedural terrain patches.
            // The protected camp clearing is restored around the spawn hub.
            int patch=hash(Math.floorDiv(gx,5),Math.floorDiv(gy,5));
            int biome=Math.floorMod(patch,4);
            int tint=(biome==0?0xff375347:biome==1?0xff414d39:
                      biome==2?0xff40544b:0xff4b503d);
            if(Math.hypot(x-CAMP_X,y-CAMP_Y)<320)tint=0xff53624c;
            rect(c,x,y,tile,tile,tint);
            rect(c,x+10+(h&17),y+30,4,3,0xff60745c);
            if((h&15)==1){rect(c,x+33,y+52,7,5,0xff647a61);rect(c,x+41,y+46,3,6,0xff557156);}
        }
        rect(c,0,925,WORLD_W,225,0xff565b50);
        rect(c,0,940,WORLD_W,8,0xff3e493e);
        rect(c,0,1134,WORLD_W,7,0xff323f3a);
        for(int x=20;x<WORLD_W;x+=123)rect(c,x,1035,56,6,0xffa1a78d);
        rect(c,1500,0,220,WORLD_H,0xff525b50);
        rect(c,1500,0,9,WORLD_H,0xff3c473f);
        for(int y=0;y<WORLD_H;y+=135)rect(c,1604,y+12,7,63,0xffa5aa8e);
        // Bushes and trees are always behind buildings and actors.
        for(int i=0;i<140;i++){
            int x=(137*i+27*i*i)%3180,y=(211*i+47*i*i)%2170;
            if(y>912&&y<1160)continue;
            if(x>1480&&x<1740)continue;
            if(Math.hypot(x-CAMP_X,y-CAMP_Y)<325)continue;
            if((i%7)==0){
                rect(c,x+7,y+19,8,24,0xff243c30);
                rect(c,x-8,y,37,28,0xff172b25);
                rect(c,x-4,y-6,30,27,0xff4e7351);
                rect(c,x+2,y-9,19,13,0xff65845d);
            }else{
                rect(c,x,y+7,19,8,0xff233c30);
                rect(c,x+3,y,17,11,0xff557253);
                rect(c,x+8,y-4,8,7,0xff647f58);
            }
        }
        for(Cover box:covers)drawCover(c,box);
        drawSpawnCamp(c);
    }
    void drawSpawnCamp(Canvas c){
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
    }
    void drawCover(Canvas c,Cover box){
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
    // V51: user-approved body colors/geometry are immutable in source archives.
    // Stable atlases pre-normalize ALL four poses to the exact same head anchor.
    // No per-frame black inset is drawn: front contour is identical in pixels.
    void stablePose(Canvas c,Bitmap atlas,int variant,int frame,float s,float breath){
        if(atlas==null)return;
        int row=Math.max(0,variant)*160;
        int f=Math.max(0,Math.min(3,frame));
        if(breath==Float.POSITIVE_INFINITY){
            src.set(f*260,row,f*260+260,row+160);
            dest.set(-70*s,-136*s,190*s,24*s);
            c.drawBitmap(atlas,src,dest,pixel);
        }else{
            // Planted source frame 2 from the SAME role atlas; feet stay static.
            src.set(520,row+92,780,row+160);
            dest.set(-70*s,(92-136)*s,190*s,24*s);
            c.drawBitmap(atlas,src,dest,pixel);
            src.set(520,row,780,row+101);
            dest.set(-70*s,-136*s+breath*s,190*s,(-136+101)*s+breath*s);
            c.drawBitmap(atlas,src,dest,pixel);
        }
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
    void character(Canvas c,float x,float y,int weapon,int facing,int frame,float breath,float aimAng,float kick,
                   boolean player,boolean bandit,int npcVariant){
        float s=.76f*scale;
        c.save();c.translate(x,y);if(facing<0)c.scale(-1,1);
        color(0x670b1a18);c.drawOval(-26*s,-7*s,26*s,7*s,p);
        Bitmap atlas=npcVariant>=0?npcRoleAtlas:stableBody;
        stablePose(c,atlas,npcVariant<0?0:npcVariant,frame,s,breath);
        if(!bandit){
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
                    drawApprovedAxe(c,(MAIN_X[weapon]-70f)*s,(MAIN_Y[weapon]-136f)*s,scale);
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
            float bob=(float)Math.sin(worldTimer*5+d.x)*2;
            rect(c,d.x-9,d.y-13+bob,18,16,DK);
            rect(c,d.x-7,d.y-11+bob,14,12,d.type==2?0xffd7e2d7:d.type==1?0xff8e9b9d:ORANGE);
            if(d.type==2){rect(c,d.x-1,d.y-9+bob,3,9,RED);rect(c,d.x-5,d.y-6+bob,11,3,RED);}
        }
        ArrayList<DrawEntity> order=new ArrayList<>();
        for(float[] fire:FIXED_CAMPFIRES){
            final float fx=fire[0],fy=fire[1];
            order.add(new DrawEntity(fy,()->{
                drawCampfire(c,fx,fy,false);
                drawCampfire(c,fx,fy,true);
            }));
        }
        for(float[] fire:builtCampfires){
            final float fx=fire[0],fy=fire[1];
            order.add(new DrawEntity(fy,()->{
                drawCampfire(c,fx,fy,false);
                drawCampfire(c,fx,fy,true);
            }));
        }
        for(Bandit e:enemies)if(e.active)order.add(new DrawEntity(e.y,()->{
            character(c,e.x,e.y,0,e.face,e.animation.frame(),
                    e.animation.isWalking()?Float.POSITIVE_INFINITY:e.animation.breathOffset(),
                    0,0,false,true,e.variant);
            rect(c,e.x-23,e.y-114,46,5,DK);rect(c,e.x-22,e.y-113,44*clamp(e.hp/78,0,1),3,RED);
        }));
        for(Survivor f:friends)order.add(new DrawEntity(f.y,()->{
            character(c,f.x,f.y,f.gun,f.face,f.animation.frame(),
                    f.animation.isWalking()?Float.POSITIVE_INFINITY:f.animation.breathOffset(),
                    Ballistics.angle(f.aimX,f.aimY,f.face),0,false,false,f.variant);
            rect(c,f.x-5,f.y-117,10,4,OLIVE);
        }));
        for(Survivor npc:campStaff)order.add(new DrawEntity(npc.y,()->{
            character(c,npc.x,npc.y,npc.gun,npc.face,npc.animation.frame(),
                npc.animation.isWalking()?Float.POSITIVE_INFINITY:npc.animation.breathOffset(),
                0,0,false,false,npc.variant);
        }));
        order.add(new DrawEntity(playerY,()->{
            float angle=Ballistics.angle(aimX,aimY,face);
            character(c,playerX,playerY,gun,face,playerAnimation.frame(),
                    playerAnimation.isWalking()?Float.POSITIVE_INFINITY:playerAnimation.breathOffset(),
                    angle,recoil*2.7f,true,false,-1);
        }));
        order.sort((a,b)->Float.compare(a.y,b.y));
        for(DrawEntity e:order)e.draw.run();
        for(Shot projectile:shots){
            // Short, subtle tracer instead of slow glowing projectile blocks.
            float inv=1f/Math.max(1f,(float)Math.hypot(projectile.vx,projectile.vy));
            float vx=projectile.vx*inv,vy=projectile.vy*inv;
            color(projectile.color);p.setStrokeWidth(1.6f);
            c.drawLine(projectile.x-vx*19,projectile.y-vy*19,
                    projectile.x,projectile.y,p);
            rect(c,projectile.x-1,projectile.y-1,3,3,WHITE);
        }
        for(Flash flash:flashes){
            float alpha=clamp(flash.ttl/.065f,0,1),length=18*alpha;
            color(0xffffdf95);p.setStrokeWidth(Math.max(1.5f,3f*alpha));
            c.drawLine(flash.x,flash.y,flash.x+flash.dx*length,
                    flash.y+flash.dy*length,p);
            rect(c,flash.x-2,flash.y-2,4,4,0xfffff7cf);
        }
        for(Spark s:sparks)rect(c,s.x,s.y,4,4,s.color);
        // Last pass darkens the *entire* world, including all characters,
        // equipment, projectiles and props; real lights punch through this mask.
        if(lightAlpha>0)applyWorldLighting(c);else drawFixtures(c,true);
        c.restore();
    }
    static class DrawEntity {float y;Runnable draw;DrawEntity(float y,Runnable r){this.y=y;draw=r;}}
    void btn(Canvas c,float x,float y,float w,float h,String label,int fill){
        rounded(c,x,y,w,h,9,fill);
        label(c,label,x+12,y+h*.66f,14,WHITE,true);
    }
    void hud(Canvas c){
        rect(c,0,0,viewW,56,0xc90e2228);
        label(c,"SURVIVAL PARADISE",17,23,18,WHITE,true);
        label(c,"HP "+(int)health+"   AMMO "+ammo+"/"+MAG[gun]+"   WAVE "+wave+
                "   KILLS "+kills,18,44,13,OLIVE,false);
        btn(c,viewW-84,7,77,42,"⚙ SET",0xff30554d);
        btn(c,viewW-170,7,78,42,paused?"RESUME":"PAUSE",0xff293f46);
        btn(c,viewW-244,7,68,42,"BAG",0xff293f46);
        btn(c,viewW-324,7,75,42,lampOn?"LAMP ON":"LAMP OFF",0xff364d48);
        btn(c,viewW-410,7,79,42,"CAMP",0xff5b463a);
        btn(c,viewW-498,7,81,42,lightAlpha>nightDarkness*.5f?"NOON":"NIGHT",0xff34414c);
        rect(c,0,viewH-42,viewW,42,0xca122529);
        label(c,"SCRAP "+scrap+"   MED "+medkits+"   AMMO BOX "+ammoPacks+
                "   "+MainActivity.LOADOUTS[gun]+"  "+clock.display()+
                (automaticDayNight?" [AUTO]":" [MANUAL]"),
                14,viewH-16,14,ORANGE,true);
        // Independent touch controls, never an autonomous-only simulation.
        float jy=viewH-140,rx=viewW-118,ry=viewH-145;
        color(0x663e625a);c.drawCircle(120,jy,86,p);
        color(0x9b96b8a5);c.drawCircle(120+stickX*46,jy+stickY*46,31,p);
        color(0x665b6f61);c.drawCircle(rx,ry,82,p);
        color(0xaaaa9d71);c.drawCircle(rx,ry,52,p);
        color(0xfff2deb0);c.drawCircle(rx+aimX*39,ry+aimY*39,11,p);
        label(c,gun==3?"AIM":"FIRE",rx-20,ry+6,19,WHITE,true);
        btn(c,viewW-348,viewH-105,103,44,"RELOAD",0xff344e51);
        btn(c,viewW-348,viewH-160,103,44,"SWAP",0xff344e51);
        label(c,"MOVE",81,viewH-30,12,0xffb8d4c5,true);
        if(reloadClock>0)label(c,"RELOADING...",viewW-235,viewH-227,17,ORANGE,true);
    }
    void menu(Canvas c){
        rounded(c,viewW/2-300,viewH/2-200,600,398,20,0xef14272b);
        label(c,"SURVIVAL PARADISE",viewW/2-254,viewH/2-115,34,WHITE,true);
        label(c,"NATIVE ANDROID SURVIVAL SHOOTER  •  ALPHA 51",
                viewW/2-254,viewH/2-80,15,OLIVE,true);
        label(c,"Move with the left stick. Aim & fire with the right.",viewW/2-254,viewH/2-40,15,WHITE,false);
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
    @Override protected void onDraw(Canvas canvas){
        super.onDraw(canvas);
        long now=System.nanoTime();float dt=lastFrame==0?0:(now-lastFrame)/1e9f;lastFrame=now;
        drawScale=Math.max(.1f,getHeight()/H);
        viewW=getWidth()/drawScale;viewH=H;
        update(dt);
        float effectiveZoom=zoom;
        // Camera follow and clamping in world coordinates.
        camX=clamp(playerX-viewW/(2*effectiveZoom),0,Math.max(0,WORLD_W-viewW/effectiveZoom));
        camY=clamp(playerY-viewH/(2*effectiveZoom),0,Math.max(0,WORLD_H-viewH/effectiveZoom));
        canvas.drawColor(0xff101f24);
        canvas.save();canvas.scale(drawScale,drawScale);
        canvas.save();canvas.scale(effectiveZoom,effectiveZoom);
        float drawW=viewW/effectiveZoom,drawH=viewH/effectiveZoom;
        float oldW=viewW,oldH=viewH;
        viewW=drawW;viewH=drawH;
        drawWorld(canvas);viewW=oldW;viewH=oldH;
        canvas.restore();
        if(playing){
            hud(canvas);
            if(paused&&!settingsPause)pauseOverlay(canvas);
        }else menu(canvas);
        canvas.restore();
        postInvalidateDelayed(16);
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
        camX=clamp(playerX-viewW/2,0,Math.max(0,WORLD_W-viewW));
        camY=clamp(playerY-viewH/2,0,Math.max(0,WORLD_H-viewH));
        canvas.drawColor(0xff101f24);canvas.save();canvas.scale(s,s);
        if(playing){drawWorld(canvas);hud(canvas);}else menu(canvas);
        canvas.restore();
    }
    void updateStick(float x,float y,boolean right){
        float cx=right?viewW-118:120,cy=right?viewH-145:viewH-140;
        float dx=(x-cx)/74,dy=(y-cy)/74;
        float length=(float)Math.hypot(dx,dy);
        if(length>1){dx/=length;dy/=length;}
        if(right){
            if(length>.14){aimX=dx;aimY=dy;
                if(dx>.025f)face=1;else if(dx<-.025f)face=-1;
            }
            // Right-stick aim persists when released/centered. Never auto-target
            // enemies or reset the direction just because the joystick returned.

        }else {stickX=dx;stickY=dy;}
    }
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
        if(within(x,y,viewW-84,7,77,42)){host.settings();return;}
        if(within(x,y,viewW-170,7,78,42)){togglePause();return;}
        if(within(x,y,viewW-324,7,75,42)){toggleLamp();return;}
        if(within(x,y,viewW-410,7,79,42)){placeCampfire();return;}
        if(within(x,y,viewW-498,7,81,42)){toggleNight();return;}
        if(within(x,y,viewW-244,7,68,42)){
            if(medkits>0&&health<100){medkits--;health=Math.min(100,health+40);}
            host.runOnUiThread(()->android.widget.Toast.makeText(host,
                    "INVENTORY   Scrap: "+scrap+"   Medkits: "+medkits+
                    "   Ammo boxes: "+ammoPacks,android.widget.Toast.LENGTH_SHORT).show());
            return;
        }
        if(paused)return;
        if(within(x,y,viewW-348,viewH-160,103,44)){switchWeapon();return;}
        if(within(x,y,viewW-348,viewH-105,103,44)){reload();return;}
        if(x<viewW*.37f&&y>viewH*.45f)return;
        if(x>viewW*.61f&&y>viewH*.42f)return;
    }
    @Override public boolean onTouchEvent(MotionEvent e){
        int action=e.getActionMasked(),i=e.getActionIndex(),id=e.getPointerId(i);
        float x=e.getX(i)/Math.max(.01f,drawScale),y=e.getY(i)/Math.max(.01f,drawScale);
        switch(action){
            case MotionEvent.ACTION_DOWN:
            case MotionEvent.ACTION_POINTER_DOWN:
                if(!playing||paused||y<58||within(x,y,viewW-348,viewH-165,114,111)){
                    tap(x,y);return true;
                }
                if(x<viewW*.42f&&y>viewH*.48f&&leftPointer<0){
                    leftPointer=id;updateStick(x,y,false);return true;
                }
                if(x>viewW*.56f&&y>viewH*.45f&&rightPointer<0){
                    rightPointer=id;
                    firing=gun!=3;
                    updateStick(x,y,true);return true;
                }
                tap(x,y);return true;
            case MotionEvent.ACTION_MOVE:
                for(int j=0;j<e.getPointerCount();j++){
                    int pointer=e.getPointerId(j);
                    float px=e.getX(j)/Math.max(.01f,drawScale);
                    float py=e.getY(j)/Math.max(.01f,drawScale);
                    if(pointer==leftPointer)updateStick(px,py,false);
                    if(pointer==rightPointer)updateStick(px,py,true);
                }return true;
            case MotionEvent.ACTION_POINTER_UP:
            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_CANCEL:
                if(id==leftPointer||action==MotionEvent.ACTION_CANCEL){
                    leftPointer=-1;stopWalking();
                }
                if(id==rightPointer||action==MotionEvent.ACTION_CANCEL){
                    rightPointer=-1;firing=false;
                }
                return true;
        }
        return true;
    }
}