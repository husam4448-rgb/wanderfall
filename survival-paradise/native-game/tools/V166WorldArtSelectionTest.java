package com.survivalparadise.nativegame;

/** V166 art selector must not mutate world seeds, IDs or render-dependent RNG. */
public final class V166WorldArtSelectionTest {
    private static void yes(boolean x,String message){
        if(!x)throw new AssertionError(message);
    }
    public static void main(String[] ignored){
        yes(WorldArtSelectionV166.SPRITES==23,"Atlas count drift");
        yes(WorldArtSelectionV166.familyCount()==8,"Family index drift");
        int all=0;
        for(int family=0;family<8;family++){
            int seen=0;
            for(int i=0;i<256;i++){
                float x=i*133.5f,y=(i%37)*-211.25f;
                int first=WorldArtSelectionV166.choose(family,x,y,14901,i);
                int again=WorldArtSelectionV166.choose(family,x,y,14901,i);
                yes(first==again&&WorldArtSelectionV166.valid(first),
                    "Seeded sprite unstable/out of bounds: "+family);
                seen|=1<<(first%32);
                int altered=WorldArtSelectionV166.choose(family,x,y,82011,i);
                yes(WorldArtSelectionV166.valid(altered),"Alternate seed invalid");
            }
            all+=WorldArtSelectionV166.count(family);
            yes(Integer.bitCount(seen)==WorldArtSelectionV166.count(family),
                "Insufficient family variation: "+family);
        }
        yes(all==WorldArtSelectionV166.SPRITES,"Missing sprite entries");
        yes(WorldArtSelectionV166.choose(-1,0,0,1,1)==-1,"Invalid family");
        // These world identities must keep the original saved semantics.
        yes(WorldChunkModel.WORLD_SEED==14901L,"Seed modified");
        System.out.println("PASS V166: 23 authored indexes, seed-stable choices, 8 families");
    }
}
