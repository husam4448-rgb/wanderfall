package com.survivalparadise.nativegame;

/** One-time lossless atlas-alpha compression for fast native combat hit tests. */
public final class PackedAlphaMaskV75 implements CharacterCollision.PixelMask {
    private final int width,height;
    private final int[] bits;
    private PackedAlphaMaskV75(int w,int h,int[] b){width=w;height=h;bits=b;}
    public static PackedAlphaMaskV75 fromArgb(int[] argb,int w,int h){
        if(argb==null||w<=0||h<=0||(long)w*h>Integer.MAX_VALUE||argb.length!=w*h)
            throw new IllegalArgumentException("Invalid sprite atlas dimensions");
        int[] b=new int[(argb.length+31)>>>5];
        for(int i=0;i<argb.length;i++)
            if((argb[i]>>>24)!=0)b[i>>>5]|=1<<(i&31);
        return new PackedAlphaMaskV75(w,h,b);
    }
    @Override public boolean opaque(int x,int y){
        if(x<0||y<0||x>=width||y>=height)return false;
        int offset=y*width+x;
        return (bits[offset>>>5]&(1<<(offset&31)))!=0;
    }
    public int byteSize(){return bits.length*Integer.BYTES;}
}
