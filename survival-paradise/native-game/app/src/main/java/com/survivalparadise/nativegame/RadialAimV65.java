package com.survivalparadise.nativegame;

/** V65: the player, not the previous cursor position, anchors every aim gesture. */
public final class RadialAimV65 {
    private RadialAimV65(){}

    // V66: genuine weapon reach indicator at rest (world pixels).
    // Firearms sit WELL beyond their muzzle even when the stick is released.
    // Slot order: pistol, revolver, UZI, torch, carbine, AK, bullpup,
    // shotgun, sniper, LMG, grenade launcher, axe.
    // Rests remain below each weapon's existing ballistic maximum; melee is close.
    private static final float[] REST={190f,205f,175f,185f,325f,315f,
                                     300f,255f,505f,330f,260f,66f};

    public static float rest(int weapon){
        return REST[Math.max(0,Math.min(REST.length-1,weapon))];
    }

    /** Tune the same per-weapon release distances without corrupting other slots. */
    public static float rest(int weapon,float sliderPercent){
        float scale=Math.max(.50f,Math.min(2.0f,sliderPercent/100f));
        float distance=rest(weapon)*scale;
        // The axe has only an 88px hit radius, regardless of HUD setting.
        return weapon==11?Math.min(88f,distance):distance;
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

    /** V67 adjustable rest anchor, preserving V65 legacy signature. */
    public static float distance(float previous,int weapon,float max,
                                 boolean aiming,float deflection,
                                 float travelPixelsPerSecond,float seconds,float restPercent){
        float close=rest(weapon,restPercent);
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
