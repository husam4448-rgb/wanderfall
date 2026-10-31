package com.survivalparadise.nativegame;

/** JVM checks independent user locomotion and unchanged world-time ratios. */
public final class V77MovementTest {
    private static void check(boolean good,String text){if(!good)throw new AssertionError(text);}
    private static void close(float actual,float expected){
        check(Math.abs(actual-expected)<0.001f,actual+" != "+expected);
    }
    public static void main(String[]args){
        close(PlayerMovementV77.multiplier(130),1.3f);
        close(PlayerMovementV77.multiplier(75),.75f);
        close(PlayerMovementV77.multiplier(200),2f);
        close(PlayerMovementV77.multiplier(10),.75f);
        close(PlayerMovementV77.multiplier(999),2f);
        close(PlayerMovementV77.speed(236f,1f,1f,false),236f);
        close(PlayerMovementV77.speed(236f,1.3f,1f,false),306.8f);
        close(PlayerMovementV77.speed(169f,1.3f,1f,false),219.7f);
        close(PlayerMovementV77.speed(236f,1.3f,1.52f,false),466.336f);
        close(PlayerMovementV77.speed(236f,1.3f,1f,true),162.604f);
        close(PlayerMovementV77.gait(1.3f,false),10.66f);
        close(PlayerMovementV77.gait(1.3f,true),12.61f);
        System.out.println("V77 PASS: faster walk, weapon/run/crouch ratios and gait synchronized");
    }
}
