package com.survivalparadise.nativegame;

import android.content.SharedPreferences;

/** Persist screenshot defaults ONLY on a fresh V121 install or explicit reset.
 * Existing user-modified slider values and transferred saves are never
 * overwritten automatically. Global "scale" applies to player and NPCs.
 */
final class ScreenshotSettingsV121 {
    static final String CHARACTER_MARKER="v121_screenshot_character_defaults";
    static final String HUD_MARKER="v121_screenshot_hud_defaults";
    private ScreenshotSettingsV121(){}

    static void applyCharacters(SharedPreferences prefs,boolean overwrite) {
        SharedPreferences.Editor out=prefs.edit();
        for(int scope=CharacterScopeV113.PLAYER;scope<=CharacterScopeV113.NPCS;scope++){
            for(int i=0;i<ScreenshotDefaultsV121.CHARACTER_KEYS.length;i++) {
                String key=CharacterScopeV113.key(
                    ScreenshotDefaultsV121.CHARACTER_KEYS[i],scope);
                if(overwrite||!prefs.contains(key))
                    out.putInt(key,ScreenshotDefaultsV121.CHARACTER_VALUES[i]);
            }
        }
        if(overwrite||!prefs.contains("scale"))
            out.putInt("scale",ScreenshotDefaultsV121.CHARACTER_SCALE);
        if(overwrite||!prefs.contains("playerSkinV109"))
            out.putInt("playerSkinV109",ScreenshotDefaultsV121.PLAYER_CHARACTER);
        out.putBoolean(CHARACTER_MARKER,true).apply();
    }

    static void applyHud(SharedPreferences prefs,float viewWidth,boolean overwrite){
        SharedPreferences.Editor out=prefs.edit();
        if(overwrite){
            // Restore individual V121 defaults, not V72. Removes stale offsets
            // for every control, including the approved default-position ones.
            for(int id=0;id<ScreenshotDefaultsV121.COUNT;id++){
                out.remove("uiX"+id).remove("uiY"+id)
                   .remove("uiSize"+id).remove("uiAlpha"+id)
                   .remove("uiEnabled"+id);
            }
        }
        for(int id:ScreenshotDefaultsV121.MOVED) {
            String x="uiX"+id,y="uiY"+id,size="uiSize"+id;
            if(overwrite||!prefs.contains(x))out.putInt(x,
                ScreenshotDefaultsV121.defaultXOffset(id,viewWidth));
            if(overwrite||!prefs.contains(y))out.putInt(y,
                ScreenshotDefaultsV121.defaultYOffset(id));
            if(overwrite||!prefs.contains(size))out.putInt(size,
                ScreenshotDefaultsV121.defaultSize(id));
        }
        if(overwrite||!prefs.contains("hudPanelX"))out.putInt(
            "hudPanelX",ScreenshotDefaultsV121.hudPanelOffsetX(viewWidth));
        if(overwrite||!prefs.contains("hudPanelY"))out.putInt(
            "hudPanelY",ScreenshotDefaultsV121.hudPanelTop());
        if(overwrite||!prefs.contains("hudPanelSize"))out.putInt(
            "hudPanelSize",ScreenshotDefaultsV121.HUD_PANEL_SCALE);
        if(overwrite||!prefs.contains("movePadSize"))out.putInt("movePadSize",180);
        if(overwrite||!prefs.contains("aimPadSize"))out.putInt("aimPadSize",180);
        if(overwrite||!prefs.contains("uiSize"+ScreenshotDefaultsV121.HOTBAR))
            out.putInt("uiSize"+ScreenshotDefaultsV121.HOTBAR,105);
        if(overwrite||!prefs.contains("uiX"+ScreenshotDefaultsV121.HOTBAR))
            out.putInt("uiX"+ScreenshotDefaultsV121.HOTBAR,-17);
        if(overwrite||!prefs.contains("uiY"+ScreenshotDefaultsV121.HOTBAR))
            out.putInt("uiY"+ScreenshotDefaultsV121.HOTBAR,0);
        if(overwrite) {
            // CROUCH is orange outlined when editing the screenshot; it is
            // deliberately hidden during ordinary gameplay, as in V72.
            out.putBoolean("uiEnabled"+LegacyControlsV58.CROUCH,false);
            out.putBoolean("editControls",false);
            out.putInt("hudOpacityV73",100);
            out.putInt("topButtonOpacityV76",22);
        }
        out.putBoolean(HUD_MARKER,true).apply();
    }
}
