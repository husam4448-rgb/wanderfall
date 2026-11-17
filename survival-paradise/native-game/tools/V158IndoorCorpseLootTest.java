package com.survivalparadise.nativegame;

/** Exact reusable corpse-bag identities and save-migration regressions. */
public final class V158IndoorCorpseLootTest {
    private static void yes(boolean ok,String reason){
        if(!ok)throw new AssertionError(reason);
    }
    private static ClinicActorsV90.Actor dead(int kind,int id){
        ClinicActorsV90.Actor a=new ClinicActorsV90.Actor(
            kind,800f+id*20f,450f+id*20f,0f,id);
        a.active=false;
        return a;
    }
    private static int gear(BanditLootV87.Bag b,int type){
        return b.extra[type-OutfitInventoryV140.FIRST];
    }
    public static void main(String[] args){
        IndoorCorpseLootV158 interior=new IndoorCorpseLootV158();
        ClinicActorsV90.Actor raider=dead(ClinicActorsV90.RAIDER,5);
        raider.gun=4;raider.rounds=11;raider.spareRounds=17;
        int raiderSkin=1+Math.floorMod(raider.type*31+37,200);
        BanditLootV87.Bag b=interior.ensure(5,raider,0,raiderSkin,1645,false);
        yes(b!=null&&b.corpse&&b.id==6&&b.gearManifestV141,
            "indoor corpse identity or snapshot missing");
        yes(b.count[BanditLootV87.SCRAP]==2,"raider scrap missing");
        yes(gear(b,OutfitInventoryV140.TORSO+
            OutfitInventoryV140.npcTorso(0,raiderSkin))==1,
            "raider torso not a real item");
        yes(gear(b,OutfitInventoryV140.PANTS+
            OutfitInventoryV140.npcPants(0,raiderSkin))==1,
            "raider pants not lootable");
        yes(gear(b,OutfitInventoryV140.BOOTS+
            OutfitInventoryV140.npcBoots(0,raiderSkin))==1,
            "raider boots not lootable");
        yes(gear(b,OutfitInventoryV140.WEAPONS+4)==1,
            "tactical carbine missing from body");
        int family=AmmoInventoryV143.forGun(4)-AmmoInventoryV143.FIRST;
        yes(family>=0&&family<AmmoInventoryV143.COUNT&&
            b.ammoExtraV143[family]==28,"raider ammo type/quantity mismatch");
        yes(b.nutsV143==1645,"corpse currency altered");
        // Existing transfer routine empties a specific selected stack, not
        // every item in the corpse like obsolete V129 SEARCH did.
        yes(interior.stock.takeExtra(b,OutfitInventoryV140.TORSO+
            OutfitInventoryV140.npcTorso(0,raiderSkin)-
            OutfitInventoryV140.FIRST)==1,"cannot loot individual torso");
        yes(interior.stock.take(b,BanditLootV87.SCRAP)==2,
            "cannot loot single supply stack");
        yes(b.count[BanditLootV87.SCRAP]==0&&b.nutsV143==1645&&
            gear(b,OutfitInventoryV140.PANTS+
                OutfitInventoryV140.npcPants(0,raiderSkin))==1,
            "item-by-item looting destroyed other items");
        yes(interior.ensure(5,raider,0,raiderSkin,9999,false)==b,
            "repeat interact rerolled corpse or coins");
        String serialized=interior.encode();
        IndoorCorpseLootV158 loaded=new IndoorCorpseLootV158();
        loaded.decode(serialized);
        BanditLootV87.Bag restored=loaded.get(5);
        yes(restored!=null&&restored.count[BanditLootV87.SCRAP]==0&&
            restored.nutsV143==1645&&gear(restored,OutfitInventoryV140.WEAPONS+4)==1&&
            restored.ammoExtraV143[family]==28,
            "partial transfer did not survive interior save/reload");
        yes(loaded.ensure(5,raider,0,raiderSkin,5000,false)==restored,
            "re-entering same site duplicated saved corpse loot");
        // Each site has a separate encoded record. An unknown site is empty.
        IndoorCorpseLootV158 otherSite=new IndoorCorpseLootV158();
        yes(otherSite.get(5)==null&&otherSite.encode().isEmpty(),
            "another building sees the corpse from the current building");
        // Legacy saves that already searched corpse index 6 must remain
        // empty after V158 migration and after repeated app restarts.
        ClinicActorsV90.Actor medic=dead(ClinicActorsV90.MEDIC,6);
        BanditLootV87.Bag legacy=loaded.ensure(6,medic,4,131,900,true);
        yes(legacy!=null&&legacy.empty(),"legacy searched corpse refilled");
        loaded.decode(loaded.encode());
        yes(loaded.get(6)!=null&&loaded.get(6).empty(),
            "empty legacy corpse regenerated on reload");
        // Fresh medic preserves its medkit, water, three garments and torch.
        IndoorCorpseLootV158 fresh=new IndoorCorpseLootV158();
        BanditLootV87.Bag med=fresh.ensure(6,medic,4,131,900,false);
        yes(med.count[BanditLootV87.MEDKIT]==1&&
            med.count[BanditLootV87.WATER]==1&&
            gear(med,OutfitInventoryV140.WEAPONS+3)==1,
            "medic original possessions incomplete");
        ClinicActorsV90.Actor feral=dead(ClinicActorsV90.FERAL,4);
        BanditLootV87.Bag animal=fresh.ensure(4,feral,0,75,9999,false);
        yes(animal.empty(),"animal was given invented human equipment/currency");
        ClinicActorsV90.Actor living=new ClinicActorsV90.Actor(
            ClinicActorsV90.SURVIVOR,710,310,85,7);
        yes(fresh.ensure(7,living,10,190,200,false)==null,
            "living NPC exposed corpse loot");
        System.out.println("PASS V158 indoor corpse grid: 8 index identities, "+
            "per-item loot, precise original gear, ammo and nuts, old-save "+
            "compatibility, persistent stripped state and separate buildings");
    }
}
