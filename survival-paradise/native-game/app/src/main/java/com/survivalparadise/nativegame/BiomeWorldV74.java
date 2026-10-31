package com.survivalparadise.nativegame;

/** Pure-Java deterministic world-coordinate climate model. V73 camp is locked. */
public final class BiomeWorldV74 {
    private BiomeWorldV74(){}
    public static final int FOREST=0,GRASSLAND=1,DESERT=2,SCRUBLAND=3,WETLAND=4,HIGHLANDS=5;
    public static final int CELL=128,SPRITES=7;
    private static float clamp(float a){return Math.max(0f,Math.min(1f,a));}
    private static float smooth(float a,float b,float x){
        float v=clamp((x-a)/(b-a));return v*v*(3f-2f*v);
    }
    private static float noise(float x,float y,float scale,int salt){
        double ax=x/scale,ay=y/scale;
        int ix=(int)Math.floor(ax),iy=(int)Math.floor(ay);
        float fx=smooth(0,1,(float)(ax-ix)),fy=smooth(0,1,(float)(ay-iy));
        float a=(WorldChunkModel.hash(ix+salt,iy-salt)&65535)/65535f;
        float b=(WorldChunkModel.hash(ix+1+salt,iy-salt)&65535)/65535f;
        float c=(WorldChunkModel.hash(ix+salt,iy+1-salt)&65535)/65535f;
        float d=(WorldChunkModel.hash(ix+1+salt,iy+1-salt)&65535)/65535f;
        return (a+(b-a)*fx)*(1-fy)+(c+(d-c)*fx)*fy;
    }
    public static float moisture(float x,float y){
        return noise(x,y,5200f,431)*.72f+noise(x,y,1900f,271)*.28f;
    }
    public static float elevation(float x,float y){
        return noise(x,y,7400f,773)*.8f+noise(x,y,2200f,509)*.2f;
    }
    public static int biome(float x,float y){
        float m=moisture(x,y),e=elevation(x,y);
        if(e>.74f)return HIGHLANDS;
        if(m<.34f)return DESERT;
        if(m<.46f)return SCRUBLAND;
        if(m>.70f&&e<.56f)return WETLAND;
        if(m>.57f)return FOREST;
        return GRASSLAND;
    }
    private static int mix(int a,int b,float w){return Math.round(a+(b-a)*clamp(w));}
    private static int tintTo(int base,int tint,float weight){
        return 0xff000000|
            mix((base>>>16)&255,(tint>>>16)&255,weight)<<16|
            mix((base>>>8)&255,(tint>>>8)&255,weight)<<8|
            mix(base&255,tint&255,weight);
    }
    public static int tint(float x,float y,int base,int campX,int campY){
        float dx=x-campX,dy=y-campY;
        float fade=smooth(365f,940f,(float)Math.hypot(dx,dy));
        if(fade==0f)return base;
        float m=moisture(x,y),e=elevation(x,y);
        int col=tintTo(base,0xffac9870,smooth(.50f,.30f,m)*.86f*fade);
        col=tintTo(col,0xff8c8666,smooth(.58f,.43f,m)*.21f*fade);
        col=tintTo(col,0xff34583f,smooth(.50f,.72f,m)*.30f*fade);
        col=tintTo(col,0xff516856,smooth(.68f,.85f,m)*(1f-smooth(.52f,.72f,e))*.78f*fade);
        return tintTo(col,0xff73756c,smooth(.65f,.85f,e)*.78f*fade);
    }
    public static int prop(float x,float y,int seed){
        int n=Math.floorMod(seed,9);
        switch(biome(x,y)){
            case DESERT: return n<3?2:n<5?3:4;
            case SCRUBLAND: return n<3?3:n<6?4:2;
            case HIGHLANDS: return n<6?4:n<8?3:6;
            case WETLAND: return n<5?6:n<7?0:5;
            case FOREST: return n<4?0:n<6?1:n<8?6:5;
            default: return n<3?5:n<5?1:n<7?6:0;
        }
    }
    public static int detail(int biome,int h){
        switch(biome){
            case DESERT:return (h&4)==0?0xffb1a078:0xff857756;
            case SCRUBLAND:return (h&4)==0?0xff938960:0xff747c58;
            case HIGHLANDS:return (h&4)==0?0xff898b81:0xff696e68;
            case WETLAND:return (h&4)==0?0xff54705c:0xff455f50;
            default:return (h&4)==0?0xff72805e:0xff4b6848;
        }
    }
}
