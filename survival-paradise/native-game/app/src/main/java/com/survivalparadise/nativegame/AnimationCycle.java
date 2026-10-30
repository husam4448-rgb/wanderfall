package com.survivalparadise.nativegame;

/**
 * Native animation state. Walking uses the exact approved four-frame atlas.
 * Idle is a separate three-phase BREATHING cycle made from unchanged V31 pixels,
 * with boots stationary and head/torso/attached gear moving together.
 */
public final class AnimationCycle {
    public static final int IDLE_FRAME=0;
    public static final int WALK_FRAMES=4;
    public static final int IDLE_PHASES=3;
    public static final float IDLE_PHASE_SECONDS=.65f;
    private static final float WALK_FRAME_FACTOR=1.25f;
    private static final float[] BREATH_OFFSETS={0f,-4f,-2f};

    private float walkPhase=0f;
    private float idleTime=0f;
    private boolean walking=false;

    public void reset(){
        walking=false;
        walkPhase=0f;
        idleTime=0f;
    }

    public void step(boolean actuallyMoving,float dt,float rate){
        dt=Math.max(0f,Math.min(dt,.25f));
        if(!actuallyMoving){
            if(walking){walking=false;walkPhase=0f;idleTime=0f;}
            else idleTime=(idleTime+dt)%(IDLE_PHASES*IDLE_PHASE_SECONDS);
            return;
        }
        if(!walking){
            walking=true;walkPhase=0f;idleTime=0f;
        }else{
            walkPhase=(walkPhase+dt*Math.max(0f,rate))%(WALK_FRAMES/WALK_FRAME_FACTOR);
        }
    }

    public boolean isWalking(){return walking;}
    public int frame(){
        return walking?Math.min(WALK_FRAMES-1,(int)(walkPhase*WALK_FRAME_FACTOR)):IDLE_FRAME;
    }
    public int idlePhase(){
        return walking?0:Math.min(IDLE_PHASES-1,(int)(idleTime/IDLE_PHASE_SECONDS));
    }
    public float breathOffset(){
        return walking?0f:BREATH_OFFSETS[idlePhase()];
    }
}
