package com.survivalparadise.nativegame;
/** Independent geometry for fast, frame-rate-safe projectiles. */
public final class Ballistics {
 private Ballistics(){}
 public static final float[] SPEED={2050f,2350f,2050f,0f,3100f,2850f,3000f,2350f,3950f,2950f,1450f,0f};
 public static float angle(float dx,float dy,int facing){
  return (float)Math.atan2(dy*(facing<0?-1f:1f),Math.max(0f,facing*dx));
 }
 public static float[] muzzle(float x,float y,int facing,float aimX,float aimY,float scale,
                              float mx,float my,float gx,float gy,float kick){
  float a=angle(aimX,aimY,facing),cs=(float)Math.cos(a),sn=(float)Math.sin(a);
  float px=(gx-70f)*scale,py=(gy-136f)*scale;
  float dx=(mx-gx)*scale,dy=(my-gy)*scale;
  return new float[]{x+facing*(px+cs*dx-sn*dy-kick),y+py+sn*dx+cs*dy};
 }

 // V36 rig: aim rotates about torso center. Weapon + two hands are first translated
 // as one assembly so the grip rests beside the chest; neither hand can orbit
 // a distant weapon-local point. Pixel art/source atlases remain unchanged.
 public static final float TORSO_X=75f,TORSO_Y=103f;
 public static final float GRIP_X=85f,GRIP_Y=99f;
 public static float[] rigMuzzle(float worldX,float worldY,int facing,
       float aimX,float aimY,float scale,float muzzleX,float muzzleY,
       float sourceGripX,float sourceGripY,float recoil){
   float a=angle(aimX,aimY,facing);
   float cs=(float)Math.cos(a),sn=(float)Math.sin(a);
   float tx=(TORSO_X-70f)*scale,ty=(TORSO_Y-136f)*scale;
   float dx=(GRIP_X-TORSO_X+muzzleX-sourceGripX)*scale;
   float dy=(GRIP_Y-TORSO_Y+muzzleY-sourceGripY)*scale;
   return new float[]{
     worldX+facing*(tx+cs*dx-sn*dy-recoil),
     worldY+ty+sn*dx+cs*dy
   };
 }
 public static float[] rigGrip(float worldX,float worldY,int facing,
      float aimX,float aimY,float scale,float recoil){
   return rigMuzzle(worldX,worldY,facing,aimX,aimY,scale,
       GRIP_X,GRIP_Y,GRIP_X,GRIP_Y,recoil);
 }
 public static float segmentCircle(float x0,float y0,float x1,float y1,float cx,float cy,float radius){
  float dx=x1-x0,dy=y1-y0,fx=x0-cx,fy=y0-cy,a=dx*dx+dy*dy;
  if(a<1e-8f)return fx*fx+fy*fy<=radius*radius?0f:Float.POSITIVE_INFINITY;
  float cc=fx*fx+fy*fy-radius*radius;
  if(cc<=0)return 0f;
  float b=2f*(fx*dx+fy*dy),delta=b*b-4f*a*cc;
  if(delta<0)return Float.POSITIVE_INFINITY;
  float t=(-b-(float)Math.sqrt(delta))/(2f*a);
  return t>=0&&t<=1?t:Float.POSITIVE_INFINITY;
 }
 public static float segmentBox(float x0,float y0,float x1,float y1,
                                float left,float top,float right,float bottom){
  if(x0>=left&&x0<=right&&y0>=top&&y0<=bottom)return 0f;
  float dx=x1-x0,dy=y1-y0,lo=0f,hi=1f;
  if(Math.abs(dx)<1e-7f){if(x0<left||x0>right)return Float.POSITIVE_INFINITY;}
  else{
   float a=(left-x0)/dx,b=(right-x0)/dx;
   lo=Math.max(lo,Math.min(a,b));hi=Math.min(hi,Math.max(a,b));
   if(lo>hi)return Float.POSITIVE_INFINITY;
  }
  if(Math.abs(dy)<1e-7f){if(y0<top||y0>bottom)return Float.POSITIVE_INFINITY;}
  else{
   float a=(top-y0)/dy,b=(bottom-y0)/dy;
   lo=Math.max(lo,Math.min(a,b));hi=Math.min(hi,Math.max(a,b));
   if(lo>hi)return Float.POSITIVE_INFINITY;
  }
  return lo>=0&&lo<=1&&lo<=hi?lo:Float.POSITIVE_INFINITY;
 }
}
