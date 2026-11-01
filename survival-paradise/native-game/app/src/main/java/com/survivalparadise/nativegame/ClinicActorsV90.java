package com.survivalparadise.nativegame;

/** Finite indoor encounters; persisted independently from outside NPC waves. */
public final class ClinicActorsV90 {
    public static final int ZOMBIE=0,FERAL=1,RAIDER=2,MEDIC=3,SURVIVOR=4;
    public static final class Actor {
        public final int type;
        public float x,y,hp,cooldown,wandering;
        public final float spawnX,spawnY;
        public boolean active=true;
        Actor(int type,float x,float y,float hp){
            this.type=type;this.x=x;this.y=y;this.spawnX=x;this.spawnY=y;
            this.hp=hp;
        }
        public boolean hostile(){return type<=RAIDER;}
    }
    private static final int[] TYPES={ZOMBIE,ZOMBIE,ZOMBIE,FERAL,FERAL,RAIDER,
        MEDIC,SURVIVOR};
    // World coordinates are scaled from the authored original department map.
    private static final float[][] START={
        {465,423},{740,425},{1254,415},{1384,951},{270,977},{1222,932},
        {898,421},{380,419}
    };
    public final Actor[] actors=new Actor[TYPES.length];
    public ClinicActorsV90(ClinicInteriorV89 map){reset(map);}
    public void reset(ClinicInteriorV89 map){
        for(int i=0;i<actors.length;i++){
            float x=START[i][0]*ClinicInteriorV89.EXPANSION_V90;
            float y=START[i][1]*ClinicInteriorV89.EXPANSION_V90;
            if(map.blocked(x,y,13)){
                boolean found=false;
                for(int rad=20;rad<=210&&!found;rad+=20)
                    for(int angle=0;angle<16;angle++){
                        float a=(float)(angle*Math.PI/8);
                        float tx=x+(float)Math.cos(a)*rad;
                        float ty=y+(float)Math.sin(a)*rad;
                        if(!map.blocked(tx,ty,14)){
                            x=tx;y=ty;found=true;break;
                        }
                    }
            }
            actors[i]=new Actor(TYPES[i],x,y,TYPES[i]==FERAL?55:85);
        }
    }
    public static boolean lineOfSight(ClinicInteriorV89 map,float x,float y,
                                      float px,float py){
        float dx=px-x,dy=py-y,len=(float)Math.hypot(dx,dy);
        if(len<1)return true;
        int steps=Math.max(1,(int)Math.ceil(len/20f));
        for(int i=1;i<steps;i++){
            float t=(float)i/steps;
            if(map.blocked(x+dx*t,y+dy*t,3f))return false;
        }
        return true;
    }
    /** One stable deterministic tick, returns cumulative player damage. */
    public float tick(float dt,float px,float py,ClinicInteriorV89 map){
        dt=Math.min(.05f,Math.max(0f,dt));
        float damage=0f;
        for(Actor a:actors){
            if(!a.active)continue;
            a.cooldown=Math.max(0,a.cooldown-dt);
            a.wandering+=dt;
            float dx=px-a.x,dy=py-a.y,d=(float)Math.hypot(dx,dy);
            boolean sees=d<500&&lineOfSight(map,a.x,a.y,px,py);
            float mx,my,speed;
            if(a.hostile()&&sees){
                mx=dx/Math.max(1,d);my=dy/Math.max(1,d);
                speed=a.type==FERAL?118f:a.type==RAIDER?92f:61f;
                if(a.type==RAIDER&&d<180){
                    mx=-my;my=dx/Math.max(1,d); // flank rather than close
                }
            }else{
                float angle=a.wandering*.45f+a.type*1.2f;
                mx=(float)Math.cos(angle);my=(float)Math.sin(angle);
                speed=a.hostile()?18f:27f;
                if(Math.hypot(a.x-a.spawnX,a.y-a.spawnY)>185){
                    float home=(float)Math.atan2(a.spawnY-a.y,a.spawnX-a.x);
                    mx=(float)Math.cos(home);my=(float)Math.sin(home);
                }
            }
            if(!a.hostile()&&d<100){mx=-dx/Math.max(1,d);my=-dy/Math.max(1,d);}
            float nx=a.x+mx*speed*dt,ny=a.y+my*speed*dt;
            if(!map.blocked(nx,a.y,16))a.x=nx;
            if(!map.blocked(a.x,ny,16))a.y=ny;
            if(a.hostile()&&sees&&d<(a.type==RAIDER?245:64)&&a.cooldown<=0){
                damage+=a.type==FERAL?9f:a.type==RAIDER?6f:6f;
                a.cooldown=a.type==FERAL?1.1f:a.type==RAIDER?1.65f:1.45f;
            }
        }
        return damage;
    }
    /** Use a small aim-width tolerance, but never hit actors through walls. */
    public Actor target(float px,float py,float dx,float dy,
                        float reach,ClinicInteriorV89 map){
        float m=(float)Math.hypot(dx,dy);if(m<.01f)return null;
        dx/=m;dy/=m;
        Actor best=null;float bestDistance=reach;
        for(Actor a:actors){
            if(!a.active||!a.hostile())continue;
            float ax=a.x-px,ay=a.y-py;
            float dot=ax*dx+ay*dy;
            if(dot<=0||dot>bestDistance)continue;
            float lateral=Math.abs(ax*dy-ay*dx);
            if(lateral>30f)continue;
            if(!lineOfSight(map,px,py,a.x,a.y))continue;
            bestDistance=dot;best=a;
        }
        return best;
    }
    public boolean hit(Actor target,float damage){
        if(target==null||!target.active||!target.hostile())return false;
        target.hp=Math.max(0,target.hp-Math.max(0,damage));
        if(target.hp==0)target.active=false;
        return true;
    }
    public String encode(){
        StringBuilder b=new StringBuilder();
        for(Actor a:actors){
            if(b.length()>0)b.append(';');
            b.append(a.type).append(',').append(Math.round(a.x))
                .append(',').append(Math.round(a.y))
                .append(',').append(Math.round(a.hp))
                .append(',').append(a.active?1:0);
        }
        return b.toString();
    }
    public void decode(String data,ClinicInteriorV89 map){
        reset(map);if(data==null||data.isEmpty())return;
        String[] groups=data.split(";");
        if(groups.length!=actors.length)return;
        int[][] parsed=new int[actors.length][5];
        try{
            for(int i=0;i<groups.length;i++){
                String[] p=groups[i].split(",");
                if(p.length!=5)return;
                for(int j=0;j<5;j++)parsed[i][j]=Integer.parseInt(p[j]);
                if(parsed[i][0]!=actors[i].type||parsed[i][3]<0||
                    parsed[i][3]>100||parsed[i][4]<0||parsed[i][4]>1||
                    parsed[i][1]<30||parsed[i][1]>ClinicInteriorV89.WIDTH-30||
                    parsed[i][2]<30||parsed[i][2]>ClinicInteriorV89.HEIGHT-30)
                    return;
            }
            for(int i=0;i<actors.length;i++){
                Actor a=actors[i];a.x=parsed[i][1];a.y=parsed[i][2];
                a.hp=parsed[i][3];a.active=parsed[i][4]==1&&a.hp>0;
            }
        }catch(NumberFormatException ignored){reset(map);}
    }
}
