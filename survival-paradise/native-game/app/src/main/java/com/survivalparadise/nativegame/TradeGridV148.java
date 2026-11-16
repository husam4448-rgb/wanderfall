package com.survivalparadise.nativegame;

/** Stateless density-aware trade grid sizing. Never modifies item data. */
final class TradeGridV148 {
    private TradeGridV148(){}
    static int columns(int screenPx,float density){
        if(screenPx<=0||density<=0f)return 8;
        // ~94% window width, two panes, inner padding and scrollbar.
        float paneDp=screenPx*.94f/(2f*density)-14f;
        return Math.max(6,Math.min(10,(int)Math.floor(paneDp/43f)));
    }
    static int rows(int items,int columns){
        return (Math.max(0,items)+Math.max(1,columns)-1)/Math.max(1,columns);
    }
}
