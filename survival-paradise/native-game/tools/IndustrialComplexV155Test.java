package com.survivalparadise.nativegame;

import java.util.HashSet;

/** V155 realistic industrial hall dimensions, aligned collision and save keys. */
public final class IndustrialComplexV155Test {
    private static void check(boolean v,String why){
        if(!v)throw new AssertionError(why);
    }
    public static void main(String[] args){
        int facilities=0,vehicle=0,sites=0;
        HashSet<Integer> kinds=new HashSet<>();
        HashSet<String> shapes=new HashSet<>();
        for(int seed:new int[]{0,14901,-11,2026,80073}){
            for(int sy=-8;sy<=8;sy++)for(int sx=-8;sx<=8;sx++){
                IndustrialOpenWorldV124.Plot p=IndustrialOpenWorldV124.plot(sx,sy,seed);
                if(!p.enterable())continue;
                facilities++;kinds.add(p.kind);
                shapes.add((int)p.buildingW+":"+(int)p.buildingH);
                check(p.buildingW>=990f&&p.buildingH>=560f,
                      "industrial main hall smaller than a real complex");
                check(p.buildingW<=1080f&&p.buildingH<=600f,
                      "hall crosses protected arterial setbacks");
                check(p.doorX==p.x+700f&&p.doorY==p.y+810f,
                      "historical doors or save coordinates drift");
                IndustrialWorldV123.District d=IndustrialWorldV123.district(sx,sy,seed);
                check(d.id.equals(p.id())&&d.doorX==p.doorX&&d.doorY==p.doorY,
                      "saved industrial site identity lost");
                check(!IndustrialOpenWorldV124.blocked(
                      p.doorX,p.doorY+35f,22f,seed),"door landing blocked");
                for(float y=p.doorY+35f;y<=p.y+1190f;y+=26f)
                    check(!IndustrialOpenWorldV124.blocked(
                          p.doorX,y,20f,seed),
                          "central door / yard gate access blocked at "+y);
                check(!IndustrialOpenWorldV124.blocked(
                      p.x+700f,p.y+1240f,22f,seed),"south gate blocked");
                float[] b=IndustrialComplexV155.bounds(p);
                check(b[0]>=p.x+140f&&b[2]<=p.x+1255f&&
                      b[1]>=p.y+151f&&b[3]<=p.y+900f,
                      "compound overlaps arterial road, curb or supply yard");
                IndustrialComplexV155.Wing a=IndustrialComplexV155.left(p);
                IndustrialComplexV155.Wing right=IndustrialComplexV155.right(p);
                for(IndustrialComplexV155.Wing wing:
                        new IndustrialComplexV155.Wing[]{a,right}){
                    float cx=wing.x+wing.w*.5f,cy=wing.y+wing.h*.5f;
                    check(IndustrialOpenWorldV124.blocked(cx,cy,2f,seed),
                          "opaque annex art is intangible");
                    check(!wing.blocks(wing.x-30f,wing.y+wing.h*.5f,1f),
                          "invisible rectangle margin obstructs path");
                }
                check(!IndustrialComplexV155.blocks(
                      p,p.doorX,p.doorY+35f,25f),
                      "annex blocks historic entrance");
                int vehicleCount=0;
                for(IndustrialPropLayoutV126.Prop part:
                        IndustrialPropLayoutV126.forPlot(p)){
                    if(part.sprite==IndustrialPropLayoutV126.FORKLIFT||
                            part.sprite==IndustrialPropLayoutV126.TRUCK){
                        vehicleCount++;
                        vehicle++;
                        float vx=p.x+part.x+part.w*(part.left+part.right)/2f;
                        float vy=p.y+part.y+part.h*(part.top+part.bottom)/2f;
                        check(!IndustrialFacadeShapeV126.buildingBlocks(p,vx,vy,0),
                              "vehicle parked through a solid factory roof");
                    }
                }
                check(vehicleCount==1,"missing distinct outdoor truck/forklift");
                // Four old fixed salvage positions, quantities and loot keys
                // are retained; each remains physically reachable outside
                // the enlarged hall and unblocked by parked machinery.
                for(int stock=0;stock<4;stock++){
                    float px=d.materialX(stock),py=d.materialY(stock);
                    check(!IndustrialOpenWorldV124.blocked(px,py,20f,seed),
                          "existing stockpile trapped by new factory: "+stock);
                    String key=d.lootKey(stock,false);
                    check(key.equals(seed+":"+p.id()+":yard:"+stock),
                          "persistent yard stockpile key changed");
                    sites++;
                }
                for(int y=0;y<=8;y++){
                    float yy=p.y+880f+y*39f;
                    check(!IndustrialComplexV155.blocks(p,p.doorX,yy,22f),
                          "wide central loading lane is obstructed");
                }
                // A nonopaque source corner stays walkable even after the
                // approved PNG is rendered inside the larger roof transform.
                float sourceX=p.buildingX-12f+(p.buildingW+24f)*.055f;
                float sourceY=p.buildingY-22f+(p.buildingH+46f)*.055f;
                check(!IndustrialFacadeShapeV126.buildingBlocks(
                    p,sourceX,sourceY,0),"transparent PNG corner became wall");
            }
            for(int npc=0;npc<5;npc++){
                float[] pos=IndustrialCampV125.home(npc,seed);
                check(IndustrialCampV125.clear(pos[0],pos[1],seed),
                      "industrial worker spawns in new factory geometry");
            }
        }
        check(facilities>700&&vehicle==facilities&&sites==facilities*4,
              "insufficient generated facility coverage");
        check(kinds.size()==8&&shapes.size()>=4,
              "missing real industrial scale or architectural diversity");
        System.out.println("PASS V155: "+facilities+" full-scale complexes, "+
            "eight distinct industries, four facade proportions, "+
            "unblocked saved entrances/stockpiles/NPC patrols, source alpha and roads");
    }
}
