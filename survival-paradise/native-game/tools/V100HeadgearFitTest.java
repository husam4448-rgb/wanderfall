package com.survivalparadise.nativegame;
/** Headgear fitting verification without Android build or APK generation. */
public final class V100HeadgearFitTest {
  static void check(boolean ok,String name){if(!ok)throw new AssertionError(name);}
  public static void main(String[] args){
    for(int type=0;type<4;type++){
      float lastWidth=0,lastHeight=0;
      for(float h:new float[]{.75f,1f,1.6f}){
        float[] b=HeadgearFitV100.bounds(type,1f,h,0f);
        float w=b[2]-b[0],ht=b[3]-b[1];
        check(w>lastWidth&&ht>lastHeight,"scale not monotonic, type "+type);
        check(b[0]<b[2]&&b[1]<b[3],"bad rectangle");
        float[] bob=HeadgearFitV100.bounds(type,1f,h,-4f);
        check(Math.abs(bob[1]-b[1]+4f)<.001f,"top bob");
        check(Math.abs(bob[3]-b[3]+4f)<.001f,"bottom bob");
        float[] scale=HeadgearFitV100.bounds(type,2f,h,0f);
        check(Math.abs((scale[2]-scale[0])-2*w)<.001f,"world scaling");
        lastWidth=w;lastHeight=ht;
      }
    }
    System.out.println("V100 VISUAL-ONLY PASS: four approved sprites, "+
      "75%, 100%, 160% head sizes, 0/-4px breathing, world scaling");
  }
}