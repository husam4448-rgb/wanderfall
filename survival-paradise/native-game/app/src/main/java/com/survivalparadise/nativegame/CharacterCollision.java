package com.survivalparadise.nativegame;

/**
 * Swept projectile vs the ORIGINAL V31 body atlas opacity.
 *
 * The display transform (200% exported 10x13 pixel character) is reproduced
 * exactly: sprite origin (70,136), V39 planted idle atlas frame 2, and left
 * facing mirrored on the X axis. Idle head bob shifts ONLY source rows 0..101;
 * legs/boots stay at their fixed original location. No new sprite artwork.
 */
public final class CharacterCollision {
    private CharacterCollision(){}

    public interface PixelMask {
        /** Absolute pixel coordinate into the unchanged 1040 x 160 body atlas. */
        boolean opaque(int x, int y);
    }

    public static final int FRAME_WIDTH=260, FRAME_HEIGHT=160;
    public static final int STANDING_FRAME=2;
    public static final float BASE_SCALE=.76f;
    public static final int HEAD_TOP=0, HEAD_END=101, LOWER_START=92;

    // Source alpha bounds over all four V31 character walk/idle poses.
    // Enlarge the broad-phase by only two world pixels for projectile thickness.
    private static final float SOURCE_LEFT=14f, SOURCE_RIGHT=113f;
    private static final float SOURCE_TOP=16f, SOURCE_BOTTOM=140f;
    private static final float ANCHOR_X=70f, ANCHOR_Y=136f;
    private static final float HIT_RADIUS=1.15f;

    public static float firstHit(float x0,float y0,float x1,float y1,
            float actorX,float actorY,int facing,int walkingFrame,
            boolean walking,float breath,float characterScale,PixelMask atlas) {
        if(atlas==null || characterScale<=0f)return Float.POSITIVE_INFINITY;
        final float s=BASE_SCALE*characterScale;
        final int f=walking?Math.max(0,Math.min(3,walkingFrame)):STANDING_FRAME;
        final int face=facing<0?-1:1;
        float l=actorX+face*(SOURCE_LEFT-ANCHOR_X)*s-HIT_RADIUS;
        float r=actorX+face*(SOURCE_RIGHT-ANCHOR_X)*s+HIT_RADIUS;
        float top=actorY+(SOURCE_TOP-ANCHOR_Y+Math.min(0,breath))*s-HIT_RADIUS;
        float bottom=actorY+(SOURCE_BOTTOM-ANCHOR_Y)*s+HIT_RADIUS;
        float minX=Math.min(l,r),maxX=Math.max(l,r);

        final float enter=Ballistics.segmentBox(x0,y0,x1,y1,minX,top,maxX,bottom);
        if(Float.isInfinite(enter))return Float.POSITIVE_INFINITY;
        final float dx=x1-x0,dy=y1-y0;
        final float distance=(float)Math.hypot(dx,dy);
        final float dt=distance>0f?Math.min(1f,1.1f/distance):1f;
        // Continuous ray sampling inside the broad phase prevents fast-round
        // tunneling; small projectile radius forgives subpixel edge contact.
        boolean entered=false;
        for(float t=Math.max(0,enter);t<=1f+1e-5f;t+=dt){
            float tt=Math.min(1f,t),xx=x0+dx*tt,yy=y0+dy*tt;
            boolean inside=xx>=minX&&xx<=maxX&&yy>=top&&yy<=bottom;
            if(!inside){
                if(entered)break; // Segment has left the convex bounding box.
                continue;
            }
            entered=true;
            if(opaqueAt(xx,yy,actorX,actorY,face,f,walking,breath,s,atlas) ||
               opaqueAt(xx-HIT_RADIUS,yy,actorX,actorY,face,f,walking,breath,s,atlas) ||
               opaqueAt(xx+HIT_RADIUS,yy,actorX,actorY,face,f,walking,breath,s,atlas) ||
               opaqueAt(xx,yy-HIT_RADIUS,actorX,actorY,face,f,walking,breath,s,atlas) ||
               opaqueAt(xx,yy+HIT_RADIUS,actorX,actorY,face,f,walking,breath,s,atlas)){
                return tt;
            }
            if(tt>=1f)break;
        }
        return Float.POSITIVE_INFINITY;
    }

    private static boolean opaqueAt(float x,float y,float actorX,float actorY,
         int facing,int frame,boolean walking,float breath,float s,PixelMask atlas) {
        int xx=(int)Math.floor((x-actorX)*facing/s+ANCHOR_X);
        float localY=(y-actorY)/s+ANCHOR_Y;
        if(xx<0||xx>=FRAME_WIDTH)return false;
        if(walking){
            int yy=(int)Math.floor(localY);
            return yy>=0&&yy<FRAME_HEIGHT&&atlas.opaque(frame*FRAME_WIDTH+xx,yy);
        }
        // Exactly the source-overdraw order in GameView.idleBody():
        // unchanged lower part first; then existing head pixels offset for breath.
        int headY=(int)Math.floor(localY-breath);
        if(headY>=HEAD_TOP&&headY<HEAD_END&&atlas.opaque(
                STANDING_FRAME*FRAME_WIDTH+xx,headY))return true;
        int bottomY=(int)Math.floor(localY);
        return bottomY>=LOWER_START&&bottomY<FRAME_HEIGHT&&
            atlas.opaque(STANDING_FRAME*FRAME_WIDTH+xx,bottomY);
    }
}
