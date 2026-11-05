package com.survivalparadise.nativegame;

/**
 * Rig for the locked V109 200x260 original idle + four walk poses.
 *
 * Source rows 180..219 contain the blue pelvis band; y220..239 contains
 * its black underside AND the rigid brown/black boot blocks.
 * Instead of narrowing these foot blocks, identify each shape in its
 * actual original animation pose and translate it horizontally only.
 * The overlap frame has one combined centered step; leave it centered.
 */
public final class PelvisLegRigV116 {
    public static final int PELVIS_TOP=180;
    public static final int LAYER_BOTTOM=260;
    public static final int PELVIS_BAND_BOTTOM=240;
    public static final int PELVIS=0;
    public static final int LEFT_FOOT=1;
    public static final int RIGHT_FOOT=2;
    public static final int OVERLAP_FOOT=3;

    private PelvisLegRigV116() {}

    /** Number of integer original-source pixels to translate each planted foot.
     * Positive moves the left foot right; the right foot moves left by -shift. */
    public static int inwardPixels(int pelvisPercent) {
        int clamped=PelvisWidthV115.percent(pelvisPercent);
        return Math.round(TorsoWidthV114.SPRITE_WIDTH*(100f-clamped)/200f);
    }

    /** Exact original 20px-grid foot masks, including frame-specific steps.
     * 0=idle, 1..4=the four locked V109 walking frames.
     *
     * The mask is applied to original RGBA pixels, not reconstructed artwork.
     * Every foot source pixel is copied into exactly one rigid layer.
     */
    public static int part(int frame,int x,int y) {
        if(x<0||x>=200||y<PELVIS_TOP||y>=LAYER_BOTTOM)return PELVIS;
        switch(frame) {
            case 1:
                if(y>=220&&x<40)return LEFT_FOOT;
                if(y>=200&&y<220&&x>=160)return RIGHT_FOOT;
                if(y>=220&&y<240&&x>=140)return RIGHT_FOOT;
                return PELVIS;
            case 2:
                // Both steps coincide in this original intermediate pose;
                // keep its 60x20 foot cluster rigid and centered.
                if(y>=220&&y<240&&x>=60&&x<120)return OVERLAP_FOOT;
                return PELVIS;
            case 3:
                // Forward left foot rises through original waist rows 180/200.
                if(y>=180&&y<240&&x<40)return LEFT_FOOT;
                if(y>=220&&x>=140&&x<180)return RIGHT_FOOT;
                return PELVIS;
            case 0:
            case 4:
            default:
                if(y>=220&&x<40)return LEFT_FOOT;
                if(y>=220&&x>=140&&x<180)return RIGHT_FOOT;
                return PELVIS;
        }
    }
}
