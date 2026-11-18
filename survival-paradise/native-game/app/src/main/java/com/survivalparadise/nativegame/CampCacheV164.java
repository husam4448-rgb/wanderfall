package com.survivalparadise.nativegame;

import java.util.LinkedHashMap;

/** Fixed physical camp chests, with durable independent eight-item inventories. */
public final class CampCacheV164 {
    private static final int COUNT=BanditLootV87.ITEMS;
    private final LinkedHashMap<String,int[]> contents=new LinkedHashMap<>();
    public CampCacheV164(CampWorldV164.Site[] camps){
        for(CampWorldV164.Site s:camps){
            int h=IndustrialWorldV123.hash(s.tx*47+s.slot,
                s.ty*71+s.variation,s.seed^0x164BA8);
            int[] quantities={
                3+Math.floorMod(h,9),1+Math.floorMod(h>>>4,3),
                2+Math.floorMod(h>>>6,4),2+Math.floorMod(h>>>8,4),
                2+Math.floorMod(h>>>10,5),2+Math.floorMod(h>>>13,7),
                1+Math.floorMod(h>>>17,4),2+Math.floorMod(h>>>21,6)};
            contents.put(s.saveId(),quantities);
        }
    }
    public int count(CampWorldV164.Site site,int type){
        int[] items=site==null?null:contents.get(site.saveId());
        return items==null||type<0||type>=COUNT?0:items[type];
    }
    public int take(CampWorldV164.Site site,int type){
        if(site==null||type<0||type>=COUNT)return 0;
        int[] items=contents.get(site.saveId());
        if(items==null)return 0;
        int amount=items[type];items[type]=0;return amount;
    }
    public boolean empty(CampWorldV164.Site site){
        for(int i=0;i<COUNT;i++)if(count(site,i)>0)return false;
        return true;
    }
    public String encode(){
        StringBuilder result=new StringBuilder("1");
        for(java.util.Map.Entry<String,int[]> e:contents.entrySet()){
            result.append(';').append(e.getKey()).append('=');
            for(int i=0;i<COUNT;i++){
                if(i>0)result.append(',');
                result.append(e.getValue()[i]);
            }
        }
        return result.toString();
    }
    /** Saved stock by stable camp ID. Unknown/removed camps are harmless. */
    public void decode(String data){
        if(data==null||!data.startsWith("1;")||data.length()>40000)return;
        for(String entry:data.substring(2).split(";")){
            int pivot=entry.indexOf('=');
            if(pivot<1)continue;
            int[] existing=contents.get(entry.substring(0,pivot));
            if(existing==null)continue;
            String[] cells=entry.substring(pivot+1).split(",",-1);
            if(cells.length!=COUNT)continue;
            int[] next=new int[COUNT];boolean valid=true;
            for(int i=0;i<COUNT;i++){
                try{
                    next[i]=Integer.parseInt(cells[i]);
                    if(next[i]<0||next[i]>999){valid=false;break;}
                }catch(NumberFormatException ex){valid=false;break;}
            }
            if(valid)System.arraycopy(next,0,existing,0,COUNT);
        }
    }
}
