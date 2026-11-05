package com.survivalparadise.nativegame;

/** Pure-JVM tests; pixel-exact idle/walk image QA runs separately in CI. */
public final class PelvisWidthV115Test {
    static void assertTrue(boolean v,String message) {
        if(!v)throw new AssertionError(message);
    }
    static void near(float actual,float expected,String message) {
        assertTrue(Math.abs(actual-expected)<.0001f,
            message+": expected "+expected+", got "+actual);
    }
    public static void main(String[] args) {
        assertTrue(PelvisWidthV115.PELVIS_TOP==180,"canonical pelvis source starts y180");
        assertTrue(PelvisWidthV115.LEGS_TOP==200,"original legs and feet start y200");
        assertTrue(PelvisWidthV115.DEFAULT_PERCENT==100,"neutral fit unchanged");
        assertTrue(PelvisWidthV115.percent(-20)==55,"lower clamp");
        assertTrue(PelvisWidthV115.percent(180)==100,"upper clamp");
        for(int percent=55;percent<=100;percent++) {
            float left=PelvisWidthV115.left(-100f,1f,percent);
            float right=PelvisWidthV115.right(-100f,1f,percent);
            near((left+right)*.5f,0f,"center preserved at "+percent+"%");
            near(right-left,200f*percent/100f,
                "pelvis source width responds at "+percent+"%");
            for(int y=200;y<260;y++)assertTrue(
                PelvisWidthV115.preserveLegRow(y),
                "all 60 leg and foot rows stay unmodified");
            assertTrue(!PelvisWidthV115.preserveLegRow(180),
                "pelvis row editable");
            assertTrue(!PelvisWidthV115.preserveLegRow(199),
                "last pelvis row editable");
            assertTrue(!PelvisWidthV115.preserveLegRow(160),
                "torso controlled separately");
        }
        // Torso and pelvis independently choose width without changing origin.
        for(int torso=55;torso<=100;torso+=5) {
            for(int pelvis=55;pelvis<=100;pelvis+=5) {
                float t=TorsoWidthV114.right(-100f,1f,torso)-
                    TorsoWidthV114.left(-100f,1f,torso);
                float p=PelvisWidthV115.right(-100f,1f,pelvis)-
                    PelvisWidthV115.left(-100f,1f,pelvis);
                near(t,2f*torso,"torso independently narrowed");
                near(p,2f*pelvis,"pelvis independently narrowed");
            }
        }
        System.out.println("V115 independently narrowed pelvis; original torso and 60 leg/foot rows: PASS");
    }
}
