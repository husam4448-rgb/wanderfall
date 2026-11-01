package com.survivalparadise.nativegame;

/** Prove unmodified source crop and narrow knife motion before Android draw. */
public final class V82HeadKnifeTest {
    static void ok(boolean v,String msg){if(!v)throw new AssertionError(msg);}
    static void close(float a,float b){ok(Math.abs(a-b)<.0002f,a+" != "+b);}
    public static void main(String[]args){
        close(HeadKnifeV82.headMultiplier(100),1f);
        close(HeadKnifeV82.headMultiplier(75),.75f);
        close(HeadKnifeV82.headMultiplier(160),1.6f);
        close(HeadKnifeV82.headMultiplier(1),.75f);
        close(HeadKnifeV82.headMultiplier(999),1.6f);
        ok(HeadKnifeV82.defaultHead(1f),"legacy sprites must remain pixel identical");
        ok(!HeadKnifeV82.defaultHead(1.25f),"head edit not applied");
        ok(HeadKnifeV82.HEAD_TOP==20&&HeadKnifeV82.HEAD_BOTTOM==92,
           "atlas head region must stop at first shirt pixel");
        for(float s:new float[]{.55f,.70f,1f,1.4f}){
            close(HeadKnifeV82.headBottom(s,-2f),(92f-136f)*s-2f);
            for(float head:new float[]{.75f,1f,1.25f,1.6f}){
                close(HeadKnifeV82.headRight(s,head)-HeadKnifeV82.headLeft(s,head),
                      (HeadKnifeV82.HEAD_RIGHT-HeadKnifeV82.HEAD_LEFT)*s*head);
                close(HeadKnifeV82.headBottom(s,-2)-HeadKnifeV82.headTop(s,head,-2),
                      (HeadKnifeV82.HEAD_BOTTOM-HeadKnifeV82.HEAD_TOP)*s*head);
            }
        }
        close(HeadKnifeV82.sweep(0f),-27f);
        close(HeadKnifeV82.sweep(.5f),0f);
        close(HeadKnifeV82.sweep(1f),27f);
        ok(HeadKnifeV82.MELEE_SWEEP_DEGREES<60f,
           "melee must not sweep a half-circle");
        ok(HeadKnifeV82.KNIFE_TRAIL_LENGTH<=24f,"knife trail too long");
        ok(HeadKnifeV82.KNIFE_SIZE>=1.45f,"knife not visibly enlarged");
        close(HeadKnifeV82.localBearing(0,1),0f);
        close(HeadKnifeV82.localBearing(4,-1),0f);
        close(HeadKnifeV82.localBearing(1,1),45f);
        close(HeadKnifeV82.localBearing(3,-1),45f);
        System.out.println("V82 PASS original 100% head, scalable atlas head 75-160%, "+
            "mirrored short-sweep 1.55x knife and compact slash stroke");
    }
}
