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
    Bitmap body,gear;
    final Random rng=new Random(14901);
    static final float H=660, WORLD_W=3200, WORLD_H=2200;
    static final int[] RANGES={250,265,220,0,430,415,395,325,650,435,330,74};
    static final int[] MAG={12,6,28,1,30,30,28,6,5,75,8,1};
    static final float[] RATES={.35f,.54f,.14f,999,.13f,.19f,.2f,.68f,1.35f,.095f,.95f,.58f};
    static final int[] POWER={23,37,12,0,15,20,19,46,110,11,78,52};
    static final float[] MX={147,171,154,129,220,215,213,225,238,228,216,183};
    static final float[] MY={79,73,75,88,75,78,72,80,74,72,71,92};
    static final float[] MAIN_X={103,103,103,97,102,101,101,101,101,102,101,102};
    static final float[] MAIN_Y={76,75,76,78,77,77,77,77,77,77,77,81};
    static final float[] OFF_X={0,0,0,0,135,146,148,151,145,149,141,0};
    static final float[] OFF_Y={0,0,0,0,77,75,72,75,73,71,74,0};
    static final int DK=0xff101b1a,WHITE=0xffedf2e6,OLIVE=0xff8ab397,ORANGE=0xffe8bc72,RED=0xffce766b;

    float scale=1,handScale=1,support=0,timeSpeed=1,zoom=1;
    boolean showHands=true,showWeapons=true,anchors=false,hitboxes=false,enemyAI=true,
            aimRotation=true,recoilFX=true,lootEnabled=true,night=false;
    boolean playing=false,paused=false,settingsPause=false,wasPaused=false,hasSave=false,gameOver=false;
    float playerX=1000,playerY=1060,health=100,stamina=100,walkClock=0,shotClock=0,reloadClock=0,recoil=0;
    float aimX=1,aimY=0,stickX=0,stickY=0;
    int face=1,gun=0,ammo=12,kills=0,wave=1,scrap=0,medkits=0,ammoPacks=0,enemyCount=0;
    float worldTimer=0,autSaveClock=0,shake=0;
    long lastFrame=0;
    float viewW=1200,viewH=660,drawScale=1,camX=0,camY=0;
    int leftPointer=-1,rightPointer=-1;
    boolean firing=false,moving=false;
    final ArrayList<Bandit> enemies=new ArrayList<>();
    final ArrayList<Survivor> friends=new ArrayList<>();
    final ArrayList<Shot> shots=new ArrayList<>();
    final ArrayList<Drop> drops=new ArrayList<>();
    final ArrayList<Spark> sparks=new ArrayList<>();
    final ArrayList<Cover> covers=new ArrayList<>();
    int allySetting=1,allyCurrent=1;
    final Rect src=new Rect();
    final RectF dest=new RectF();
    final float PAD=46;
    static class Bandit {float x,y,hp=78,cd,walk,hit;int face=1;boolean active=true;
        Bandit(float a,float b){x=a;y=b;cd=.7f;}}
    static class Survivor {float x,y,cd,walk;int gun,face=1;
        Survivor(float a,float b,int g){x=a;y=b;gun=g;}}
    static class Shot {float x,y,vx,vy,life,damage;boolean hostile;int color;
        Shot(float x,float y,float vx,float vy,float damage,boolean enemy){
            this.x=x;this.y=y;this.vx=vx;this.vy=vy;this.damage=damage;this.life=1.3f;
            this.hostile=enemy;this.color=enemy?0xffffa88a:0xffeada9e;
        }}
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
        night=host.option("night",false);
        int next=host.setting("gun",0);
        if(next!=gun){gun=Math.max(0,Math.min(11,next));ammo=MAG[gun];reloadClock=0;}
        allySetting=host.setting("survivors",1);
        if(playing)adjustFriends();
        invalidate();
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
        playerX=1000;playerY=1060;health=100;stamina=100;walkClock=0;shotClock=0;
        gun=Math.max(0,Math.min(11,host.setting("gun",0)));ammo=MAG[gun];
        kills=0;wave=1;scrap=0;medkits=1;ammoPacks=2;worldTimer=0;autSaveClock=0;
        enemies.clear();friends.clear();shots.clear();drops.clear();sparks.clear();
        playing=true;paused=false;settingsPause=false;gameOver=false;
        adjustFriends();spawnWave();
        saveProgress();invalidate();
    }
    void continueGame(){
        if(!hasSave){newGame();return;}
        playerX=host.prefs.getFloat("px",1000);playerY=host.prefs.getFloat("py",1060);
        health=host.prefs.getFloat("hp",100);kills=host.setting("kills",0);
        wave=Math.max(1,host.setting("wave",1));
        scrap=host.setting("scrap",0);medkits=host.setting("medkits",1);ammoPacks=host.setting("ammoPacks",2);
        gun=Math.max(0,Math.min(11,host.setting("gun",0)));
        ammo=Math.max(0,Math.min(MAG[gun],host.setting("ammo",MAG[gun])));
        enemies.clear();friends.clear();shots.clear();drops.clear();sparks.clear();
        playing=true;paused=false;gameOver=false;
        adjustFriends();spawnWave();invalidate();
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
                .putInt("ammoPacks",ammoPacks).putInt("ammo",ammo).apply();
        hasSave=true;
    }
    void menuPause(boolean b){
        if(b){wasPaused=paused;settingsPause=true;paused=true;}
        else{settingsPause=false;paused=wasPaused;}
        invalidate();
    }
    void togglePause(){if(!playing)return;paused=!paused;saveProgress();invalidate();}
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
    void shoot(float x,float y,float dx,float dy,int weapon,boolean hostile){
        float length=(float)Math.hypot(dx,dy);if(length<.01f){dx=1;dy=0;length=1;}
        dx/=length;dy/=length;
        if(weapon==3)return;
        if(weapon==11){
            if(hostile){if(distance(x,y,playerX,playerY)<92)hurt(POWER[11]);}
            else for(Bandit e:enemies)if(e.active&&distance(x,y,e.x,e.y)<88)damage(e,POWER[11]);
            particles(x+dx*26,y-35,ORANGE,3);
            return;
        }
        int pellets=weapon==7?5:1;
        float theta=(float)Math.atan2(dy,dx);
        float spriteFactor=.72f*scale;
        float mx=(MX[weapon]-70)*spriteFactor;
        float my=(MY[weapon]-136)*spriteFactor;
        float bx=x+Math.signum(dx==0?1:dx)*mx;
        float by=y+my;
        for(int i=0;i<pellets;i++){
            float jitter=(rng.nextFloat()-.5f)*(weapon==7?.34f:.055f);
            float angle=theta+jitter;float speed=weapon==10?640:870;
            Shot bullet=new Shot(bx,by,(float)Math.cos(angle)*speed,
                    (float)Math.sin(angle)*speed,POWER[weapon]/(pellets==5?2f:1f),hostile);
            shots.add(bullet);
        }
        particles(bx,by,ORANGE,weapon==10?9:4);
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
        dt=Math.min(.04f,dt)*timeSpeed;
        worldTimer+=dt;autSaveClock+=dt;
        if(autSaveClock>9){saveProgress();autSaveClock=0;}
        shotClock=Math.max(0,shotClock-dt);
        recoil=Math.max(0,recoil-dt*5);
        if(reloadClock>0){
            reloadClock-=dt;if(reloadClock<=0){ammo=MAG[gun];reloadClock=0;}
        }
        float vx=stickX,vy=stickY;
        float length=(float)Math.hypot(vx,vy);
        if(length>.06f){
            vx/=Math.max(1,length);vy/=Math.max(1,length);
            float speed=gun==9?147:207;
            float nx=clamp(playerX+vx*speed*dt,35,WORLD_W-40);
            float ny=clamp(playerY+vy*speed*dt,50,WORLD_H-40);
            if(!blocked(nx,playerY,20))playerX=nx;
            if(!blocked(playerX,ny,20))playerY=ny;
            walkClock+=dt*7;
            if(!firing)face=vx>=0?1:-1;
            moving=true;
        }else moving=false;
        if(firing){
            if(aimX>.1f)face=1;else if(aimX<-.1f)face=-1;
            if(shotClock<=0&&reloadClock==0){
                if(ammo>0||gun==11||gun==3){
                    shoot(playerX,playerY,aimX,aimY,gun,false);
                    if(gun!=3){shotClock=RATES[gun];ammo=Math.max(0,ammo-1);recoil=recoilFX?1:0;}
                }else reload();
            }
        }
        for(Survivor friend:friends){
            friend.cd=Math.max(0,friend.cd-dt);
            float d=distance(friend.x,friend.y,playerX,playerY);
            if(d>80){
                float ux=(playerX-friend.x)/Math.max(1,d),uy=(playerY-friend.y)/Math.max(1,d);
                float nx=friend.x+ux*170*dt,ny=friend.y+uy*170*dt;
                if(!blocked(nx,friend.y,18))friend.x=nx;
                if(!blocked(friend.x,ny,18))friend.y=ny;
                friend.walk+=dt*7;friend.face=ux>=0?1:-1;
            }
            Bandit target=nearest(friend.x,friend.y,460);
            if(target!=null&&friend.cd<=0){
                float dx=target.x-friend.x,dy=target.y-friend.y;
                friend.face=dx>=0?1:-1;
                shoot(friend.x,friend.y,dx,dy,friend.gun,false);
                friend.cd=RATES[friend.gun]+.2f;
            }
        }
        if(enemyAI)for(Bandit e:enemies){
            if(!e.active)continue;
            e.cd-=dt;e.hit=Math.max(0,e.hit-dt);
            float d=distance(e.x,e.y,playerX,playerY);
            if(d<520){
                float dx=(playerX-e.x)/Math.max(1,d),dy=(playerY-e.y)/Math.max(1,d);
                e.face=dx>=0?1:-1;
                if(d>240){
                    float nx=e.x+dx*105*dt,ny=e.y+dy*105*dt;
                    if(!blocked(nx,e.y,18))e.x=nx;
                    if(!blocked(e.x,ny,18))e.y=ny;
                    e.walk+=dt*6;
                }else if(e.cd<=0){
                    shoot(e.x,e.y,dx,dy,0,true);
                    e.cd=1.1f+rng.nextFloat()*.7f;
                }
            }
        }
        for(Iterator<Shot> iter=shots.iterator();iter.hasNext();){
            Shot s=iter.next();
            float nx=s.x+s.vx*dt,ny=s.y+s.vy*dt;s.life-=dt;
            boolean done=s.life<=0||blocked(nx,ny-18,2);
            if(!done&&s.hostile){
                if(distance(nx,ny,playerX,playerY-28)<34){hurt(s.damage);done=true;}
            }else if(!done){
                for(Bandit e:enemies)if(e.active&&distance(nx,ny,e.x,e.y-28)<32){
                    damage(e,s.damage);done=true;break;
                }
            }
            if(done)iter.remove();else{s.x=nx;s.y=ny;}
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
    void character(Canvas c,float x,float y,int weapon,int facing,float move,float aimAng,float kick,
                   boolean player,boolean bandit){
        float s=.76f*scale;
        int frame=move>0?(int)(move*1.25f)%4:0;
        c.save();c.translate(x,y);if(facing<0)c.scale(-1,1);
        color(0x670b1a18);c.drawOval(-26*s,-7*s,26*s,7*s,p);
        if(body!=null)atlas(c,body,frame*260,0,0,0,s);
        if(!bandit){
            c.save();
            float pivotX=(MAIN_X[weapon]-70)*s,pivotY=(MAIN_Y[weapon]-136)*s;
            c.translate(pivotX-kick,pivotY);
            c.rotate(aimRotation?clamp(aimAng,-.35f,.35f)*180/(float)Math.PI:0);
            c.translate(-pivotX,-pivotY);
            if(showWeapons)atlas(c,gear,weapon*260,0,0,0,s);
            if(showHands){
                handAtlas(c,weapon,2,0,0,s,handScale,0);
                handAtlas(c,weapon,1,0,0,s,handScale,support);
            }
            if(anchors){
                rect(c,pivotX-3,pivotY-3,6,6,0xffb9e9cf);
                if(OFF_X[weapon]>0)rect(c,(OFF_X[weapon]-70+support)*s-3,(OFF_Y[weapon]-136)*s-3,6,6,0xffb9e9cf);
            }
            c.restore();
        }else{
            // Bandit overlay is NEW independent art. Body pixels are not changed.
            rect(c,-16*s,-100*s,27*s,5*s,RED);
            rect(c,-16*s,-90*s,12*s,5*s,0xffad5b52);
        }
        if(hitboxes){color(bandit?RED:OLIVE);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1);
            c.drawRect(-23,-92,23,0,p);p.setStyle(Paint.Style.FILL);}
        c.restore();
    }
    void drawWorld(Canvas c){
        c.save();c.translate(-camX,-camY);
        terrain(c);
        for(Drop d:drops){
            float bob=(float)Math.sin(worldTimer*5+d.x)*2;
            rect(c,d.x-9,d.y-13+bob,18,16,DK);
            rect(c,d.x-7,d.y-11+bob,14,12,d.type==2?0xffd7e2d7:d.type==1?0xff8e9b9d:ORANGE);
            if(d.type==2){rect(c,d.x-1,d.y-9+bob,3,9,RED);rect(c,d.x-5,d.y-6+bob,11,3,RED);}
        }
        ArrayList<DrawEntity> order=new ArrayList<>();
        for(Bandit e:enemies)if(e.active)order.add(new DrawEntity(e.y,()->{
            character(c,e.x,e.y,0,e.face,e.walk,0,0,false,true);
            rect(c,e.x-23,e.y-114,46,5,DK);rect(c,e.x-22,e.y-113,44*clamp(e.hp/78,0,1),3,RED);
        }));
        for(Survivor f:friends)order.add(new DrawEntity(f.y,()->{
            character(c,f.x,f.y,f.gun,f.face,f.walk,0,0,false,false);
            rect(c,f.x-5,f.y-117,10,4,OLIVE);
        }));
        order.add(new DrawEntity(playerY,()->{
            float angle=(float)Math.atan2(aimY,Math.max(.1f,Math.abs(aimX)));
            character(c,playerX,playerY,gun,face,walkClock,angle,recoil*2.7f,true,false);
        }));
        order.sort((a,b)->Float.compare(a.y,b.y));
        for(DrawEntity e:order)e.draw.run();
        for(Shot s:shots){
            rect(c,s.x-3,s.y-2,7,4,s.color);
            rect(c,s.x-s.vx*.012f,s.y-s.vy*.012f,4,4,s.color);
        }
        for(Spark s:sparks)rect(c,s.x,s.y,4,4,s.color);
        if(night){
            // Accessible night mode: dark tint + fixed-radius illumination around player.
            color(0x95031015);c.drawRect(camX,camY,camX+viewW,camY+viewH,p);
            color(0xffb9bca2);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);
            c.drawCircle(playerX,playerY-52,68,p);p.setStyle(Paint.Style.FILL);
        }
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
        rect(c,0,viewH-42,viewW,42,0xca122529);
        label(c,"SCRAP "+scrap+"   MED "+medkits+"   AMMO BOX "+ammoPacks+
                "   "+MainActivity.LOADOUTS[gun],14,viewH-16,14,ORANGE,true);
        // Independent touch controls, never an autonomous-only simulation.
        float jy=viewH-140,rx=viewW-118,ry=viewH-145;
        color(0x663e625a);c.drawCircle(120,jy,86,p);
        color(0x9b96b8a5);c.drawCircle(120+stickX*46,jy+stickY*46,31,p);
        color(0x665b6f61);c.drawCircle(rx,ry,82,p);
        color(0xaaaa9d71);c.drawCircle(rx,ry,52,p);
        label(c,"FIRE",rx-20,ry+6,19,WHITE,true);
        btn(c,viewW-348,viewH-105,103,44,"RELOAD",0xff344e51);
        btn(c,viewW-348,viewH-160,103,44,"SWAP",0xff344e51);
        label(c,"MOVE",81,viewH-30,12,0xffb8d4c5,true);
        if(reloadClock>0)label(c,"RELOADING...",viewW-235,viewH-227,17,ORANGE,true);
    }
    void menu(Canvas c){
        rounded(c,viewW/2-300,viewH/2-200,600,398,20,0xef14272b);
        label(c,"SURVIVAL PARADISE",viewW/2-254,viewH/2-115,34,WHITE,true);
        label(c,"NATIVE ANDROID SURVIVAL SHOOTER  •  ALPHA 34",
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
            if(length>.14){aimX=dx;aimY=dy;}
            else{
                Bandit closest=nearest(playerX,playerY,680);
                if(closest!=null){float ax=closest.x-playerX,ay=closest.y-playerY;
                    float d=(float)Math.hypot(ax,ay);aimX=ax/Math.max(1,d);aimY=ay/Math.max(1,d);}
                else {aimX=face;aimY=0;}
            }
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
                    rightPointer=id;firing=true;updateStick(x,y,true);return true;
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
                    leftPointer=-1;stickX=0;stickY=0;
                }
                if(id==rightPointer||action==MotionEvent.ACTION_CANCEL){
                    rightPointer=-1;firing=false;
                }
                return true;
        }
        return true;
    }
}
