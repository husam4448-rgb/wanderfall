package com.survivalparadise.nativegame;

/** V159 physical plot, save-format, road gate and reproducibility regression. */
public final class V159WorldPlanTest {
    private static void yes(boolean result,String why){
        if(!result)throw new AssertionError(why);
    }
    public static void main(String[] args){
        int[] seeds={14901,87011,-999,0,20261117};
        String previous=null;
        int total=0;
        for(int seed:seeds){
            final int[] lastProgress={-1};
            WorldCivilizationV159.Plan plan=WorldCivilizationV159.generate(
                seed,(percent,phase)->{
                    yes(percent>=lastProgress[0]&&percent<=100,
                        "fake or backward loading-screen progress");
                    yes(phase!=null&&!phase.isEmpty(),"empty loading stage");
                    lastProgress[0]=percent;
                });
            yes(lastProgress[0]==100,"world loading stopped prematurely");
            yes(plan.parcels.length>=25,"insufficient developed city parcels");
            yes(plan.atTile(0,0)==null,"authored original camp paved over");
            String encoded=plan.encode();
            yes(encoded.length()<32000,"world save unexpectedly huge");
            yes(WorldCivilizationV159.decode("",seed)==null,
                "old worlds forced into unknown generator");
            yes(WorldCivilizationV159.decode(encoded,seed+1)==null,
                "different seed accepted an unrelated saved world");
            yes(WorldCivilizationV159.decode(encoded+"x",seed)==null,
                "corrupted plan accepted; would move old fences");
            WorldCivilizationV159.Plan loaded=WorldCivilizationV159.decode(
                encoded,seed);
            yes(loaded!=null&&loaded.encode().equals(encoded),
                "new world changed after save/restart");
            WorldCivilizationV159.Plan repeated=WorldCivilizationV159.generate(
                seed,null);
            yes(repeated.encode().equals(encoded),
                "same seed is not deterministic across New Game");
            if(previous!=null)yes(!previous.equals(encoded),
                "different seed generated an identical world");
            previous=encoded;
            for(WorldCivilizationV159.Parcel region:plan.parcels){
                total++;
                yes(region.buildings>=1&&region.fences.length>=5,
                    "empty fenced compound or no perimeter");
                yes(region.kind>=0&&region.kind<=2,"plot type invalid");
                WorldCivilizationV159.Parcel restored=loaded.atTile(
                    region.tx,region.ty);
                yes(restored!=null&&restored.variation==region.variation&&
                    restored.kind==region.kind,"plot changed on load");
                yes(plan.developed((region.left+region.right)*.5f,
                    (region.top+region.bottom)*.5f),
                    "civilization ground not inside the fence");
                // Artist AND collision must share exactly the same segments.
                for(WorldCivilizationV159.Segment fence:region.fences){
                    float midX=(fence.x1+fence.x2)*.5f;
                    float midY=(fence.y1+fence.y2)*.5f;
                    yes(plan.blocked(midX,midY,3f),
                        "visible fence is not solid for actor movement");
                }
                float originX=region.tx*NeighborhoodV154.TILE_W;
                float originY=region.ty*NeighborhoodV154.TILE_H;
                for(float roadX:new float[]{originX+1750f,originX+3550f}){
                    yes(!plan.blocked(roadX,region.top,22f)&&
                        !plan.blocked(roadX,region.bottom,22f),
                        "north/south street terminates in an invisible fence");
                }
                for(float roadY:new float[]{originY+2190f,originY+4250f}){
                    if(roadY>=region.top+200f&&roadY<=region.bottom-200f)
                        yes(!plan.blocked(region.left,roadY,22f)&&
                            !plan.blocked(region.right,roadY,22f),
                            "east/west road is blocked by fence");
                }
                if(region.tx==0&&1605f>region.left+200f&&
                    1605f<region.right-200f)
                    yes(!plan.blocked(1605f,region.top,20f),
                        "legacy north/south road blocked");
                if(region.ty==0&&1036f>region.top+200f&&
                    1036f<region.bottom-200f)
                    yes(!plan.blocked(region.left,1036f,20f),
                        "legacy east/west highway blocked");
            }
            yes(!plan.blocked(1080f,710f,20f),"starter camp fenced off");
            yes(!plan.blocked(1605f,1036f,22f),
                "main crossroads fenced off");
            // Industrial fence lies outside its protected arterial shoulder.
            WorldCivilizationV159.Segment[] boundary=
                IndustrialPerimeterV159.segments(seed);
            yes(boundary.length>=12,"missing industrial perimeter");
            boolean left=false,right=false,top=false,bottom=false;
            for(WorldCivilizationV159.Segment f:boundary){
                float cx=(f.x1+f.x2)*.5f,cy=(f.y1+f.y2)*.5f;
                yes(IndustrialPerimeterV159.blocked(cx,cy,2f,seed),
                    "industrial drawn fence is intangible");
                if(Math.abs(cx-(IndustrialBiomeBridgeV128.WEST-
                    IndustrialPerimeterV159.SETBACK))<1f)left=true;
                if(Math.abs(cx-(IndustrialBiomeBridgeV128.EAST+
                    IndustrialPerimeterV159.SETBACK))<1f)right=true;
                if(Math.abs(cy-(IndustrialBiomeBridgeV128.NORTH-
                    IndustrialPerimeterV159.SETBACK))<1f)top=true;
                if(Math.abs(cy-(IndustrialBiomeBridgeV128.SOUTH+
                    IndustrialPerimeterV159.SETBACK))<1f)bottom=true;
            }
            yes(left&&right&&top&&bottom,
                "industrial region is not enclosed on all four sides");
            for(float roadY:new float[]{
                IndustrialBiomeBridgeV128.ROAD_CENTER_Y,
                IndustrialBiomeBridgeV128.ROAD_CENTER_Y+4*IndustrialWorldV123.SECTOR}){
                if(IndustrialOpenWorldV124.horizontal(
                    Math.round((roadY-IndustrialBiomeBridgeV128.ORIGIN_Y)/
                        IndustrialWorldV123.SECTOR),0,seed))
                    yes(!IndustrialPerimeterV159.blocked(
                        IndustrialBiomeBridgeV128.WEST-
                        IndustrialPerimeterV159.SETBACK,roadY,26f,seed),
                        "industrial entrance gate blocked");
            }
            yes(!IndustrialPerimeterV159.blocked(
                IndustrialBiomeBridgeV128.WEST-110f,
                IndustrialBiomeBridgeV128.ROAD_CENTER_Y,20f,seed),
                "industrial perimeter crosses the main traffic lane");
            for(ExpeditionSitesV88.Site site:ExpeditionSitesV88.SITES)
                yes(site.x!=0f||site.y!=0f,
                    "original fixed location identity corrupted");
        }
        System.out.println("PASS V159: "+total+" checked saved civilization parcels "+
            "across "+seeds.length+" world seeds; source buildings preserved, "+
            "valid fences and real gates; industrial road remains continuous");
    }
}
