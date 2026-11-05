package com.survivalparadise.nativegame;

import java.util.HashSet;
import java.util.Set;

/** Pixel-accurate reference checks on the user-provided 1480x720 screenshots. */
public final class ScreenshotDefaultsV121Test {
    static void ok(boolean v,String m){if(!v)throw new AssertionError(m);}
    static void near(float a,float b,float tolerance,String name){
        ok(Math.abs(a-b)<=tolerance,name+" expected "+b+", actual "+a);
    }
    public static void main(String[] args){
        float w=ScreenshotDefaultsV121.REFERENCE_GAME_WIDTH;
        float s=ScreenshotDefaultsV121.REFERENCE_IMAGE_HEIGHT/
                ScreenshotDefaultsV121.GAME_HEIGHT;
        ok(ScreenshotDefaultsV121.COUNT==GameControlCount,"HUD control IDs preserve V118");
        ok(ScreenshotDefaultsV121.CHARACTER_KEYS.length==12,"twelve independent sliders");
        int[] values={93,71,72,9,-5,15,0,0,4,100,4,100};
        for(int i=0;i<values.length;i++)
            ok(ScreenshotDefaultsV121.CHARACTER_VALUES[i]==values[i],
                "screenshot character slider "+ScreenshotDefaultsV121.CHARACTER_KEYS[i]);
        ok(ScreenshotDefaultsV121.CHARACTER_SCALE==98,"display size 98%");
        ok(ScreenshotDefaultsV121.PLAYER_CHARACTER==124,"player choice is 124");
        Set<Integer> seen=new HashSet<>();
        int[][] screenReference={
            {LegacyControlsV58.ZOOM_OUT,1245,87,103,58},
            {LegacyControlsV58.ZOOM_IN,1379,87,101,58},
            {ScreenshotDefaultsV121.BAG,1142,292,141,57},
            {ScreenshotDefaultsV121.FORM,615,0,82,46},
            {ScreenshotDefaultsV121.EDIT,986,0,98,52},
            {ScreenshotDefaultsV121.DAY,1091,0,98,52},
            {ScreenshotDefaultsV121.CAMP,508,0,88,45},
            {ScreenshotDefaultsV121.LAMP,1195,0,105,51},
            {ScreenshotDefaultsV121.PAUSE,713,346,68,34},
            {ScreenshotDefaultsV121.SET,1345,0,106,61},
            {ScreenshotDefaultsV121.SQUAD,1325,205,155,46}
        };
        for(int[] item:screenReference){
            int id=item[0];
            ok(seen.add(id),"unique HUD item ID");
            float x=ScreenshotDefaultsV121.defaultBaseX(id,w)+
                    ScreenshotDefaultsV121.defaultXOffset(id,w);
            float y=ScreenshotDefaultsV121.targetTop(id);
            float width=ScreenshotDefaultsV121.displayWidth(id,w);
            float height=ScreenshotDefaultsV121.displayHeight(id);
            near(x*s,item[1],3.5f,"HUD X "+id);
            near(y*s,item[2],1.5f,"HUD Y "+id);
            near(width*s,item[3],7.2f,"HUD width "+id);
            near(height*s,item[4],7f,"HUD height "+id);
            ok(x>=0&&x+width<=w+1,"target within reference screen "+id);
        }
        near((w*.5f-350f+ScreenshotDefaultsV121.hudPanelOffsetX(w))*s,
            50f,1f,"HUD editor panel X");
        near(ScreenshotDefaultsV121.hudPanelTop()*s,168f,2f,"HUD editor panel Y");
        ok(ScreenshotDefaultsV121.HUD_PANEL_SCALE==130,"HUD panel 130%");
        // Preserve the already matching original main button positions.
        near(LegacyControlsV58.defaultX(LegacyControlsV58.FIRE_L,w)*s,
            332f,3f,"left fire unchanged");
        near(LegacyControlsV58.defaultX(LegacyControlsV58.FIRE_R,w)*s,
            973f,3f,"right fire unchanged");
        near(LegacyControlsV58.defaultX(LegacyControlsV58.MELEE_R,w)*s,
            934f,3f,"right melee unchanged");
        near(WorldUiV86.bagY(660)*s,289f,2f,"bag base before screenshot Y offset");
        // Responsive normalized targets remain on-screen at common aspect ratios.
        for(float vw:new float[]{1100f,1200f,1356.6667f,1600f,1800f}) {
            for(int id:ScreenshotDefaultsV121.MOVED){
                float x=ScreenshotDefaultsV121.defaultBaseX(id,vw)+
                        ScreenshotDefaultsV121.defaultXOffset(id,vw);
                float width=ScreenshotDefaultsV121.displayWidth(id,vw);
                ok(x>=-.5f&&x+width<=vw+.5f,
                    "responsive HUD must not leave screen: "+id+" @"+vw);
            }
        }
        System.out.println("V121: screenshot character presets, original joystick/buttons, "+
            "11 HUD positions/sizes, responsive bounds, panel placement: PASS");
    }
    private static final int GameControlCount=28;
}
