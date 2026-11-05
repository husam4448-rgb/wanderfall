package com.survivalparadise.nativegame;

/**
 * Full-circle side-view NPC weapon direction. Existing left/right mirroring
 * determines character facing; aim pitch is the real 360-degree vector and
 * keeps the head and weapon on the exact same heading.
 *
 * No changes to source head/body/hand sprites or V121 fitting.
 */
public final class NpcAimV122 {
    public static final float TURN_RATE=6.6f; // rad/sec, no instant 180-degree snapping
    public static final float SCAN_RATE=.62f; // rad/sec, completes a full 360-degree scan
    public static final float FACE_DEADZONE=.12f;
    private NpcAimV122(){}

    public static float scanX(float time,int actorIndex){
        return (float)Math.cos(time*SCAN_RATE+actorIndex*2.3999632f);
    }
    public static float scanY(float time,int actorIndex){
        return (float)Math.sin(time*SCAN_RATE+actorIndex*2.3999632f);
    }
    public static float[] toward(float fromX,float fromY,float targetX,float targetY){
        float dx=targetX-fromX,dy=targetY-fromY;
        float m=(float)Math.hypot(dx,dy);
        if(m<.0001f)return new float[]{1f,0f};
        return new float[]{dx/m,dy/m};
    }
    public static float[] turn(float oldX,float oldY,float desiredX,float desiredY,float dt){
        float a=(float)Math.atan2(oldY,oldX);
        float b=(float)Math.atan2(desiredY,desiredX);
        float diff=wrap(b-a);
        float amount=Math.max(0f,Math.min(1f,dt));
        float rotated=a+clamp(diff,-TURN_RATE*amount,TURN_RATE*amount);
        return new float[]{(float)Math.cos(rotated),(float)Math.sin(rotated)};
    }
    public static float wrap(float radians){
        while(radians>(float)Math.PI)radians-=2f*(float)Math.PI;
        while(radians<-(float)Math.PI)radians+=2f*(float)Math.PI;
        return radians;
    }
    private static float clamp(float x,float low,float high){
        return Math.max(low,Math.min(high,x));
    }
    public static int facing(float aimX,int previousFacing){
        if(aimX>FACE_DEADZONE)return 1;
        if(aimX<-FACE_DEADZONE)return -1;
        return previousFacing<0?-1:1;
    }
    public static boolean aligned(float aimX,float aimY,float wantedX,float wantedY){
        float a=(float)Math.hypot(aimX,aimY),b=(float)Math.hypot(wantedX,wantedY);
        return a>.5f&&b>.5f&&(aimX*wantedX+aimY*wantedY)/(a*b)>=.97f;
    }
}
