package com.survivalparadise.nativegame;

import java.util.HashSet;

/** Real seeded placement, rich finite economy and persistent accessible cache. */
public final class V164SettlementCampTest {
    static void yes(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    static void near(float a,float b,String why){
        yes(Math.abs(a-b)<.01f,why+": "+a+" vs "+b);
    }
    public static void main(String[] args){
        int camps=0,rural=0,urban=0,occupiedVacantParks=0;
        for(int seed:new int[]{14901,87011,23147,64320}){
            WorldGeographyV160 geo=WorldGeographyV160.prepare(seed,null);
            WorldCivilizationV159.Plan city=WorldCivilizationV159.generate(seed,null,geo);
            occupiedVacantParks+=0; // city vacancy counts tested below
            CampWorldV164.Site[] world=CampWorldV164.generate(seed,city);
            CampWorldV164.Site[] repeat=CampWorldV164.generate(seed,city);
            yes(world.length==repeat.length,"Camps regenerated at different count");
            yes(world.length>1,"No generated camps for seed "+seed);
            yes(world[0].starter,"Original survivor camp was relocated");
            near(world[0].x,1080,"Original camp X changed");
            near(world[0].y,710,"Original camp Y changed");
            int availableLots=0;
            for(WorldCivilizationV159.Parcel parcel:city.parcels)
                for(int slot=0;slot<NeighborhoodV154.COLS*NeighborhoodV154.ROWS;slot++)
                    if(NeighborhoodV154.get(parcel.tx,parcel.ty,slot,city)==null)
                        availableLots++;
            yes(availableLots>0,"City lacks public green space");
            occupiedVacantParks+=availableLots;
            HashSet<String> ids=new HashSet<>();
            for(int i=0;i<world.length;i++){
                CampWorldV164.Site s=world[i],again=repeat[i];
                near(s.x,again.x,"Deterministic camp X");
                near(s.y,again.y,"Deterministic camp Y");
                yes(s.id.equals(again.id),"Camp ID drift");
                yes(ids.add(s.saveId()),"Duplicate camp storage save ID");
                if(s.starter)continue;
                camps++;
                if(s.urban){
                    urban++;
                    yes(city.developed(s.x,s.y),"City camp not inside developed parcel");
                    yes(s.slot>=0&&NeighborhoodV154.get(
                        s.tx,s.ty,s.slot,city)==null,
                        "City camp overlaps an owned building lot");
                }else{
                    rural++;
                    yes(!city.developed(s.x,s.y),
                        "Wilderness camp placed inside city");
                }
                yes(!WorldBuildingV157.sceneryBlocked(s.x,s.y,410f,seed,city),
                    "Camp intersects roof or protected landmark");
                for(int role=0;role<CampWorldV164.ROLES;role++){
                    yes(Float.isFinite(s.npcX(role))&&Float.isFinite(s.npcY(role)),
                        "Missing role anchor");
                    float dist=(float)Math.hypot(s.npcX(role)-s.chestX(),
                        s.npcY(role)-s.chestY());
                    yes(dist>66f,"NPC spawned inside storage chest");
                }
            }
            CampCacheV164 cache=new CampCacheV164(world);
            CampWorldV164.Site selected=world[1];
            for(int type=0;type<CampCacheV164.COUNT;type++)
                yes(cache.count(selected,type)>0,
                    "Camp has no supplies or backpacks type "+type);
            int old=cache.count(selected,9);
            yes(cache.take(selected,9)==old&&cache.count(selected,9)==0,
                "Backpack taken twice");
            CampCacheV164 reloaded=new CampCacheV164(world);
            reloaded.decode(cache.encode());
            yes(reloaded.count(selected,9)==0,
                "Backpack reappears after loading");
            yes(cache.encode().equals(reloaded.encode()),
                "Camp stock changed on reload");
            yes(CampWorldV164.nearbyChest(world,selected.chestX(),
                selected.chestY(),120f)==selected,"Chest cannot be searched");
        }
        yes(rural>=8,"Too few wilderness survivor camps: "+rural);
        yes(rural>=urban*3,"Urban camps outnumber the countryside preference: rural="+rural+" urban="+urban);
        yes(occupiedVacantParks>=12,"Not enough green city lots");
        NpcTradeLedgerV143 traderLedger=new NpcTradeLedgerV143();
        NpcTradeLedgerV143.Npc trader=traderLedger.get("camp164:site14901_0:0",0);
        yes(trader!=null&&trader.wallet.iron()>=80000,
            "Trader cannot afford a player's sale");
        int stockTypes=0;
        for(int i=0;i<NpcTradeLedgerV143.ITEM_TYPES;i++)
            if(trader.count(i)>0)stockTypes++;
        yes(stockTypes>=28,"Trader only offers "+stockTypes+" item types");
        for(int backpack=24;backpack<=26;backpack++)
            yes(trader.count(backpack)>0,"Missing backpack for sale");
        int bought=trader.count(3);
        NpcTradeLedgerV143.Npc reopened=traderLedger.get(
            "camp164:site14901_0:0",0);
        yes(reopened==trader&&reopened.count(3)==bought,
            "Trader restocked on repeated interaction");
        String state=traderLedger.encode();
        NpcTradeLedgerV143 saved=new NpcTradeLedgerV143();
        yes(saved.decode(state),"New trader save does not decode");
        NpcTradeLedgerV143.Npc restored=saved.get("camp164:site14901_0:0",0);
        yes(restored!=null&&restored.count(3)==bought&&
            restored.wallet.iron()==trader.wallet.iron(),
            "Trader reloaded changed inventory or wallet");
        // Legacy 1-format must migrate without deleting previously sold goods.
        NpcTradeLedgerV143 old=new NpcTradeLedgerV143();
        yes(old.decode("1;camp:0_124|0|713|3:1"),
            "Cannot open old V143 trader save");
        NpcTradeLedgerV143.Npc upgrade=old.get("camp:0_124",0);
        yes(upgrade!=null&&upgrade.count(3)>=1&&
            upgrade.wallet.iron()>=80000,
            "Old trader failed single safe expansion");
        String migrated=old.encode();
        NpcTradeLedgerV143 migratedLedger=new NpcTradeLedgerV143();
        yes(migratedLedger.decode(migrated),"V164 upgraded NPC save not parseable");
        yes(migratedLedger.get("camp:0_124",0).count(3)==upgrade.count(3),
            "Trader restocked unexpectedly after migration save");
        System.out.println("PASS V164: "+camps+" nonstarter camps, "+
            rural+" rural and "+urban+" city vacant lots, "+
            occupiedVacantParks+" grass parks, all roles, backpacks, "+
            stockTypes+" trader SKUs, stable legacy/new NPC and chest saves");
    }
}
