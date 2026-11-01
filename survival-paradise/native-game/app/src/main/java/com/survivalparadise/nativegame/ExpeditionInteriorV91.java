package com.survivalparadise.nativegame;

/** Distinct themed room-map variant sharing V90 indoor physics, vision and AI. */
public final class ExpeditionInteriorV91 extends ClinicInteriorV89 {
    private final float[][] walls,furniture;
    private final String[] labels;
    private final String title;
    public final int kind;
    public ExpeditionInteriorV91(ExpeditionSitesV88.Site site){
        super();
        kind=site.kind;title=site.name;
        walls=new float[WALLS.length][];
        for(int i=0;i<WALLS.length;i++)walls[i]=WALLS[i].clone();
        furniture=new float[FURNITURE.length][];
        for(int i=0;i<FURNITURE.length;i++){
            furniture[i]=FURNITURE[i].clone();
            // Different site-specific furnishings, preserving physical door gaps.
            furniture[i][0]=Math.floorMod((int)FURNITURE[i][0]+kind+(i%3),6);
        }
        labels=roomLabels(kind);
        String[] boxNames={"LOCKER","WORKBENCH","DRAWER","CRATE","SHELF","CABINET",
            "STORAGE BIN","TOOLBOX","EQUIPMENT CASE","SUPPLY BOX","STORAGE TRUNK",
            "UTILITY DRAWER","METAL CHEST","BACKROOM CASE"};
        for(int i=0;i<storages.length;i++){
            int[] loot=new int[8];
            loot[0]=1+Math.floorMod(kind+i,4);
            loot[1]=i%8==0?1:0;
            loot[2]=(kind==ExpeditionSitesV88.CHECKPOINT||kind==ExpeditionSitesV88.RELAY)&&i%4==0?2:0;
            loot[3]=i%5==0?1:0;
            loot[4]=i%6==0?1:0;
            loot[5]=i%3==0?2:0;
            loot[6]=i%4==0?1:0;
            loot[7]=i%2==0?2:0;
            storages[i]=new Storage(storages[i].x,storages[i].y,
                boxNames[i],loot);
        }
    }
    public String siteName(){return title;}
    public String[] roomNames(){return labels;}
    public float[][] sceneWalls(){return walls;}
    public float[][] sceneFurniture(){return furniture;}
    private static String[] roomLabels(int k){
        switch(k){
            case ExpeditionSitesV88.CABIN:
                return new String[]{"KITCHEN","SLEEPING QUARTERS","PANTRY","COMMON ROOM","STORAGE","BUNK ROOM"};
            case ExpeditionSitesV88.GARAGE:
            case ExpeditionSitesV88.WORKSHOP:
                return new String[]{"WORK BAY","PARTS STORAGE","ENGINE SHOP","OFFICE","TOOL LOCKERS","SCRAP ROOM"};
            case ExpeditionSitesV88.RELAY:
            case ExpeditionSitesV88.TOWER:
                return new String[]{"RADIO ROOM","POWER CONTROL","MAINTENANCE","OPERATOR","CABLE STORAGE","REST QUARTERS"};
            case ExpeditionSitesV88.FARM:
                return new String[]{"KITCHEN","SEED STORAGE","WORK ROOM","LIVING AREA","FEED ROOM","UTILITY"};
            case ExpeditionSitesV88.CHECKPOINT:
                return new String[]{"GUARD ROOM","ARMORY","SECURITY","OFFICE","EQUIPMENT","BUNKHOUSE"};
            case ExpeditionSitesV88.MOTEL:
                return new String[]{"ROOM A","ROOM B","RECEPTION","ROOM C","LINEN ROOM","ROOM D"};
            default:
                return new String[]{"STORAGE","OFFICE","WORK ROOM","BACKROOM","UTILITY","REST AREA"};
        }
    }
    @Override public boolean blocked(float x,float y,float r){
        if(x-r<23*EXPANSION_V90||x+r>1577*EXPANSION_V90||
           y-r<23*EXPANSION_V90||y+r>1095*EXPANSION_V90)return true;
        for(float[] q:walls)if(x+r>q[0]&&x-r<q[0]+q[2]&&
            y+r>q[1]&&y-r<q[1]+q[3])return true;
        for(float[] q:furniture)if(x+r>q[1]+4&&x-r<q[1]+q[3]-4&&
            y+r>q[2]+4&&y-r<q[2]+q[4]-4)return true;
        return false;
    }
}