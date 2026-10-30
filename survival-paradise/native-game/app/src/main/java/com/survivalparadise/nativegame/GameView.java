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
    Bitmap body,approvedWalkColors,gear,approvedAxe;
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

    float scale=1,handScale=1,support=0,timeSpeed=1,zoom=1;
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
    final CharacterCollision.PixelMask bodyMask=(x,y)->body!=null &&
            x>=0&&y>=0&&x<body.getWidth()&&y<body.getHeight() &&
            (body.getPixel(x,y)>>>24)!=0;
    final CharacterCollision.PixelMask walkMask=(x,y)->approvedWalkColors!=null &&
            x>=0&&y>=0&&x<approvedWalkColors.getWidth()&&y<approvedWalkColors.getHeight() &&
            (approvedWalkColors.getPixel(x,y)>>>24)!=0;
    final ArrayList<Bandit> enemies=new ArrayList<>();
    final ArrayList<Survivor> friends=new ArrayList<>();
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
        Bandit(float a,float b){x=a;y=b;cd=.7f;}}
    static class Survivor {float x,y,cd,aimX=1,aimY=0;int gun,face=1;
        final AnimationCycle animation=new AnimationCycle();
        Survivor(float a,float b,int g){x=a;y=b;gun=g;}}
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
                    2+friends.size()%9));
        }
        while(friends.size()>allySetting-1)friends.remove(friends.size()-1);
        allyCurrent=1+friends.size();
    }
    void newGame(){
        playerX=1000;playerY=1060;health=100;stamina=100;playerAnimation.reset();moving=false;stickX=0;stickY=0;shotClock=0;
        gun=Math.max(0,Math.min(11,host.setting("gun",0)));ammo=MAG[gun];
        kills=0;wave=1;scrap=0;medkits=1;ammoPacks=2;worldTimer=0;autSaveClock=0;
        clock.setClock(night?21*60f:12*60f,1);
        face=1;aimX=1;aimY=0;refreshDaylight();
        enemies.clear();friends.clear();shots.clear();drops.clear();sparks.clear();flashes.clear();builtCampfires.clear();
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
    void spawnWave(){
        enemies.clear();enemyCount=5+Math.min(17,wave*2);
        for(int i=0;i<enemyCount;i++){
            float a=(float)(rng.nextDouble()*Math.PI*2);
            float distance=430+rng.nextInt(620);
            float x=clamp(playerX+(float)Math.cos(a)*distance,85,WORLD_W-85);
            float y=clamp(playerY+(float)Math.sin(a)*distance,100,WORLD_H-90);
            if(blocked(x,y,22)){x=clamp(x+140,90,WORLD_W-100);y=clamp(y+130,90,WORLD_H-100);}
            enemies.add(new Bandit(x,y));
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
                        playerX+(playerAnimation.isWalking()?
                            WalkAlignmentV48.worldOffsetX(playerAnimation.frame(),face,scale):0f),
                        playerY,face,playerAnimation.frame(),
                        playerAnimation.isWalking(),playerAnimation.breathOffset(),scale,
                        playerAnimation.isWalking()?walkMask:bodyMask);
                if(t<first){first=t;victim=null;hitPlayer=true;hitCover=false;}
            }else{
                for(Bandit e:enemies)if(e.active){
                    float t=CharacterCollision.firstHit(bullet.x,bullet.y,nx,ny,
                            e.x+(e.animation.isWalking()?
                                WalkAlignmentV48.worldOffsetX(e.animation.frame(),e.face,scale):0f),
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
        for(float[] f:FIXED_CAMPFIRES)drawCampfire(c,f[0],f[1],emissive);
        for(float[] f:builtCampfires)drawCampfire(c,f[0],f[1],emissive);
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
    void drawCampfire(Canvas c,float x,float y,boolean emissive){
        // Pixel-art campfire: stone hearth, crossed firewood, glowing coals,
        // asynchronous layered flame tongues, small embers, subtle smoke.
        // No sprite assets are edited; all layers use world-space coordinates.
        float a=(float)Math.sin(worldTimer*7.2f+x*.013f);
        float b=(float)Math.sin(worldTimer*11.8f+y*.037f);
        if(!emissive){
            rect(c,x-23,y+6,47,8,0xff192323); // ash shadow under stones
            rect(c,x-22,y+4,9,7,0xff66645b);
            rect(c,x-18,y+2,6,3,0xff9b9884);
            rect(c,x-11,y+9,10,6,0xff777366);
            rect(c,x+3,y+9,11,6,0xff625f57);
            rect(c,x+15,y+3,9,8,0xff6c6962);
            rect(c,x+17,y+4,5,2,0xffada996);
            rect(c,x-11,y+2,22,9,0xff342922); // embers inside the hearth
            if(campfiresLit){
                rect(c,x-10,y+5,20,4,0xff973e1e);
                rect(c,x-7,y+5,5,3,0xffd55e28);
                rect(c,x+2,y+6,6,2,0xffc9652b);
                // Two diagonal bundles of logs on an 8-bit grid.
                for(int i=0;i<5;i++){
                    rect(c,x-20+i*8,y+7-i*2,9,5,0xff603c29);
                    rect(c,x-18+i*8,y+8-i*2,5,2,0xffa07443);
                    rect(c,x+12-i*7,y-1+i*2,9,5,0xff6d4126);
                    rect(c,x+14-i*7,y+i*2,4,2,0xffa47c4d);
                }
            }else{
                rect(c,x-17,y+5,34,5,0xff54473c);
            }
            // Semi-transparent smoke belongs to the world: it darkens naturally
            // with the rest of the scene at night, never glows in isolation.
            if(campfiresLit){
                float drift=(float)Math.sin(worldTimer*1.6f+x*.02f)*4f;
                rect(c,x-5+drift,y-34,8,5,0x445c6461);
                rect(c,x-9-drift*.5f,y-48,6,4,0x2d7b8179);
            }
        }else if(campfiresLit){
            float h1=18f+a*4f,h2=15f+b*3f;
            // Dark orange edge, amber body, lively yellow center.
            rect(c,x-13,y-9,25,13,0xffa9431d);
            rect(c,x-11,y-14-h1*.25f,8,20+h1*.25f,0xffed6d24);
            rect(c,x+4,y-13-h2*.33f,8,17+h2*.33f,0xffd95a1b);
            rect(c,x-8,y-11-h1*.70f,11,16+h1*.70f,0xffff9b31);
            rect(c,x-2,y-13-h2*.72f,9,16+h2*.72f,0xffffc34f);
            rect(c,x-4,y-12-h1*.47f,6,12+h1*.47f,0xffffe588);
            rect(c,x-1,y-9,3,13,0xfffff0b1);
            // Small independent rising fire sparks, never an enormous torch.
            for(int i=0;i<3;i++){
                float drift=(float)Math.sin(worldTimer*2.7f+i*2.8f+x*.05f)*5f;
                float phase=(worldTimer*(12f+i*2f)+i*17f+x*.11f)%48f;
                rect(c,x-8+i*8+drift,y-8-phase,2.5f,3f,
                    i==1?0xffffdd77:0xfff79a3d);
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
        // Only lamps and flames emit after darkness; people do NOT self-illuminate.
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
            rect(c,x,y,tile,tile,(h&3)==0?0xff3b5141:0xff364d40);
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
    // Breath in three distinct frames using the UNCHANGED approved V31 atlas pixels.
    // Bottom/feet are drawn first at the original position; upper body shifts very
    // slightly relative to fixed boots. The overlap hides gaps around the waist.
    // No source pixel geometry is redrawn, recolored, regenerated or re-encoded.
    // Frame 2 of the unchanged V31 atlas has the two planted boots found in the
    // approved 10x13 master idle template. Frame 0 is a one-foot stride pose.
    // Do not change BODY_PNG or walking-frame order. The idle body is a
    // pixel-exact split of the planted stance; only the head region breathes.
    static final int APPROVED_PLANTED_IDLE_FRAME=2;
    static final int IDLE_HEAD_BODY_SPLIT=92;
    static final int IDLE_HEAD_OVERLAP=101;
    void idleBody(Canvas c,int unusedWalkFrame,float s,float breath){
        if(body==null)return;
        final int sx=APPROVED_PLANTED_IDLE_FRAME*260;
        // The exact approved feet, pants and torso remain fixed at every phase.
        src.set(sx,IDLE_HEAD_BODY_SPLIT,sx+260,160);
        dest.set(-70*s,(IDLE_HEAD_BODY_SPLIT-136)*s,190*s,24*s);
        c.drawBitmap(body,src,dest,pixel);
        // Head-only movement. 9px overlap inside the existing shirt row avoids
        // gaps around the neck and guarantees feet cannot inherit head bob.
        float headBob=breath*s;
        src.set(sx,0,sx+260,IDLE_HEAD_OVERLAP);
        dest.set(-70*s,-136*s+headBob,190*s,
                (IDLE_HEAD_OVERLAP-136)*s+headBob);
        c.drawBitmap(body,src,dest,pixel);
    }
    void handAtlas(Canvas c,int weapon,int row,float x,float y,float s,float size,float reach){
        float px=row==2?MAIN_X[weapon]:OFF_X[weapon];
        float py=row==2?MAIN_Y[weapon]:OFF_Y[weapon];
        if(px==0)return;
        c.save();
        c.translate((px-70+reach)*s,(py-136)*s);
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
                   boolean player,boolean bandit){
        float s=.76f*scale;
        // Approved character identity/palette preserved for ALL frames; V44 uses
        // original torso/head pixels with user's four WALK OUTLINES only.
        // The original approved idle/breathing animation is unchanged.
        c.save();c.translate(x,y);if(facing<0)c.scale(-1,1);
        color(0x670b1a18);c.drawOval(-26*s,-7*s,26*s,7*s,p);
        if(body!=null){
            if(breath==Float.POSITIVE_INFINITY){
                // Compensate the approved 4-frame atlas source x-origin drift.
                // This affects ONLY the body. Weapons/hands and their aim pivot
                // stay fixed in world space; NO approved sprite bytes change.
                c.save();
                c.translate(WalkAlignmentV48.sourceOffsetX(frame)*s,0f);
                atlas(c,approvedWalkColors!=null?approvedWalkColors:body,frame*260,0,0,0,s);
                c.restore();
            }else idleBody(c,frame,s,breath);
        }
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
                handAtlas(c,weapon,2,0,0,s,handScale,0);
                handAtlas(c,weapon,1,0,0,s,handScale,support);
            }
            if(anchors){
                // Debug the torso parent + the attached contact points separately.
                rect(c,pivotX-offsetX-3,pivotY-offsetY-3,6,6,0xff6ccde1);
                rect(c,(MAIN_X[weapon]-70f)*s-3,(MAIN_Y[weapon]-136f)*s-3,6,6,0xffb9e9cf);
                if(OFF_X[weapon]>0)rect(c,(OFF_X[weapon]-70f+support)*s-3,
                    (OFF_Y[weapon]-136f)*s-3,6,6,0xffe9cc8c);
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
        for(Bandit e:enemies)if(e.active)order.add(new DrawEntity(e.y,()->{
            character(c,e.x,e.y,0,e.face,e.animation.frame(),
                    e.animation.isWalking()?Float.POSITIVE_INFINITY:e.animation.breathOffset(),
                    0,0,false,true);
            rect(c,e.x-23,e.y-114,46,5,DK);rect(c,e.x-22,e.y-113,44*clamp(e.hp/78,0,1),3,RED);
        }));
        for(Survivor f:friends)order.add(new DrawEntity(f.y,()->{
            character(c,f.x,f.y,f.gun,f.face,f.animation.frame(),
                    f.animation.isWalking()?Float.POSITIVE_INFINITY:f.animation.breathOffset(),
                    Ballistics.angle(f.aimX,f.aimY,f.face),0,false,false);
            rect(c,f.x-5,f.y-117,10,4,OLIVE);
        }));
        order.add(new DrawEntity(playerY,()->{
            float angle=Ballistics.angle(aimX,aimY,face);
            character(c,playerX,playerY,gun,face,playerAnimation.frame(),
                    playerAnimation.isWalking()?Float.POSITIVE_INFINITY:playerAnimation.breathOffset(),
                    angle,recoil*2.7f,true,false);
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
        label(c,"NATIVE ANDROID SURVIVAL SHOOTER  •  ALPHA 49",
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
