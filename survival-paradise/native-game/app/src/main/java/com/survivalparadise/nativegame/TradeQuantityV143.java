package com.survivalparadise.nativegame;

/** Economy quantity limits are computed before the player confirms a trade.
 * All arithmetic uses integer nuts; no conversion rounding or credit creation.
 */
public final class TradeQuantityV143 {
    private TradeQuantityV143(){}
    public static int buyMaximum(NpcTradeLedgerV143.Npc npc,int type,
                                 NpcTradeLedgerV143.Inventory player,
                                 NutWalletV143 buyer){
        if(npc==null||player==null||buyer==null||
           type<0||type>=NpcTradeLedgerV143.ITEM_TYPES||type==97||
           !player.capacity(type))return 0;
        long price=NpcTradeLedgerV143.price(type);
        if(price<=0)return 0;
        long affordable=buyer.iron()/price;
        long npcRoom=(NutWalletV143.MAX-npc.wallet.iron())/price;
        return (int)Math.max(0,Math.min(npc.count(type),
            Math.min(affordable,npcRoom)));
    }
    public static int sellMaximum(NpcTradeLedgerV143.Npc npc,int type,
                                  NpcTradeLedgerV143.Inventory player,
                                  NutWalletV143 seller){
        if(npc==null||player==null||seller==null||
           type<0||type>=NpcTradeLedgerV143.ITEM_TYPES||type==97)return 0;
        long price=NpcTradeLedgerV143.resale(type);
        if(price<=0)return 0;
        long affordable=npc.wallet.iron()/price;
        long buyerRoom=(NutWalletV143.MAX-seller.iron())/price;
        long stockRoom=NpcTradeLedgerV143.MAX_STOCK-npc.count(type);
        return (int)Math.max(0,Math.min(player.available(type),
            Math.min(affordable,Math.min(buyerRoom,stockRoom))));
    }
    public static int clamp(int requested,int maximum){
        if(maximum<1)return 0;
        return Math.max(1,Math.min(requested,maximum));
    }
}
