package com.survivalparadise.nativegame;

/**
 * Calibrated from the immutable original 260x160 gear atlas.
 * Each weapon endpoint sits immediately outside the actual opaque muzzle face,
 * with y at the visual centerline of the barrel, NOT the receiver/grip.
 * No sprite geometry, color, or equipment attachment points are modified.
 */
public final class MuzzleGeometryV49 {
    private MuzzleGeometryV49(){}
    public static final float[] X={147,171,154,129,220,215,213,225,238,228,216,183};
    public static final float[] Y={62,58,67,88,67,66,68,66,69,56,69,92};
    public static boolean isProjectile(int weapon){return weapon>=0&&weapon<11&&weapon!=3;}
}
