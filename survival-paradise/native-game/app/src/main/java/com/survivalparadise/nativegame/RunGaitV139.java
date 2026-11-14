package com.survivalparadise.nativegame;

/**
 * V139: preserve the approved four original walk poses while accelerating their
 * playback progressively when the player runs. Does not change world movement,
 * stamina, head artwork, NPC timing, equipment effects or collision geometry.
 */
final class RunGaitV139 {
    static final float MAX_MULTIPLIER=1.8f;
    static final float RAMP_UP_SECONDS=.32f;
    static final float RAMP_DOWN_SECONDS=.24f;
    private float runBlend=0f;
    private float gaitSeconds=0f;

    void reset(){runBlend=0f;gaitSeconds=0f;}

    void step(float dt,boolean moving,boolean running){
        dt=Math.max(0f,Math.min(.25f,dt));
        if(!moving){reset();return;}
        if(running)
            runBlend=Math.min(1f,runBlend+dt/RAMP_UP_SECONDS);
        else
            runBlend=Math.max(0f,runBlend-dt/RAMP_DOWN_SECONDS);
        // Smoothstep eliminates a sudden jump in stride frequency at either end.
        float eased=runBlend*runBlend*(3f-2f*runBlend);
        gaitSeconds+=dt*(1f+(MAX_MULTIPLIER-1f)*eased);
        // Prevent float time overflow after extended play; preserves phase for
        // normal play sessions without touching sprite or frame ordering.
        if(gaitSeconds>100000f)gaitSeconds-=100000f;
    }

    float timeSeconds(){return gaitSeconds;}
    float runBlend(){return runBlend;}
}
