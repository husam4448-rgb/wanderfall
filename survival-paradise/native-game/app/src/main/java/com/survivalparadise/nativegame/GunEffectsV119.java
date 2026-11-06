package com.survivalparadise.nativegame;

/** Restrained, real-projectile fire graphics. No synthetic glowing bullet rays.
 * Side-view muzzle flashes are short-lived and limited to actual firearms.
 */
public final class GunEffectsV119 {
    public static final float FLASH_SECONDS=.155f;
    public static final float BULLET_TRAIL_LENGTH=13f;
    private GunEffectsV119(){}

    public static boolean firearm(int weapon) {
        return GunEffectsV118.firearm(weapon); // flashlight + axe excluded
    }
    public static float alpha(float timeRemaining) {
        return Math.max(0f,Math.min(1f,timeRemaining/FLASH_SECONDS));
    }
    public static float muzzleLength(float alpha,int weapon) {
        float base=(weapon==7||weapon==10)?12f:9f;
        return base*(.5f+.5f*Math.max(0f,Math.min(1f,alpha)));
    }
    public static float muzzleHalfWidth(float alpha) {
        return 2f+2f*Math.max(0f,Math.min(1f,alpha));
    }
    public static int bulletColor(boolean hostile) {
        return hostile?0xffd6ac83:0xffdecfa5;
    }
}
