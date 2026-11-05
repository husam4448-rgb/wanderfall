package com.survivalparadise.nativegame;

public final class CharacterScopeV113Test {
    static void check(boolean b,String message){if(!b)throw new AssertionError(message);}
    public static void main(String[] args){
        String[] keys={"headSizeV82","headAimTiltV111","fitHeadXV108",
            "fitHeadYV108","fitIdleBreathV108","idleBreathingSpeedV110",
            "fitWalkFpsV108","walkingAnimationSpeedV79"};
        for(String k:keys){
            check(CharacterScopeV113.key(k,0).equals(k),"legacy player setting unchanged "+k);
            check(CharacterScopeV113.key(k,1).equals(k+"NpcV113"),"NPC key independent "+k);
            check(!CharacterScopeV113.key(k,0).equals(CharacterScopeV113.key(k,1)),
                "independent actor calibration "+k);
        }
        check(CharacterScopeV113.headSizeMultiplier(100)==1f,"approved V5 size at 100%");
        check(CharacterScopeV113.headSizeMultiplier(75)==.75f,"smaller actual head");
        check(CharacterScopeV113.headSizeMultiplier(160)==1.6f,"larger actual head");
        check(CharacterScopeV113.headSizeMultiplier(0)==.75f,"lower limit");
        check(CharacterScopeV113.headSizeMultiplier(200)==1.6f,"upper limit");
        for(int i=1;i<=200;i++){
            float fitted=1f+(i%40)*.01f;
            check(Math.abs(fitted*CharacterScopeV113.headSizeMultiplier(100)-fitted)<.0001f,
                "preserve all 200 V5 fittings at neutral");
            check(fitted*CharacterScopeV113.headSizeMultiplier(140)>fitted,
                "change size for every character");
        }
        System.out.println("V113 independent player/NPC slider keys and 200 V5 head sizes: PASS");
    }
}
