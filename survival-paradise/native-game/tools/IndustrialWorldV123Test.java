package com.survivalparadise.nativegame;
public final class IndustrialWorldV123Test {
    private static void ok(boolean b,String m){if(!b)throw new AssertionError(m);}
    public static void main(String[] args){
        int seed=490731;
        for(int sy=-40;sy<=40;sy++)for(int sx=-40;sx<=40;sx++){
            IndustrialWorldV123.District d=IndustrialWorldV123.district(sx,sy,seed);
            IndustrialWorldV123.District again=IndustrialWorldV123.district(sx,sy,seed);
            ok(d.id.equals(again.id)&&d.kind==again.kind,"determinism");
            ok(IndustrialWorldV123.at(d.doorX,d.doorY,seed).id.equals(d.id),"site coordinates");
            ok(IndustrialWorldV123.nearestEntrance(d.doorX,d.doorY,105,seed).id.equals(d.id),"portal");
            ok(!IndustrialWorldV123.roadAt(d.doorX,d.doorY),"building on road");
            ok(IndustrialWorldV123.roadAt(sx*(float)IndustrialWorldV123.SECTOR,sy*(float)IndustrialWorldV123.SECTOR),"road intersection");
            for(int i=0;i<4;i++){
                ok(d.materialQuantity(i)>=2&&d.materialQuantity(i)<=6,"loot bounds");
                ok(!d.lootKey(i,true).equals(d.lootKey(i,false)),"loot namespace");
                ok(!IndustrialWorldV123.roadAt(d.materialX(i),d.materialY(i)),"stockpile on road");
            }
        }
        ok(IndustrialWorldV123.sector(-.1f)==-1,"negative sector floor");
        ok(IndustrialWorldV123.sector(1400f)==1,"sector boundary");
        ok(!IndustrialWorldV123.saveNamespace(123).equals(IndustrialWorldV123.saveNamespace(456)),"seed isolation");
        ok(IndustrialWorldV123.roadWidth(4)==270&&IndustrialWorldV123.roadWidth(5)==168,"arterial roads");
        boolean differing=false;
        for(int i=0;i<12;i++)if(IndustrialWorldV123.district(i,-i,seed).kind!=IndustrialWorldV123.district(i,-i,seed+1).kind)differing=true;
        ok(differing,"distinct seeds");
        System.out.println("PASS: V123 13,122 seeded districts, persistent site identity, roads, portals, materials, save isolation");
    }
}
