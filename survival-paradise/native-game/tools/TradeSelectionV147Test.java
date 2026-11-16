package com.survivalparadise.nativegame;

/** Offline regression: unit price must update for each selected trade kind. */
public final class TradeSelectionV147Test {
    private static void check(boolean ok){if(!ok)throw new AssertionError("V147 trade preview failure");}
    public static void main(String[] args){
        String buy=TradeSelectionV147.priceLine("SCRAP",true,
            NpcTradeLedgerV143.price(0),3,5);
        check(buy.contains("SCRAP")&&buy.contains("BUY")&&
            buy.contains("EACH: 0g 0s 5i")&&buy.contains("TOTAL: 0g 0s 15i"));
        String sell=TradeSelectionV147.priceLine("SCRAP",false,
            NpcTradeLedgerV143.resale(0),2,7);
        check(sell.contains("SELL")&&sell.contains("EACH: 0g 0s 3i")&&
            sell.contains("TOTAL: 0g 0s 6i"));
        check(TradeSelectionV147.priceLine("",true,0,0,0).contains("TAP AN ITEM"));
        check(TradeSelectionV147.priceLine("ITEM",true,10,0,0).contains("UNAVAILABLE"));
        check("QTY  0 / 0".equals(TradeSelectionV147.quantity(0,0)));
        NutWalletV143 coins=new NutWalletV143(120304);
        check(coins.coins(NutWalletV143.GOLD_COIN)==12);
        check(coins.coins(NutWalletV143.SILVER_COIN)==3);
        check(coins.coins(NutWalletV143.IRON)==4);
        System.out.println("PASS V147 selected-item price and player wallet display");
    }
}
