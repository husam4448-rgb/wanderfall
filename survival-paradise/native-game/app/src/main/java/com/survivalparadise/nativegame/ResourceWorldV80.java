package com.survivalparadise.nativegame;

import java.util.HashMap;
import java.util.Map;

/**
 * V80 seeded world resources. Coordinates and depleted flags are independent
 * of the tile bitmap cache: leaving/reentering a chunk never resets gathering.
 * This is a pure-Java model (testable without Android).
 */
public final class ResourceWorldV80 {
    public static final int CELL=288, SLOTS=4, BUSH=7;
    public static final int WOOD=0, STONE=1, FIBER=2;
    public static final float USE_RADIUS=110f;
    private final HashMap<Long,Integer> harvested=new HashMap<>();

    public static final class Node {
        public final int cx,cy,slot,kind,seed;
        public final float x,y;
        Node(int cx,int cy,int slot,int kind,int seed,float x,float y){
            this.cx=cx;this.cy=cy;this.slot=slot;this.kind=kind;
            this.seed=seed;this.x=x;this.y=y;
        }
        public int resource(){return kind==BUSH?FIBER:kind==4?STONE:WOOD;}
        public int quantity(){return resource()==WOOD?3:resource()==STONE?2:2;}
        public String name(){return resource()==FIBER?"FIBER":resource()==STONE?"STONE":"WOOD";}
    }

    public static int seed(int cx,int cy,int slot){
        return slot<3?WorldChunkModel.hash(cx*7+slot,cy*11-slot):
            WorldChunkModel.hash(cx*23+17,cy*37-9);
    }
    public static float worldX(int cx,int seed){
        return cx*CELL+20+Math.floorMod(seed,CELL-40);
    }
    public static float worldY(int cy,int seed){
        return cy*CELL+20+Math.floorMod(seed>>>8,CELL-40);
    }
    public static boolean placed(float x,float y,int slot,int seed,
                                 float campX,float campY,float worldW,float worldH){
        if(y>912&&y<1160 || x>1480&&x<1740)return false; // V74 roads
        double dx=x-campX,dy=y-campY,ds=dx*dx+dy*dy;
        boolean hub=x>=0&&x<=worldW&&y>=0&&y<=worldH;
        if(!hub)return ds>=470f*470f && (slot!=3||Math.floorMod(seed,3)==0);
        // Sparse, testable harvest nodes near the starting camp without
        // repainting the V73 camp itself or flooding authored landmarks.
        return ds>=320f*320f&&ds<=1250f*1250f &&
            Math.floorMod(seed,slot==3?2:4)==0;
    }
    public static Node node(int cx,int cy,int slot,
                            float campX,float campY,float worldW,float worldH){
        if(slot<0||slot>=SLOTS)return null;
        int seed=seed(cx,cy,slot);
        float x=worldX(cx,seed),y=worldY(cy,seed);
        if(!placed(x,y,slot,seed,campX,campY,worldW,worldH))return null;
        int kind=slot==3?BUSH:BiomeWorldV74.prop(x,y,seed);
        return new Node(cx,cy,slot,kind,seed,x,y);
    }
    public boolean exhausted(int cx,int cy,int slot){
        Integer bits=harvested.get(WorldChunkModel.chunkKey(cx,cy));
        return bits!=null&&(bits&(1<<slot))!=0;
    }
    public boolean harvest(Node n){
        if(n==null||exhausted(n.cx,n.cy,n.slot))return false;
        long key=WorldChunkModel.chunkKey(n.cx,n.cy);
        Integer old=harvested.get(key);
        harvested.put(key,(old==null?0:old)|(1<<n.slot));
        return true;
    }
    public void clear(){harvested.clear();}
    public int depletedCells(){return harvested.size();}
    public int depletedNodes(){
        int n=0;for(Integer mask:harvested.values())n+=Integer.bitCount(mask);return n;
    }
    /** Stable sparse save: one entry per modified 288px resource cell. */
    public String encode(){
        StringBuilder b=new StringBuilder(harvested.size()*20);
        for(Map.Entry<Long,Integer> entry:harvested.entrySet()){
            long key=entry.getKey();
            b.append((int)(key>>32)).append(',')
                .append((int)key).append(',')
                .append(entry.getValue()).append(';');
        }
        return b.toString();
    }
    public void decode(String saved){
        harvested.clear();
        if(saved==null||saved.isEmpty())return;
        int cursor=0;
        while(cursor<saved.length()){
            int end=saved.indexOf(';',cursor);
            if(end<0)end=saved.length();
            int a=saved.indexOf(',',cursor);
            int b=a<0?-1:saved.indexOf(',',a+1);
            if(a>cursor&&b>a&&b<end){
                try{
                    int cx=Integer.parseInt(saved.substring(cursor,a));
                    int cy=Integer.parseInt(saved.substring(a+1,b));
                    int mask=Integer.parseInt(saved.substring(b+1,end));
                    if(mask>0&&mask<16)
                        harvested.put(WorldChunkModel.chunkKey(cx,cy),mask);
                }catch(NumberFormatException ignored){/* ignore damaged entry */}
            }
            cursor=end+1;
        }
    }
    public Node nearest(float px,float py,float radius,
                        float campX,float campY,float worldW,float worldH){
        float best2=radius*radius;
        Node closest=null;
        int x0=(int)Math.floor((px-radius)/CELL)-1;
        int x1=(int)Math.floor((px+radius)/CELL)+1;
        int y0=(int)Math.floor((py-radius)/CELL)-1;
        int y1=(int)Math.floor((py+radius)/CELL)+1;
        for(int cy=y0;cy<=y1;cy++)for(int cx=x0;cx<=x1;cx++)
            for(int slot=0;slot<SLOTS;slot++){
                if(exhausted(cx,cy,slot))continue;
                int h=seed(cx,cy,slot);
                float x=worldX(cx,h),y=worldY(cy,h);
                if(!placed(x,y,slot,h,campX,campY,worldW,worldH))continue;
                float dx=x-px,dy=y-py,ds=dx*dx+dy*dy;
                if(ds<=best2){
                    best2=ds;
                    int kind=slot==3?BUSH:BiomeWorldV74.prop(x,y,h);
                    closest=new Node(cx,cy,slot,kind,h,x,y);
                }
            }
        return closest;
    }
}
