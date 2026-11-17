package com.survivalparadise.nativegame;

import java.util.ArrayList;

/**
 * A controlled, fenced industrial region, separate from the wilderness.
 * Physical fence sits inside the authored V128 natural/industry boundary;
 * every existing industrial arterial remains open through a wide gate.
 * Both painter and collision use precisely these immutable segments.
 */
public final class IndustrialPerimeterV159 {
    private IndustrialPerimeterV159(){}
    public static final int INSET=103;
    public static final float GATE_HALF=208f;
    private static volatile int currentSeed=Integer.MIN_VALUE;
    private static volatile WorldCivilizationV159.Segment[] current;
    public static WorldCivilizationV159.Segment[] segments(int seed){
        WorldCivilizationV159.Segment[] cached=current;
        if(currentSeed==seed&&cached!=null)return cached;
        synchronized(IndustrialPerimeterV159.class){
            if(currentSeed==seed&&current!=null)return current;
            ArrayList<WorldCivilizationV159.Segment> all=new ArrayList<>(160);
            float west=IndustrialBiomeBridgeV128.WEST+INSET;
            float east=IndustrialBiomeBridgeV128.EAST-INSET;
            float north=IndustrialBiomeBridgeV128.NORTH+INSET;
            float south=IndustrialBiomeBridgeV128.SOUTH-INSET;
            int originX=IndustrialBiomeBridgeV128.ORIGIN_X;
            int originY=IndustrialBiomeBridgeV128.ORIGIN_Y;
            int size=IndustrialWorldV123.SECTOR;
            for(int side=0;side<4;side++){
                boolean vertical=side<2;
                float start=vertical?north:west;
                float end=vertical?south:east;
                float fixed=side==0?west:side==1?east:
                    side==2?north:south;
                ArrayList<Float> gates=new ArrayList<>();
                if(vertical){
                    int sector=side==0?0:
                        IndustrialBiomeBridgeV128.INDUSTRIAL_MAX_SX-1;
                    for(int sy=IndustrialBiomeBridgeV128.INDUSTRIAL_MIN_SY;
                            sy<=IndustrialBiomeBridgeV128.INDUSTRIAL_MAX_SY;sy++)
                        if(IndustrialOpenWorldV124.horizontal(sy,sector,seed))
                            gates.add(originY+sy*(float)size);
                }else{
                    int sector=side==2?
                        IndustrialBiomeBridgeV128.INDUSTRIAL_MIN_SY:
                        IndustrialBiomeBridgeV128.INDUSTRIAL_MAX_SY-1;
                    for(int sx=IndustrialBiomeBridgeV128.INDUSTRIAL_MIN_SX;
                            sx<=IndustrialBiomeBridgeV128.INDUSTRIAL_MAX_SX;sx++)
                        if(IndustrialOpenWorldV124.vertical(sx,sector,seed))
                            gates.add(originX+sx*(float)size);
                }
                float cursor=start;
                for(float gate:gates){
                    float from=Math.max(start,gate-GATE_HALF);
                    float to=Math.min(end,gate+GATE_HALF);
                    if(to<=start||from>=end||to<=cursor)continue;
                    emit(all,vertical,fixed,cursor,from,side);
                    cursor=Math.max(cursor,to);
                }
                emit(all,vertical,fixed,cursor,end,side);
            }
            current=all.toArray(new WorldCivilizationV159.Segment[0]);
            currentSeed=seed;
            return current;
        }
    }
    private static void emit(ArrayList<WorldCivilizationV159.Segment> out,
                             boolean vertical,float fixed,float a,float b,
                             int salt){
        if(b-a<40f)return;
        out.add(vertical?
            new WorldCivilizationV159.Segment(fixed,a,fixed,b,
                WorldCivilizationV159.OUTPOST,salt):
            new WorldCivilizationV159.Segment(a,fixed,b,fixed,
                WorldCivilizationV159.OUTPOST,salt));
    }
    public static boolean blocked(float x,float y,float radius,int seed){
        if(x<IndustrialBiomeBridgeV128.WEST-150f||
           x>IndustrialBiomeBridgeV128.EAST+150f||
           y<IndustrialBiomeBridgeV128.NORTH-150f||
           y>IndustrialBiomeBridgeV128.SOUTH+150f)return false;
        for(WorldCivilizationV159.Segment f:segments(seed))
            if(f.blocked(x,y,radius))return true;
        return false;
    }
}
