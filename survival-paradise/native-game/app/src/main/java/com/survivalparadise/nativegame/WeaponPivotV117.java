package com.survivalparadise.nativegame;

/**
 * Additive 2D fitting for the entire approved weapon + two-hand assembly.
 *
 * Coordinates are V31 rig source units, before applying runtime character
 * scale. The same position shifts the rotation pivot and every weapon/hand
 * pixel, never the source artwork, grip geometry, aim angle or recoil.
 *
 * Left-facing is mirrored once by the existing canvas; world projectile
 * origin uses facing sign only for the horizontal part.
 */
public final class WeaponPivotV117 {
    public static final int MIN=-48,MAX=48,DEFAULT=0;
    private WeaponPivotV117(){}

    public static int clamp(int value) {
        return Math.max(MIN,Math.min(MAX,value));
    }

    public static float localX(int offset,float scale) {
        return clamp(offset)*scale;
    }
    public static float localY(int offset,float scale) {
        return clamp(offset)*scale;
    }

    public static float worldX(int offset,int facing,float scale) {
        return (facing<0?-1f:1f)*localX(offset,scale);
    }

    /**
     * Applies exactly the additive shift used by the drawn rotation pivot to
     * ballistics, reticles and flashlight origins. Zero is byte-for-byte the
     * pre-V117 muzzle. Mutates the caller's original two-coordinate result.
     */
    public static float[] relocateMuzzle(float[] muzzle,int facing,float scale,
                                         int offsetX,int offsetY) {
        if(muzzle==null||muzzle.length<2)
            throw new IllegalArgumentException("Expected a 2D muzzle");
        muzzle[0]+=worldX(offsetX,facing,scale);
        muzzle[1]+=localY(offsetY,scale);
        return muzzle;
    }
}
