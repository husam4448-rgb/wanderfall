package com.survivalparadise.nativegame;
public final class LightGeometryV45Test {
 static void check(boolean v,String description){if(!v)throw new AssertionError(description);}
 static void near(float x,float y,float epsilon,String desc){check(Math.abs(x-y)<epsilon,desc+" got "+x+" expected "+y);}
 public static void main(String[] args){
  float angle=(float)Math.toRadians(30);
  check(LightGeometryV45.inCone(0,0,1,0,350,0,490,angle),"flashlight illuminates forward");
  check(!LightGeometryV45.inCone(0,0,1,0,-130,0,490,angle),"no light backward");
  check(!LightGeometryV45.inCone(0,0,1,0,200,240,490,angle),"no light outside cone");
  check(LightGeometryV45.inCone(0,0,-1,0,-350,0,490,angle),"left-facing flashlight mirrors");
  check(!LightGeometryV45.inCone(0,0,-1,0,350,0,490,angle),"mirrored flashlight does not shine right");
  check(LightGeometryV45.inCone(100,100,0,-1,100,0,490,angle),"vertical aim flashlight");
  near(LightGeometryV45.rayBox(0,0,1,0,490,100,-50,140,50),98,1,"building blocks beam");
  near(LightGeometryV45.rayBox(0,0,-1,0,490,-140,-50,-100,50),98,1,"mirrored building shadow");
  near(LightGeometryV45.rayBox(0,0,1,0,490,100,100,140,160),490,.1f,"building off-ray no shadow");
  near(LightGeometryV45.radialIntensity(0,0,0,0,200,1),1,.001f,"fire center luminous");
  check(LightGeometryV45.radialIntensity(220,0,0,0,200,1)==0,"outside campfire dim");
  check(LightGeometryV45.radialIntensity(80,0,0,0,200,1)>
      LightGeometryV45.radialIntensity(160,0,0,0,200,1),"inverse distance falloff");
  // Approved characters are deliberately absent from light source math.
  System.out.println("V45 lighting tests PASSED: direction, mirroring, occlusion, warm falloff");
 }
}