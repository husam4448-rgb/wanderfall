package com.survivalparadise.nativegame;

public final class TorsoWidthV114Test {
    static void check(boolean b,String message) {
        if(!b)throw new AssertionError(message);
    }
    static void near(float actual,float expected,String message) {
        check(Math.abs(actual-expected)<.00001f,
              message+" expected "+expected+" got "+actual);
    }
    public static void main(String[] args) {
        check(TorsoWidthV114.TORSO_TOP==160,"V109 approved head mask ends at y=160");
        check(TorsoWidthV114.LOWER_BODY_TOP==180,"pants begin at y=180");
        check(TorsoWidthV114.percent(100)==100,"neutral original width");
        check(TorsoWidthV114.percent(55)==55,"maximum narrowing");
        check(TorsoWidthV114.percent(0)==55,"avoid zero-width torso");
        check(TorsoWidthV114.percent(150)==100,"never widen original torso");
        near(TorsoWidthV114.margin(100),0f,"neutral has no width change");
        near(TorsoWidthV114.margin(80),20f,"80% narrows both sides by 20 source px");
        near(TorsoWidthV114.margin(60),40f,"60% narrows both sides by 40 source px");
        for(int percent=55;percent<=100;percent++){
            float left=TorsoWidthV114.left(-100f,1f,percent);
            float right=TorsoWidthV114.right(-100f,1f,percent);
            near((left+right)*.5f,0f,"torso centered "+percent);
            near(right-left,200f*percent/100f,"symmetric torso span "+percent);
            // All source pixels at y=180..259 belong to a single unchanged draw.
            for(int row=180;row<260;row++){
                check(TorsoWidthV114.isUnchangedLowerBody(row),
                    "all original pants, legs and feet must remain untouched");
            }
            check(!TorsoWidthV114.isUnchangedLowerBody(160),
                "only upper torso can be scaled");
            check(!TorsoWidthV114.isUnchangedLowerBody(179),
                "last upper torso row scales");
        }
        System.out.println("V114 torso-only narrowing, centered / original legs & feet: PASS");
    }
}
