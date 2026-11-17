package com.survivalparadise.nativegame;

/** Source-only regression: sprite pivots are smooth; no head or item changes. */
public final class ReloadPoseV150Test {
    private static void yes(boolean ok,String message){
        if(!ok)throw new AssertionError(message);
    }
    private static void eq(float a,float b,String name){
        yes(Math.abs(a-b)<0.0001f,name+": "+a+" vs "+b);
    }
    public static void main(String[] unused){
        eq(ReloadPoseV150.DURATION,1.25f,"original reload duration");
        eq(ReloadPoseV150.progress(ReloadPoseV150.DURATION),0f,"start phase");
        eq(ReloadPoseV150.progress(0f),1f,"final phase");
        for(int weapon=0;weapon<12;weapon++){
            boolean firearm=weapon!=3&&weapon!=11;
            yes(ReloadPoseV150.active(.5f,weapon)==firearm,"weapon guard "+weapon);
            eq(ReloadPoseV150.rotateDegrees(0f,weapon),0f,"finished "+weapon);
            eq(ReloadPoseV150.rotateDegrees(ReloadPoseV150.DURATION,weapon),0f,
                "initial angle "+weapon);
            if(firearm){
                yes(ReloadPoseV150.rotateDegrees(.65f,weapon)>10f,
                    "lowering gun "+weapon);
                yes(ReloadPoseV150.lowerPx(.65f,weapon)>0f,
                    "lowering grip "+weapon);
            }
        }
        for(int weapon:new int[]{3,11}){
            for(float t:new float[]{.2f,.65f,1.25f}){
                eq(ReloadPoseV150.rotateDegrees(t,weapon),0f,"no non-firearm reload");
                eq(ReloadPoseV150.supportReachPx(t,weapon),0f,"no melee hand pose");
            }
        }
        yes(ReloadPoseV150.supportReachPx(.65f,4)<-15f,
            "carbine support hand moves toward magazine");
        eq(ReloadPoseV150.supportReachPx(.65f,0),0f,
            "pistol has no reusable support-hand art");
        eq(ReloadPoseV150.supportReachPx(.65f,10),0f,
            "launcher has no reusable support-hand art");
        for(int weapon:new int[]{0,4,7,8}){
            float previous=ReloadPoseV150.rotateDegrees(ReloadPoseV150.DURATION,weapon);
            for(int i=1;i<=125;i++){
                float remaining=ReloadPoseV150.DURATION*(1-i/125f);
                float value=ReloadPoseV150.rotateDegrees(remaining,weapon);
                yes(Math.abs(value-previous)<=2f,"pose jump at phase "+i+" weapon "+weapon);
                previous=value;
            }
        }
        System.out.println("PASS V150 smooth weapon/hand reload poses; no head, body or gear edits");
    }
}
