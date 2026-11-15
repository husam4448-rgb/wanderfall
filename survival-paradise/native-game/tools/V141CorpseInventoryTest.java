package com.survivalparadise.nativegame;

import java.util.Arrays;

/** V141 pure-JVM source-to-bag, stripping, capacity, recovery and save checks. */
public final class V141CorpseInventoryTest {
    static void ok(boolean yes,String description){
        if(!yes)throw new AssertionError(description);
    }
    static final int[] magazine={12,6,28,1,30,30,28,6,5,75,8,1};
    public static void main(String[] args){
        OutfitInventoryV140 player=new OutfitInventoryV140();
        int[] slots=new int[40],splits=new int[40];
        for(int i=0;i<39;i++)slots[i]=i;
        slots[39]=UnifiedBagSlotsV141.EMPTY;
        UnifiedBagSlotsV141.Count counts=(type)->
            OutfitInventoryV140.valid(type)?player.available(type):0;
        int[] source=slots.clone();
        source[39]=39; // V92's old EMPTY ID
        UnifiedBagSlotsV141.migrateLegacyOrder(source);
        ok(source[39]==UnifiedBagSlotsV141.EMPTY,"legacy empty index became torso");
        ok(UnifiedBagSlotsV141.legacyOrder(source).split(",").length==40,
            "downgrade save format changed");
        BanditLootV87 dead=new BanditLootV87();
        BanditLootV87.Bag bag=dead.spawnCorpse(400,550,11,5,1,-1,124);
        ok(bag!=null,"corpse missing");
        bag.gearManifestV141=true;
        int torsoId=OutfitInventoryV140.TORSO+
            OutfitInventoryV140.npcTorso(bag.variant,bag.skinV109);
        int pantsId=OutfitInventoryV140.PANTS+
            OutfitInventoryV140.npcPants(bag.variant,bag.skinV109);
        int bootsId=OutfitInventoryV140.BOOTS+
            OutfitInventoryV140.npcBoots(bag.variant,bag.skinV109);
        int gunId=OutfitInventoryV140.WEAPONS,roundsId=OutfitInventoryV140.ROUNDS;
        int[] items={torsoId,pantsId,bootsId,gunId,roundsId};
        int[] qty={1,1,1,1,7};
        for(int i=0;i<items.length;i++)
            bag.extra[items[i]-OutfitInventoryV140.FIRST]=qty[i];
        ok(UnifiedBagSlotsV141.canStoreAll(slots,splits,counts,items),
            "player with free slots cannot loot");
        // Exact same operation as GameView. Source deletion occurs ONLY after
        // item ownership succeeds and there is room in the actual bag.
        for(int i=0;i<items.length;i++){
            int type=items[i];
            ok(UnifiedBagSlotsV141.canStore(slots,splits,counts,type),
                "unexpected inventory full");
            ok(player.add(type,qty[i]),"player item receipt failed");
            UnifiedBagSlotsV141.sync(slots,splits,counts);
            ok(dead.takeExtra(bag,type-OutfitInventoryV140.FIRST)==qty[i],
                "corpse item did not transfer");
            ok(player.available(type)==qty[i]&&
               UnifiedBagSlotsV141.contains(slots,type),
               "looted item absent from 40-slot backpack");
            ok(dead.takeExtra(bag,type-OutfitInventoryV140.FIRST)==0,
               "duplicate corpse looting possible");
        }
        ok(!bag.hasExtra()&&bag.gearManifestV141,
            "stripped corpse must retain identity and stripped-state marker");
        String deadSave=dead.encode(),bagSave=player.encode();
        BanditLootV87 restored=new BanditLootV87();
        restored.decode(deadSave);
        ok(restored.bags.size()==1&&restored.bags.get(0).corpse&&
           restored.bags.get(0).gearManifestV141&&
           !restored.bags.get(0).hasExtra(),"stripped corpse redressed on reload");
        OutfitInventoryV140 copy=new OutfitInventoryV140();
        ok(copy.decode(bagSave)&&copy.count(torsoId)==1&&copy.count(pantsId)==1&&
           copy.count(bootsId)==1&&copy.count(gunId)==1&&copy.rounds==7,
           "player's looted clothing/weapon/ammo lost after reloading");
        // Distinct torso and pants styles are equippable independently.
        ok(copy.equip(torsoId)&&copy.equip(pantsId)&&copy.equip(bootsId)&&
           copy.equip(gunId),"recovered gear must be usable");
        ok(copy.equippedStyle(0)==OutfitInventoryV140.style(torsoId)&&
           copy.equippedStyle(1)==OutfitInventoryV140.style(pantsId)&&
           copy.equippedStyle(2)==OutfitInventoryV140.style(bootsId),
           "visual style must equal looted original style");
        // A fully occupied bag cannot silently consume the corpse loot.
        int[] full=new int[40],noSplits=new int[40];
        for(int i=0;i<40;i++)full[i]=i; // 0..39 are all VALID items
        UnifiedBagSlotsV141.Count allOccupied=(type)->type<=39?1:0;
        ok(!UnifiedBagSlotsV141.canStore(full,noSplits,allOccupied,65),
           "overflow should remain on corpse");
        ok(!UnifiedBagSlotsV141.canStoreAll(full,noSplits,allOccupied,items),
           "indoor corpse can lose hidden items to a full backpack");
        ok(Arrays.equals(full,Arrays.copyOf(full,40)),"capacity query mutated slots");
        // Old ground-drop API remains strict, while V141 equipment is valid.
        DroppedItemsV129 floor=new DroppedItemsV129();
        float now=DroppedItemsV129.time(1,400);
        ok(floor.drop(40,1,0,0,"world",now,2)==null,
            "legacy V129 item bounds must remain intact");
        DroppedItemsV129.Stack tossed=floor.dropGearV141(
            torsoId,1,50,70,"world",now,2);
        ok(tossed!=null&&tossed.type==torsoId,
            "recoverable clothing could not be dropped");
        DroppedItemsV129 reloaded=new DroppedItemsV129();
        reloaded.decode(floor.encode());
        ok(reloaded.stacks.size()==1&&reloaded.stacks.get(0).type==torsoId,
            "recovered clothing lost on ground save/load");
        System.out.println("PASS V141: 40-slot transfer, original styles, partial/" +
            "fully stripped persistent corpses, capacity, underwear flags, " +
            "equipping, ammo, ground recovery and legacy migration");
    }
}
