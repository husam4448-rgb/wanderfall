package com.survivalparadise.nativegame;

public final class V69BoundedCameraTest {
    static void ok(boolean yes,String why){if(!yes)throw new AssertionError(why);}
    static void near(float got,float want,String why){
        ok(Math.abs(got-want)<.001f,why+": "+got+" expected "+want);
    }
    public static void main(String[] args){
        float cap=BoundedCameraV69.limit(65f,1480f,660f,1f);
        near(cap,65f,"default strict cap");
        near(BoundedCameraV69.limit(0,1480,660,1),0,"zero disables pan");
        near(BoundedCameraV69.limit(2000,1480,660,1),79.2f,"hard-screen fraction");
        near(BoundedCameraV69.limit(180,1480,660,2),39.6f,"zoom safely limits displacement");
        near(BoundedCameraV69.beyondMargin(100,440),0,"no pan near player");
        near(BoundedCameraV69.beyondMargin(5000,440),4560,"long sniper ray should not dictate pan limit");
        near(BoundedCameraV69.beyondMargin(-5000,440),-4560,"negative long ray");
        float k=BoundedCameraV69.radialFactor(3000f,4000f,cap);
        near(k,65f/5000f,"diagonal normalization");
        ok(Math.hypot(3000f*k,4000f*k)<=65.001f,"diagonal cannot exceed cap");
        float previousX=800f,previousY=-900f;
        float previousScale=BoundedCameraV69.radialFactor(previousX,previousY,cap);
        near((float)Math.hypot(previousX*previousScale,previousY*previousScale),
            65f,"preexisting runaway camera is clamped immediately");
        near(BoundedCameraV69.radialFactor(10,15,cap),1,"within cap remains untouched");
        ok(BoundedCameraV69.limit(180,1480,660,1)<=180,
           "user setting cannot allow huge camera excursion");
        System.out.println("V69 PASS: camera cannot pan beyond a small circular offset, including sniper and zoom");
    }
}
