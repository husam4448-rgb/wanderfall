package com.survivalparadise.nativegame;

/** Verify V153 movement of old supplies without corrupting inventory/saves. */
public final class V153SiteMigrationTest {
    private static void check(boolean value,String message){
        if(!value)throw new AssertionError(message);
    }
    public static void main(String[] args){
        BanditLootV87 loot=new BanditLootV87();
        int i=0;
        BanditLootV87.Bag old=loot.spawn(
            ExpeditionSitesV88.LEGACY_X[i]+115f,
            ExpeditionSitesV88.LEGACY_Y[i]+91f,3,4,0);
        check(old!=null,"legacy site cache absent");
        old.extra[12]=17;old.ammoExtraV143[3]=11;
        old.gearManifestV141=true;old.nutsV143=12789;
        int originalId=old.id;
        int[] previous=old.count.clone();
        BanditLootV87.Bag corpse=loot.spawn(
            ExpeditionSitesV88.LEGACY_X[1]+115f,
            ExpeditionSitesV88.LEGACY_Y[1]+91f,5,7,0);
        corpse.corpse=true;
        float corpseX=corpse.x,corpseY=corpse.y;
        int count=loot.migrateFixedSiteCachesV153();
        check(count==1,"expected one living supply cache relocation");
        BanditLootV87.Bag moved=loot.bags.get(0);
        check(moved.id==originalId,"cache identity changed");
        check(moved.x==ExpeditionSitesV88.SITES[0].x+120f&&
              moved.y==ExpeditionSitesV88.SITES[0].y+
                  ExteriorFootprintV130.anchor(ExpeditionSitesV88.SITES[0])+36f,
              "cache not moved to institution entrance");
        for(int j=0;j<previous.length;j++)
            check(moved.count[j]==previous[j],"item stack corrupted "+j);
        check(moved.extra[12]==17&&moved.ammoExtraV143[3]==11&&
            moved.nutsV143==12789&&moved.gearManifestV141,
            "gear/ammo/wallet lost in migration");
        check(loot.bags.get(1).x==corpseX&&loot.bags.get(1).y==corpseY,
              "historical corpse moved");
        check(loot.migrateFixedSiteCachesV153()==0,"migration not idempotent");
        BanditLootV87 loaded=new BanditLootV87();
        loaded.decode(loot.encode());
        check(loaded.bags.size()==2,"migrated cache save was lost");
        check(loaded.bags.get(0).extra[12]==17&&
            loaded.bags.get(0).ammoExtraV143[3]==11&&
            loaded.bags.get(0).nutsV143==12789,
            "migrated equipment failed save round trip");
        System.out.println("PASS V153: cache ID, stacks, headless corpse, ammunition, wallet and gear");
    }
}
