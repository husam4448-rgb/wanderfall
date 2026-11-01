package com.survivalparadise.nativegame;

public final class V91WorldGearTest {
    private static void check(boolean ok,String reason){
        if(!ok)throw new AssertionError(reason);
    }
    public static void main(String[] args){
        check(ExpeditionSitesV88.SITES.length>=22,"expanded facility count");
        check(ExpeditionSitesV88.SITES[1].kind==ExpeditionSitesV88.CLINIC,
            "V90 original clinic index remains stable");
        FieldFindsV91 gear=new FieldFindsV91();
        int successes=0;
        for(int i=0;i<ExpeditionSitesV88.SITES.length;i++){
            ClinicInteriorV89 map=i==1?new ClinicInteriorV89():
                new ExpeditionInteriorV91(ExpeditionSitesV88.SITES[i]);
            check(map.storages.length==14,"all buildings have 14 searchable boxes");
            check(!map.blocked(ClinicInteriorV89.ENTRANCE_X,
                ClinicInteriorV89.ENTRANCE_Y,19f),"building entry clear");
            check(!map.blocked(ClinicInteriorV89.EXIT_X,
                ClinicInteriorV89.EXIT_Y,17f),"building exit clear");
            String special=gear.scavenge(i,1);
            check(special.contains("FOUND"),"bag in each building's container");
            check(gear.scavenge(i,1).isEmpty(),"no duplicate pickup");
            successes++;
            if(i!=1){
                ExpeditionInteriorV91 other=(ExpeditionInteriorV91)map;
                check(!other.roomNames()[0].isEmpty(),"authored room labels");
                int before=other.storages[0].amount[0];
                String save=other.encode();
                ExpeditionInteriorV91 restore=new ExpeditionInteriorV91(
                    ExpeditionSitesV88.SITES[i]);
                restore.decode(save);
                check(restore.storages[0].amount[0]==before,"persistent site supplies");
                check(!restore.storages[0].label.isEmpty(),"site-specific container label");
            }
        }
        gear.equip(1);
        check(gear.capacity()==63,"hiking pack load capacity");
        String saved=gear.encode();
        FieldFindsV91 restored=new FieldFindsV91();
        restored.decode(saved);
        check(restored.capacity()==63&&restored.searched(3,1),
            "bag and searched cache survive reload");
        check(restored.scavenge(3,1).isEmpty(),"cache cannot reroll");
        check(restored.items[0]>=0,"additional item counters");
        System.out.println("V91 PASS: "+successes+" enterable facilities, persistent cases, bags and new items.");
    }
}