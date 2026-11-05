package com.survivalparadise.nativegame;

/**
 * V121 screenshot-derived defaults. Reference: the user's approved
 * 1480x720 landscape HUD screenshot (2026-11-05) and character slider
 * screenshot (same day). Coordinates are logical 660-height game units.
 *
 * IMPORTANT: These are preferences ONLY. All 200 original heads, V5 fitting
 * overrides, original foot pixels and gameplay assets stay unchanged.
 */
public final class ScreenshotDefaultsV121 {
    public static final float REFERENCE_IMAGE_WIDTH=1480f;
    public static final float REFERENCE_IMAGE_HEIGHT=720f;
    public static final float GAME_HEIGHT=660f;
    public static final float REFERENCE_GAME_WIDTH=
        REFERENCE_IMAGE_WIDTH*GAME_HEIGHT/REFERENCE_IMAGE_HEIGHT;

    // Shared Player + World NPC calibration. Character #124 is a PLAYER
    // SELECTION only; NPC identities must remain independent and diverse.
    public static final int CHARACTER_SCALE=98,PLAYER_CHARACTER=124;
    public static final String[] CHARACTER_KEYS={
        "headSizeV82","bodyWidthV114","pelvisWidthV115",
        "weaponPivotXV117","weaponPivotYV117","headAimTiltV111",
        "fitHeadXV108","fitHeadYV108","fitIdleBreathV108",
        "idleBreathingSpeedV110","fitWalkFpsV108",
        "walkingAnimationSpeedV79"
    };
    public static final int[] CHARACTER_VALUES={
        93,71,72,9,-5,15,0,0,4,100,4,100
    };

    public static final int MOVE_PAD=LegacyControlsV58.COUNT; // 11
    public static final int AIM_PAD=MOVE_PAD+1;
    public static final int HOTBAR=AIM_PAD+1,BAG=HOTBAR+1,TALK=BAG+1;
    public static final int FORM=TALK+1,EDIT=FORM+1,DAY=EDIT+1;
    public static final int CAMP=DAY+1,LAMP=CAMP+1,PAUSE=LAMP+1,SET=PAUSE+1;
    public static final int STATUS=SET+1,HEADER=STATUS+1,FOOTER=HEADER+1;
    public static final int PERF=FOOTER+1,SQUAD=PERF+1,COUNT=SQUAD+1;

    /** Elements whose screenshot position differs from the older V72 layout. */
    public static final int[] MOVED={
        LegacyControlsV58.ZOOM_OUT,LegacyControlsV58.ZOOM_IN,
        BAG,FORM,EDIT,DAY,CAMP,LAMP,PAUSE,SET,SQUAD
    };
    private ScreenshotDefaultsV121(){}

