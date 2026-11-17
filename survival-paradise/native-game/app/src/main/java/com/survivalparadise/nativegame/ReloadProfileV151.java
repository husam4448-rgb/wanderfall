package com.survivalparadise.nativegame;

/**
 * V151 distinct reload kinematics for the twelve existing weapon indices.
 * Pure state-free math: gameplay ammo ownership remains with V143/V140.
 * All coordinates refer to immutable source atlas pixels (260 x 160).
 */
public final class ReloadProfileV151 {
    public static final int PISTOL=0, REVOLVER=1, UZI=2, FLASHLIGHT=3,
        CARBINE=4, AK=5, BULLPUP=6, SHOTGUN=7, SNIPER=8,
        BELT_FED_LMG=9, GRENADE_LAUNCHER=10, AXE=11;
    public static final int NONE=-1, SLIM_PISTOL=0, SPEEDLOADER=1, UZI_BOX=2,
        STANAG=4, CURVED_AK=5, BULLPUP_BOX=6, TOP_SHELLS=7,
        PRECISION_BOX=8, BELT_BOX=9, GRENADE_ROUNDS=10;

    public static final float[] DURATION={
        1.35f,2.25f,1.55f,0f,1.70f,1.90f,2.05f,3.15f,2.35f,3.20f,2.70f,0f
    };
    // Where the support hand starts and where it performs the loading operation.
    private static final float[] HOME_X={
        87f,91f,100f,0f,135f,146f,148f,151f,145f,149f,141f,0f};
    private static final float[] HOME_Y={
        121f,117f,116f,0f,77f,75f,72f,75f,73f,71f,74f,0f};
    private static final float[] LOAD_X={
        110f,110f,117f,0f,114f,131f,104f,126f,125f,136f,133f,0f};
    private static final float[] LOAD_Y={
        100f,73f,95f,0f,100f,102f,96f,53f,99f,108f,101f,0f};
    private static final float[] WEAPON_TILT={
        19f,29f,20f,0f,14f,17f,15f,8f,11f,12f,15f,0f};

    private ReloadProfileV151() {}

    public static boolean canReload(int weapon){
        return weapon>=0&&weapon<DURATION.length&&DURATION[weapon]>0f;
    }
    public static boolean needsBorrowedHand(int weapon){
        return weapon==PISTOL||weapon==REVOLVER||weapon==UZI;
    }
    public static boolean topFeed(int weapon){
        return weapon==SHOTGUN;
    }
    public static int propKind(int weapon){
        return canReload(weapon)?weapon:NONE;
    }
    public static float duration(int weapon){
        return canReload(weapon)?DURATION[weapon]:0f;
    }
    public static float progress(int weapon,float remaining){
        return !canReload(weapon)?1f:
            clamp(1f-Math.max(0f,remaining)/duration(weapon));
    }
    private static float clamp(float t){return Math.max(0f,Math.min(1f,t));}
    private static float smooth(float x){x=clamp(x);return x*x*(3f-2f*x);}
    /** The supporting hand travels, works, then returns to its normal grip. */
    public static float operation(float p){
        if(p<=.07f||p>=.95f)return 0f;
        if(p<.29f)return smooth((p-.07f)/.22f);
        if(p<.73f)return 1f;
        return 1f-smooth((p-.73f)/.22f);
    }
    private static float lerp(float a,float b,float u){return a+(b-a)*u;}
    public static float handX(int weapon,float remaining){
        if(!canReload(weapon))return 0f;
        float p=progress(weapon,remaining);
        return lerp(HOME_X[weapon],LOAD_X[weapon],operation(p));
    }
    public static float handY(int weapon,float remaining){
        if(!canReload(weapon))return 0f;
        float p=progress(weapon,remaining);
        float y=lerp(HOME_Y[weapon],LOAD_Y[weapon],operation(p));
        if(topFeed(weapon)&&p>.28f&&p<.78f){
            // Repeated visible shell strokes DOWN into the top loading port.
            float repeat=(p-.28f)/.50f*6f;
            float step=repeat-(float)Math.floor(repeat);
            float arc=(float)Math.sin(Math.PI*step);
            y+=9f*arc*arc;
        }
        return y;
    }
    /**
     * Keep the support hand moving throughout the complete reload.
     * Previously it snapped back to its weapon grip at ~83% progress, while
     * the actual motion did not return home until ~95%.
     * Single-hand weapons borrow a hand emerging from the torso; it enters
     * at the rest pose and departs only once it has returned home.
     */
    public static boolean supportHandActive(int weapon,float remaining){
        if(!canReload(weapon)||remaining<=0f)return false;
        if(!needsBorrowedHand(weapon))return true;
        float p=progress(weapon,remaining);
        return p>.07f&&p<.95f;
    }
    /** Suppress the prop when the off-hand is not actually holding ammo. */
    public static boolean propVisible(int weapon,float remaining){
        if(!canReload(weapon)||remaining<=0f)return false;
        float p=progress(weapon,remaining);
        return p>=.105f&&p<.83f;
    }
    public static float tiltDegrees(int weapon,float remaining){
        if(!canReload(weapon)||remaining<=0f)return 0f;
        float p=progress(weapon,remaining);
        return WEAPON_TILT[weapon]*operation(p);
    }
    public static float lowerPx(int weapon,float remaining){
        if(!canReload(weapon)||remaining<=0f)return 0f;
        return 7f*operation(progress(weapon,remaining));
    }
    public static float pullBackPx(int weapon,float remaining){
        if(!canReload(weapon)||remaining<=0f)return 0f;
        return -5f*operation(progress(weapon,remaining));
    }
    /** Magazines must stay different: never re-use handgun art for AK or LMG. */
    public static String propName(int weapon){
        switch(weapon){
            case PISTOL:return "slim straight pistol magazine";
            case REVOLVER:return "six-round revolver speedloader";
            case UZI:return "long straight SMG box magazine";
            case CARBINE:return "STANAG 5.56 magazine";
            case AK:return "curved AK-pattern magazine";
            case BULLPUP:return "short rear-mounted bullpup magazine";
            case SHOTGUN:return "12-gauge loose top-loading shells";
            case SNIPER:return "precision-rifle box magazine";
            case BELT_FED_LMG:return "belt-fed LMG ammunition box and links";
            case GRENADE_LAUNCHER:return "large 40mm grenade cartridges";
            default:return "no reload";
        }
    }
}
