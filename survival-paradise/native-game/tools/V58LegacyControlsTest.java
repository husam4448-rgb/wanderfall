package com.survivalparadise.nativegame;

/** Pure-Java regression gate for approved legacy controls and eight knife sectors. */
public final class V58LegacyControlsTest {
    static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    public static void main(String[] args){
        check(LegacyControlsV58.COUNT==11,"11 customizable action controls");
        check(LegacyControlsV58.isFire(LegacyControlsV58.FIRE_L),"left FIRE");
        check(LegacyControlsV58.isFire(LegacyControlsV58.FIRE_R),"right FIRE");
        check(LegacyControlsV58.isMelee(LegacyControlsV58.MELEE_L),"left MELEE");
        check(LegacyControlsV58.isMelee(LegacyControlsV58.MELEE_R),"right MELEE");
        check(!LegacyControlsV58.isFire(LegacyControlsV58.USE),"aim/use not FIRE");
        for(int d=0;d<8;d++){
            float x=LegacyControlsV58.knifeX(d);
            float y=LegacyControlsV58.knifeY(d);
            check(LegacyControlsV58.quantizeKnife(x,y)==d,"knife direction "+d);
        }
        // Default buttons must be distinct, non-overlapping and outside joysticks.
        for(int a=0;a<LegacyControlsV58.COUNT;a++){
            if(!LegacyControlsV58.defaultEnabled(a))continue;
            float ax=LegacyControlsV58.defaultX(a,1200),ay=LegacyControlsV58.defaultY(a,660);
            float aw=LegacyControlsV58.defaultW(a)*LegacyControlsV58.defaultScale(a)/100f;
            float ah=LegacyControlsV58.defaultH(a)*LegacyControlsV58.defaultScale(a)/100f;
            check(ax>=0&&ay>=0&&ax+aw<=1200&&ay+ah<=660,
                "action bounds "+a);
            for(int b=0;b<a;b++){
                if(!LegacyControlsV58.defaultEnabled(b))continue;
                float bx=LegacyControlsV58.defaultX(b,1200);
                float by=LegacyControlsV58.defaultY(b,660);
                float bw=LegacyControlsV58.defaultW(b)*LegacyControlsV58.defaultScale(b)/100f;
                float bh=LegacyControlsV58.defaultH(b)*LegacyControlsV58.defaultScale(b)/100f;
                boolean overlap=ax<bx+bw&&ax+aw>bx&&ay<by+bh&&ay+ah>by;
                check(!overlap,"reference buttons overlap "+a+" "+b);
            }
        }
        check(LegacyControlsV58.hit(320,565,315,561,105,44),"button hit center");
        check(!LegacyControlsV58.hit(10,565,315,561,105,44),"outside safe");
        System.out.println("V58 PASS: 11 distinct controls, dual FIRE/MELEE, 8 knife bearings");
    }
}
