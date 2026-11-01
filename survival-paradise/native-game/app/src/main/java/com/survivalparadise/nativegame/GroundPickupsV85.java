package com.survivalparadise.nativegame;
import java.util.HashSet;

/** Tiny independently persistent loose items, no resource/tool animation needed. */
public final class GroundPickupsV85 {
    public static final int CELL=164,SLOTS=3,STONE=0,WOOD=1,SCRAP=2;
    public static final float REACH=98f;
    private final HashSet<Long> taken=new HashSet<>();
    public static final class Item {
        public final int cx,cy,slot,seed;
        public final float x,y;
        Item(int cx,int cy,int slot,int seed,float x,float y){
            this.cx=cx;this.cy=cy;this.slot=slot;this.seed=seed;this.x=x;this.y=y;
        }
        public int quantity(){return slot==STONE?1:slot==WOOD?2:1;}
        public String label(){return slot==STONE?"STONE":slot==WOOD?"WOOD":"SCRAP";}
    }
    static long key(int cx,int cy,int slot){
        return WorldChunkModel.chunkKey(cx*4+slot,cy);
    }
    public static int seed(int cx,int cy,int slot){
        return WorldChunkModel.hash(cx*17+slot*43+2,cy*29-slot*11-71);
    }
    public static float worldX(int cx,int seed){return cx*CELL+25+Math.floorMod(seed,CELL-50);}
    public static float worldY(int cy,int seed){return cy*CELL+25+Math.floorMod(seed>>>9,CELL-50);}
    public static boolean placed(int slot,int seed,float x,float y,
                                 float campX,float campY){
        float dx=x-campX,dy=y-campY,d2=dx*dx+dy*dy;
        if(d2<145f*145f)return false; // preserve camp center and NPCs
        if(Math.floorMod(seed,slot==STONE?3:slot==WOOD?5:7)!=0)return false;
        if(y>912&&y<1160||x>1480&&x<1740)return false;
        return true;
    }
    public static Item item(int cx,int cy,int slot,float campX,float campY){
        if(slot<0||slot>=SLOTS)return null;
        int seed=seed(cx,cy,slot);
        float x=worldX(cx,seed),y=worldY(cy,seed);
        if(!placed(slot,seed,x,y,campX,campY))return null;
        return new Item(cx,cy,slot,seed,x,y);
    }
    public boolean collected(int cx,int cy,int slot){return taken.contains(key(cx,cy,slot));}
    public boolean collect(Item item){return item!=null&&taken.add(key(item.cx,item.cy,item.slot));}
    public int collectedCount(){return taken.size();}
    public void clear(){taken.clear();}
    public String encode(){
        StringBuilder b=new StringBuilder(taken.size()*25);
        for(long key:taken){if(b.length()>0)b.append(';');
            b.append((int)(key>>32)).append(',').append((int)key);
        }
        return b.toString();
    }
    public void decode(String text){
        clear();if(text==null||text.isEmpty())return;
        for(String pair:text.split(";")){
            String[] p=pair.split(",");if(p.length!=2)continue;
            try{taken.add(WorldChunkModel.chunkKey(
                Integer.parseInt(p[0]),Integer.parseInt(p[1])));
            }catch(NumberFormatException ignored){}
        }
    }
    public Item nearest(float px,float py,float reach,float campX,float campY){
        float best=reach*reach;Item out=null;
        int x0=(int)Math.floor((px-reach)/CELL)-1,x1=(int)Math.floor((px+reach)/CELL)+1;
        int y0=(int)Math.floor((py-reach)/CELL)-1,y1=(int)Math.floor((py+reach)/CELL)+1;
        for(int cy=y0;cy<=y1;cy++)for(int cx=x0;cx<=x1;cx++)
        for(int slot=0;slot<SLOTS;slot++){
            if(collected(cx,cy,slot))continue;
            int seed=seed(cx,cy,slot);
            float x=worldX(cx,seed),y=worldY(cy,seed);
            if(!placed(slot,seed,x,y,campX,campY))continue;
            float dx=x-px,dy=y-py,d2=dx*dx+dy*dy;
            if(d2<=best){best=d2;out=new Item(cx,cy,slot,seed,x,y);}
        }
        return out;
    }
}
