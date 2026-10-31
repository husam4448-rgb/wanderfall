package com.survivalparadise.nativegame;

public final class V68StableAimTest {
    static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    static void near(float a,float b,float tolerance,String why){
        check(Math.abs(a-b)<=tolerance,why+" actual="+a+" expected="+b);
    }
    public static void main(String[] args){
        // Slight movement near the thumb center must not cause jitter.
        near(StableAimV68.normalizedDeadzone(.10f,.17f),0,.00001f,"micro movements ignored");
        near(StableAimV68.normalizedDeadzone(.19f,.17f),0,.00001f,"deadzone hysteresis");
        check(StableAimV68.normalizedDeadzone(.55f,.17f)>.5f,"strong valid aim");
        check(!StableAimV68.deliberateReverse(1,0,-1,0,.2f),
              "minor gesture must not flip aim");
        check(StableAimV68.deliberateReverse(1,0,-1,0,.96f),
              "strong 180 degree reversal must be immediate");
        check(!StableAimV68.deliberateReverse(1,0,0,1,.98f),
              "90 degrees should steer rather than teleport");
        float small=StableAimV68.angularStep(1,0,.98480775f,.17364818f,
                                            .3f,4200f,1f/60f,100f);
        check(small>0f&&small<.01f,"sniper micro adjustment capped");
        // At long range, a single frame can only sweep a bounded world distance.
        float large=StableAimV68.angularStep(1,0,0,1,1f,5000,1f/60f,100);
        check(large>0f&&large*5000f<=45f,
              "long range movement cannot jump hundreds of pixels in one frame");
        float close=StableAimV68.angularStep(1,0,0,1,1f,300,1f/60f,100);
        check(close>large,"short range still responds quickly");
        float slowed=StableAimV68.angularStep(1,0,0,1,.4f,3000,1f/60f,60);
        check(slowed<large,"fine input respects tuning and range");
        near(StableAimV68.angularStep(1,0,0,1,1f,3000,0,100),
             0,.00001f,"stopped time stopped aim");
        near(StableAimV68.panStep(2000f,1f/60f,350f,6f),
             350f/60f,.001f,"camera pan has a real velocity cap");
        near(StableAimV68.panStep(-100f,1f/60f,350f,6f),
             -350f/60f,.001f,"reverse camera pan velocity bound");
        near(StableAimV68.panStep(10f,1f/60f,350f,3f),
             .5f,.001f,"camera easing is independent of cursor speed");
        System.out.println("V68 PASS: micro-jitter suppressed, long-distance angular movement bounded, intentional reverse fast, camera velocity capped");
    }
}
