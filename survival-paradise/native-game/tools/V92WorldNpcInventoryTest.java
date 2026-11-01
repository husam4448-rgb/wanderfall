package com.survivalparadise.nativegame;
/** Pure JVM regression test: no Android or device services required. */
public final class V92WorldNpcInventoryTest {
    static void check(boolean b,String s){if(!b)throw new AssertionError(s);}
    public static void main(String[] args){
        WorldSafetyV92.Collision walls=(x,y,r)->
            x+r>0&&x-r<150&&y+r>0&&y-r<150;
        float[] exit=WorldSafetyV92.resolveExit(walls,80,80);
        check(WorldSafetyV92.safe(walls,exit[0],exit[1]),"exit inside building obstacle");
        check(!WorldSafetyV92.hostileAllowed(1080,710,1080,710),"camp radius");
        check(WorldSafetyV92.hostileAllowed(2100,710,1080,710),"world bandit spawn");
        WardrobeV92 outfit=new WardrobeV92();
        String found=outfit.scavenge(1,0);
        check(!found.isEmpty(),"wearables not in cases");
        boolean owns=false;
        for(int i=0;i<4;i++)for(int j=0;j<3;j++)
            if(outfit.found[i][j]>0){owns=true;check(outfit.equip(i,j),"wearable should equip");}
        check(owns,"missing clothing");
        WardrobeV92 reloaded=new WardrobeV92();
        reloaded.decode(outfit.encode());
        check(java.util.Arrays.equals(outfit.equipped,reloaded.equipped),"wardrobe persistence");
        for(int i=0;i<12;i++)for(int j=0;j<4;j++)
            check(WardrobeV92.npcOutfit(i,j)>=0&&WardrobeV92.npcOutfit(i,j)<3,"npc outfit variation");
        NPCRelationshipsV92 npc=new NPCRelationshipsV92();
        check(npc.speech(NPCRelationshipsV92.HOSTILE,0,true).contains("trespassing"),
            "hostile threat speech");
        check(npc.speech(NPCRelationshipsV92.FRIENDLY,2,false).length()>5,"ally speech");
        npc.trade();npc.trade();
        check(npc.canRecruit(),"trade trust progression");
        NPCRelationshipsV92 npc2=new NPCRelationshipsV92();npc2.decode(npc.encode());
        check(npc2.reputation==npc.reputation&&npc2.tradeCount==2,"reputation persistence");
        for(int i=0;i<ExpeditionSitesV88.SITES.length;i++){
            ExpeditionSitesV88.Site s=ExpeditionSitesV88.SITES[i];
            check(s.name.length()>=5,"enterable building name");
        }
        check(ExpeditionSitesV88.SITES.length>=26,"all four legacy buildings have sites");
        System.out.println("V92 PASS clear exits, safe camp, outdoor/indoor dialogue, clothes and reputation.");
    }
}