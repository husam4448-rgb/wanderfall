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
    public static int defaultX(int id,float w){
        switch(id){
            case FIRE_L:case MELEE_L:return 315;
            case FIRE_R:case MELEE_R:return Math.round(w-348);
            case RUN:case CROUCH:return 433;
            case USE:return Math.round(w*.5f-54);
            case SWAP:case RELOAD:return Math.round(w-481);
            case ZOOM_IN:return Math.round(w-88);
            case ZOOM_OUT:return Math.round(w-174);
            default:throw new IllegalArgumentException("unknown control "+id);
        }
    }
    public static int defaultY(int id,float h){
        switch(id){
            case FIRE_L:case FIRE_R:case RUN:case USE:case RELOAD:return Math.round(h-99);
            case MELEE_L:case MELEE_R:case CROUCH:case SWAP:return Math.round(h-157);
            case ZOOM_IN:case ZOOM_OUT:return 66;
            default:throw new IllegalArgumentException("unknown control "+id);
        }
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
