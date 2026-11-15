package com.survivalparadise.nativegame;

import java.util.Arrays;

/** Separate, persistent ammunition families. Stable inventory IDs 98..103;
 * ID 97 remains the V141 empty-backpack sentinel. Legacy ID 96 stays usable.
 */
public final class AmmoInventoryV143 {
    public static final int FIRST=98,COUNT=6,TOTAL=FIRST+COUNT;
    public static final int HANDGUN=FIRST,SMG=FIRST+1,
        RIFLE=FIRST+2,SHOTGUN=FIRST+3,
        PRECISION=FIRST+4,GRENADE=FIRST+5;
    public static final String[] NAMES={
        "HANDGUN ROUNDS","SMG ROUNDS","RIFLE ROUNDS",
        "SHOTGUN SHELLS","PRECISION ROUNDS","GRENADE CARTRIDGES"};
    private final int[] qty=new int[COUNT];
    public static boolean valid(int type){return type>=FIRST&&type<TOTAL;}
    public static int forGun(int gun){
        switch(gun){
            case 0:case 1:return HANDGUN;
            case 2:return SMG;
            case 4:case 5:case 6:case 9:return RIFLE;
            case 7:return SHOTGUN;
            case 8:return PRECISION;
            case 10:return GRENADE;
            default:return -1;
        }
    }
    public static String name(int type){return valid(type)?NAMES[type-FIRST]:"";}
    public int count(int type){return valid(type)?qty[type-FIRST]:0;}
    public boolean add(int type,int n){
        if(!valid(type)||n<1||n>9999-qty[type-FIRST])return false;
        qty[type-FIRST]+=n;return true;
    }
    public boolean remove(int type,int n){
        if(!valid(type)||n<1||qty[type-FIRST]<n)return false;
        qty[type-FIRST]-=n;return true;
    }
    public int consumeForGun(int gun,int maximum){
        int type=forGun(gun);
        if(type<0||maximum<1)return 0;
        int n=Math.min(maximum,qty[type-FIRST]);
        qty[type-FIRST]-=n;return n;
    }
    public String encode(){
        StringBuilder b=new StringBuilder("1");
        for(int v:qty)b.append(',').append(v);
        return b.toString();
    }
    public boolean decode(String data){
        if(data==null)return false;
        String[] p=data.split(",",-1);
        if(p.length!=COUNT+1||!"1".equals(p[0]))return false;
        int[] next=new int[COUNT];
        try{
            for(int i=0;i<COUNT;i++){
                int n=Integer.parseInt(p[i+1]);
                if(n<0||n>9999)return false;
                next[i]=n;
            }
        }catch(NumberFormatException ignored){return false;}
        System.arraycopy(next,0,qty,0,COUNT);return true;
    }
    public void clear(){Arrays.fill(qty,0);}
}