    /** Original right-anchored HUD geometry with responsive screenshot targets. */
    public static int defaultXOffset(int id,float viewWidth) {
        float targetX=targetLeft(id,viewWidth);
        float baseX=defaultBaseX(id,viewWidth);
        // Respect screen bounds when screen proportions differ.
        float w=displayWidth(id,viewWidth);
        targetX=Math.max(0f,Math.min(Math.max(0f,viewWidth-w),targetX));
        return Math.round(targetX-baseX);
    }
    public static int defaultYOffset(int id){
        return Math.round(targetTop(id)-defaultBaseY(id));
    }
    public static int defaultSize(int id) {
        switch(id){
            case LegacyControlsV58.ZOOM_OUT:
            case LegacyControlsV58.ZOOM_IN:return 120;
            case FORM:return 135;
            case EDIT:case DAY:return 155;
            case CAMP:return 130;
            case LAMP:return 150;
            case PAUSE:case SQUAD:return 100;
            case SET:return 180;
            case BAG:return 100;
            default:return 100;
        }
    }
    public static float targetLeft(int id,float viewWidth){
        float fraction;
        switch(id){
            case LegacyControlsV58.ZOOM_OUT:fraction=1245f/REFERENCE_IMAGE_WIDTH;break;
            case LegacyControlsV58.ZOOM_IN:fraction=1379f/REFERENCE_IMAGE_WIDTH;break;
            case BAG:fraction=1142f/REFERENCE_IMAGE_WIDTH;break;
            case FORM:fraction=615f/REFERENCE_IMAGE_WIDTH;break;
            case EDIT:fraction=986f/REFERENCE_IMAGE_WIDTH;break;
            case DAY:fraction=1091f/REFERENCE_IMAGE_WIDTH;break;
            case CAMP:fraction=508f/REFERENCE_IMAGE_WIDTH;break;
            case LAMP:fraction=1195f/REFERENCE_IMAGE_WIDTH;break;
            case PAUSE:fraction=713f/REFERENCE_IMAGE_WIDTH;break;
            case SET:fraction=1345f/REFERENCE_IMAGE_WIDTH;break;
            case SQUAD:fraction=1325f/REFERENCE_IMAGE_WIDTH;break;
            default:throw new IllegalArgumentException("No screenshot HUD target for "+id);
        }
        return fraction*viewWidth;
    }
    public static float targetTop(int id){
        switch(id){
            case LegacyControlsV58.ZOOM_OUT:
            case LegacyControlsV58.ZOOM_IN:return 87f*GAME_HEIGHT/REFERENCE_IMAGE_HEIGHT;
            case BAG:return 292f*GAME_HEIGHT/REFERENCE_IMAGE_HEIGHT;
            case PAUSE:return 346f*GAME_HEIGHT/REFERENCE_IMAGE_HEIGHT;
            case SQUAD:return 205f*GAME_HEIGHT/REFERENCE_IMAGE_HEIGHT;
            case FORM:case EDIT:case DAY:case CAMP:case LAMP:case SET:return 0f;
            default:throw new IllegalArgumentException("No screenshot HUD target Y for "+id);
        }
    }
    public static float displayWidth(int id,float viewWidth){
        int scale=defaultSize(id);
        if(id==BAG)return WorldUiV86.BAG_W*scale/100f;
        if(id==SQUAD)return 142f*scale/100f;
        if(id>=FORM&&id<=SET)
            return TopHudV76.buttonWidth(topId(id),viewWidth)*scale/100f;
        return LegacyControlsV58.defaultW(id)*scale/100f;
    }
    public static float displayHeight(int id){
        int scale=defaultSize(id);
        if(id==BAG)return WorldUiV86.BAG_H*scale/100f;
        if(id==SQUAD)return 42f*scale/100f;
        if(id>=FORM&&id<=SET)return TopHudV76.HEIGHT*scale/100f;
        return LegacyControlsV58.defaultH(id)*scale/100f;
    }
    private static int topId(int id){
        switch(id){
            case FORM:return TopHudV76.FORM;
            case EDIT:return TopHudV76.EDIT;
            case DAY:return TopHudV76.DAY;
            case CAMP:return TopHudV76.CAMP;
            case LAMP:return TopHudV76.LAMP;
            case PAUSE:return TopHudV76.PAUSE;
            case SET:return TopHudV76.SET;
            default:throw new IllegalArgumentException("No top HUD ID "+id);
        }
    }
    public static float defaultBaseX(int id,float width){
        if(id==BAG)return WorldUiV86.bagX(width);
        if(id==SQUAD)return width-195f;
        if(id>=FORM&&id<=SET)return TopHudV76.x(topId(id),width);
        return LegacyControlsV58.defaultX(id,width);
    }
    private static float defaultBaseY(int id){
        if(id==BAG)return WorldUiV86.bagY(GAME_HEIGHT);
        if(id==SQUAD)return 58f;
        if(id>=FORM&&id<=SET)return TopHudV76.Y;
        return LegacyControlsV58.defaultY(id,GAME_HEIGHT);
    }
    public static int hudPanelOffsetX(float width){
        // Screenshot panel left=50 actual px at 1480: preserved relative width.
        float target=50f/REFERENCE_IMAGE_WIDTH*width;
        return Math.round(target-(width*.5f-350f));
    }
    public static int hudPanelTop(){
        return Math.round(168f*GAME_HEIGHT/REFERENCE_IMAGE_HEIGHT);
    }
    public static final int HUD_PANEL_SCALE=130;
}
