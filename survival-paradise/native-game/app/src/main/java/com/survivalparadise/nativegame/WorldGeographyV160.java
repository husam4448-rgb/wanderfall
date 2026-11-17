package com.survivalparadise.nativegame;

import java.nio.charset.StandardCharsets;
import java.util.zip.CRC32;

/**
 * V160 seeded natural geography: persistent seed/version, continuous 2D
 * continental-scale moisture, relief and warmth, with coherent blended soil.
 * No camera- or chunk-dependent random state; same seed + world coordinate
 * produces the identical ground and biomes after restart.
 *
 * Old saves without this record continue to use untouched V74/V54 geography.
 * Natural biome maps do not replace roads, buildings, interiors or loot IDs.
 */
public final class WorldGeographyV160 {
    public static final int VERSION=160;
    public final int seed;
    private final int latitudeSalt,humiditySalt,reliefSalt;
    public interface Progress { void step(int progress,String stage); }
    private WorldGeographyV160(int seed){
        this.seed=seed;
        latitudeSalt=seed^0x16016A7;
        humiditySalt=seed^0x6D50B;
        reliefSalt=seed^0x52A9C;
    }
    public static WorldGeographyV160 prepare(int seed,Progress progress){
        WorldGeographyV160 landscape=new WorldGeographyV160(seed);
        if(progress!=null)progress.step(78,"Sculpting mountains and lowlands");
        // Catch invalid geography before replacing a player's current save.
        int regions=0,differences=0,previous=-1;
        for(int iy=-9;iy<=9;iy++)
            for(int ix=-9;ix<=9;ix++){
                int biome=landscape.biomeAt(ix*3770f,iy*3110f);
                if(biome<BiomeWorldV74.FOREST||biome>BiomeWorldV74.HIGHLANDS)
                    throw new IllegalStateException("Invalid generated biome");
                if(biome!=previous)differences++;
                regions++;previous=biome;
            }
        if(progress!=null)progress.step(90,"Validating biome transitions");
        if(regions!=361||differences<15)
            throw new IllegalStateException("Geography lacks regional variation");
        int campsite=landscape.colorAt(1080,710);
        if((campsite>>>24)!=255)
            throw new IllegalStateException("Opaque terrain required");
        if(progress!=null)progress.step(100,"World geography prepared");
        return landscape;
    }
    private static float clamp(float x){return Math.max(0f,Math.min(1f,x));}
    private static float smooth(float low,float high,float x){
        float p=clamp((x-low)/(high-low));
        return p*p*(3f-2f*p);
    }
    private float rand(int x,int y,int salt){
        return (IndustrialWorldV123.hash(x*31+salt*7,y*37-salt*13,
            seed^salt)&0xffff)/65535f;
    }
    private float noise(float x,float y,float scale,int salt){
        double ux=x/scale,uy=y/scale;
        int ix=(int)Math.floor(ux),iy=(int)Math.floor(uy);
        float fx=smooth(0f,1f,(float)(ux-ix));
        float fy=smooth(0f,1f,(float)(uy-iy));
        float a=rand(ix,iy,salt),b=rand(ix+1,iy,salt);
        float c=rand(ix,iy+1,salt),d=rand(ix+1,iy+1,salt);
        return (a+(b-a)*fx)*(1f-fy)+(c+(d-c)*fx)*fy;
    }
    public float moisture(float x,float y){
        return clamp((noise(x,y,12500f,humiditySalt)*.57f+
            noise(x,y,4700f,humiditySalt^99)*.30f+
            noise(x,y,1350f,humiditySalt^377)*.13f-.5f)*1.65f+.5f);
    }
    public float elevation(float x,float y){
        return clamp((noise(x,y,15800f,reliefSalt)*.64f+
            noise(x,y,5700f,reliefSalt^47)*.25f+
            noise(x,y,1700f,reliefSalt^307)*.11f-.5f)*1.55f+.5f);
    }
    public float warmth(float x,float y){
        return clamp((noise(x,y,19000f,latitudeSalt)*.72f+
            noise(x,y,6200f,latitudeSalt^17)*.28f-.5f)*1.6f+.5f);
    }
    public int biomeAt(float x,float y){
        float m=moisture(x,y),h=elevation(x,y),t=warmth(x,y);
        if(h>.70f)return BiomeWorldV74.HIGHLANDS;
        if(m>.69f&&h<.52f)return BiomeWorldV74.WETLAND;
        if(m<.35f&&t>.35f)return BiomeWorldV74.DESERT;
        if(m<.48f)return BiomeWorldV74.SCRUBLAND;
        if(m>.60f)return BiomeWorldV74.FOREST;
        return BiomeWorldV74.GRASSLAND;
    }
    private static int blend(int a,int b,float t){
        return Math.round(a+(b-a)*clamp(t));
    }
    private static int compose(int r,int g,int b){
        return 0xff000000|(Math.max(0,Math.min(255,r))<<16)
            |(Math.max(0,Math.min(255,g))<<8)
            |Math.max(0,Math.min(255,b));
    }
    private static int tint(int base,int target,float t){
        return compose(
            blend((base>>>16)&255,(target>>>16)&255,t),
            blend((base>>>8)&255,(target>>>8)&255,t),
            blend(base&255,target&255,t));
    }
    /**
     * World-smooth climate color interpolation. Unlike a biome-ID-only palette,
     * this has NO sudden hard color changes across classification thresholds.
     * Retains the approved original starter clearing at the camp.
     */
    public int colorAt(float x,float y){
        int original=WorldChunkModel.groundColorAt(x,y,1080,710);
        float distance=(float)Math.hypot(x-1080f,y-710f);
        float fade=smooth(660f,1500f,distance);
        if(fade==0f)return original;
        float m=moisture(x,y),e=elevation(x,y),t=warmth(x,y);
        int color=tint(0xffae9670,0xff67784b,smooth(.21f,.65f,m));
        color=tint(color,0xff3f6249,smooth(.52f,.82f,m)*.82f);
        color=tint(color,0xff666c65,smooth(.55f,.81f,e)*.9f);
        color=tint(color,0xff4c6b5b,
            smooth(.60f,.85f,m)*(1f-smooth(.50f,.70f,e))*.56f);
        color=tint(color,0xffbaa579,(1f-smooth(.22f,.47f,m))*
            smooth(.35f,.75f,t)*.75f);
        // The base low-frequency soil texture remains visible. True ground
        // art stays crisp, but continuous color grading separates provinces.
        return tint(original,color,.83f*fade);
    }
    /** Same visible biome family as the originally approved V74 asset atlas. */
    public int prop(float x,float y,int h){
        int n=Math.floorMod(h^seed*31,9);
        switch(biomeAt(x,y)){
            case BiomeWorldV74.DESERT:return n<3?2:n<5?3:4;
            case BiomeWorldV74.SCRUBLAND:return n<3?3:n<6?4:2;
            case BiomeWorldV74.HIGHLANDS:return n<6?4:n<8?3:6;
            case BiomeWorldV74.WETLAND:return n<5?6:n<7?0:5;
            case BiomeWorldV74.FOREST:return n<4?0:n<6?1:n<8?6:5;
            default:return n<3?5:n<5?1:n<7?6:0;
        }
    }
    public String encode(){
        String head=VERSION+"|"+seed;
        CRC32 crc=new CRC32();
        crc.update(head.getBytes(StandardCharsets.UTF_8));
        return head+"|"+Long.toHexString(crc.getValue());
    }
    public static WorldGeographyV160 decode(String save,int seed){
        if(save==null||save.length()>80)return null;
        try{
            String[] fields=save.split("\\|",-1);
            if(fields.length!=3||Integer.parseInt(fields[0])!=VERSION||
               Integer.parseInt(fields[1])!=seed)return null;
            String head=fields[0]+"|"+fields[1];
            CRC32 crc=new CRC32();
            crc.update(head.getBytes(StandardCharsets.UTF_8));
            return Long.toHexString(crc.getValue()).equals(fields[2])?
                new WorldGeographyV160(seed):null;
        }catch(RuntimeException malformed){return null;}
    }
}
