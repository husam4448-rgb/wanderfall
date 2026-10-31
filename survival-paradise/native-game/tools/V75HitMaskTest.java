package com.survivalparadise.nativegame;

/** Pure JVM sprite alpha mask equivalence and collision regression. */
public final class V75HitMaskTest {
    private static void check(boolean b,String message){if(!b)throw new AssertionError(message);}
    public static void main(String[] args){
        int w=1040,h=160;int[] src=new int[w*h];
        for(int y=0;y<h;y++)for(int x=0;x<w;x++){
            int value=WorldChunkModel.hash(x,y);
            src[y*w+x]=((value&7)==0||(x%17)==0)?0xff000000:value&0xffffff;
        }
        PackedAlphaMaskV75 packed=PackedAlphaMaskV75.fromArgb(src,w,h);
        check(packed.byteSize()<=21000,"packed mask memory");
        for(int y=0;y<h;y++)for(int x=0;x<w;x++)
            check(packed.opaque(x,y)==((src[y*w+x]>>>24)!=0),"pixel mismatch");
        check(!packed.opaque(-1,0)&&!packed.opaque(w,0)&&!packed.opaque(0,h),
              "out of bounds");
        check(CharacterCollision.BASE_SCALE==.70f,"actor size");
        check(Float.isInfinite(CharacterCollision.firstHit(0,0,200,200,100,100,1,0,
              false,0,1f,(x,y)->false)),"transparent body collided");
        System.out.println("V75 PASS: "+(w*h)+" identical alpha cells, "+packed.byteSize()+" mask bytes");
    }
}
