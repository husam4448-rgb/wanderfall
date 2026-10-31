package com.survivalparadise.nativegame;

/**
 * V68 aim stabilizer. Angular motion is rate-limited in WORLD/SCREEN units,
 * preventing tiny thumb movements from sweeping long-range reticles across
 * hundreds of pixels. A strong deliberate reverse gesture remains instant.
 */
public final class StableAimV68 {
    private StableAimV68(){}

    public static float normalizedDeadzone(float rawMagnitude,float deadzone){
        float threshold=Math.max(.03f,Math.min(.30f,deadzone));
        return rawMagnitude>threshold+.025f?rawMagnitude:0f;
    }

    /** Full reversal is a distinct intentional action, not joystick jitter. */
    public static boolean deliberateReverse(float ax,float ay,float tx,float ty,float magnitude){
        return magnitude>=.67f && ax*tx+ay*ty<=-.80f;
    }

    /** Signed angle to rotate this frame, without crossing the player origin. */
    public static float angularStep(float ax,float ay,float tx,float ty,
                                    float magnitude,float reach,float dt,float steeringPercent){
        float delta=(float)Math.atan2(ax*ty-ay*tx,ax*tx+ay*ty);
        if(dt<=0f||magnitude<=0f)return 0f;
        float tuning=Math.max(.35f,Math.min(2f,steeringPercent/100f));
        float rate=(3.0f+7f*magnitude)*tuning;
        float maxTangentialSpeed=(500f+1800f*magnitude)*tuning;
        float maxStep=Math.min(rate*dt,maxTangentialSpeed*dt/Math.max(100f,reach));
        return Math.max(-maxStep,Math.min(maxStep,delta));
    }

    public static float panStep(float error,float dt,float pixelsPerSecond,float easing){
        float maxDelta=Math.max(0f,pixelsPerSecond)*Math.max(0f,dt);
        float desired=error*Math.min(1f,Math.max(.01f,easing)*Math.max(0f,dt));
        return Math.max(-maxDelta,Math.min(maxDelta,desired));
    }
}
