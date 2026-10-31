package com.survivalparadise.nativegame;

/** V72 symmetrical camera look: one circular offset, weapon-class reach. */
public final class WeaponCameraV72 {
    private WeaponCameraV72(){}
    // Matches the 12 equipped slots. Pistols/SMG are short, assault rifles
    // medium, sniper longest. Melee remains deliberately short.
    public static int weaponMaximum(int weapon){
        switch(weapon){
            case 0: case 1: case 2: return 180;
            case 3: return 140;     // flashlight, short visual look
            case 4: case 5: case 6: return 280; // rifles / carbine
            case 7: return 210;    // shotgun
            case 8: return 360;    // sniper
            case 9: return 300;    // LMG
            case 10: return 240;   // launcher
            case 11: return 90;    // axe
            default: return 180;
        }
    }
    /** Prevents pushing the actor out of the vertical viewport at any zoom. */
    public static int visibleMaximum(int weapon,float w,float h,float zoom){
        int viewport=(int)Math.floor(Math.max(0f,Math.min(w,h)*.48f/
            Math.max(.01f,zoom)));
        return Math.max(0,Math.min(weaponMaximum(weapon),viewport));
    }
    public static float distance(int weapon,int percent,float w,float h,float zoom){
        int p=Math.max(0,Math.min(100,percent));
        return visibleMaximum(weapon,w,h,zoom)*p/100f;
    }
    /** Camera movement constrained to an identical circular radius. */
    public static float[] circle(float dx,float dy,float limit){
        float size=(float)Math.hypot(dx,dy);
        float factor=size>limit&&size>0?Math.max(0f,limit)/size:1f;
        return new float[]{dx*factor,dy*factor};
    }
}
