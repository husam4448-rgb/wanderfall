package com.survivalparadise.nativegame;

import android.content.SharedPreferences;
import org.json.JSONException;
import org.json.JSONObject;

/**
 * V108 non-destructive character-fit calibration. Pure geometry: never
 * modifies canonical V31/V56 bitmaps, animation timing, controls or saves.
 * Neutral values deliberately preserve the established V98 compositor.
 */
public final class CharacterFitV108 {
    private CharacterFitV108() {}

    public static final String X_KEY="fitHeadXV108";
    public static final String Y_KEY="fitHeadYV108";
    public static final String BREATH_KEY="fitIdleBreathV108";
    public static final String WALK_FPS_KEY="fitWalkFpsV108";

    public static final int HEAD_X_DEFAULT=0,HEAD_Y_DEFAULT=0;
    public static final int BREATH_DEFAULT=4,WALK_FPS_DEFAULT=0;
    public static final int HEAD_OFFSET_MIN=-24,HEAD_OFFSET_MAX=24;
    public static final int BREATH_MIN=0,BREATH_MAX=12;
    public static final int WALK_FPS_MIN=0,WALK_FPS_MAX=12;

    public static int clamp(int x,int lo,int hi){return Math.max(lo,Math.min(hi,x));}

    public static int headX(SharedPreferences p){
        return clamp(p.getInt(X_KEY,HEAD_X_DEFAULT),HEAD_OFFSET_MIN,HEAD_OFFSET_MAX);
    }
    public static int headY(SharedPreferences p){
        return clamp(p.getInt(Y_KEY,HEAD_Y_DEFAULT),HEAD_OFFSET_MIN,HEAD_OFFSET_MAX);
    }
    public static int breathPixels(SharedPreferences p){
        return clamp(p.getInt(BREATH_KEY,BREATH_DEFAULT),BREATH_MIN,BREATH_MAX);
    }
    public static int walkFps(SharedPreferences p){
        return clamp(p.getInt(WALK_FPS_KEY,WALK_FPS_DEFAULT),WALK_FPS_MIN,WALK_FPS_MAX);
    }

    /** The existing two-phase cycle is 0 and -4 source pixels. */
    public static float breath(float original,int amplitude){
        return original*(clamp(amplitude,BREATH_MIN,BREATH_MAX)/4f);
    }
    /** AnimationCycle uses a 1.25 frame multiplier, so 3 fps -> rate 2.4. */
    public static float rate(float original,int overrideFps){
        int fps=clamp(overrideFps,WALK_FPS_MIN,WALK_FPS_MAX);
        return fps==0?original:fps/1.25f;
    }
    public static boolean separateHead(float scale,int x,int y,int breathAmplitude){
        return !HeadKnifeV82.defaultHead(scale)||x!=0||y!=0||breathAmplitude!=BREATH_DEFAULT;
    }

    public static void reset(SharedPreferences p){
        p.edit().putInt(X_KEY,HEAD_X_DEFAULT)
            .putInt(Y_KEY,HEAD_Y_DEFAULT).putInt(BREATH_KEY,BREATH_DEFAULT)
            .putInt(WALK_FPS_KEY,WALK_FPS_DEFAULT).apply();
    }

    /** Portable, human-readable fitting-only JSON; excludes world and saves. */
    public static JSONObject exportJson(SharedPreferences p) throws JSONException {
        JSONObject o=new JSONObject();
        o.put("format","survival-paradise-character-fit-v108");
        o.put("schema",1);
        o.put("headScalePercent",HeadKnifeV82.HEAD_MIN+
            clamp(p.getInt("headSizeV82",HeadKnifeV82.HEAD_DEFAULT)-
              HeadKnifeV82.HEAD_MIN,0,HeadKnifeV82.HEAD_MAX-HeadKnifeV82.HEAD_MIN));
        o.put("horizontalFitPx",headX(p));
        o.put("verticalFitPx",headY(p));
        o.put("idleBreathingPx",breathPixels(p));
        o.put("walkFrameRateFps",walkFps(p));
        o.put("walkFrameRateMode",walkFps(p)==0?"AUTO_GAIT_SYNC":"FIXED_TEST");
        o.put("walkingAnimationSpeedPercent",clamp(
            p.getInt("walkingAnimationSpeedV79",100),50,200));
        o.put("characterScalePercent",clamp(p.getInt("scale",100),65,135));
        o.put("headScaleIsUniform",true);
        o.put("bodyTemplate","V31/V56 LOCKED");
        o.put("facing","mirrored");
        return o;
    }
}
