package com.survivalparadise.nativegame;

/** V58 native-Java reconstruction of the approved dual-side mobile controls.
 * Default layouts do not overlap either joystick at 1200x660 logical units.
 * All coordinates are logical-screen units, not physical-pixel coordinates. */
public final class LegacyControlsV58 {
    private LegacyControlsV58(){}
    public static final int FIRE_L=0,FIRE_R=1,MELEE_L=2,MELEE_R=3,
        RUN=4,CROUCH=5,USE=6,SWAP=7,RELOAD=8,ZOOM_IN=9,ZOOM_OUT=10;
    public static final int COUNT=11;
    public static final String[] NAMES={
        "Left FIRE","Right FIRE","Left MELEE","Right MELEE","RUN",
        "CROUCH","USE","SWAP","RELOAD","ZOOM +","ZOOM -"};
    public static final String[] LABELS={
        "FIRE","FIRE","MELEE","MELEE","RUN","CROUCH","USE",
        "SWAP","RELOAD","ZOOM +","ZOOM -"};
    // V72 screenshot-based 1480x720 reference, normalized horizontally
    // for narrower mobile screens. Default joystick and hotbar also move.
    public static int defaultX(int id,float w){
        switch(id){
            case FIRE_L:return Math.round(w*.225f);
            case MELEE_L:return Math.round(w*.243f);
            case FIRE_R:return Math.round(w-465f);
            case MELEE_R:return Math.round(w-501f);
            case RUN:return Math.round(w-145f);
            case CROUCH:return Math.round(w*.28f);
            case USE:return Math.round(w*.397f);
            case SWAP:return Math.round(Math.min(w*.505f,w-619f));
            case RELOAD:return Math.round(w-513f);
            case ZOOM_IN:return Math.round(w-88f);
            case ZOOM_OUT:return Math.round(w-174f);
            default:throw new IllegalArgumentException("unknown control "+id);
        }
    }
    public static int defaultY(int id,float h){
        switch(id){
            case FIRE_L:return Math.round(h-302f);
            case FIRE_R:return Math.round(h-324f);
            case MELEE_L:return Math.round(h-199f);
            case MELEE_R:return Math.round(h-95f);
            case RUN:return Math.round(h-372f);
            case CROUCH:return Math.round(h-199f);
            case USE:case SWAP:return Math.round(h-47f);
            case RELOAD:return Math.round(h-219f);
            case ZOOM_IN:case ZOOM_OUT:return 66;
            default:throw new IllegalArgumentException("unknown control "+id);
        }
    }
    /** Screenshot-based button scales; individual HUD edits still override. */
    public static int defaultScale(int id){
        switch(id){
            case FIRE_L:case FIRE_R:return 140;
            case MELEE_L:return 110;
            case MELEE_R:case RELOAD:return 130;
            case RUN:return 110;
            case USE:case SWAP:return 105;
            default:return 100;
        }
    }
    public static boolean defaultEnabled(int id){
        return id!=CROUCH; // hidden in the requested reference HUD
    }
    public static int defaultW(int id){
        return (id==ZOOM_IN||id==ZOOM_OUT)?78:105;
    }
    public static int defaultH(int id){
        return (id==ZOOM_IN||id==ZOOM_OUT)?43:44;
    }
    public static boolean isFire(int id){return id==FIRE_L||id==FIRE_R;}
    public static boolean isMelee(int id){return id==MELEE_L||id==MELEE_R;}
    public static boolean hit(float x,float y,float left,float top,float w,float h){
        return x>=left&&x<=left+w&&y>=top&&y<=top+h;
    }
    public static int quantizeKnife(float dx,float dy){
        if(Math.abs(dx)+Math.abs(dy)<.0001f)return 0; // east
        int octant=Math.round((float)(Math.atan2(dy,dx)*4/Math.PI));
        return Math.floorMod(octant,8); // E,SE,S,SW,W,NW,N,NE (screen Y down)
    }
    public static float knifeX(int octant){
        return (float)Math.cos(octant*Math.PI/4);
    }
    public static float knifeY(int octant){
        return (float)Math.sin(octant*Math.PI/4);
    }
}
