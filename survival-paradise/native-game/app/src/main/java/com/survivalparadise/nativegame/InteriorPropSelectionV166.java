package com.survivalparadise.nativegame;

/**
 * Deterministic V166 art lookup: 16 original furniture silhouettes plus
 * 16 dedicated interiors, mapped through one stable 0..63 sprite vocabulary.
 * Physical coordinates, saves and collisions remain owned by V163.
 */
public final class InteriorPropSelectionV166 {
    private InteriorPropSelectionV166(){}
    public static final int CELL=256,COLS=4,ROWS=4,SPRITES=160;
    public static int choose(int theme,int type,int index,float width,float height){
        // V166 semantic direct-sprite role; older 0..5 lookup remains stable.
        if(type>=16&&type<16+SPRITES)return type-16;
        if(theme<0||theme>=NeighborhoodV154.TYPES)return -1;
        float aspect=width/Math.max(1f,height);
        int variant;
        switch(theme){
            case NeighborhoodV154.APARTMENTS:
                variant=type==0?0:1;break; // bed or wood cabinet
            case NeighborhoodV154.OFFICES:
                variant=aspect>1.17f?0:1;break; // workstation or files
            case NeighborhoodV154.MARKET:
                variant=aspect>1.17f?1:0;break; // store shelf or checkout
            case NeighborhoodV154.HOTEL:
                variant=(type==0||index%4==0)?0:1;break;
            case NeighborhoodV154.SCHOOL:
                variant=(type==2&&index%3!=0)?0:1;break;
            case NeighborhoodV154.FACTORY:
                variant=index%3==0?0:1;break; // motor/control or racks
            case NeighborhoodV154.WAREHOUSE:
                variant=index%3==0?0:1;break; // pallet or shelving
            default:
                variant=(type==3||index%3==0)?0:1;break;
        }
        return theme*2+variant;
    }
    public static boolean valid(int sprite){
        return sprite>=0&&sprite<SPRITES;
    }
}
