package com.survivalparadise.nativegame;

/** Timed tool swing, impact count, cancellation, and V80 persistence integration. */
public final class V81HarvestTest {
    private static void ok(boolean pass,String what){if(!pass)throw new AssertionError(what);}
    private static ResourceWorldV80.Node choose(int kind){
        for(int cy=-12;cy<12;cy++)for(int cx=-12;cx<12;cx++)
            for(int k=0;k<ResourceWorldV80.SLOTS;k++){
                ResourceWorldV80.Node n=ResourceWorldV80.node(cx,cy,k,1080,710,3200,2200);
                if(n!=null&&n.resource()==kind)return n;
            }
        throw new AssertionError("Missing "+kind+" node");
    }
    private static void simulation(int kind,int fps){
        ResourceWorldV80 w=new ResourceWorldV80();
        ResourceWorldV80.Node node=choose(kind);
        HarvestActionV81 action=new HarvestActionV81();
        ok(action.begin(node),"start failed");
        ok(!action.begin(node),"overlap should be rejected");
        ok(!w.exhausted(node.cx,node.cy,node.slot),"instant gathering");
        int impacts=0,frames=0;
        boolean sawWindup=false,sawStrike=false,sawRecover=false;
        while(action.active&&frames<3000){
            if(action.advance(1f/fps))impacts++;
            sawWindup|=action.phase()==HarvestActionV81.WINDUP;
            sawStrike|=action.phase()==HarvestActionV81.STRIKE;
            sawRecover|=action.phase()==HarvestActionV81.RECOVER;
            ok(!w.exhausted(node.cx,node.cy,node.slot),"depletion before finish");
            frames++;
        }
        ok(frames<3000&&action.finished,"harvest never completes");
        ok(impacts==action.hitsRequired,"incorrect impact count");
        ok(sawWindup&&sawStrike&&sawRecover,"missing visible swing phase");
        ok(action.totalProgress()==1f,"not completed");
        ok(action.canComplete(node.x,node.y,ResourceWorldV80.USE_RADIUS,false),
           "final collection denied at target");
        ok(!action.canComplete(node.x+200f,node.y,ResourceWorldV80.USE_RADIUS,false),
           "out-of-range collection");
        ok(!action.canComplete(node.x,node.y,ResourceWorldV80.USE_RADIUS,true),
           "already depleted rewarded twice");
        ok(w.harvest(node),"first final reward failed");
        ok(!w.harvest(node),"duplicated final reward");
        String saved=w.encode();ResourceWorldV80 reloaded=new ResourceWorldV80();
        reloaded.decode(saved);
        ok(reloaded.exhausted(node.cx,node.cy,node.slot),"gathered resource regenerated");
        action.cancel();
        ok(!action.active&&!action.finished&&action.target==null,
           "state not reset after completion");
    }
    private static void canceled(int kind){
        ResourceWorldV80 w=new ResourceWorldV80();
        ResourceWorldV80.Node n=choose(kind);HarvestActionV81 a=new HarvestActionV81();
        ok(a.begin(n),"start failed");
        for(int frame=0;frame<5;frame++)a.advance(a.period()/6f); // real frame steps: one impact, no completion
        ok(a.hitsDone>0,"cancellation test did not reach impact");
        a.cancel();
        ok(!a.active&&!a.finished&&a.target==null,"cannot cancel");
        ok(!a.canComplete(n.x,n.y,110,false),"cancel granted a reward");
        ok(!w.exhausted(n.cx,n.cy,n.slot),"cancel depleted node");
        ok(a.begin(n),"cannot retry after cancel");
        ok(!a.advance(0f),"zero timestep produced impact");
    }
    public static void main(String[]args){
        for(int k=0;k<3;k++){
            canceled(k);
            for(int fps:new int[]{30,60,90,120})simulation(k,fps);
        }
        HarvestActionV81 state=new HarvestActionV81();
        ok(state.phase()==HarvestActionV81.IDLE,"initial state");
        ok(!state.advance(.02f),"idle produced impact");
        System.out.println("V81 PASS axe/pickaxe/knife strikes, end-only rewards, cancel/retry, "+
            "world persistence and 30/60/90/120 FPS timing");
    }
}
