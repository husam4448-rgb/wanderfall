package com.survivalparadise.nativegame;

/** Stable actual gun type for each NPC, never a cosmetic pistol fallback.
 * Melee and flashlight are excluded from hostile firearm assignment.
 */
public final class NpcGearV143 {
    private static final int[] BANDIT={0,1,2,4,5,6,7,8,9};
    private static final int[] INDOOR={0,2,4,5,7,8};
    private NpcGearV143(){}
    public static int banditGun(int variant,int skin){
        return BANDIT[Math.floorMod(skin*17+variant*7,BANDIT.length)];
    }
    public static int indoorRaiderGun(int index,int skin){
        return INDOOR[Math.floorMod(index*5+skin,INDOOR.length)];
    }
    public static final int[] MAGAZINE={12,6,28,1,30,30,28,6,5,75,8,1};
    public static int magazine(int weapon){
        return weapon>=0&&weapon<MAGAZINE.length?MAGAZINE[weapon]:0;
    }
    public static int ammoType(int weapon){
        return AmmoInventoryV143.forGun(weapon);
    }
    public static int[] ammo(int weapon,int magazine){
        int mag=Math.max(1,magazine);
        int spare=Math.max(mag,Math.min(4*mag,mag*(2+(weapon%3))));
        return new int[]{mag,spare};
    }
    public static int pocketIron(int variant,int skin,int level){
        return 6+Math.floorMod(variant*31+skin*7+level*19,250);
    }
    /** Distinct caliber/shell labels for the corresponding weapon. */
    public static String ammoName(int gun){
        switch(gun){
            case 0:case 1:return "Handgun rounds";
            case 2:return "SMG rounds";
            case 4:case 5:case 6:case 9:return "Rifle rounds";
            case 7:return "Shotgun shells";
            case 8:return "Precision rifle rounds";
            case 10:return "Grenade cartridges";
            default:return "No firearm ammo";
        }
    }
}
