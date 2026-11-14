package com.survivalparadise.nativegame;

/** Pure-JVM V139 regression for run-button gait acceleration. */
public final class RunGaitV139Test {
    static void require(boolean ok,String reason){if(!ok)throw new AssertionError(reason);}
    public static void main(String[] args){
        RunGaitV139 gait=new RunGaitV139();
        gait.step(.1f,true,false);
        require(Math.abs(gait.timeSeconds()-.1f)<.00001f,"walking baseline");
        gait.step(.1f,true,true);
        require(gait.timeSeconds()>.2f&&gait.timeSeconds()<.28f,"gradual ramp");
        gait.step(.1f,true,true);gait.step(.1f,true,true);gait.step(.1f,true,true);
        require(Math.abs(gait.runBlend()-1f)<.00001f,"full run blend");
        float phase=gait.timeSeconds();gait.step(.1f,true,true);
        require(Math.abs(gait.timeSeconds()-phase-.18f)<.00001f,"1.8x run playback");
        gait.step(.1f,true,false);
        require(gait.runBlend()<1f,"gradual release");
        gait.step(.1f,true,false);gait.step(.1f,true,false);
        require(gait.runBlend()==0f,"return to normal walking");
        gait.step(.2f,false,true);
        require(gait.timeSeconds()==0f&&gait.runBlend()==0f,"idle reset");
        System.out.println("PASS: run acceleration, deceleration, idle and 4-frame playback clock");
    }
}
