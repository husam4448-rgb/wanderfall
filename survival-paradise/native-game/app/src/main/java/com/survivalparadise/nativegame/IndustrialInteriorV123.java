package com.survivalparadise.nativegame;

/** V123 full-scale industrial halls, with actual traversable door gaps and collision. */
public final class IndustrialInteriorV123 extends ClinicInteriorV89 {
    public final IndustrialWorldV123.District district;
    public final float[][] machines;
    // All dimensions remain V90-compatible for its existing camera, AI and ballistics.
    public static final float[][] WALLS = {
        {0,0,2720,35}, {0,0,35,1904}, {2685,0,35,1904},
        {0,1860,1235,44}, {1485,1860,1235,44},
        // Left four-room wing: deliberately broad doors at Y 330, 850 and 1350.
        {510,35,28,280},{510,465,28,345},{510,1030,28,285},{510,1525,28,335},
        // Right four-room wing with identical unobstructed entries.
        {2180,35,28,280},{2180,465,28,345},
        {2180,1030,28,285},{2180,1525,28,335}
    };
    // Floor standing assets, approximate physical collision hulls aligned with art.
    public static final float[][] MACHINES = {
        {650,160,370,315}, {1695,160,370,315},
        {650,1100,380,285}, {1695,1100,380,285},
        {740,615,250,135}, {1720,615,250,135},
        {180,185,200,94},{2340,185,200,94},
        {165,640,220,135},{2330,640,220,135},
        {165,1110,220,160},{2330,1110,220,160},
        {165,1620,220,120},{2330,1620,220,120},
        {760,1600,200,100},{1760,1600,200,100}
    };
    public IndustrialInteriorV123(IndustrialWorldV123.District site) {
        super();
        district=site;
        machines=new float[MACHINES.length][4];
        for(int i=0;i<MACHINES.length;i++){
            System.arraycopy(MACHINES[i],0,machines[i],0,4);
            int shift=IndustrialWorldV123.hash(site.sx+i*19,site.sy-i*7,site.seed);
            machines[i][0]+=(Math.floorMod(shift,5)-2)*9f;
            machines[i][1]+=(Math.floorMod(shift>>>6,5)-2)*7f;
        }
        // All 14 original reusable container slots are retained for V122 loot UI.
        float[][] points={
            {230,345},{230,900},{230,1400},{230,1770},
            {2450,345},{2450,900},{2450,1400},{2450,1770},
            {1150,370},{1580,370},{1150,880},{1580,880},
            {1150,1430},{1580,1430}
        };
        String[] labels={"STEEL LOCKER","GEAR CASE","CASTING PARTS","SCRAP CRATE",
            "POWER CABINET","WIRE SPOOLS","TOOLBOX","SPARES BIN",
            "IRON ROD RACK","ASSEMBLY BOX","COPPER COILS","MACHINE PARTS",
            "METAL STOCK","SUPPLY CHEST"};
        for(int i=0;i<storages.length;i++){
            int[] items=new int[8];
            int h=IndustrialWorldV123.hash(site.sx*17+i,site.sy*31-i,site.seed);
            items[0]=2+Math.floorMod(h,6); // scrap
            items[2]=i%5==0?2:0;items[5]=i%4==0?1:0;
            items[6]=i%3==0?2:0;items[7]=i%6==0?1:0;
            items[3]=i%7==0?2:0;items[4]=i%7==0?2:0;
            storages[i]=new Storage(points[i][0],points[i][1],labels[i],items);
        }
    }
    private static boolean intersects(float x,float y,float r,float[] q) {
        return x+r>q[0] && x-r<q[0]+q[2] && y+r>q[1] && y-r<q[1]+q[3];
    }
    @Override public boolean blocked(float x,float y,float radius){
        for(float[] q:WALLS)if(intersects(x,y,radius,q))return true;
        for(float[] q:machines)if(intersects(x,y,radius,q))return true;
        return false;
    }
    @Override public void decode(String data){
        // Superclass decode calls reset(); that is why we save pre-seeded loot
        // quantities, restore them after decode only when there is no old state.
        if(data==null||data.isEmpty())return;
        String[] rows=data.split(";",-1);
        if(rows.length!=storages.length)return;
        int[][] values=new int[storages.length][8];
        try{
            for(int i=0;i<rows.length;i++){
                String[] numbers=rows[i].split(",",-1);
                if(numbers.length!=8)return;
                for(int j=0;j<8;j++){
                    values[i][j]=Integer.parseInt(numbers[j]);
                    if(values[i][j]<0||values[i][j]>999)return;
                }
            }
            for(int i=0;i<rows.length;i++)
                System.arraycopy(values[i],0,storages[i].amount,0,8);
        }catch(NumberFormatException ignored){}
    }
}
