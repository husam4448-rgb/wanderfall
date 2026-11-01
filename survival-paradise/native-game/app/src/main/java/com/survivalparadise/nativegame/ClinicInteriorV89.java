package com.survivalparadise.nativegame;

/**
 * Standalone, streaming-free indoor scene. The outdoors remains in its original
 * world coordinates and is never re-generated when this scene is loaded.
 * All geometry uses logical world pixels; only container contents are mutable.
 */
public final class ClinicInteriorV89 {
    public static final int WIDTH=1600,HEIGHT=1120;
    public static final float ENTRANCE_X=800f,ENTRANCE_Y=1034f;
    public static final float EXIT_X=800f,EXIT_Y=1072f;
    public static final float USE_RADIUS=122f;
    public static final String[] ROOMS={"TRIAGE","OPERATING THEATRE",
        "DIAGNOSTICS LAB","PHARMACY","RECEPTION","RECOVERY WARD"};
    // Buildings are proper rooms separated by a central horizontal corridor.
    // All six doors are explicit gaps in the corridor-facing walls.
    public static final float[][] WALLS={
        {0,0,1600,23},{0,0,22,1120},{1578,0,22,1120},
        {0,1095,755,25},{845,1095,755,25},
        {22,23,1556,21},{22,1070,1556,23},
        {530,44,21,444},{1050,44,21,444}, // top room partitions
        {530,642,21,428},{1050,642,21,428}, // bottom rooms
        {22,486,225,22},{335,486,445,22},{870,486,445,22},
        {1405,486,173,22}, // top doors centered on room portions
        {22,620,225,22},{335,620,445,22},{870,620,445,22},
        {1405,620,173,22}, // bottom doors centered
        // Entrance gap under reception: replace lower interior wall with doorway.
    };
    /** kind 0 beds; 1 cabinets; 2 desks; 3 tables; 4 equipment; 5 lockers. */
    public static final float[][] FURNITURE={
        {0,95,104,84,165},{0,205,104,84,165},{0,315,104,84,165},
        {1,68,324,90,46},{2,350,324,120,65},
        {3,665,153,225,105},{4,980,108,47,150},
        {1,620,361,114,58},{4,900,360,82,55},
        {2,1190,105,170,75},{4,1415,112,65,115},
        {3,1210,306,198,70},{5,1483,328,70,110},
        {1,65,701,110,53},{1,225,701,110,53},{1,390,701,110,53},
        {5,82,895,87,122},{5,208,895,87,122},
        {2,678,705,198,78},{3,636,920,115,61},
        {3,874,917,107,61},{1,947,722,60,93},
        {0,1130,721,84,170},{0,1250,721,84,170},
        {0,1370,721,84,170},{2,1130,961,124,64},
        {1,1450,956,88,68},
        // Central corridor props along wall edges, not obstructing central path.
        {5,66,532,82,64},{1,1425,536,102,55}
    };
    public static final float[][] DOOR_SIGNS={
        {286,476},{827,476},{1350,476},{286,642},{827,642},{1350,642}
    };
    public static final float[][] ROOM_LABELS={
        {126,77},{652,77},{1200,77},{134,678},{684,678},{1215,678}
    };
    public static final class Storage {
        public final float x,y;public final String label;public final int[] amount=new int[8];
        Storage(float x,float y,String label,int[] items){
            this.x=x;this.y=y;this.label=label;
            System.arraycopy(items,0,amount,0,8);
        }
        public boolean empty(){for(int n:amount)if(n>0)return false;return true;}
        public int total(){int n=0;for(int q:amount)n+=q;return n;}
    }
    private static final float[] CACHE_X={111,243,418,678,835,1261,1464,
        121,283,429,976,1150,1480,1472};
    private static final float[] CACHE_Y={351,346,358,390,392,353,385,
        741,743,746,755,964,976,182};
    public static final String[] CACHE_NAMES={"TRIAGE CART","MEDICAL CABINET",
        "NURSE STATION","OPERATING LOCKER","STERILE SUPPLIES",
        "LAB CHEMICALS","LAB FREEZER","PHARMACY SHELF",
        "DRUG CABINET","BACKSTOCK","RECEPTION DRAWER",
        "WARD SUPPLIES","LINEN CABINET","DIAGNOSTICS LOCKER"};
    public final Storage[] storages=new Storage[CACHE_NAMES.length];
    public ClinicInteriorV89(){reset();}
    public void reset(){
        for(int i=0;i<storages.length;i++){
            int[] v=new int[8];
            // Index 0=SCRAP, 1=MEDKIT, 2=AMMO, 3=FOOD, 4=WATER,
            // 5=WOOD, 6=STONE, 7=FIBER. Consumable supplies prevail.
            v[1]=1+((i%4)==0?2:((i%3)==0?1:0));
            v[4]=i%3==0?2:0;
            v[3]=i%5==0?2:0;
            v[0]=i%2==0?2:1;
            v[2]=i%6==0?1:0;
            v[7]=i%7==0?1:0;
            storages[i]=new Storage(CACHE_X[i],CACHE_Y[i],CACHE_NAMES[i],v);
        }
    }
    public boolean blocked(float x,float y,float r){
        if(x-r<23||x+r>1577||y-r<23||y+r>1095)return true;
        for(float[] q:WALLS)
            if(x+r>q[0]&&x-r<q[0]+q[2]&&
               y+r>q[1]&&y-r<q[1]+q[3])return true;
        for(float[] q:FURNITURE)
            if(x+r>q[1]+4&&x-r<q[1]+q[3]-4&&
               y+r>q[2]+4&&y-r<q[2]+q[4]-4)return true;
        return false;
    }
    public Storage nearest(float x,float y,float reach){
        float best=reach*reach;Storage result=null;
        for(Storage s:storages){
            if(s.empty())continue;
            float dx=x-s.x,dy=y-s.y,d=dx*dx+dy*dy;
            if(d<=best){best=d;result=s;}
        }
        return result;
    }
    public boolean contains(Storage s){
        if(s==null)return false;
        for(Storage q:storages)if(q==s)return true;
        return false;
    }
    public int take(Storage s,int type){
        if(!contains(s)||type<0||type>=8)return 0;
        int count=s.amount[type];s.amount[type]=0;return count;
    }
    public int[] takeAll(Storage s){
        int[] out=new int[8];if(!contains(s))return out;
        System.arraycopy(s.amount,0,out,0,8);
        java.util.Arrays.fill(s.amount,0);return out;
    }
    public String encode(){
        StringBuilder b=new StringBuilder(storages.length*29);
        for(int i=0;i<storages.length;i++){
            if(i>0)b.append(';');
            for(int n=0;n<8;n++){
                if(n>0)b.append(',');
                b.append(storages[i].amount[n]);
            }
        }
        return b.toString();
    }
    public void decode(String data){
        reset();if(data==null||data.length()==0)return;
        String[] containers=data.split(";",-1);
        if(containers.length!=storages.length)return;
        int[][] decoded=new int[storages.length][8];
        for(int i=0;i<containers.length;i++){
            String[] counts=containers[i].split(",",-1);
            if(counts.length!=8)return;
            for(int j=0;j<8;j++){
                try{
                    int n=Integer.parseInt(counts[j]);
                    if(n<0||n>999)return;
                    decoded[i][j]=n;
                }catch(NumberFormatException ex){return;}
            }
        }
        for(int i=0;i<storages.length;i++)
            System.arraycopy(decoded[i],0,storages[i].amount,0,8);
    }
}
