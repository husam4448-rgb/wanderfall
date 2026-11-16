package com.survivalparadise.nativegame;

public final class TradeGridV148Test {
    static void eq(int actual,int expected){if(actual!=expected)
        throw new AssertionError(actual+" expected "+expected);}
    public static void main(String[] args){
        // Smaller tiles than five-column V147, but still around 43 dp wide.
        eq(TradeGridV148.columns(1280,1.375f),9);
        eq(TradeGridV148.columns(2220,3.0f),7);
        eq(TradeGridV148.columns(1536,2.0f),8);
        eq(TradeGridV148.columns(0,0f),8);
        eq(TradeGridV148.rows(40,10),4);
        eq(TradeGridV148.rows(40,8),5);
        eq(TradeGridV148.rows(0,8),0);
        System.out.println("PASS V148 responsive compact trade grid: 4-5 rows of 40 items");
    }
}
