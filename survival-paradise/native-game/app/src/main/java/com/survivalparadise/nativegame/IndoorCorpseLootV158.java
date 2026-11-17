package com.survivalparadise.nativegame;

/**
 * Persistent indoor corpse inventories, separated by building/industrial
 * district. Uses the exact same V87/V141/V143 bag encoding and inventory
 * type IDs as outdoor corpses; actor index + 1 is the stable corpse ID.
 * No global/outdoor bags are spawned at indoor coordinates.
 */
public final class IndoorCorpseLootV158 {
    final BanditLootV87 stock=new BanditLootV87();

    public void clear(){stock.clear();}
    public String encode(){return stock.encode();}
    public void decode(String text){
        stock.decode(text);
        // Never accept an outdoor cache or a duplicate/unrelated actor in
        // this per-interior stream.
        for(int i=stock.bags.size()-1;i>=0;i--){
            BanditLootV87.Bag b=stock.bags.get(i);
            if(!b.corpse||b.id<1||b.id>8)
                stock.bags.remove(i);
        }
    }
    public BanditLootV87.Bag get(int actorIndex){
        if(actorIndex<0||actorIndex>=8)return null;
        for(BanditLootV87.Bag b:stock.bags)
            if(b.id==actorIndex+1)return b;
        return null;
    }
    /** Initialize once, on first examination. Never reroll a partially
     * looted body; legacy one-click-searched corpses stay permanently empty.
     */
    public BanditLootV87.Bag ensure(int actorIndex,ClinicActorsV90.Actor actor,
                                    int appearance,int skin,long pocketIron,
                                    boolean legacySearched){
        if(actor==null||actor.active||actorIndex<0||actorIndex>=8)return null;
        BanditLootV87.Bag old=get(actorIndex);
        if(old!=null)return old;
        BanditLootV87.Bag b=new BanditLootV87.Bag(
            actorIndex+1,actor.x,actor.y);
        b.corpse=true;
        b.gearManifestV141=true;
        b.variant=appearance;
        b.skinV109=skin;
        b.face=(actor.type&1)==0?1:-1;
        if(!legacySearched){
            switch(actor.type){
                case ClinicActorsV90.RAIDER:
                    b.count[BanditLootV87.SCRAP]=2;break;
                case ClinicActorsV90.MEDIC:
                    b.count[BanditLootV87.MEDKIT]=1;
                    b.count[BanditLootV87.WATER]=1;break;
                case ClinicActorsV90.SURVIVOR:
                    b.count[BanditLootV87.FOOD]=1;
                    b.count[BanditLootV87.SCRAP]=1;break;
                case ClinicActorsV90.ZOMBIE:
                    b.count[BanditLootV87.SCRAP]=1;break;
                default:break;
            }
            if(actor.type!=ClinicActorsV90.FERAL){
                if(skin>=1&&skin<=200){
                    b.extra[OutfitInventoryV140.TORSO+
                        OutfitInventoryV140.npcTorso(appearance,skin)-
                        OutfitInventoryV140.FIRST]=1;
                    b.extra[OutfitInventoryV140.PANTS+
                        OutfitInventoryV140.npcPants(appearance,skin)-
                        OutfitInventoryV140.FIRST]=1;
                    b.extra[OutfitInventoryV140.BOOTS+
                        OutfitInventoryV140.npcBoots(appearance,skin)-
                        OutfitInventoryV140.FIRST]=1;
                }
                if(actor.type==ClinicActorsV90.RAIDER&&actor.gun>=0&&actor.gun<12){
                    b.extra[OutfitInventoryV140.WEAPONS+actor.gun-
                        OutfitInventoryV140.FIRST]=1;
                    int ammo=AmmoInventoryV143.forGun(actor.gun);
                    if(ammo>=AmmoInventoryV143.FIRST&&
                       ammo<AmmoInventoryV143.FIRST+AmmoInventoryV143.COUNT)
                        b.ammoExtraV143[ammo-AmmoInventoryV143.FIRST]=
                            Math.max(0,actor.rounds+actor.spareRounds);
                }else if(actor.type==ClinicActorsV90.MEDIC||
                         actor.type==ClinicActorsV90.SURVIVOR){
                    b.extra[OutfitInventoryV140.WEAPONS+3-
                        OutfitInventoryV140.FIRST]=1;
                }
                b.nutsV143=Math.max(0,Math.min(NutWalletV143.MAX,pocketIron));
            }
        }
        stock.bags.add(b);
        return b;
    }
    public boolean hasRemainingGarment(int actorIndex,int inventoryType){
        BanditLootV87.Bag b=get(actorIndex);
        if(b==null)return true; // unseen legacy corpse: default outfit
        int id=inventoryType-OutfitInventoryV140.FIRST;
        return id>=0&&id<b.extra.length&&b.extra[id]>0;
    }
}
