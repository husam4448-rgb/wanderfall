package com.survivalparadise.nativegame;

/** Firearms-only visible muzzle effects. Flashlight and melee never flash/fire bullets. */
public final class GunEffectsV118 {
    public static final float FLASH_SECONDS=.16f,TRACER_SECONDS=.23f;
    private GunEffectsV118(){}
    public static boolean firearm(int weapon){return weapon>=0&&weapon<12&&weapon!=3&&weapon!=11;}
    public static float lifeFraction(float remaining,float duration){
        return Math.max(0f,Math.min(1f,remaining/Math.max(.001f,duration)));
    }
    public static int muzzleColor(int weapon) {
        return weapon==10?0xffffbc78:0xffffeeaf;
    }
}
