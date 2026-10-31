package com.survivalparadise.nativegame;

/** Bounded follower arrival prevents oscillation/facing swaps at the target. */
public final class FollowerArrivalV78 {
    private FollowerArrivalV78(){}
    public static final float STOP_RADIUS=14f;
    public static float step(float distance,float dt,float maxSpeed){
        if(distance<=STOP_RADIUS||dt<=0f||maxSpeed<=0f)return 0f;
        float excess=distance-STOP_RADIUS;
        float speed=Math.min(maxSpeed,Math.max(30f,excess*7.5f));
        return Math.min(excess,speed*dt);
    }
    /** Keep the torch's horizontal orientation stable in the near-arrival zone. */
    public static boolean shouldTurn(float deltaX,float distance){
        return distance>36f&&Math.abs(deltaX)>30f;
    }
    public static boolean visuallyWalking(float displacement){
        return displacement>.25f;
    }
}
