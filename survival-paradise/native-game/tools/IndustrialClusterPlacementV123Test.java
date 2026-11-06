package com.survivalparadise.nativegame;
import java.util.*;
public final class IndustrialClusterPlacementV123Test {
    private static void verify(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    public static void main(String[] args){
        HashSet<Integer> variants=new HashSet<>();int count=0;
        for(int sy=-12;sy<=12;sy++)for(int sx=-12;sx<=12;sx++){
            List<IndustrialClusterPlacementV123.Placement> a=
                IndustrialClusterPlacementV123.inSector(sx,sy,1234567);
            List<IndustrialClusterPlacementV123.Placement> b=
                IndustrialClusterPlacementV123.inSector(sx,sy,1234567);
            verify(a.size()==b.size(),"sector layout changed");
            for(int i=0;i<a.size();i++){
                IndustrialClusterPlacementV123.Placement p=a.get(i);
                verify(p.id().equals(b.get(i).id()),"seed instability");
                variants.add(p.sprite);count++;
                if(p.zone==IndustrialClusterPlacementV123.ROAD_MARK ||
                        p.zone==IndustrialClusterPlacementV123.ROAD_SURFACE)
                    verify(IndustrialClusterPlacementV123.onRoad(p.x,p.y),"road cluster off-road");
                if(p.zone==IndustrialClusterPlacementV123.YARD){
                    verify(!IndustrialClusterPlacementV123.onRoad(p.x,p.y),"yard pile on road");
                    verify(Math.abs(p.x-(sx*1400f+540))>140 ||
                           p.y<sy*1400f+720,"entrance blocked");
                }
                if(p.zone==IndustrialClusterPlacementV123.CORNER){
                    float dx=Math.abs(p.x-sx*1400f),dy=Math.abs(p.y-sy*1400f);
                    verify(Math.abs(dx-(IndustrialWorldV123.roadWidth(sx)*.5f+18))<.01,"corner x");
                    verify(Math.abs(dy-(IndustrialWorldV123.roadWidth(sy)*.5f+18))<.01,"corner y");
                }
                verify(p.sprite!=11 && p.sprite!=35 && p.sprite!=69,
                        "rail art must be reserved until a railway is generated");
                verify(p.sprite!=80,"broken fence requires a damaged fence anchor");
                verify(p.sprite!=97,"culvert requires actual drainage outlet");
                verify(p.sprite!=27,"parking art requires a real parking bay");
            }
        }
        verify(variants.size()>50,"not enough distinct artwork variants: "+variants.size());
        System.out.println("PASS terrain eligible, stable seed, road geometry, clear portal; "+count+
            " instances, "+variants.size()+" authored variants");
    }
}
