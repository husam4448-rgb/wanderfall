package com.survivalparadise.nativegame;

/** Stable individual HUD IDs, allowing a global edit with no saved-layout reset. */
public final class HudOpacityV142 {
    public static final int DEFAULT_GLOBAL=90,DEFAULT_BUTTON=58,
        DEFAULT_JOYSTICK=70,DEFAULT_HOTBAR=78,DEFAULT_TOP=82,
        DEFAULT_STATUS=72,MIN=15,MAX=100;
    private HudOpacityV142(){}
    public static int clamp(int value){return Math.max(MIN,Math.min(MAX,value));}
    public static int defaultFor(int id,int pad1,int pad2,int hotbar,
                                 int topStart,int statusStart){
        if(id==pad1||id==pad2)return DEFAULT_JOYSTICK;
        if(id==hotbar)return DEFAULT_HOTBAR;
        if(id>=statusStart)return DEFAULT_STATUS;
        if(id>=topStart)return DEFAULT_TOP;
        return DEFAULT_BUTTON;
    }
    /** Global opacity changes every HUD control without losing its size/position. */
    public static void applyAll(int value,int count,Setter setter){
        int alpha=clamp(value);
        for(int i=0;i<count;i++)setter.set(i,alpha);
    }
    public interface Setter {void set(int id,int opacity);}
}
