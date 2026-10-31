package com.survivalparadise.nativegame;

/**
 * V78 dynamic light-source fingerprint for the 10Hz static-camera lightmap.
 * Cache only when position, orientation and radius of all light sources match.
 * Pure Java, allocation free, no dependency on frame rate or visual brightness.
 */
public final class LightCacheV78 {
    private LightCacheV78(){}
    public static long seed(int pointCount,int beamCount){
        long hash=0xcbf29ce484222325L;
        hash=mix(hash,pointCount);
        return mix(hash,beamCount);
    }
    private static long mix(long hash,int value){
        return (hash^(value&0xffffffffL))*0x100000001b3L;
    }
    public static long point(long hash,float x,float y,float radius,int color){
        hash=mix(hash,Float.floatToIntBits(x));
        hash=mix(hash,Float.floatToIntBits(y));
        hash=mix(hash,Float.floatToIntBits(radius));
        return mix(hash,color);
    }
    public static long beam(long hash,float x,float y,float dx,float dy,float reach){
        hash=mix(hash,Float.floatToIntBits(x));
        hash=mix(hash,Float.floatToIntBits(y));
        hash=mix(hash,Float.floatToIntBits(dx));
        hash=mix(hash,Float.floatToIntBits(dy));
        return mix(hash,Float.floatToIntBits(reach));
    }
    public static boolean canReuse(boolean staticCache,boolean cacheValid,
          boolean cameraStill,boolean darknessStable,boolean refreshNotDue,
          long previousSignature,long currentSignature){
        return staticCache&&cacheValid&&cameraStill&&darknessStable
            &&refreshNotDue&&previousSignature==currentSignature;
    }
}
