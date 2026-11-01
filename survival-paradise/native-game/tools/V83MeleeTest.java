package com.survivalparadise.nativegame;
public final class V83MeleeTest {
 static void ok(boolean b,String s){if(!b)throw new AssertionError(s);}
 public static void main(String[]args){
  ok(Math.abs(MeleeSlashV83.angle(0)+52)<.001,"start angle");
  ok(Math.abs(MeleeSlashV83.angle(.5f))<.001,"middle angle");
  ok(Math.abs(MeleeSlashV83.angle(1)-52)<.001,"end angle");
  ok(MeleeSlashV83.DURATION<=.19f,"faster animation");
  ok(MeleeSlashV83.COOLDOWN<=.35f,"faster cooldown");
  ok(MeleeSlashV83.REACH>=150,"increase hit reach");
  ok(MeleeSlashV83.ARC>=100&&MeleeSlashV83.ARC<135,"wider but not half circle");
  ok(MeleeSlashV83.STREAK>=40,"longer clear streak");
  ok(MeleeSlashV83.streakVisible(.50f),"trail visible at strike");
  ok(!MeleeSlashV83.streakVisible(.05f),"no trail before windup");
  System.out.println("V83 PASS fast 104 degree sweep, high contrast slash, increased reach");
 }
}
