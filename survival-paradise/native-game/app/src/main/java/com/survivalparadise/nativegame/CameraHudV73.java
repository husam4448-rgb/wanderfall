package com.survivalparadise.nativegame;

/** Safe camera zoom and global HUD compositing values for V73. */
public final class CameraHudV73 {
    private CameraHudV73(){}

    /** 45% minimum exposes roughly 2.22x the horizontal world span. */
    public static float zoom(float settingPercent){
        return Math.max(.45f,Math.min(1.80f,settingPercent/100f));
    }

    /** HUD may fade for immersion; the crosshair is outside the HUD layer. */
    public static int opacity(int settingPercent){
        return Math.max(15,Math.min(100,settingPercent));
    }
    public static int alpha(int percent){
        return Math.round(255f*opacity(percent)/100f);
    }
}
