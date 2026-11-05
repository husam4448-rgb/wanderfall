package com.survivalparadise.nativegame;

public final class NpcAimV122Test {
    private static void ok(boolean v,String m){if(!v)throw new AssertionError(m);}
    private static void near(float actual,float expected,float tolerance,String m){
        ok(Math.abs(actual-expected)<=tolerance,m+" "+actual+" expected "+expected);
    }
    public static void main(String[] args){
        for(int i=0;i<24;i++){
            float theta=(float)(2*Math.PI*i/24d);
            float[] target=NpcAimV122.toward(0,0,(float)Math.cos(theta)*300,
                (float)Math.sin(theta)*300);
            near((float)Math.hypot(target[0],target[1]),1f,.001f,"unit target");
            float[] a={1,0};
            for(int n=0;n<60;n++)a=NpcAimV122.turn(a[0],a[1],target[0],target[1],1f/60f);
            ok(NpcAimV122.aligned(a[0],a[1],target[0],target[1]),
                "must target every one of 24 compass bearings "+i);
            float bearing=Ballistics.angle(a[0],a[1],NpcAimV122.facing(a[0],1));
            ok(Float.isFinite(bearing),"finite weapon bearing");
            near((float)Math.hypot(a[0],a[1]),1f,.01f,"stable normalized aim");
        }
        for(int j=0;j<24;j++){
            float t=(float)(j*2*Math.PI/24d/NpcAimV122.SCAN_RATE);
            float x=NpcAimV122.scanX(t,0),y=NpcAimV122.scanY(t,0);
            near(x,(float)Math.cos(j*2*Math.PI/24d),.001f,"scan x");
            near(y,(float)Math.sin(j*2*Math.PI/24d),.001f,"scan y");
        }
        ok(NpcAimV122.facing(-1,1)==-1,"left");
        ok(NpcAimV122.facing(1,-1)==1,"right");
        ok(NpcAimV122.facing(0,-1)==-1,"no flicker near vertical");
        ok(!NpcAimV122.aligned(1,0,-1,0),"never fire backwards while turning");
        float[] wrap=NpcAimV122.turn(-1f,.05f,-1f,-.05f,.016f);
        ok(wrap[0]<-.95f,"short arc across -180/+180 boundary");
        for(int gun=0;gun<12;gun++)
            ok(NpcGunfireV122.firearm(gun)==(gun!=3&&gun!=11),
                "only actual firearms generate shots "+gun);
        float[] v=NpcGunfireV122.velocity(0,0,0,200);
        near(v[0],0,.01f,"vertical gunfire vx");
        near(v[1],NpcGunfireV122.INDOOR_ROUND_SPEED,.01f,"vertical gunfire vy");
        near(NpcGunfireV122.life(0,0,100,0),
            100/NpcGunfireV122.INDOOR_ROUND_SPEED,.001f,"hit-scan visual arrival time");
        System.out.println("V122 NPC full-circle aiming, facing, smooth turn and firearm-only projectile FX: PASS");
    }
}
