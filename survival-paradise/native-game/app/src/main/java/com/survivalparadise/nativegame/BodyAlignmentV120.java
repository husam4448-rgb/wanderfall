package com.survivalparadise.nativegame;

/**
 * V120 pixel-source geometry for approved right-facing 200x260 body sprites.
 *
 * Original y160 torso / y180..219 pelvis:
 *  x20..39 black rear edge, x160..179 black front edge.
 * Original y220 hip/leg bridge:
 *  x40..139; rear boot x0..39; front boot x140..179.
 *
 * V116 moved both boots inward by half the amount of width reduction,
 * putting the front boot BEHIND the final front line of the torso. V120
 * anchors its right-most pixel to the visible leading body outline while
 * shifting the rear boot only enough to connect with the hip bridge.
 *
 * LEFT/RIGHT are local sprite-space. GameView mirrors the complete render
 * canvas for left-facing characters. All four original walking poses
 * retain their original stride offsets and boot source pixels.
 */
public final class BodyAlignmentV120 {
    public static final int TORSO_TOP=160;
    public static final int TORSO_OUTLINE_HEIGHT=8; // source pixels, not new body cell
    public static final int REAR_EDGE=20,FRONT_EDGE_EXCLUSIVE=180;
    public static final int BRIDGE_REAR_START=40;
    public static final int REAR_FOOT_END_EXCLUSIVE=40;

    private BodyAlignmentV120(){}

    private static float ratio(int percent){
        return TorsoWidthV114.percent(percent)*.01f;
    }

    /** Existing source-black side outline x20..179 after centered scaling. */
    public static float bodyFrontExclusive(int percent){
        return 100f+(FRONT_EDGE_EXCLUSIVE-100f)*ratio(percent);
    }
    public static float bodyRear(int percent){
        return 100f+(REAR_EDGE-100f)*ratio(percent);
    }

    /** Final frontmost torso or pelvis black outline (x180 exclusive).
     * All feet and torso geometry are unchanged at the 100/100 default. */
    public static float leadingEdge(int torsoPercent,int pelvisPercent) {
        return Math.max(bodyFrontExclusive(torsoPercent),
            bodyFrontExclusive(pelvisPercent));
    }

    /** Move the forward boot only as needed to keep its leading edge
     * exactly aligned with the last body outline. Preserve its walking
     * stride protrusion: the original boot in pose #1 reaches x200, so
     * the same delta leaves that 20px forward step intact.
     */
    public static int frontBootShift(int torsoPercent,int pelvisPercent) {
        return Math.round(leadingEdge(torsoPercent,pelvisPercent)-
            FRONT_EDGE_EXCLUSIVE);
    }

    /** Hip bridge x40 begins where the rear boot x0..39 ends in the
     * original silhouette. Maintain contact without hauling the back
     * boot to the body's center.
     */
    public static int rearBootShift(int pelvisPercent) {
        float bridge=100f+(BRIDGE_REAR_START-100f)*ratio(pelvisPercent);
        return Math.max(0,Math.round(bridge-REAR_FOOT_END_EXCLUSIVE));
    }

    /** The original 20px black side columns remain; add only a thin
     * top cap between those columns, no new resized body pixels. */
    public static float outlineLeft(int torsoPercent){
        return bodyRear(torsoPercent);
    }
    public static float outlineRight(int torsoPercent){
        return bodyFrontExclusive(torsoPercent);
    }
}
