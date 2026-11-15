package com.survivalparadise.nativegame;

/** Pure JVM regression gate: exact NPC wardrobe indexing, no dupes, old saves. */
public final class V140EquipmentLootTest {
    static void ok(boolean v,String msg){if(!v)throw new AssertionError(msg);}
    public static void main(String[] args){
        ok(OutfitInventoryV140.TORSO==39&&OutfitInventoryV140.PANTS==59&&
           OutfitInventoryV140.BOOTS==79&&OutfitInventoryV140.WEAPONS==84&&
           OutfitInventoryV140.ROUNDS==96,"stable new item IDs");
        OutfitInventoryV140 player=new OutfitInventoryV140();
        player.migrate(10,12,3,0,true,true,true);
        ok(player.equippedStyle(0)==10&&player.equippedStyle(1)==12&&
           player.equippedStyle(2)==3,"existing looks must migrate");
        ok(player.available(OutfitInventoryV140.TORSO+10)==0,
           "equipped torso must not be spendable");
        ok(!player.remove(OutfitInventoryV140.TORSO+10,1),
           "dropping equipped garment would duplicate it");
        ok(player.add(OutfitInventoryV140.TORSO+10,1)&&
           player.available(OutfitInventoryV140.TORSO+10)==1,
           "duplicate stack reserve wrong");
        ok(player.remove(OutfitInventoryV140.TORSO+10,1)&&
           player.available(OutfitInventoryV140.TORSO+10)==0,
           "stack decrement wrong");
        ok(player.add(OutfitInventoryV140.TORSO+19,1)&&
           player.equip(OutfitInventoryV140.TORSO+19)&&
           player.equippedStyle(0)==19,
           "new torso must drive appearance");
        ok(player.add(OutfitInventoryV140.PANTS+4,1)&&
           player.equip(OutfitInventoryV140.PANTS+4)&&
           player.equippedStyle(1)==4,
           "pants cannot be equipped independently");
        ok(player.add(OutfitInventoryV140.WEAPONS+5,1)&&
           player.equip(OutfitInventoryV140.WEAPONS+5)&&
           player.equippedStyle(3)==5,
           "looted firearm cannot equip");
        ok(player.add(OutfitInventoryV140.ROUNDS,17)&&
           player.remove(OutfitInventoryV140.ROUNDS,12)&&
           player.rounds==5,"remaining rounds not exact");
        OutfitInventoryV140 restore=new OutfitInventoryV140();
        ok(restore.decode(player.encode()),"new outfit decode rejected valid save");
        ok(restore.equippedStyle(0)==19&&restore.equippedStyle(1)==4&&
           restore.equippedStyle(3)==5&&restore.rounds==5,
           "save/load lost equipped looks, firearm or rounds");
        String save=restore.encode();
        ok(!restore.decode("corrupt"),"corrupt save accepted");
        ok(save.equals(restore.encode()),"corrupt save modified existing inventory");
        ok(OutfitInventoryV140.npcTorso(0,1)==3&&
           OutfitInventoryV140.npcPants(0,1)==7&&
           OutfitInventoryV140.npcBoots(0,1)==1,"NPC visual formulas drifted");
        BanditLootV87 corpses=new BanditLootV87();
        BanditLootV87.Bag bag=corpses.spawnCorpse(250,300,1,2,0,-1,42);
        int torso=OutfitInventoryV140.TORSO+
            OutfitInventoryV140.npcTorso(0,42)-OutfitInventoryV140.FIRST;
        int pants=OutfitInventoryV140.PANTS+
            OutfitInventoryV140.npcPants(0,42)-OutfitInventoryV140.FIRST;
        int boots=OutfitInventoryV140.BOOTS+
            OutfitInventoryV140.npcBoots(0,42)-OutfitInventoryV140.FIRST;
        int weapon=OutfitInventoryV140.WEAPONS-OutfitInventoryV140.FIRST;
        int rounds=OutfitInventoryV140.ROUNDS-OutfitInventoryV140.FIRST;
        bag.extra[torso]=1;bag.extra[pants]=1;
        bag.extra[boots]=1;bag.extra[weapon]=1;bag.extra[rounds]=14;
        String encoded=corpses.encode();
        BanditLootV87 restored=new BanditLootV87();
        restored.decode(encoded);
        ok(restored.bags.size()==1&&restored.bags.get(0).skinV109==42,
           "corpse identity disappeared after save");
        BanditLootV87.Bag loaded=restored.bags.get(0);
        ok(loaded.extra[torso]==1&&loaded.extra[pants]==1&&
           loaded.extra[boots]==1&&loaded.extra[weapon]==1&&
           loaded.extra[rounds]==14,"wrong corpse outfit or ammo restored");
        ok(restored.takeExtra(loaded,torso)==1&&
           restored.takeExtra(loaded,torso)==0,"duplicated torso on repeated search");
        restored.takeAllExtra(loaded);
        ok(loaded.extra[rounds]==0&&restored.contains(loaded)&&
           restored.takeExtra(loaded,rounds)==0,
           "taken ammo respawned or body disappeared");
        String old="17,550,600,2,0,3,0,0,0,0,0";
        BanditLootV87 oldSave=new BanditLootV87();
        oldSave.decode(old);
        ok(oldSave.bags.size()==1&&!oldSave.bags.get(0).hasExtra(),
           "old V87 save broken");
        System.out.println("PASS V140: 57 exact inventory items, preservation, "+
            "wearable matching, corpse persistence, anti-dup and ammunition");
    }
}
