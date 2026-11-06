package com.survivalparadise.nativegame;

public final class IndustrialGeometryV126Test {
    private static void ok(boolean b,String error){if(!b)throw new AssertionError(error);}
    public static void main(String[] args){
        int facades=0,shrunk=0,props=0;
        for(int kind=0;kind<8;kind++){
            int facade=IndustrialFacadeShapeV126.facade(kind);
            ok(facade>=0&&facade<=3,"invalid facade");
            ok(!IndustrialFacadeShapeV126.opaque(facade,0,0),"alpha top corner is clear");
            ok(IndustrialFacadeShapeV126.opaque(facade,16,19),"visible facade center opaque");
        }
        for(int seed:new int[]{14901,-11,0,2026,813501}){
            for(int sy=-10;sy<=10;sy++)for(int sx=-10;sx<=10;sx++){
                IndustrialOpenWorldV124.Plot p=IndustrialOpenWorldV124.plot(sx,sy,seed);
                if(!p.developed())continue;
                if(p.enterable()){
                    facades++;
                    float artLeft=p.buildingX-12f,artTop=p.buildingY-22f;
                    float artW=p.buildingW+24f,artH=p.buildingH+46f;
                    // Old collision would wrongly block these completely
                    // transparent portions of the facade source PNG.
                    float blankX=artLeft+artW*.055f;
                    float blankY=artTop+artH*.055f;
                    ok(!IndustrialFacadeShapeV126.buildingBlocks(p,blankX,blankY,0),
                       "upper transparent corner still has invisible wall");
                    shrunk++;
                    ok(IndustrialFacadeShapeV126.buildingBlocks(
                        p,p.buildingX+p.buildingW*.5f,
                        p.buildingY+p.buildingH*.55f,16),
                       "actual opaque roof missing collision");
                    ok(!IndustrialOpenWorldV124.blocked(
                        p.doorX,p.doorY+35f,20,seed),
                       "real entrance blocked by wrong art/physics");
                }
                ok(!IndustrialOpenWorldV124.blocked(
                    p.x+700,p.y+1240,19,seed),
                   "fenced entrance or yard route blocked");
                for(IndustrialPropLayoutV126.Prop prop:
                        IndustrialPropLayoutV126.forPlot(p)){
                    props++;
                    ok(prop.w>=175&&prop.h>=145,
                       "world prop below its minimum world-unit scale");
                    float cx=p.x+prop.x+prop.w*(prop.left+prop.right)*.5f;
                    float cy=p.y+prop.y+prop.h*(prop.top+prop.bottom)*.5f;
                    ok(prop.blocks(cx,cy,0,p),
                       "visible machine has no collision");
                    // Source bitmap margins are NEVER part of a collision.
                    ok(!prop.blocks(p.x+prop.x-15,p.y+prop.y-15,0,p),
                       "invisible image margin blocks movement");
                }
                if(p.type==IndustrialOpenWorldV124.FACILITY){
                    int found=0;
                    for(IndustrialPropLayoutV126.Prop prop:
                            IndustrialPropLayoutV126.forPlot(p)){
                        if(prop.sprite==IndustrialPropLayoutV126.FORKLIFT){
                            found++;
                            ok(prop.w>=250&&prop.h>=185,
                               "forklift remains player-sized");
                        }
                        if(prop.sprite==IndustrialPropLayoutV126.TRUCK){
                            found++;
                            ok(prop.w>=270&&prop.h>=190,
                               "utility truck is still too small");
                        }
                    }
                    ok(found==1,"vehicle not deterministically present");
                }
            }
            // NPCs still spawn with clearance around new, scale-correct props.
            for(int i=0;i<5;i++){
                float[] pos=IndustrialCampV125.home(i,seed);
                ok(IndustrialCampV125.clear(pos[0],pos[1],seed),
                   "NPC body overlaps enlarged machinery/building");
            }
        }
        ok(facades>700&&shrunk==facades&&props>3000,"inadequate test coverage");
        System.out.println("PASS V126: "+facades+
            " source-traced facades, "+props+
            " size-correct props, empty margins and accessible roads");
    }
}
