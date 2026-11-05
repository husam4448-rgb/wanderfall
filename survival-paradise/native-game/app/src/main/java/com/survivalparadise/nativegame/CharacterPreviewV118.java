package com.survivalparadise.nativegame;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.view.View;

/**
 * Draws the actual GameView-approved native character/weapon renderer inside
 * Settings. No regenerated stand-in body, no equipment overlay, no source edits.
 * Repainted after slider changes without closing/reopening the settings window.
 */
public final class CharacterPreviewV118 extends View {
    private final MainActivity host;
    private final Paint ink=new Paint(Paint.ANTI_ALIAS_FLAG);
    private boolean walkPreview=false;
    public CharacterPreviewV118(Context context) {
        super(context);host=(MainActivity)context;
        setMinimumHeight(Math.round(185f*getResources().getDisplayMetrics().density));
    }
    public void setWalkingPreview(boolean b){walkPreview=b;invalidate();}
    @Override protected void onMeasure(int w,int h){
        int height=Math.round(185f*getResources().getDisplayMetrics().density);
        setMeasuredDimension(resolveSize(250,w),resolveSize(height,h));
    }
    @Override protected void onDraw(Canvas c){
        super.onDraw(c);
        int w=getWidth(),h=getHeight();
        c.drawColor(0xff23383b);
        ink.setColor(0xff40564c);
        c.drawRect(0,h*.79f,w,h,ink);
        ink.setColor(0xff91c5af);ink.setTextSize(14f);
        boolean npc=host.prefs.getInt(CharacterScopeV113.SCOPE_KEY,0)==1;
        c.drawText(npc?"WORLD NPC • LIVE":"PLAYER • LIVE",12,20,ink);
        GameView g=host.game;
        if(g==null||g.characterSkinsV109==null||!g.characterSkinsV109.ready()) {
            c.drawText("Approved character renderer unavailable",12,h*.5f,ink);
            return;
        }
        // The preview uses the SAME original character + weapon/hand draw path.
        // No saved world state or body sprites are changed.
        int id=npc?1+Math.floorMod(37,200):g.playerSkinV109;
        int weapon=g.gun;
        int variant=0;
        if(npc){
            if(!g.friends.isEmpty()){
                GameView.Survivor f=g.friends.get(0);
                id=f.skinV109;weapon=f.gun;variant=f.variant;
            }else if(!g.campStaff.isEmpty()){
                GameView.Survivor f=g.campStaff.get(0);
                id=f.skinV109;weapon=f.gun;variant=f.variant;
            }
        }
        c.save();
        float zoom=Math.min(2.2f,Math.max(1f,Math.min(w/220f,h/200f)));
        c.translate(w*.5f,h*.80f);
        c.scale(zoom,zoom);
        float playerBefore=g.playerHeadTiltV111;
        float angle=-.28f;
        if(!npc)g.playerHeadTiltV111=HeadAimV111.targetDegrees(angle,g.headAimMaxDegreesV111);
        try {
            g.character(c,0,0,weapon,1,0,
                walkPreview?Float.POSITIVE_INFINITY:0f,
                angle,0f,!npc,false,variant,id);
        }finally {
            if(!npc)g.playerHeadTiltV111=playerBefore;
            c.restore();
        }
        ink.setColor(0xffe5e7d8);ink.setTextSize(12f);
        c.drawText("Approved head • body • weapon • hands",12,h-8,ink);
    }
}
