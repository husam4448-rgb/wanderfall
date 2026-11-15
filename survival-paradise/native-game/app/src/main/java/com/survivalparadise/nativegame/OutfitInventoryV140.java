package com.survivalparadise.nativegame;

import java.util.Arrays;

/**
 * V140 additive wearable/weapon inventory. Legacy 0..38 item IDs, the V92
 * wardrobe and its save format, backpack slots, and the original art remain
 * untouched. IDs 39..96 are stable and independently lootable.
 */
public final class OutfitInventoryV140 {
    public static final int FIRST=39,STYLES=20,TORSO=FIRST,
        PANTS=TORSO+STYLES,BOOTS=PANTS+STYLES,
        WEAPONS=BOOTS+5,ROUNDS=WEAPONS+12,TOTAL=ROUNDS+1,
        COUNT=TOTAL-FIRST;
    public static final String[] STYLE_NAMES={
        "T-Shirt","Hoodie","Jacket","Denim","Flannel",
        "Tactical Vest","Armor","Hazmat","Medical","Workwear",
        "Military","Desert","Snow","Forest","Urban",
        "Leather","Winter","Survivor","Ranger","Civilian"
    };
    public static final String[] WEAPON_NAMES={
        "Pistol","Revolver","UZI","Flashlight","Tactical Carbine",
        "AK Rifle","Bullpup","Pump Shotgun","Sniper Rifle","LMG",
        "Grenade Launcher","Red Axe"
    };
    private final int[] owned=new int[COUNT];
    // 0 torso, 1 pants, 2 boots, 3 held weapon. -1 means legacy/default.
    private final int[] equipped={-1,-1,-1,-1};
    public int rounds=0;

    public static boolean valid(int type){return type>=FIRST&&type<TOTAL;}
    public static int slot(int type){
        return type>=TORSO&&type<PANTS?0:
            type>=PANTS&&type<BOOTS?1:
            type>=BOOTS&&type<WEAPONS?2:
            type>=WEAPONS&&type<ROUNDS?3:-1;
    }
    public static int style(int type){
        int slot=slot(type);
        return slot==0?type-TORSO:slot==1?type-PANTS:
            slot==2?type-BOOTS:slot==3?type-WEAPONS:-1;
    }
    public static String name(int type){
        if(type==ROUNDS)return "LOOSE AMMO ROUNDS";
        int slot=slot(type),id=style(type);
        if(slot==0)return STYLE_NAMES[id]+" TORSO";
        if(slot==1)return STYLE_NAMES[id]+" PANTS";
        if(slot==2)return new String[]{"Classic Brown Boots","Combat Boots",
            "Desert Boots","Reinforced Work Boots","Trail Boots"}[id];
        if(slot==3)return WEAPON_NAMES[id];
        return "";
    }
    public static float weight(int type){
        int slot=slot(type);
        return slot==0?2f:slot==1?1.5f:slot==2?2.2f:
            slot==3?3f:type==ROUNDS?.025f:0f;
    }
    public static int npcTorso(int variant,int skin){
        return Math.floorMod(Math.max(0,variant)*7+skin*3,STYLES);
    }
    public static int npcPants(int variant,int skin){
        return Math.floorMod(Math.max(0,variant)*11+skin*7,STYLES);
    }
    public static int npcBoots(int variant,int skin){
        return Math.floorMod(variant*3+skin,5);
    }

    public int count(int type){
        return type==ROUNDS?rounds:valid(type)?owned[type-FIRST]:0;
    }
    public int available(int type){
        if(!valid(type))return 0;
        int reserved=0;
        int sl=slot(type);
        if(sl>=0&&equipped[sl]==type)reserved=1;
        return Math.max(0,count(type)-reserved);
    }
    public boolean add(int type,int quantity){
        if(!valid(type)||quantity<1)return false;
        int now=count(type);
        if(quantity>9999-now)return false;
        if(type==ROUNDS)rounds+=quantity;
        else owned[type-FIRST]+=quantity;
        return true;
    }
    public boolean remove(int type,int quantity){
        if(!valid(type)||quantity<1||available(type)<quantity)return false;
        if(type==ROUNDS)rounds-=quantity;
        else owned[type-FIRST]-=quantity;
        return true;
    }
    public boolean equip(int type){
        int sl=slot(type);
        if(sl<0||count(type)<1)return false;
        equipped[sl]=type;
        return true;
    }
    public boolean unequip(int sl){
        if(sl<0||sl>=equipped.length)return false;
        equipped[sl]=-1;return true;
    }
    public int equippedType(int sl){
        return sl>=0&&sl<equipped.length?equipped[sl]:-1;
    }
    public int equippedStyle(int sl){return style(equippedType(sl));}
    public void clear(){
        Arrays.fill(owned,0);Arrays.fill(equipped,-1);rounds=0;
    }

    /** One-time, non-destructive migration of already equipped legacy looks. */
    public void migrate(int torsoStyle,int pantStyle,int bootStyle,int weapon,
                        boolean hasTorso,boolean hasPants,boolean hasBoots){
        clear();
        if(hasTorso){int t=TORSO+Math.floorMod(torsoStyle,STYLES);add(t,1);equip(t);}
        if(hasPants){int t=PANTS+Math.floorMod(pantStyle,STYLES);add(t,1);equip(t);}
        if(hasBoots){int t=BOOTS+Math.floorMod(bootStyle,5);add(t,1);equip(t);}
        int w=WEAPONS+Math.floorMod(weapon,12);
        add(w,1);equip(w);
    }

    /** A versioned independent save field; never rewrites legacy inventory data. */
    public String encode(){
        StringBuilder s=new StringBuilder("1|");
        for(int i=0;i<equipped.length;i++){
            if(i>0)s.append(',');
            s.append(equipped[i]);
        }
        s.append('|').append(rounds).append('|');
        for(int i=0;i<owned.length;i++){
            if(i>0)s.append(',');
            s.append(owned[i]);
        }
        return s.toString();
    }
    public boolean decode(String data){
        if(data==null||data.isEmpty())return false;
        String[] p=data.split("\\|",-1);
        if(p.length!=4||!"1".equals(p[0]))return false;
        String[] eq=p[1].split(","),list=p[3].split(",");
        if(eq.length!=4||list.length!=COUNT)return false;
        try{
            int[] next=new int[COUNT],nextEq=new int[4];
            int nextRounds=Integer.parseInt(p[2]);
            if(nextRounds<0||nextRounds>9999)return false;
            for(int i=0;i<COUNT;i++){
                int n=Integer.parseInt(list[i]);
                if(n<0||n>9999)return false;
                next[i]=n;
            }
            for(int i=0;i<4;i++){
                int t=Integer.parseInt(eq[i]);
                if(t!=-1&&(slot(t)!=i||next[t-FIRST]<1))return false;
                nextEq[i]=t;
            }
            System.arraycopy(next,0,owned,0,COUNT);
            System.arraycopy(nextEq,0,equipped,0,4);
            rounds=nextRounds;
            return true;
        }catch(NumberFormatException ignored){return false;}
    }
}
