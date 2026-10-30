package com.survivalparadise.nativegame;

/**
 * Pure-Java character animation state. Never infer locomotion from a historical
 * clock: a stopped actor must use the approved neutral V31 atlas frame 0.
 * Source sprites are not edited or regenerated.
 */
public final class AnimationCycle {
    public static final int IDLE_FRAME = 0;
    public static final int WALK_FRAMES = 4;
    private static final float FRAME_RATE_FACTOR = 1.25f;
    private float phase;
    private boolean walking;

    public void reset() {
        walking = false;
        phase = 0f;
    }

    public void step(boolean actuallyMoving, float dt, float rate) {
        if (!actuallyMoving) {
            reset();
            return;
        }
        if (!walking) {
            walking = true;
            phase = 0f; // Every new walk starts from the first approved walk pose.
        } else {
            // Bound phase to prevent float overflow in very long offline sessions.
            phase = (phase + Math.max(0f, dt) * Math.max(0f, rate)) % (WALK_FRAMES / FRAME_RATE_FACTOR);
        }
    }

    public boolean isWalking() { return walking; }

    public int frame() {
        if (!walking) return IDLE_FRAME;
        return Math.min(WALK_FRAMES - 1, (int)(phase * FRAME_RATE_FACTOR));
    }
}
