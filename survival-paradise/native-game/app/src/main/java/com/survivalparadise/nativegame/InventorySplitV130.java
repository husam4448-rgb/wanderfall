package com.survivalparadise.nativegame;

/**
 * Slot-specific splits overlay the original 40-slot immutable type ordering.
 * Item counters remain the authoritative inventory source; no duplication.
 * All temporary allocations are kept by slot and saved separately.
 */
public final class InventorySplitV130 {
    public static final int SLOTS=40,EMPTY=39;
    public final int[] splitType=new int[SLOTS];
    public final int[] splitCount=new int[SLOTS];
    public InventorySplitV130(){clear();}
    public void clear(){
        java.util.Arrays.fill(splitType,-1);
        java.util.Arrays.fill(splitCount,0);
    }
    public int type(int slot,int[] base){
        if(slot<0||slot>=SLOTS)return EMPTY;
        return splitType[slot]>=0?splitType[slot]:base[slot];
    }
    public void reconcile(int[] base,int[] totals){
        for(int i=0;i<SLOTS;i++)if(splitType[i]>=0){
            int kind=splitType[i];
            if(kind==EMPTY||kind<0||kind>=totals.length||
               totals[base[i]]>0||splitCount[i]<=0){
                splitType[i]=-1;splitCount[i]=0;
            }
        }
        for(int kind=0;kind<EMPTY;kind++){
            int rest=Math.max(0,totals[kind]);
            for(int i=0;i<SLOTS;i++)if(splitType[i]==kind){
                splitCount[i]=Math.min(splitCount[i],rest);
                rest-=splitCount[i];
                if(splitCount[i]<=0)splitType[i]=-1;
            }
        }
    }
    public int count(int slot,int[] base,int[] totals){
        if(slot<0||slot>=SLOTS)return 0;
        int kind=type(slot,base);
        if(kind==EMPTY||kind<0||kind>=totals.length)return 0;
        if(splitType[slot]>=0)return Math.max(0,Math.min(splitCount[slot],totals[kind]));
        int rest=totals[kind];
        for(int i=0;i<SLOTS;i++)if(splitType[i]==kind)
            rest-=splitCount[i];
        return Math.max(0,rest);
    }
    public boolean split(int source,int quantity,int[] base,int[] totals){
        reconcile(base,totals);
        int kind=type(source,base);
        int available=count(source,base,totals);
        if(source<0||source>=SLOTS||kind==EMPTY||available<2||
            quantity<1||quantity>=available)return false;
        int target=-1;
        for(int i=0;i<SLOTS;i++)if(i!=source&&splitType[i]<0&&
                 totals[base[i]]==0&&base[i]!=kind){
            target=i;break;
        }
        if(target<0)return false;
        splitType[target]=kind;splitCount[target]=quantity;
        if(splitType[source]>=0)splitCount[source]-=quantity;
        return true;
    }
    public void consumed(int slot,int amount){
        if(slot>=0&&slot<SLOTS&&splitType[slot]>=0){
            splitCount[slot]=Math.max(0,splitCount[slot]-amount);
            if(splitCount[slot]==0)splitType[slot]=-1;
        }
    }
    public void moved(int source,int dest){
        if(source<0||dest<0||source>=SLOTS||dest>=SLOTS||source==dest)return;
        int t=splitType[source],n=splitCount[source];
        int begin=Math.min(source,dest),amount=Math.abs(source-dest);
        System.arraycopy(splitType,begin+(source<dest?1:0),
            splitType,begin+(source<dest?0:1),amount);
        System.arraycopy(splitCount,begin+(source<dest?1:0),
            splitCount,begin+(source<dest?0:1),amount);
        splitType[dest]=t;splitCount[dest]=n;
    }
    public String encode(){
        StringBuilder b=new StringBuilder();
        for(int i=0;i<SLOTS;i++)if(splitType[i]>=0&&splitCount[i]>0){
            if(b.length()>0)b.append(';');
            b.append(i).append(',').append(splitType[i]).append(',')
                .append(splitCount[i]);
        }
        return b.toString();
    }
    public void decode(String raw,int[] base,int[] totals){
        clear();if(raw==null||raw.isEmpty())return;
        for(String row:raw.split(";")){
            String[] p=row.split(",");if(p.length!=3)continue;
            try{
                int slot=Integer.parseInt(p[0]),kind=Integer.parseInt(p[1]),
                    count=Integer.parseInt(p[2]);
                if(slot<0||slot>=SLOTS||kind<0||kind>=EMPTY||
                   count<=0||count>9999||totals[base[slot]]!=0)continue;
                splitType[slot]=kind;splitCount[slot]=count;
            }catch(NumberFormatException ignored){}
        }
        reconcile(base,totals);
    }
}
