package com.survivalparadise.nativegame;

/** V95: visible, draggable and saved gear stacks. No hidden SEARCH GEAR action.
 * The 15 item codes match the existing three backpacks and 12 clothing variants.
 * Every case's contents are deterministic; only transferred stacks are marked claimed.
 */
public final class GearLootV95 {
    public static final int FIRST=BanditLootV87.ITEMS;
    public static final int TYPES=15;
    public static final int TOTAL=FIRST+TYPES;
    public static final String[] NAMES={
        "DAYPACK","HIKING PACK","TACTICAL PACK",
        "CAP","FIELD HAT","TACTICAL HELMET",
        "WORK JACKET","TRAVEL COAT","BODY ARMOR",
        "CARGO PANTS","FIELD TROUSERS","ARMORED PANTS",
        "WORK BOOTS","HIKING BOOTS","TACTICAL BOOTS"
    };
    private final boolean[][][] claimed=new boolean[64][14][TYPES];
    public void clear(){
        for(boolean[][] site:claimed)
            for(boolean[] box:site)java.util.Arrays.fill(box,false);
    }
    public static int[] lootTypes(int site,int box){
        int first=Math.floorMod(site*5+box*11+2,TYPES);
        int second=box%6==1?Math.floorMod(first+6,TYPES):-1;
        return new int[]{first,second};
    }
    public boolean available(int site,int box,int type,boolean searchedV91){
        if(searchedV91||site<0||site>=claimed.length||
            box<0||box>=14||type<0||type>=TYPES||claimed[site][box][type])
            return false;
        int[] possible=lootTypes(site,box);
        return type==possible[0]||type==possible[1];
    }
    public boolean hasLoot(int site,int box,boolean searchedV91){
        for(int i=0;i<TYPES;i++)if(available(site,box,i,searchedV91))return true;
        return false;
    }
    public boolean transfer(int site,int box,int type,boolean searchedV91,
            FieldFindsV91 bags,WardrobeV92 clothes){
        if(!available(site,box,type,searchedV91))return false;
        if(type<3)bags.bags[type]=Math.min(99,bags.bags[type]+1);
        else {
            int slot=(type-3)/3,variant=(type-3)%3;
            clothes.found[slot][variant]=Math.min(99,clothes.found[slot][variant]+1);
        }
        claimed[site][box][type]=true;
        return true;
    }
    public String encode(){
        StringBuilder b=new StringBuilder("1|");
        for(int i=0;i<claimed.length;i++)
            for(int j=0;j<claimed[i].length;j++)
                for(int k=0;k<TYPES;k++)
                    if(claimed[i][j][k])b.append(i).append(':').append(j)
                        .append(':').append(k).append(',');
        return b.toString();
    }
    public void decode(String src){
        clear();
        if(src==null||!src.startsWith("1|"))return;
        for(String bit:src.substring(2).split(",")){
            String[] a=bit.split(":");
            if(a.length!=3)continue;
            try{
                int site=Integer.parseInt(a[0]),box=Integer.parseInt(a[1]),
                    type=Integer.parseInt(a[2]);
                if(site>=0&&site<64&&box>=0&&box<14&&type>=0&&type<TYPES)
                    claimed[site][box][type]=true;
            }catch(NumberFormatException ignored){}
        }
    }
}
