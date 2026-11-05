package com.survivalparadise.nativegame;

public final class WeaponPivotV117Test {
    static void check(boolean valid,String m){if(!valid)throw new AssertionError(m);}
    static void near(float a,float b,String m){
        check(Math.abs(a-b)<.00001f,m+": expected "+b+", got "+a);
    }
    public static void main(String[] args) {
        check(WeaponPivotV117.clamp(-70)==-48,"minimum clamp");
        check(WeaponPivotV117.clamp(90)==48,"maximum clamp");
        check(WeaponPivotV117.clamp(0)==0,"zero default");
        for(int x=-48;x<=48;x+=4)for(int y=-48;y<=48;y+=4) {
            for(int facing:new int[]{-1,1})for(float scale:new float[]{.31f,1f,1.5f}) {
                float[] base=Ballistics.rigMuzzle(140f,520f,facing,1f,-.25f,
                    scale,152f,75f,102f,76f,0f);
                float originalX=base[0],originalY=base[1];
                float[] actual=WeaponPivotV117.relocateMuzzle(base,facing,scale,x,y);
                near(actual[0],originalX+(facing<0?-1f:1f)*x*scale,
                    "bullet / visible weapon X alignment");
                near(actual[1],originalY+y*scale,
                    "bullet / visible weapon Y alignment");
            }
        }
        for(int facing:new int[]{-1,1}){
            float[] center=Ballistics.rigMuzzle(140,520,facing,1,-.25f,
                .5f,152,75,102,76,0f);
            float x=center[0],y=center[1];
            WeaponPivotV117.relocateMuzzle(center,facing,.5f,0,0);
            near(center[0],x,"approved neutral muzzle X");
            near(center[1],y,"approved neutral muzzle Y");
        }
        check(WeaponPivotV117.MIN==-48&&WeaponPivotV117.MAX==48,
            "UI must retain symmetrical slider range");
        System.out.println("V117 independent world-space player/NPC muzzle & grip fit: PASS");
    }
}
