package com.survivalparadise.nativegame;

/**
 * Seed-stable regional stitching for the original continuous world.
 *
 * The original east-west highway at world Y=1036 meets the V124 industrial
 * horizontal arterial at local (0,0). World coordinates are NEVER saved as
 * industrial-local coordinates: conversion happens only at the region edge.
 *
 * A fixed regional origin avoids rebuilding historical camp, resource or NPC
 * locations. Industrial site IDs and stockpile keys retain V123 coordinates.
 */
public final class IndustrialBiomeBridgeV128 {
    private IndustrialBiomeBridgeV128(){}
    public static final int ORIGIN_X=5600, ORIGIN_Y=1036;
    public static final int ACCESS_ROAD_BEGIN_X=3370;
    public static final int ROAD_CENTER_Y=1036;
    public static final int INDUSTRIAL_MIN_SX=0,INDUSTRIAL_MAX_SX=12;
    public static final int INDUSTRIAL_MIN_SY=-5,INDUSTRIAL_MAX_SY=5;
    public static final int WEST=ORIGIN_X;
    public static final int EAST=ORIGIN_X+INDUSTRIAL_MAX_SX*IndustrialWorldV123.SECTOR;
    public static final int NORTH=ORIGIN_Y+INDUSTRIAL_MIN_SY*IndustrialWorldV123.SECTOR;
    public static final int SOUTH=ORIGIN_Y+INDUSTRIAL_MAX_SY*IndustrialWorldV123.SECTOR;
    public static final float TRANSITION_WIDTH=480f;

    public static float localX(float x){return x-ORIGIN_X;}
    public static float localY(float y){return y-ORIGIN_Y;}
    public static float worldX(float x){return x+ORIGIN_X;}
    public static float worldY(float y){return y+ORIGIN_Y;}
    public static int activeSeed(int selectedWorldSeed){return selectedWorldSeed;}
    public static boolean industrialPlot(int sx,int sy){
        return sx>=INDUSTRIAL_MIN_SX&&sx<INDUSTRIAL_MAX_SX&&
               sy>=INDUSTRIAL_MIN_SY&&sy<INDUSTRIAL_MAX_SY;
    }
    public static boolean bounds(float x,float y){
        return x>=WEST-200&&x<=EAST+200&&y>=NORTH-200&&y<=SOUTH+200;
    }
    private static int rand(int n,int seed,int salt){
        return IndustrialWorldV123.hash(n,salt,seed^0x614EA721);
    }
    private static float lerp(float a,float b,float t){return a+(b-a)*t;}
    private static float noise1(float value,int seed,int salt){
        float at=value/310f;
        int i=(int)Math.floor(at);
        float f=at-i;f=f*f*(3f-2f*f);
        float n0=Math.floorMod(rand(i,seed,salt),201)-100;
        float n1=Math.floorMod(rand(i+1,seed,salt),201)-100;
        return lerp(n0,n1,f);
    }
    private static float entranceEnvelope(float y){
        // Exactly zero edge displacement on the through-road, ensuring there
        // is never a broken or diagonal seam at the player's highway entry.
        float d=Math.abs(y-ROAD_CENTER_Y);
        return Math.min(1f,d/340f);
    }
    public static float westEdge(float y,int seed){
        return WEST+noise1(y,seed,7)*.75f*entranceEnvelope(y);
    }
    public static float eastEdge(float y,int seed){
        return EAST+noise1(y,seed,11)*.75f;
    }
    public static float northEdge(float x,int seed){
        return NORTH+noise1(x,seed,17)*.75f;
    }
    public static float southEdge(float x,int seed){
        return SOUTH+noise1(x,seed,23)*.75f;
    }
    /** Same jagged edge is used for render clipping and interaction gates. */
    public static boolean contains(float x,float y,int seed){
        if(!bounds(x,y))return false;
        return x>=westEdge(y,seed)&&x<eastEdge(y,seed)
            &&y>=northEdge(x,seed)&&y<southEdge(x,seed);
    }
    /** No invisible walls at regional edges; only real factory/prop hulls. */
    public static boolean blocked(float wx,float wy,float radius,int seed){
        if(!contains(wx,wy,seed))return false;
        int sx=IndustrialOpenWorldV124.sx(localX(wx));
        int sy=IndustrialOpenWorldV124.sy(localY(wy));
        if(!industrialPlot(sx,sy))return false;
        return IndustrialOpenWorldV124.blocked(localX(wx),localY(wy),radius,seed);
    }
    public static IndustrialWorldV123.District nearestEntrance(float wx,float wy,
                                                                  float radius,int seed){
        if(!contains(wx,wy,seed))return null;
        IndustrialWorldV123.District site=IndustrialOpenWorldV124.nearestEntrance(
            localX(wx),localY(wy),radius,seed);
        return site!=null&&industrialPlot(site.sx,site.sy)?site:null;
    }
    public static boolean hasIndustrialLoot(float wx,float wy,int seed){
        if(!contains(wx,wy,seed))return false;
        return industrialPlot(IndustrialOpenWorldV124.sx(localX(wx)),
                              IndustrialOpenWorldV124.sy(localY(wy)));
    }
    /** World road y=1036 and industrial y=0 are one continuous drive lane. */
    public static boolean approachRoad(float wx,float wy){
        return wx>=ACCESS_ROAD_BEGIN_X&&wx<=WEST
            &&Math.abs(wy-ROAD_CENTER_Y)<=113f+
                (wx-ACCESS_ROAD_BEGIN_X)/(WEST-(float)ACCESS_ROAD_BEGIN_X)*22f;
    }
    public static boolean roadAt(float wx,float wy,int seed){
        if(approachRoad(wx,wy))return true;
        return contains(wx,wy,seed)
            &&IndustrialOpenWorldV124.roadAt(localX(wx),localY(wy),seed);
    }
    /** Soft transition strength for textured ground dressing. */
    public static float boundaryStrength(float wx,float wy,int seed){
        float dist=Math.min(Math.min(Math.abs(wx-westEdge(wy,seed)),
                                    Math.abs(wx-eastEdge(wy,seed))),
                            Math.min(Math.abs(wy-northEdge(wx,seed)),
                                     Math.abs(wy-southEdge(wx,seed))));
        return Math.max(0f,1f-dist/TRANSITION_WIDTH);
    }
}
