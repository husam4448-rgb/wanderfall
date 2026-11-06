package com.survivalparadise.nativegame;

/** Pure immutable inventory metadata shared by sorted bag, loot and item details.
 * Mass units follow the original encumbrance system (inventory load units).
 */
public final class InventoryCatalogV131 {
    private InventoryCatalogV131(){}
    public static final int COUNT=39;
    public static final float[] WEIGHT={
        .8f,7f,5f,1.7f,2f,.6f,1.8f,.3f,
        6f,4.5f,7f,11f,.5f,1.3f,
        .5f,.8f,.35f,.55f,1.4f,.75f,.25f,2.2f,.6f,1.5f,
        1.2f,2.4f,4f,.3f,.65f,1.8f,2.1f,2.8f,7f,
        1.25f,1.5f,3.4f,1.3f,1.6f,2.6f
    };
    /** Families: medical, food, crafting, supplies, packs, head, torso, legs, feet. */
    public static int category(int type){
        if(type<0||type>=COUNT)return 99;
        if(type==1||type==12||type==17)return 0;
        if(type==3||type==4||type==13)return 1;
        if(type==0||type==5||type==6||type==7||
           (type>=8&&type<=11))return 2;
        if(type==2||(type>=14&&type<=23))return 3;
        if(type<27)return 4;
        return 5+(type-27)/3;
    }
    /** Clothing and bags map to the eight equipment sockets in the UI. */
    public static int equipmentSlot(int type){
        if(type<24||type>=COUNT)return -1;
        if(type<27)return 5; // back
        if(type<30)return 0; // head
        if(type<33)return 2; // torso
        if(type<36)return 3; // legs
        return 4; // feet
    }
    public static boolean compatible(int type,int slot){
        return equipmentSlot(type)==slot;
    }
    public static float weight(int type){
        return type<0||type>=COUNT?0f:WEIGHT[type];
    }
    public static int compare(int left,int right,int mode,String[] names){
        if(left==right)return 0;
        int result=0;
        switch(mode){
            case 1:result=Integer.compare(category(left),category(right));break;
            case 2:result=Float.compare(weight(right),weight(left));break;
            case 3:result=names[left].compareToIgnoreCase(names[right]);break;
            default:break;
        }
        if(result!=0)return result;
        if(mode==1||mode==2)
            return names[left].compareToIgnoreCase(names[right]);
        return Integer.compare(left,right);
    }
    public static String massLabel(int type,int quantity){
        float value=weight(type)*Math.max(0,quantity);
        if(Math.abs(value-Math.round(value))<.005f)
            return Integer.toString(Math.round(value));
        return String.format(java.util.Locale.US,"%.2f",value);
    }
}
