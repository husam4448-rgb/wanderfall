package com.survivalparadise.nativegame;
public class BallisticsTest{
 static void check(boolean yes,String msg){if(!yes)throw new AssertionError(msg);}
 static void near(float got,float want,float eps,String msg){check(Math.abs(got-want)<eps,msg+" "+got+" vs "+want);}
 public static void main(String[]args){
  check(Ballistics.SPEED[0]>2000&&Ballistics.SPEED[8]>3900&&Ballistics.SPEED[10]<Ballistics.SPEED[0],"weapon velocity bands");
  float[] r=Ballistics.muzzle(1000,1100,1,1,0,.76f,147,79,103,76,0);
  float[] l=Ballistics.muzzle(1000,1100,-1,-1,0,.76f,147,79,103,76,0);
  near(r[0]-1000,1000-l[0],.01f,"left/right barrel mirror");
  near(r[1],l[1],.01f,"barrel height");
  float[] up=Ballistics.muzzle(1000,1100,1,0,-1,.76f,147,79,103,76,0);
  float[] down=Ballistics.muzzle(1000,1100,1,0,1,.76f,147,79,103,76,0);
  check(up[1]<r[1]&&down[1]>r[1],"vertical aiming for full 180-deg arc");
  near(Ballistics.segmentCircle(0,0,100,0,49,0,1),.48f,.0001f,"swept target");
  near(Ballistics.segmentBox(0,0,100,0,45,-2,55,2),.45f,.0001f,"swept cover");
  check(Float.isInfinite(Ballistics.segmentCircle(0,0,100,0,50,60,1)),"miss target");
  System.out.println("V35 ballistic regression checks PASS");
 }
}
