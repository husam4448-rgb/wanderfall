package com.survivalparadise.nativegame;

import java.util.HashSet;

/** V84 repeatable deterministic world scrap sources, independently depleted. */
public final class SalvageWorldV84 {
    public static final int CELL=512,SLOTS=2,CAR=0,PILE=1,BARRELS=2;
    public static final float REACH=140f;
    private final HashSet<Long> depleted=new HashSet<>();
    public static final class Node {
        public final int cx,cy,slot,type,seed;
        public final float x,y;
        Node(int cx,int cy,int slot,int type,int seed,float x,float y){
            this.cx=cx;this.cy=cy;this.slot=slot;this.type=type;this.seed=seed;
            this.x=x;this.y=y;
        }
        public int quantity(){return type==CAR?5:type==PILE?3:2;}
        public String name(){return type==CAR?"RUSTED CAR":type==PILE?"SCRAP PILE":"RUSTED BARRELS";}
    }
    private static long key(int cx,int cy,int slot){
        return WorldChunkModel.chunkKey(cx*2+slot,cy);
    }
    public static int seed(int cx,int cy,int slot){
        return WorldChunkModel.hash(cx*19+slot*53+61,cy*29+slot*31-23);
    }
    public static float x(int cx,int seed){return cx*CELL+64+Math.floorMod(seed,CELL-128);}
    public static float y(int cy,int seed){return cy*CELL+64+Math.floorMod(seed>>>11,CELL-128);}
    public static boolean placed(float x,float y,int seed,
                                 float campX,float campY,float worldW,float worldH){
        float dx=x-campX,dy=y-campY,d2=dx*dx+dy*dy;
        if(d2<420f*420f)return false;
        if(x>=0&&x<=worldW&&y>=0&&y<=worldH){
            return d2<1800f*1800f && Math.floorMod(seed,3)!=0 &&
                 !(y>912&&y<1160)&&!(x>1480&&x<1740);
        }
        return Math.floorMod(seed,4)!=0;
    }
    public static Node node(int cx,int cy,int slot,float campX,float campY,float ww,float wh){
        if(slot<0||slot>=SLOTS)return null;
        int seed=seed(cx,cy,slot);float x=x(cx,seed),y=y(cy,seed);
        if(!placed(x,y,seed,campX,campY,ww,wh))return null;
        return new Node(cx,cy,slot,Math.floorMod(seed,3),seed,x,y);
    }
    public boolean exhausted(int cx,int cy,int slot){return depleted.contains(key(cx,cy,slot));}
    public boolean harvest(Node n){
        return n!=null&&depleted.add(key(n.cx,n.cy,n.slot));
    }
    public void clear(){depleted.clear();}
    public int depletedCount(){return depleted.size();}
    public String encode(){
        StringBuilder b=new StringBuilder(depleted.size()*23);
        for(long key:depleted){
            if(b.length()>0)b.append(';');
            b.append((int)(key>>32)).append(',').append((int)key);
        }
        return b.toString();
    }
    public void decode(String data){
        clear();if(data==null||data.isEmpty())return;
        for(String item:data.split(";")){
            String[] p=item.split(",");if(p.length!=2)continue;
            try{
                int x=Integer.parseInt(p[0]),y=Integer.parseInt(p[1]);
                depleted.add(WorldChunkModel.chunkKey(x,y));
            }catch(NumberFormatException ignored){}
        }
    }
    public Node nearest(float px,float py,float range,float campX,float campY,float ww,float wh){
        float best=range*range;Node result=null;
        int x0=(int)Math.floor((px-range)/CELL)-1,x1=(int)Math.floor((px+range)/CELL)+1;
        int y0=(int)Math.floor((py-range)/CELL)-1,y1=(int)Math.floor((py+range)/CELL)+1;
        for(int cy=y0;cy<=y1;cy++)for(int cx=x0;cx<=x1;cx++)for(int k=0;k<SLOTS;k++){
            if(exhausted(cx,cy,k))continue;
            int seed=seed(cx,cy,k);float x=x(cx,seed),y=y(cy,seed);
            if(!placed(x,y,seed,campX,campY,ww,wh))continue;
            float dx=x-px,dy=y-py,d2=dx*dx+dy*dy;
            if(d2<=best){best=d2;result=new Node(cx,cy,k,Math.floorMod(seed,3),seed,x,y);}
        }
        return result;
    }
}
