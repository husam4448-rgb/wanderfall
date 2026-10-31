package com.survivalparadise.nativegame;

/** JVM validation: animation-only slider follows motion with optional tempo trim. */
public final class V79WalkingAnimationTest {
    private static void ok(boolean valid,String what){
        if(!valid)throw new AssertionError(what);
    }
    private static void eq(float a,float b){
        if(Math.abs(a-b)>.0001f)throw new AssertionError(a+" != "+b);
    }
    private static int frameAfter(int percent,float walkMultiplier,float seconds){
        AnimationCycle cycle=new AnimationCycle();
        float dt=1f/120f;
        float gait=WalkingAnimationV79.rate(PlayerMovementV77.gait(walkMultiplier,false),percent);
        int count=(int)(seconds/dt);
        for(int i=0;i<count;i++)cycle.step(true,dt,gait);
        ok(cycle.isWalking(),"moving player must animate");
        return cycle.frame();
    }
    public static void main(String[] args){
        eq(WalkingAnimationV79.multiplier(100),1f);
        eq(WalkingAnimationV79.multiplier(50),.5f);
        eq(WalkingAnimationV79.multiplier(200),2f);
        eq(WalkingAnimationV79.multiplier(5),.5f);
        eq(WalkingAnimationV79.multiplier(999),2f);
        eq(WalkingAnimationV79.rate(PlayerMovementV77.gait(1.3f,false),100),
           PlayerMovementV77.gait(1.3f,false));
        eq(WalkingAnimationV79.rate(PlayerMovementV77.gait(1.3f,true),100),12.61f);
        eq(WalkingAnimationV79.rate(PlayerMovementV77.gait(1.3f,false),50),5.33f);
        eq(WalkingAnimationV79.rate(PlayerMovementV77.gait(1.3f,false),200),21.32f);
        // Animation slider does not change running/crouch or collision physics.
        eq(PlayerMovementV77.speed(236f,1.3f,1f,false),306.8f);
        eq(PlayerMovementV77.speed(236f,1.3f,1.52f,false),466.336f);
        eq(PlayerMovementV77.speed(236f,1.3f,1f,true),162.604f);
        int slow=frameAfter(50,1.3f,.30f);
        int normal=frameAfter(100,1.3f,.30f);
        int fast=frameAfter(200,1.3f,.30f);
        ok(slow!=normal||normal!=fast,"animation slider has no visible effect");
        AnimationCycle still=new AnimationCycle();
        still.step(false,1f/60f,WalkingAnimationV79.rate(8.2f,200));
        ok(!still.isWalking()&&still.frame()==AnimationCycle.IDLE_FRAME,
            "idle feet/pose changed");
        for(int i=0;i<90;i++)still.step(false,1f/60f,WalkingAnimationV79.rate(8.2f,50));
        ok(!still.isWalking(),"idle should not become walking at high tempo");
        System.out.println("V79 PASS: gait 50-200%, auto-linked at 100%, sprites and movement unchanged");
    }
}
