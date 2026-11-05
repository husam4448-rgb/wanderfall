package com.survivalparadise.nativegame;

/**
 * V115 independent hip/pelvis width adjustment for exact V109 200x260 bodies.
 *
 * Canonical sprite rows:
 *  160..179 - upper torso, independently controlled by V114
 *  180..199 - pelvis / waist and shirt hem (this slider only)
 *  200..259 - moving legs, pants below pelvis, boots and feet: never scaled
 *
 * Centered rendering alters no source image pixels, outfit color, silhouette
 * rows outside the pelvis, head fitting, aim or weapon rig. All idle and four
 * approved walking frames use the same boundaries.
 */
public final class PelvisWidthV115 {
    public static final int PELVIS_TOP = TorsoWidthV114.LOWER_BODY_TOP;
    public static final int LEGS_TOP = 200;
    public static final int MIN_PERCENT = 55;
    public static final int MAX_PERCENT = 100;
    public static final int DEFAULT_PERCENT = 100;

    private PelvisWidthV115() {}

    public static int percent(int value) {
        return Math.max(MIN_PERCENT, Math.min(MAX_PERCENT, value));
    }

    public static float left(float bodyLeft, float bodyUnit, int value) {
        return TorsoWidthV114.left(bodyLeft, bodyUnit, percent(value));
    }

    public static float right(float bodyLeft, float bodyUnit, int value) {
        return TorsoWidthV114.right(bodyLeft, bodyUnit, percent(value));
    }

    public static boolean preserveLegRow(int sourceY) {
        return sourceY >= LEGS_TOP && sourceY < TorsoWidthV114.SPRITE_HEIGHT;
    }
}
