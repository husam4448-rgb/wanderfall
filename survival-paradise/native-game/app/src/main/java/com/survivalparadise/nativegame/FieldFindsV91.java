package com.survivalparadise.nativegame;

/** Persistent scavenging and wearable carry gear. No procedural rerolls on re-entry. */
public final class FieldFindsV91 {
    public static final String[] NAMES={"CLOTH","BATTERY","WIRING","ANTISEPTIC",
        "FUEL","WATER FILTER","SEEDS","TOOLKIT","ROPE","SPARE PARTS"};
    public static final String[] BAGS={"DAYPACK","HIKING BACKPACK","TACTICAL RUCKSACK"};
    public static final int[] CAPACITY_BONUS={10,23,40};
    public final int[] items=new int[NAMES.length],bags=new int[BAGS.length];
    public int equipped=-1;
    private final boolean[][] searched=new boolean[64][ClinicInteriorV89.CACHE_NAMES.length];

    public void clear(){
        java.util.Arrays.fill(items,0);java.util.Arrays.fill(bags,0);
        for(boolean[] s:searched)java.util.Arrays.fill(s,false);
        equipped=-1;
    }
    public int capacity(){return 40+(equipped>=0&&equipped<3?CAPACITY_BONUS[equipped]:0);}
    public float weight(){
        float out=0;
        float[] w={.5f,.8f,.35f,.55f,1.4f,.75f,.25f,2.2f,.6f,1.5f};
        for(int i=0;i<items.length;i++)out+=items[i]*w[i];
        return out;
    }
    public boolean equip(int kind){
        if(kind<0||kind>=3||bags[kind]<1)return false;
        equipped=kind;return true;
    }
    public void unequip(){equipped=-1;}
    public boolean searched(int site,int box){
        return valid(site,box)&&searched[site][box];
    }
    private boolean valid(int site,int box){
        return site>=0&&site<searched.length&&box>=0&&box<searched[0].length;
    }
    /** Searches a physical case once; deterministic by site and case, saved separately. */
    public String scavenge(int site,int box){
        if(!valid(site,box)||searched[site][box])return "";
        searched[site][box]=true;
        int kind=Math.floorMod(site*17+box*7+3,NAMES.length);
        int count=1+Math.floorMod(site+box*3,3);
        items[kind]=Math.min(999,items[kind]+count);
        String result=NAMES[kind]+" +"+count;
        if(box==1||box==5||box==11){
            int bag=Math.floorMod(site+box/5,3);
            bags[bag]=Math.min(99,bags[bag]+1);
            result+="  •  "+BAGS[bag]+" FOUND";
        }
        return result;
    }
    public String encode(){
        StringBuilder b=new StringBuilder("1");
        b.append('|').append(equipped).append('|');
        for(int i=0;i<items.length;i++){if(i>0)b.append(',');b.append(items[i]);}
        b.append('|');
        for(int i=0;i<bags.length;i++){if(i>0)b.append(',');b.append(bags[i]);}
        b.append('|');
        for(int i=0;i<searched.length;i++)for(int j=0;j<searched[i].length;j++)
            if(searched[i][j])b.append(i).append(':').append(j).append(',');
        return b.toString();
    }
    public void decode(String src){
        clear();if(src==null||src.isEmpty())return;
        try{
            String[] p=src.split("\\|",-1);
            if(p.length!=5||!"1".equals(p[0]))return;
            int q=Integer.parseInt(p[1]);
            String[] it=p[2].split(","),ba=p[3].split(",");
            if(it.length!=items.length||ba.length!=bags.length)return;
            for(int i=0;i<items.length;i++)items[i]=Math.max(0,Math.min(999,Integer.parseInt(it[i])));
            for(int i=0;i<bags.length;i++)bags[i]=Math.max(0,Math.min(99,Integer.parseInt(ba[i])));
            equipped=q>=0&&q<bags.length&&bags[q]>0?q:-1;
            for(String bit:p[4].split(",")){
                String[] ij=bit.split(":");
                if(ij.length!=2)continue;
                int i=Integer.parseInt(ij[0]),j=Integer.parseInt(ij[1]);
                if(valid(i,j))searched[i][j]=true;
            }
        }catch(NumberFormatException ex){clear();}
    }
}