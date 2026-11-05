package com.survivalparadise.nativegame;

/** No Android dependencies: verify observable V110 visual animation timing. */
public final class CharacterAnimationV110Test {
    static void check(boolean ok,String label) {
        if(!ok)throw new AssertionError(label);
    }
    public static void main(String[] args) {
        check(CharacterAnimationV110.bodyFrame(false,8f,2,0,1f)==0,
              "idle remains a fixed, original body pose");
        check(CharacterAnimationV110.bodyFrame(true,0f,2,0,1f)==1,
              "walking begins on approved original pose 1");
        check(CharacterAnimationV110.bodyFrame(true,.3f,2,0,1f)==1,
              "default retains fitted V109 rate");
        check(CharacterAnimationV110.bodyFrame(true,.3f,2,0,2f)==2,
              "200% visibly advances faster");
        check(CharacterAnimationV110.bodyFrame(true,.6f,2,0,.5f)==1,
              "50% visibly advances slower");
        check(CharacterAnimationV110.bodyFrame(true,.3f,2,4,1f)==2,
              "fixed-fps override changes the base rate");
        check(CharacterAnimationV110.bodyFrame(true,.3f,2,4,.5f)==1,
              "walk speed slider still works with fixed-fps override");
        check(CharacterAnimationV110.bodyFrame(true,.3f,3,0,1f)==1,
              "V5 individual fitted rate retained");
        for(int id=1;id<=200;id++)for(int n=0;n<1000;n++){
            int frame=CharacterAnimationV110.bodyFrame(true,n*.016f,2,0,1f);
            check(frame>=1&&frame<=4,"no altered/extra walk frames");
        }
        float t=(float)Math.PI/8f; // sin(4t)=1 at default speed
        check(Math.abs(CharacterAnimationV110.breathOffset(false,t,3,1f)-3f)<.0001f,
              "default smooth head-only breathing");
        check(Math.abs(CharacterAnimationV110.breathOffset(false,t,3,2f))<.0001f,
              "200% breathing completes a phase twice as fast");
        check(Math.abs(CharacterAnimationV110.breathOffset(false,t,3,.5f)-
              3f*(float)Math.sqrt(.5))<.0001f,
              "50% breathing is slower");
        check(CharacterAnimationV110.breathOffset(true,t,3,2f)==0f,
              "walking disables idle breathing");
        check(CharacterAnimationV110.breathOffset(false,t,0,1f)==0f,
              "zero breathing amplitude holds head still");
        check(CharacterAnimationV110.breathingMultiplier(100)==1f,
              "default 100% breathing rate");
        check(CharacterAnimationV110.breathingMultiplier(25)==.25f &&
              CharacterAnimationV110.breathingMultiplier(250)==2.5f,
              "complete adjustable breathing range");
        System.out.println("V110 adjustable visual animation regression: PASS");
    }
}
