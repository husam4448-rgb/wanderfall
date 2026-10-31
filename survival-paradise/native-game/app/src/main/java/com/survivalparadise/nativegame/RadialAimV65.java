package com.survivalparadise.nativegame;

/** V65: the player, not the previous cursor position, anchors every aim gesture. */
public final class RadialAimV65 {
    private RadialAimV65(){}

    // A close neutral position for each distinct equipped weapon (world pixels).
    private static final float[] REST={76f,84f,72f,62f,108f,112f,
                                     105f,98f,142f,118f,115f,66f};

    public static float rest(int weapon){
        return REST[Math.max(0,Math.min(REST.length-1,weapon))];
    }

    public static float maximum(int weapon,int ballisticRange,float userCap){
        float near=rest(weapon);
        // The weapon has the final say; flashlight and melee use a short arc.
        float reach=ballisticRange>0?ballisticRange:near+100f;
        return Math.max(near,Math.min(reach,Math.max(near,userCap)));
    }

    /** Immediately restores close-range reticle position when the thumb lifts. */
    public static float distance(float previous,int weapon,float max,
                                 boolean aiming,float deflection,
                                 float travelPixelsPerSecond,float seconds){
        float close=rest(weapon);
        if(!aiming)return close;
        if(deflection<=0f)return Math.max(close,Math.min(max,previous));
        float delta=Math.max(0f,travelPixelsPerSecond)*Math.max(0f,seconds)
                    *Math.min(1f,deflection);
        return Math.max(close,Math.min(max,Math.max(close,previous)+delta));
    }

    /** Reversal occurs instantaneously: no interpolation through the player. */
    public static float direction(float stickAxis,float length){
        return length>.0001f?stickAxis/length:0f;
    }
}
