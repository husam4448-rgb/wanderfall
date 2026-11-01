package com.survivalparadise.nativegame;
/** Modular clothing overlays. All original character sprite pixels stay immutable. */
public final class WardrobeV92 {
    public static final String[] SLOTS={"HEAD","TORSO","LEGS","BOOTS"};
    public static final String[][] NAMES={
        {"CAP","FIELD HAT","TACTICAL HELMET"},
        {"WORK JACKET","TRAVEL COAT","BODY ARMOR"},
        {"CARGO PANTS","FIELD TROUSERS","ARMORED PANTS"},
        {"WORK BOOTS","HIKING BOOTS","TACTICAL BOOTS"}
    };
    public final int[][] found=new int[4][3];
    public final int[] equipped={-1,-1,-1,-1};
    public void clear(){
        for(int[] slot:found)java.util.Arrays.fill(slot,0);
        java.util.Arrays.fill(equipped,-1);
    }
    public boolean equip(int slot,int variant){
        if(slot<0||slot>=4)return false;
        if(variant<0){equipped[slot]=-1;return true;}
        if(variant>=3||found[slot][variant]<1)return false;
        equipped[slot]=variant;return true;
    }
    public String scavenge(int site,int box){
        // Clothes from some of the cases, including the starting field clinic.
        if(box%3!=0)return "";
        int slot=Math.floorMod(site+box/3,4);
        int variant=Math.floorMod(site*3+box/3,3);
        found[slot][variant]=Math.min(99,found[slot][variant]+1);
        return NAMES[slot][variant];
    }
    public static int npcOutfit(int npc,int slot){
        return Math.floorMod(npc*7+slot*5+4,3);
    }
    public String encode(){
        StringBuilder b=new StringBuilder();
        for(int i=0;i<4;i++){
            if(i>0)b.append(';');
            b.append(equipped[i]);
            for(int j=0;j<3;j++)b.append(',').append(found[i][j]);
        }
        return b.toString();
    }
    public void decode(String src){
        clear();if(src==null||src.isEmpty())return;
        try{
            String[] rows=src.split(";",-1);
            if(rows.length!=4)return;
            for(int i=0;i<4;i++){
                String[] p=rows[i].split(",",-1);if(p.length!=4){clear();return;}
                int chosen=Integer.parseInt(p[0]);
                for(int j=0;j<3;j++)found[i][j]=Math.max(0,Math.min(99,Integer.parseInt(p[j+1])));
                equipped[i]=chosen>=0&&chosen<3&&found[i][chosen]>0?chosen:-1;
            }
        }catch(NumberFormatException ignored){clear();}
    }
}