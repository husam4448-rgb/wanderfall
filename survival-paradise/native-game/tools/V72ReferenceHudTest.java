package com.survivalparadise.nativegame;
public final class V72ReferenceHudTest {
    static void ok(boolean b,String message){if(!b)throw new AssertionError(message);}
    static void near(float x,float target,String message){
        ok(Math.abs(x-target)<2f,message+" got="+x+" expected="+target);
    }
    public static void main(String[] args){
        int F=LegacyControlsV58.FIRE_L,R=LegacyControlsV58.FIRE_R;
        int M=LegacyControlsV58.MELEE_L,MR=LegacyControlsV58.MELEE_R;
        int RU=LegacyControlsV58.RUN;
        near(LegacyControlsV58.defaultX(F,1480),333,"reference left fire X");
        near(LegacyControlsV58.defaultY(F,720),418,"reference left fire Y");
        near(LegacyControlsV58.defaultX(R,1480),1015,"reference right fire X");
        near(LegacyControlsV58.defaultY(R,720),396,"reference right fire Y");
        near(LegacyControlsV58.defaultX(M,1480),360,"reference left melee X");
        near(LegacyControlsV58.defaultX(MR,1480),979,"reference right melee X");
        near(LegacyControlsV58.defaultX(RU,1480),1335,"reference RUN upper right");
        near(LegacyControlsV58.defaultY(RU,720),348,"reference RUN Y");
        ok(!LegacyControlsV58.defaultEnabled(LegacyControlsV58.CROUCH),
           "reference screenshot hides crouch button");
        ok(LegacyControlsV58.defaultScale(R)>=135,
           "screenshot larger fire button");
        for(int[] size:new int[][]{{1480,720},{1200,660}}){
            float w=size[0],h=size[1];
            for(int a=0;a<LegacyControlsV58.COUNT;a++){
                if(!LegacyControlsV58.defaultEnabled(a))continue;
                float ax=LegacyControlsV58.defaultX(a,w),ay=LegacyControlsV58.defaultY(a,h);
                float aw=LegacyControlsV58.defaultW(a)*LegacyControlsV58.defaultScale(a)/100f;
                float ah=LegacyControlsV58.defaultH(a)*LegacyControlsV58.defaultScale(a)/100f;
                ok(ax>=0&&ay>=0&&ax+aw<=w&&ay+ah<=h,
                   "reference HUD button on-screen "+a+" size "+w);
                for(int b=0;b<a;b++){
                    if(!LegacyControlsV58.defaultEnabled(b))continue;
                    float bx=LegacyControlsV58.defaultX(b,w);
                    float by=LegacyControlsV58.defaultY(b,h);
                    float bw=LegacyControlsV58.defaultW(b)*LegacyControlsV58.defaultScale(b)/100f;
                    float bh=LegacyControlsV58.defaultH(b)*LegacyControlsV58.defaultScale(b)/100f;
                    boolean intersection=ax<bx+bw&&ax+aw>bx&&ay<by+bh&&ay+ah>by;
                    ok(!intersection,"HUD controls overlap "+a+" and "+b+" at "+w);
                }
            }
        }
        System.out.println("V72 PASS: reference screenshot HUD layout and no button overlap");
    }
}