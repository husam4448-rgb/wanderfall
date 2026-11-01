package com.survivalparadise.nativegame;
/** Wide quick strike with a visible short streak (not a semicircle). */
public final class MeleeSlashV83 {
 private MeleeSlashV83(){}
 public static final float DURATION=.18f,COOLDOWN=.34f,REACH=155f;
 public static final float ARC=104f,STREAK=43f;
 public static float angle(float t){float q=Math.max(0,Math.min(1,t));q=q*q*(3-2*q);return (q-.5f)*ARC;}
 public static boolean streakVisible(float t){return t>=.18f&&t<=.78f;}
}
