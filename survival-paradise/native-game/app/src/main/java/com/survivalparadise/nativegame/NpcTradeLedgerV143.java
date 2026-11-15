package com.survivalparadise.nativegame;

import java.util.LinkedHashMap;
import java.util.Map;

/** Deterministic NPC pockets and limited real stocks, persisted by NPC identity.
 * Wallet and stock operate independently of player head/outfit/save formats.
 */
public final class NpcTradeLedgerV143 {
    public static final int ITEM_TYPES=104; // 97 is reserved EMPTY; 98..103 ammo
    public static final int MAX_NPCS=512,MAX_STOCK=9999;
    public interface Inventory {
        int available(int type);
        boolean add(int type,int quantity);
        boolean remove(int type,int quantity);
        boolean capacity(int type);
        /** A destination's stack cap, distinct from free backpack cells. */
        default int maxReceivable(int type){
            return capacity(type)?MAX_STOCK:0;
        }
    }
    public static final class Npc {
        public final String id;
        public final int role;
        public final NutWalletV143 wallet;
        public final int[] stock=new int[ITEM_TYPES];
        private Npc(String id,int role,long iron){
            this.id=id;this.role=role;
            this.wallet=new NutWalletV143(iron);
        }
        public int count(int type){return type>=0&&type<ITEM_TYPES?stock[type]:0;}
    }
    private final LinkedHashMap<String,Npc> byId=new LinkedHashMap<>();
    public Npc find(String id){return byId.get(id);}
    public Npc get(String id,int role){
        if(!validId(id))return null;
        Npc current=byId.get(id);if(current!=null)return current;
        if(byId.size()>=MAX_NPCS)return null;
        int seed=Math.floorMod(id.hashCode()^(role*7477),9997);
        Npc npc=new Npc(id,role,65+seed%3900L);
        // Real finite stock: once bought, the item is no longer for sale.
        npc.stock[0]=3+seed%7; // scrap
        npc.stock[3]=2+seed%5; // food
        npc.stock[4]=2+(seed/3)%5;
        if(role==0||role==1)npc.stock[1]=1+seed%3;
        if(role==1)npc.stock[12]=2+seed%5; // bandages
        if(role==2){
            npc.stock[2]=1+seed%4; // legacy compatibility
            npc.stock[AmmoInventoryV143.RIFLE]=15+seed%30;
            npc.stock[AmmoInventoryV143.HANDGUN]=8+seed%18;
        }
        if(role==3)npc.stock[8]=1+(seed%3);
        if(role==4)npc.stock[7]=4+seed%8; // fiber
        npc.stock[39+Math.floorMod(seed,20)]=1; // one real garment
        npc.stock[79+Math.floorMod(seed,5)]=1; // one real boot design
        byId.put(id,npc);return npc;
    }
    private static boolean validId(String id){
        return id!=null&&id.length()>0&&id.length()<=100&&
            id.indexOf('|')<0&&id.indexOf(';')<0&&id.indexOf(',')<0&&
            id.indexOf(':')>=0;
    }
    public static long price(int type){
        if(type<0||type>=ITEM_TYPES||type==97)return 0;
        if(AmmoInventoryV143.valid(type))
            return type==AmmoInventoryV143.GRENADE?85:
                type==AmmoInventoryV143.SHOTGUN?12:6;
        if(type>=OutfitInventoryV140.WEAPONS&&type<OutfitInventoryV140.ROUNDS)
            return 180+45*(type-OutfitInventoryV140.WEAPONS);
        if(type>=OutfitInventoryV140.BOOTS)return 55;
        if(type>=OutfitInventoryV140.PANTS)return 47;
        if(type>=OutfitInventoryV140.TORSO)return 65;
        if(type>=24)return 70;
        switch(type){
            case 0:return 5;
            case 1:return 90;
            case 2:return 32;
            case 3:case 4:return 12;
            case 12:return 35;
            default:return 10;
        }
    }
    public static long resale(int type){long p=price(type);return p<=0?0:Math.max(1,p*70/100);}
    /** Destination inventory first, then NPC stock and wallets, avoiding
     * deleting an item when no backpack space or insufficient pocket funds.
     */
    public boolean buy(Npc npc,int type,int count,Inventory player,
                       NutWalletV143 money){
        if(npc==null||player==null||money==null||count<1||
           type<0||type>=ITEM_TYPES||type==97||
           npc.stock[type]<count||!player.capacity(type)||
           player.maxReceivable(type)<count)
            return false;
        long unit=price(type),bill=unit*count;
        if(unit<=0||!money.canDebit(bill)||!npc.wallet.canCredit(bill))
            return false;
        if(!player.add(type,count))return false;
        money.debit(bill);
        npc.wallet.credit(bill);
        npc.stock[type]-=count;return true;
    }
    public boolean sell(Npc npc,int type,int count,Inventory player,
                        NutWalletV143 money){
        if(npc==null||player==null||money==null||count<1||
           type<0||type>=ITEM_TYPES||type==97||
           player.available(type)<count||
           npc.stock[type]>MAX_STOCK-count)return false;
        long bill=resale(type)*count;
        if(bill<=0||!npc.wallet.canDebit(bill)||!money.canCredit(bill))
            return false;
        if(!player.remove(type,count))return false;
        npc.stock[type]+=count;
        npc.wallet.debit(bill);money.credit(bill);return true;
    }
    public String encode(){
        StringBuilder b=new StringBuilder("1");
        for(Npc npc:byId.values()){
            b.append(';').append(npc.id).append('|').append(npc.role)
                .append('|').append(npc.wallet.iron()).append('|');
            boolean first=true;
            for(int i=0;i<ITEM_TYPES;i++)if(npc.stock[i]>0){
                if(!first)b.append(',');
                first=false;b.append(i).append(':').append(npc.stock[i]);
            }
        }
        return b.toString();
    }
    public boolean decode(String text){
        if(text==null||text.isEmpty())return false;
        String[] records=text.split(";",-1);
        if(records.length<1||records.length>MAX_NPCS+1||!"1".equals(records[0]))
            return false;
        LinkedHashMap<String,Npc> replacement=new LinkedHashMap<>();
        try{
            for(int i=1;i<records.length;i++){
                String[] p=records[i].split("\\|",-1);
                if(p.length!=4||!validId(p[0])||replacement.containsKey(p[0]))
                    return false;
                int role=Integer.parseInt(p[1]);
                long funds=Long.parseLong(p[2]);
                if(role<0||role>8||funds<0||funds>NutWalletV143.MAX)return false;
                Npc npc=new Npc(p[0],role,funds);
                if(!p[3].isEmpty())for(String entry:p[3].split(",")){
                    String[] cell=entry.split(":");
                    if(cell.length!=2)return false;
                    int type=Integer.parseInt(cell[0]),count=Integer.parseInt(cell[1]);
                    if(type<0||type>=ITEM_TYPES||type==97||count<1||
                       count>MAX_STOCK||npc.stock[type]!=0)return false;
                    npc.stock[type]=count;
                }
                replacement.put(npc.id,npc);
            }
        }catch(NumberFormatException ignored){return false;}
        byId.clear();byId.putAll(replacement);return true;
    }
    public void clear(){byId.clear();}
}
