package com.survivalparadise.nativegame;

/** Pure Java regression: bonuses are actual gameplay formulas, not UI labels. */
public final class GearStatsV162Test {
    private static void yes(boolean ok,String message){
        if(!ok)throw new AssertionError(message);
    }
    private static void near(float actual,float expected,float eps,String message){
        yes(Math.abs(actual-expected)<=eps,
            message+": "+actual+" != "+expected);
    }
    public static void main(String[] args){
        int count=0,armorTypes=0;
        for(int t=27;t<OutfitInventoryV140.WEAPONS;t++){
            if(!GearStatsV162.isWearable(t))continue;
            yes(GearStatsV162.armor(t)>=0&&GearStatsV162.armor(t)<=30,
                "Invalid gear armor "+t);
            yes(GearStatsV162.agility(t)>=-10&&GearStatsV162.agility(t)<=10,
                "Invalid gear agility "+t);
            if(GearStatsV162.armor(t)>0)armorTypes++;
            count++;
        }
        yes(count==12+OutfitInventoryV140.WEAPONS-OutfitInventoryV140.TORSO,
            "Missing item stat types");
        yes(armorTypes==count,"Wearable without armor");
        GearStatsV162.Bonus armored=GearStatsV162.total(29,
            OutfitInventoryV140.TORSO+6,
            OutfitInventoryV140.PANTS+6,
            OutfitInventoryV140.BOOTS+1);
        yes(armored.armor>20,"Equipped heavy armor did not stack");
        yes(armored.agility<0,"Heavy kit should slow movement");
        near(GearStatsV162.damageAfterArmor(100f,armored),
            100f-armored.armor,.001f,"Damage/armor mismatch");
        near(GearStatsV162.movementFactor(armored),
            1f+armored.agility/100f,.001f,"Agility/speed mismatch");
        GearStatsV162.Bonus medic=GearStatsV162.total(-1,
            OutfitInventoryV140.TORSO+8,-1,-1);
        yes(medic.regenHpPerSecond>.07f,"Medical gear has no HP regeneration");
        near(GearStatsV162.encumbrance(90,0),85f,.01f,"Baseline encumbrance");
        near(GearStatsV162.encumbrance(90,40),17f,.01f,"Tactical backpack encumbrance");
        near(GearStatsV162.backpackReductionPercent(90,40),80f,.01f,
            "Backpack percent reduction");
        near(GearStatsV162.backpackReductionPercent(35,40),0f,.01f,
            "No carried overload must yield zero encumbrance reduction");
        yes(!GearStatsV162.isWearable(OutfitInventoryV140.WEAPONS),
            "Firearm must not get a clothing buff");
        System.out.println("PASS V162: "+count+" distinct wearable item IDs, armor, agility, regen, backpacks");
    }
}
