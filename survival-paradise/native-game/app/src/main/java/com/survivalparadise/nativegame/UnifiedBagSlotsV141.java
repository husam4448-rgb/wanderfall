package com.survivalparadise.nativegame;

/**
 * V141: the existing forty backpack cells are the single visible inventory for
 * legacy items AND the V140 recovered equipment (IDs 39..96). Empty slots use
 * 97, which is never an item. No item ownership is stored in slot order.
 * Old 24/40-cell V92 saves are converted when loaded; ownership stays in the
 * original versioned inventories.
 */
public final class UnifiedBagSlotsV141 {
    private UnifiedBagSlotsV141(){}
    public static final int EMPTY=OutfitInventoryV140.TOTAL;
    public static final int MAX_TYPES=EMPTY;

    public interface Count { int available(int type); }

    public static boolean valid(int type){
        return type>=0&&type<MAX_TYPES;
    }

    public static boolean contains(int[] slots,int type){
        if(!valid(type))return false;
        for(int s:slots)if(s==type)return true;
        return false;
    }

    private static int emptySlot(int[] slots,int[] splits,Count counts){
        for(int i=0;i<slots.length;i++){
            if(splits[i]!=0)continue;
            int old=slots[i];
            if(old==EMPTY||!valid(old)||counts.available(old)<=0)return i;
        }
        return -1;
    }
    /** If full, reject the corpse transfer before removing any source item. */
    public static boolean canStore(int[] slots,int[] splits,Count counts,int type){
        return valid(type)&&
            (contains(slots,type)||emptySlot(slots,splits,counts)>=0);
    }

    /**
     * Expose owned but unlisted stacks in the same real backpack grid.
     * Never touch positive split stacks or overwrite any occupied item.
     * Returns number of newly exposed item types.
     */
    public static int sync(int[] slots,int[] splits,Count counts){
        int exposed=0;
        for(int type=0;type<MAX_TYPES;type++){
            if(counts.available(type)<=0||contains(slots,type))continue;
            int position=emptySlot(slots,splits,counts);
            if(position<0)break;
            slots[position]=type;
            exposed++;
        }
        return exposed;
    }

    /** Convert V92's reserved index 39 from EMPTY to the new sentinel 97. */
    public static void migrateLegacyOrder(int[] slots){
        for(int i=0;i<slots.length;i++)
            if(slots[i]==39)slots[i]=EMPTY;
    }
    /** Never write new item IDs into the legacy V92 save field. */
    public static String legacyOrder(int[] slots){
        boolean[] seen=new boolean[40];int[] old=new int[40];int count=0;
        for(int slot:slots)if(slot>=0&&slot<39&&!seen[slot]){
            old[count++]=slot;seen[slot]=true;
        }
        for(int i=0;i<40;i++)if(!seen[i])old[count++]=i;
        StringBuilder out=new StringBuilder();
        for(int i=0;i<old.length;i++){
            if(i>0)out.append(',');
            out.append(old[i]);
        }
        return out.toString();
    }
}
