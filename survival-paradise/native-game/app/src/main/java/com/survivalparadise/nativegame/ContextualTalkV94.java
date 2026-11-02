package com.survivalparadise.nativegame;

/** Pure UI rule: TALK is contextual, never a permanent gameplay button. */
public final class ContextualTalkV94 {
    private ContextualTalkV94(){}
    public static boolean visible(boolean editing,boolean playing,
            boolean paused,boolean gameOver,boolean enabled,int npcRole){
        return editing||(playing&&!paused&&!gameOver&&enabled&&npcRole>=0);
    }
    public static boolean inBounds(float x,float y,float left,float top,
            float width,float height){
        return x>=left&&x<=left+width&&y>=top&&y<=top+height;
    }
    public static boolean canTalk(boolean editing,boolean playing,
            boolean paused,boolean gameOver,boolean enabled,int npcRole){
        return !editing&&visible(false,playing,paused,gameOver,enabled,npcRole);
    }
}