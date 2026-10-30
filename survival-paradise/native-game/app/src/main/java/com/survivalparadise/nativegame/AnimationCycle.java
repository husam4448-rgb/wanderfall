package com.survivalparadise.nativegame;

/**
 * Native animation state. Walking uses the exact approved four-frame atlas.
 * Idle is a separate two-pose BREATHING cycle made from unchanged V31 pixels,
 * with the V39 planted feet and unchanged weapon/hand rig.
 */
public final class AnimationCycle {
    public static final int IDLE_FRAME=0;
    public static final int WALK_FRAMES=4;
    public static final int IDLE_PHASES=2;
    public static final float IDLE_PHASE_SECONDS=.65f;
    private static final float WALK_FRAME_FACTOR=1.25f;
    // Direct return from the raised pose to neutral: NO intermediate -2px step.
    private static final float[] BREATH_OFFSETS={0f,-4f};

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
