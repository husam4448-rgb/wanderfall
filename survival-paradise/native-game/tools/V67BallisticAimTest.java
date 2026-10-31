package com.survivalparadise.nativegame;

/** Shared bullet simulation limit and user-adjustable per-weapon release point. */
public final class V67BallisticAimTest {
    static void check(boolean value,String message){
        if(!value)throw new AssertionError(message);
    }
    static void near(float got,float want,float eps,String message){
        check(Math.abs(got-want)<=eps,message+": got "+got+" expected "+want);
    }
    public static void main(String[] args){
        float[] projectileSpeed=Ballistics.SPEED;
        int[] actualGuns={0,1,2,4,5,6,7,8,9,10};
        for(int gun:actualGuns){
            float distance=Ballistics.unobstructedTravel(gun);
            near(distance,projectileSpeed[gun]*1.3f,.01f,
                 "same lifetime times speed as bullet for weapon "+gun);
            check(distance>RadialAimV65.rest(gun)*2,
                  "real bullet endpoint must exceed adjustable rest "+gun);
            // At 60 Hz, final step must be truncated, not overshoot the 1.3 s lifetime.
            float total=0,life=Ballistics.PROJECTILE_LIFE,dt=1f/60f;
            for(int f=0;f<200&&life>0;f++){
                float travelDt=Math.min(dt,Math.max(0f,life));
                total+=travelDt*projectileSpeed[gun];
                life-=dt;
            }
            near(total,distance,.05f,"simulation distance equals crosshair max "+gun);
        }
        for(int gun=0;gun<12;gun++){
            float defaultRest=RadialAimV65.rest(gun);
            near(RadialAimV65.rest(gun,100f),defaultRest,.001f,"rest default "+gun);
            if(gun!=11){
                near(RadialAimV65.rest(gun,50f),defaultRest*.5f,.001f,
                    "user short rest "+gun);
                near(RadialAimV65.rest(gun,200f),defaultRest*2f,.001f,
                    "user long rest "+gun);
            }
            float rest=RadialAimV65.rest(gun,175f);
            float max=(gun==11)?88f:Ballistics.unobstructedTravel(gun)+50f;
            if(gun==3)max=490f;
            near(RadialAimV65.distance(max,gun,max,false,0,2900f,.016f,175f),
                 rest,.001f,"instant release keeps last heading and adjustable rest "+gun);
        }
        near(RadialAimV65.rest(11,200f),88f,.001f,"melee snap remains inside hit radius");
        near(RadialAimV65.direction(-1f,1f),-1f,.0001f,"instant stick reversal");
        near(Ballistics.unobstructedTravel(8),5135f,.1f,"sniper actual flight distance");
        near(Ballistics.unobstructedTravel(0),2665f,.1f,"pistol actual flight distance");
        System.out.println("V67 PASS: bullet duration and crosshair reach identical; all rest sliders pass");
    }
}
