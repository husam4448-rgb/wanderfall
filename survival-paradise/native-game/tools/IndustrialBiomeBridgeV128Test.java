package com.survivalparadise.nativegame;

import java.util.HashSet;

/** Regressions for the real outdoor-world stitching, not a second map. */
public final class IndustrialBiomeBridgeV128Test {
    private static void check(boolean b,String m){if(!b)throw new AssertionError(m);}
    public static void main(String[] args){
        int sites=0,roads=0,different=0;
        for(int seed:new int[]{14901,22,-35,3041,561234}){
            check(IndustrialBiomeBridgeV128.approachRoad(3700,1036),
                  "original highway has no industrial approach");
            check(IndustrialBiomeBridgeV128.approachRoad(5590,1036),
                  "arterial discontinuity at west side");
            check(IndustrialBiomeBridgeV128.roadAt(5600,1036,seed),
                  "road stops exactly at biome boundary");
            check(IndustrialBiomeBridgeV128.roadAt(5610,1036,seed),
                  "V124 arterial has no west connection");
            check(IndustrialBiomeBridgeV128.westEdge(1036,seed)==5600f,
                  "primary entrance rim not road-aligned");
            check(!IndustrialBiomeBridgeV128.contains(2200,1036,seed),
                  "original survivor camp replaced by industrial region");
            check(!IndustrialBiomeBridgeV128.contains(
                  IndustrialBiomeBridgeV128.EAST+600,1036,seed),
                  "region should reconnect to the outside map");
            check(IndustrialBiomeBridgeV128.boundaryStrength(5600,1036,seed)>.98f,
                  "industrial edge has no surface transition");
            for(int sy=IndustrialBiomeBridgeV128.INDUSTRIAL_MIN_SY;
                    sy<IndustrialBiomeBridgeV128.INDUSTRIAL_MAX_SY;sy++){
                for(int sx=IndustrialBiomeBridgeV128.INDUSTRIAL_MIN_SX;
                        sx<IndustrialBiomeBridgeV128.INDUSTRIAL_MAX_SX;sx++){
                    IndustrialOpenWorldV124.Plot p=
                        IndustrialOpenWorldV124.plot(sx,sy,seed);
                    check(IndustrialBiomeBridgeV128.industrialPlot(sx,sy),
                          "missing seeded sector");
                    check(!IndustrialBiomeBridgeV128.industrialPlot(sx+12,sy),
                          "industrial region leaks beyond edge");
                    if(p.enterable()){
                        sites++;
                        float doorX=IndustrialBiomeBridgeV128.worldX(p.doorX);
                        float doorY=IndustrialBiomeBridgeV128.worldY(p.doorY);
                        check(IndustrialBiomeBridgeV128.contains(doorX,doorY,seed),
                              "industrial door is clipped out of world");
                        check(IndustrialBiomeBridgeV128.nearestEntrance(
                              doorX,doorY,111f,seed)!=null,
                              "factory no longer enterable");
                        check(!IndustrialBiomeBridgeV128.blocked(
                              doorX,doorY+50,18f,seed),
                              "factory portal blocked after stitching");
                        check(IndustrialOpenWorldV124.streetCount(sx,sy,seed)>0,
                              "active industrial plot without street connection");
                        check(IndustrialWorldV123.district(sx,sy,seed).lootKey(2,true)
                              .contains("indoor:2"),"seed-scoped loot identity changed");
                    }
                    float localX=p.x+500,localY=p.y+600;
                    float worldX=IndustrialBiomeBridgeV128.worldX(localX);
                    float worldY=IndustrialBiomeBridgeV128.worldY(localY);
                    check(IndustrialBiomeBridgeV128.localX(worldX)==localX &&
                          IndustrialBiomeBridgeV128.localY(worldY)==localY,
                          "world-local coordinate roundtrip broken");
                    if(IndustrialOpenWorldV124.horizontal(sy,sx,seed)){
                        float x=IndustrialBiomeBridgeV128.worldX(p.x+500);
                        float y=IndustrialBiomeBridgeV128.worldY(p.y);
                        check(IndustrialBiomeBridgeV128.roadAt(x,y,seed),
                              "industrial road disconnected within region");
                        roads++;
                    }
                    if(p.kind!=IndustrialOpenWorldV124.plot(sx,sy,seed+1).kind)
                        different++;
                }
            }
            check(!IndustrialBiomeBridgeV128.industrialPlot(-1,0),
                  "outside plots are not allowed");
            check(!IndustrialBiomeBridgeV128.industrialPlot(12,0),
                  "east border plot incorrectly allowed");
            check(!IndustrialBiomeBridgeV128.industrialPlot(0,5),
                  "south border plot incorrectly allowed");
        }
        check(sites>250,"few enterable industrial factories");
        check(roads>100,"insufficient connected industrial roads");
        check(different>80,"distinct seeds not changing the district");
        System.out.println("PASS V128 integrated world: "+sites+
            " enterable seeded sites, "+roads+" connected roads, old camp preserved, "+
            "global/local transforms, edge blending, collisions and site save keys");
    }
}
