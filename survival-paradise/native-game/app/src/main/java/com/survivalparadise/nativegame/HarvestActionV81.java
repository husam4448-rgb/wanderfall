package com.survivalparadise.nativegame;

/**
 * Frame-rate-independent gathering animation. Does NOT change the world until
 * the final recovery finishes. Renderers read phase/angle; no actor atlas edits.
 */
public final class HarvestActionV81 {
    public static final int IDLE=0, WINDUP=1, STRIKE=2, RECOVER=3;
    public static final int WOOD=ResourceWorldV80.WOOD;
    public static final int STONE=ResourceWorldV80.STONE;
    public static final int FIBER=ResourceWorldV80.FIBER;
    private static final float WOOD_PERIOD=.42f, STONE_PERIOD=.47f, FIBER_PERIOD=.31f;

    public ResourceWorldV80.Node target;
    public int kind=IDLE, hitsDone=0, hitsRequired=0;
    public boolean active=false, finished=false;
    private boolean struckThisCycle=false;
    private float timeInCycle=0f;
    private int phase=IDLE;

    public boolean begin(ResourceWorldV80.Node node){
        if(active||node==null)return false;
        target=node;kind=node.resource();
        hitsRequired=kind==WOOD?(node.kind==5?2:3):kind==STONE?3:2;
        hitsDone=0;timeInCycle=0;struckThisCycle=false;
        active=true;finished=false;phase=WINDUP;
        return true;
    }
    public void cancel(){
        active=false;finished=false;target=null;phase=IDLE;
        timeInCycle=0;hitsDone=0;hitsRequired=0;struckThisCycle=false;
    }
    public boolean advance(float dt){
        if(!active)return false;
        boolean impact=false;
        float remaining=Math.max(0f,Math.min(.12f,dt));
        // Split updates exactly at the cycle boundary for deterministic events.
        while(remaining>0f&&active){
            float period=period();
            float step=Math.min(remaining,period-timeInCycle);
            float prev=timeInCycle;
            timeInCycle+=step;
            remaining-=step;
            if(!struckThisCycle&&prev<period*.62f&&timeInCycle>=period*.62f){
                struckThisCycle=true;hitsDone++;impact=true;
            }
            float t=Math.min(1f,timeInCycle/period);
            phase=t<.30f?WINDUP:t<.66f?STRIKE:RECOVER;
            if(timeInCycle>=period-.000001f){
                if(hitsDone>=hitsRequired){
                    active=false;finished=true;phase=IDLE;
                }else{
                    timeInCycle=0f;struckThisCycle=false;phase=WINDUP;
                }
            }
        }
        return impact;
    }
    public float period(){
        return kind==STONE?STONE_PERIOD:kind==FIBER?FIBER_PERIOD:WOOD_PERIOD;
    }
    public int phase(){return phase;}
    public float cycleProgress(){return active?timeInCycle/period():0f;}
    public float totalProgress(){
        if(finished)return 1f;
        if(!active||hitsRequired==0)return 0f;
        return Math.min(1f,(hitsDone-(struckThisCycle?1:0)+cycleProgress())/hitsRequired);
    }
    public float swingDegrees(){
        float t=cycleProgress();
        float lift=kind==FIBER?-32f:-92f;
        float end=kind==FIBER?28f:kind==STONE?70f:62f;
        if(t<.30f)return -22f+(lift+22f)*(t/.30f);
        if(t<.66f){
            float u=(t-.30f)/.36f;
            return lift+(end-lift)*(u*u*(3f-2f*u));
        }
        return end+(-22f-end)*((t-.66f)/.34f);
    }
    public boolean matches(int cx,int cy,int slot){
        return target!=null&&target.cx==cx&&target.cy==cy&&target.slot==slot;
    }
    public String actionName(){
        return kind==STONE?"MINING":kind==FIBER?"CUTTING":"CHOPPING";
    }
    public boolean canComplete(float px,float py,float radius,boolean alreadyDepleted){
        if(!finished||target==null||alreadyDepleted)return false;
        float dx=target.x-px,dy=target.y-py;
        return dx*dx+dy*dy<=radius*radius;
    }
}
