package com.survivalparadise.nativegame;
public final class V86WorldUiTest {
 static void check(boolean b,String msg){if(!b)throw new AssertionError(msg);}
 static void close(float a,float b){check(Math.abs(a-b)<.001f,a+" != "+b);}
 public static void main(String[]args){
  float w=1280,h=720,l=WorldUiV86.bagX(w),t=WorldUiV86.bagY(h);
  check(t+WorldUiV86.BAG_H<h-245f,"BAG overlaps aiming stick");
  close(l+WorldUiV86.BAG_W*.5f,w-190f);
  check(WorldUiV86.BAG_W>=120&&WorldUiV86.BAG_H>=48,"BAG too small");
  check(WorldUiV86.bagHit(l+2,t+2,w,h),"BAG press rejected");
  check(!WorldUiV86.bagHit(15,15,w,h),"BAG false press");
  close(WorldUiV86.targetX(1000,1,200),1200);
  close(WorldUiV86.targetX(1000,-1,200),800);
  close(WorldUiV86.targetY(700,-1,200),458);
  close(WorldUiV86.placeDistance(10000),WorldUiV86.PLACE_MAX);
  close(WorldUiV86.placeDistance(0),WorldUiV86.PLACE_MIN);
  check(WorldUiV86.PLACE_MAX<420,"placement outside reachable world");
  System.out.println("V86 PASS BAG above aim stick, large touch target, stable aim-ray placement");
 }
}
