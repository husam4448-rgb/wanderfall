package com.survivalparadise.nativegame;

/**
 * V162 one source of truth for player equipment attributes and inventory UI.
 * All old item IDs and saves remain intact. No headgear is rendered.
 * Armor reduces received damage; agility changes player movement speed;
 * regeneration restores health continuously while alive.
 */
public final class GearStatsV162 {
    private GearStatsV162(){}
    private static final int[] TORSO_ARMOR={
        1,2,4,2,3,8,16,11,3,4,10,7,8,6,6,5,8,5,8,1
    };
    private static final int[] TORSO_AGILITY={
        3,2,1,2,2,0,-5,-4,2,1,-2,0,-1,1,2,1,-2,2,1,3
    };
    private static final int[] PANTS_ARMOR={
        1,1,2,2,2,5,9,7,2,3,6,4,5,4,4,3,5,3,5,1
    };
    private static final int[] PANTS_AGILITY={
        3,2,1,2,2,2,-3,-3,2,2,0,2,1,3,3,1,0,2,2,3
    };
    private static final int[] BOOTS_ARMOR={1,4,2,6,2};
    private static final int[] BOOTS_AGILITY={2,0,2,-2,4};
    private static final int[] LEGACY_ARMOR={
        1,2,13,4,7,19,2,4,9,2,2,5
    };
    private static final int[] LEGACY_AGILITY={
        2,1,-3,1,0,-5,2,3,-1,2,4,0
    };
    private static final float[] TORSO_REGEN={
        0,0,0,0,0,0,0,0,.075f,0,0,0,0,0,0,0,.020f,.030f,.015f,0
    };
    public static boolean isWearable(int type){
        return (type>=27&&type<=38)||
            (type>=OutfitInventoryV140.TORSO&&
             type<OutfitInventoryV140.WEAPONS);
    }
    public static int armor(int type){
        if(type>=27&&type<=38)return LEGACY_ARMOR[type-27];
        if(type>=OutfitInventoryV140.TORSO&&type<OutfitInventoryV140.PANTS)
            return TORSO_ARMOR[type-OutfitInventoryV140.TORSO];
        if(type>=OutfitInventoryV140.PANTS&&type<OutfitInventoryV140.BOOTS)
            return PANTS_ARMOR[type-OutfitInventoryV140.PANTS];
        if(type>=OutfitInventoryV140.BOOTS&&type<OutfitInventoryV140.WEAPONS)
            return BOOTS_ARMOR[type-OutfitInventoryV140.BOOTS];
        return 0;
    }
    public static int agility(int type){
        if(type>=27&&type<=38)return LEGACY_AGILITY[type-27];
        if(type>=OutfitInventoryV140.TORSO&&type<OutfitInventoryV140.PANTS)
            return TORSO_AGILITY[type-OutfitInventoryV140.TORSO];
        if(type>=OutfitInventoryV140.PANTS&&type<OutfitInventoryV140.BOOTS)
            return PANTS_AGILITY[type-OutfitInventoryV140.PANTS];
        if(type>=OutfitInventoryV140.BOOTS&&type<OutfitInventoryV140.WEAPONS)
            return BOOTS_AGILITY[type-OutfitInventoryV140.BOOTS];
        return 0;
    }
    public static float healthRegen(int type){
        if(type>=OutfitInventoryV140.TORSO&&type<OutfitInventoryV140.PANTS)
            return TORSO_REGEN[type-OutfitInventoryV140.TORSO];
        return 0f;
    }
    public static final class Bonus {
        public final int armor,agility;
        public final float regenHpPerSecond;
        public Bonus(int armor,int agility,float regenHpPerSecond){
            this.armor=Math.min(60,Math.max(0,armor));
            this.agility=Math.max(-20,Math.min(20,agility));
            this.regenHpPerSecond=Math.max(0f,Math.min(.25f,regenHpPerSecond));
        }
    }
    public static Bonus total(int head,int torso,int pants,int boots){
        int[] ids={head,torso,pants,boots};
        int armor=0,agility=0;
        float regen=0f;
        for(int type:ids){
            armor+=armor(type);
            agility+=agility(type);
            regen+=healthRegen(type);
        }
        return new Bonus(armor,agility,regen);
    }
    public static float damageAfterArmor(float incoming,Bonus worn){
        return Math.max(0f,incoming)*(1f-worn.armor/100f);
    }
    public static float movementFactor(Bonus worn){
        return 1f+worn.agility/100f;
    }
    public static float encumbrance(float totalLoad,int packCapacityBonus){
        return Math.min(100f,Math.max(0f,
            (totalLoad-(40f+Math.max(0,packCapacityBonus)))*1.7f));
    }
    /** Current carry burden relieved by this backpack, relative to carrying no pack. */
    public static float backpackReductionPercent(float load,int bonus){
        float without=encumbrance(load,0);
        if(without<.001f)return 0f;
        return Math.max(0f,Math.min(100f,100f*
            (without-encumbrance(load,bonus))/without));
    }
}
