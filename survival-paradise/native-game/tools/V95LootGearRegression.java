package com.survivalparadise.nativegame;
public final class V95LootGearRegression {
    private static void ok(boolean b,String note){if(!b)throw new AssertionError(note);}
    public static void main(String[] args){
        GearLootV95 caches=new GearLootV95();
        FieldFindsV91 packs=new FieldFindsV91();
        WardrobeV92 clothing=new WardrobeV92();
        ok(GearLootV95.TYPES==15&&GearLootV95.TOTAL==23,
            "expected 3 backpacks + 12 clothes alongside 8 classic supplies");
        int n=0,bags=0,garments=0;
        for(int site=0;site<26;site++){
            for(int box=0;box<14;box++){
                int[] types=GearLootV95.lootTypes(site,box);
                for(int type:types){
                    if(type<0)continue;
                    ok(caches.available(site,box,type,false),"unclaimed cache contents");
                    ok(caches.transfer(site,box,type,false,packs,clothing),"gear transfers");
                    ok(!caches.transfer(site,box,type,false,packs,clothing),"duplicate loot");
                    n++;if(type<3)bags++;else garments++;
                }
            }
        }
        ok(n>350&&bags>20&&garments>50,"loot distribution across sites");
        String saved=caches.encode();
        GearLootV95 loaded=new GearLootV95();loaded.decode(saved);
        for(int type:GearLootV95.lootTypes(0,0))
            if(type>=0)ok(!loaded.available(0,0,type,false),"persisted consumed stack");
        ok(!loaded.hasLoot(3,1,true),"previously searched V91 case cannot duplicate gear");
        int sum=0;
        for(int v:packs.bags)sum+=v;
        for(int[] row:clothing.found)for(int v:row)sum+=v;
        ok(sum==n,"transfer updates real wearable inventories");
        ok(clothing.equip(0,0)||clothing.equip(0,1)||clothing.equip(0,2),
            "headwear equippable");
        System.out.println("V95 PASS gear distribution, one-time transfer, save/load, equipment counts "+n);
    }
}