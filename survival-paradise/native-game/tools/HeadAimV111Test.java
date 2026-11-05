package com.survivalparadise.nativegame;

/** Pure-Java test for mirroring, clamped tilt and smooth neutral rotation. */
public final class HeadAimV111Test {
    private static void require(boolean condition,String message) {
        if(!condition)throw new AssertionError(message);
    }
    private static void near(float a,float b,String message) {
        require(Math.abs(a-b)<.0001f,message+" (actual "+a+", expected "+b+")");
    }
    public static void main(String[] args) {
        final float halfPi=(float)(Math.PI/2.0);
        final float quarterPi=(float)(Math.PI/4.0);
        near(HeadAimV111.targetDegrees(0f,10),0f,"neutral horizontal aim");
        near(HeadAimV111.targetDegrees(-quarterPi,10),-10f,"upward aim tilts head up");
        near(HeadAimV111.targetDegrees(quarterPi,10),10f,"downward aim tilts head down");
        near(HeadAimV111.targetDegrees(-halfPi,10),-10f,"steep upwards clamped");
        near(HeadAimV111.targetDegrees(halfPi,10),10f,"steep downwards clamped");
        near(HeadAimV111.targetDegrees(halfPi,0),0f,"setting zero disables tilt");
        near(HeadAimV111.targetDegrees(halfPi,25),15f,"setting beyond maximum clamped");
        near(HeadAimV111.targetDegrees(Float.NaN,10),0f,"bad aim safe");
        near(HeadAimV111.targetDegrees(
                Ballistics.angle(1f,-1f,1),10),
                HeadAimV111.targetDegrees(Ballistics.angle(-1f,-1f,-1),10),
                "left/right facing must produce the same local head tilt");
        float position=0f;
        for(int n=0;n<25;n++){
            float next=HeadAimV111.follow(position,10f,.016f);
            require(next>=position&&next<=10f,"upward smoothing without overshoot");
            position=next;
        }
        require(position>9f,"settles quickly toward target");
        for(int n=0;n<40;n++)position=HeadAimV111.follow(position,0f,.016f);
        require(Math.abs(position)<.02f,"smooth return to neutral");
        near(HeadAimV111.follow(4f,10f,0f),4f,"zero time preserves current");
        near(HeadAimV111.neckX(20f,80f),60f,"neck rotation center anchored");
        near(HeadAimV111.neckY(140f,2f),132f,"bottom-center neckline anchored");
        require(HeadAimV111.follow(9f,15f,5f)<=15f,"long dt cannot overshoot");
        System.out.println("V111 aim-following head tilt regression: PASS");
    }
}
