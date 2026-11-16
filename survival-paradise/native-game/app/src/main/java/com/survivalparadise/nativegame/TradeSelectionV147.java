package com.survivalparadise.nativegame;

/**
 * V147 touchscreen trade presentation. Formatting only: all price and wallet
 * arithmetic remains in the original V143 ledger/quantity engine.
 */
final class TradeSelectionV147 {
    private TradeSelectionV147(){}
    static String priceLine(String item,boolean buying,long unit,int count,int maximum){
        if(item==null||item.isEmpty()||unit<=0)
            return "TAP AN ITEM TO SHOW ITS UNIT PRICE";
        String direction=buying?"BUY":"SELL";
        String line=direction+"  •  "+item+"  •  EACH: "+
            NutWalletV143.price(unit)+"  •  TOTAL: "+
            NutWalletV143.price(unit*Math.max(0,count));
        return maximum==0?line+"  •  UNAVAILABLE":line;
    }
    static String quantity(int selected,int maximum){
        return "QTY  "+Math.max(0,selected)+" / "+Math.max(0,maximum);
    }
}
