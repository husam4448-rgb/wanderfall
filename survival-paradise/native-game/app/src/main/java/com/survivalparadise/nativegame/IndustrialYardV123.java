package com.survivalparadise.nativegame;

import java.util.HashSet;

/** Sparse seed-scoped salvage persistence independent of chunk cache eviction. */
public final class IndustrialYardV123 {
    public static final float REACH=124f;
    public static final class Stock {
        public final IndustrialWorldV123.District district;
        public final int slot;
        public final float x,y;
        Stock(IndustrialWorldV123.District d,int slot){
            this.district=d;this.slot=slot;
            x=d.materialX(slot);y=d.materialY(slot);
        }
        public int quantity(){return district.materialQuantity(slot);}
        public String name(){return IndustrialWorldV123.MATERIALS[slot];}
        public String key(){return district.sx+":"+district.sy+":"+slot;}
    }
    private final HashSet<String> collected=new HashSet<>();
    public void clear(){collected.clear();}
    public boolean exhausted(Stock s){return s==null||collected.contains(s.key());}
    public boolean collect(Stock s){return s!=null&&collected.add(s.key());}
    public Stock nearest(float px,float py,int seed){
        Stock result=null;float best=REACH*REACH;
        int sx=IndustrialWorldV123.sector(px),sy=IndustrialWorldV123.sector(py);
        for(int y=sy-1;y<=sy+1;y++)for(int x=sx-1;x<=sx+1;x++){
            IndustrialWorldV123.District d=IndustrialWorldV123.district(x,y,seed);
            for(int i=0;i<IndustrialWorldV123.MATERIALS.length;i++){
                Stock stock=new Stock(d,i);
                if(exhausted(stock))continue;
                float dx=px-stock.x,dy=py-stock.y,dist=dx*dx+dy*dy;
                if(dist<=best){best=dist;result=stock;}
            }
        }
        return result;
    }
    public String encode(){
        StringBuilder out=new StringBuilder();
        java.util.ArrayList<String> keys=new java.util.ArrayList<>(collected);
        java.util.Collections.sort(keys);
        for(String key:keys)out.append(key).append(';');
        return out.toString();
    }
    public void decode(String value){
        clear();if(value==null||value.isEmpty())return;
        for(String token:value.split(";")){
            if(token.isEmpty())continue;
            String[] pair=token.split(":",-1);
            if(pair.length!=3)continue;
            try{
                int x=Integer.parseInt(pair[0]),y=Integer.parseInt(pair[1]);
                int slot=Integer.parseInt(pair[2]);
                if(slot>=0&&slot<IndustrialWorldV123.MATERIALS.length)
                    collected.add(x+":"+y+":"+slot);
            }catch(NumberFormatException ignored){}
        }
    }
}
