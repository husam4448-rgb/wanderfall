package com.survivalparadise.nativegame;

/** Weapon-specific default target distances; four-frame source art remains locked. */
public final class V66ReachGaitTest {
    static void check(boolean b,String message){if(!b)throw new AssertionError(message);}
    static void near(float got,float expected,String message){
        check(Math.abs(got-expected)<.001f,message+" got="+got+" expected="+expected);
    }
    public static void main(String[] args){
        int[] ranges={250,265,220,0,430,415,395,325,650,435,330,74};
        float[] expected={190f,205f,175f,185f,325f,315f,300f,255f,505f,330f,260f,66f};
        for(int weapon=0;weapon<12;weapon++){
            float rest=RadialAimV65.rest(weapon);
            near(rest,expected[weapon],"weapon rest "+weapon);
            float max=RadialAimV65.maximum(weapon,ranges[weapon],750f);
            check(max>=rest,"range must exceed rest "+weapon);
            if(weapon!=11)check(rest>=175f,"non-melee crosshair must be far "+weapon);
            if(ranges[weapon]>0)check(rest<ranges[weapon],"rest below ballistic range "+weapon);
            near(RadialAimV65.distance(max,weapon,max,false,0f,2900f,.016f),
                rest,"release must instant-snap to far weapon rest "+weapon);
            near(RadialAimV65.distance(rest,weapon,max,true,1f,2900f,.1f),
                max,"aim extension reaches weapon cap "+weapon);
        }
        check(RadialAimV65.rest(8)>RadialAimV65.rest(4),
              "sniper indicator farther than carbine");
        check(RadialAimV65.rest(5)>RadialAimV65.rest(0),
              "AK indicator farther than pistol");
        near(RadialAimV65.direction(-1,1),-1f,"opposite stick instant turn");
        // Test retained original walking asset geometry / idle semantics.
        AnimationCycle walk=new AnimationCycle();
        walk.step(true,.016f,8.2f);
        check(walk.isWalking()&&walk.frame()<AnimationCycle.WALK_FRAMES,"walk starts");
        walk.step(true,.12f,9.7f);
        check(walk.frame()<AnimationCycle.WALK_FRAMES,"run stays in original four frames");
        walk.step(false,.016f,9.7f);
        check(!walk.isWalking()&&walk.frame()==AnimationCycle.IDLE_FRAME,
              "release immediately returns original planted idle");
        System.out.println("V66 PASS: 12 far weapon-rest distances, sprint gait, immutable four-frame geometry");
    }
}
