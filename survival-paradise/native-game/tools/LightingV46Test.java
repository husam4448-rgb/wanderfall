package com.survivalparadise.nativegame;

public final class LightingV46Test {
    private static void check(boolean b,String why){if(!b)throw new AssertionError(why);}
    public static void main(String[] args){
        int darkness=211;
        check(LightMathV46.shadowAlpha(darkness,0)==darkness,"Unlit NPC and world should be equally dark");
        check(LightMathV46.pointStrength(0,0,200,.9f)>.88f,"Campfire must visibly illuminate center");
        check(LightMathV46.shadowAlpha(darkness,LightMathV46.pointStrength(0,0,200,.9f))<30,"Fire removes actual darkness");
        check(LightMathV46.pointStrength(230,0,200,.9f)==0,"Fire doesn't light infinite distances");
        float blue=LightMathV46.pointStrength(36,20,202,.77f);
        check(blue>.3f,"Building neon casts localized light");
        float forward=LightMathV46.flashlightStrength(175,0,1,0,490);
        float reversed=LightMathV46.flashlightStrength(-175,0,-1,0,490);
        check(forward>.65f&&Math.abs(forward-reversed)<.001f,"Flashlight must work in both facing directions");
        check(LightMathV46.flashlightStrength(-175,0,1,0,490)==0,"No backwards beam");
        check(LightMathV46.flashlightStrength(0,210,1,0,490)==0,"Beam not omnidirectional");
        check(LightMathV46.flashlightStrength(500,0,1,0,490)==0,"Outside flashlight range stays dark");
        check(LightMathV46.shadowAlpha(darkness,forward)<75,"A flashlight must cut a visible light path through darkness");
        float occluded=LightGeometryV45.rayBox(0,0,1,0,490,110,-30,155,30);
        check(occluded>107&&occluded<109,"Building blocks flashlight at the actual wall boundary");
        check(LightMathV46.shadowAlpha(0,0)==0,"Daylight remains fully visible");
        System.out.println("V46 LIGHTING PASS: actual darkness, candle/neon falloff, left/right flashlight, wall occlusion");
    }
}