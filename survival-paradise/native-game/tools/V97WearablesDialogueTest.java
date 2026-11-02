package com.survivalparadise.nativegame;

/** JVM regression: backpack anchor, head-size fit, four headgear, five NPC roles. */
public final class V97WearablesDialogueTest {
    private static void check(boolean okay,String reason){
        if(!okay)throw new AssertionError(reason);
    }
    public static void main(String[] args){
        float[] pack=WearableFitV97.packBounds(1f);
        check(pack[1]>=-96f && pack[1]<=-86f,"pack too high");
        check(pack[3]<=-24f && pack[3]>=-40f,"pack below waist");
        check(pack[0]<pack[2],"rear pack X bounds");
        for(int gear=0;gear<4;gear++){
            float[] small=WearableFitV97.headBounds(gear,1,.75f,0f);
            float[] middle=WearableFitV97.headBounds(gear,1,1f,0f);
            float[] large=WearableFitV97.headBounds(gear,1,1.6f,0f);
            check(small[0]<small[2]&&small[1]<small[3],"head rectangle "+gear);
            check((large[2]-large[0])>(middle[2]-middle[0])&&
                  (middle[2]-middle[0])>(small[2]-small[0]),
                  "head width must follow setting "+gear);
            check((large[3]-large[1])>(small[3]-small[1]),"head height must follow setting");
            float[] breathing=WearableFitV97.headBounds(gear,1,1f,-4);
            check(Math.abs(breathing[1]-middle[1]+4)<.001,
                    "head breathing must translate overlay "+gear);
        }
        check(Math.abs(WearableFitV97.packBounds(2)[1]-2*pack[1])<.001,
              "pack must scale with actor, not with head setting");
        for(int role=0;role<5;role++){
            for(int question=0;question<3;question++)
                check(NPCDialogueV97.answer(role,question).length()>20,
                      "NPC reply missing "+role+" "+question);
        }
        check(NPCDialogueV97.recruitable(2)&&
              NPCDialogueV97.recruitable(4)&&
              !NPCDialogueV97.recruitable(0),"NPC eligibility");
        System.out.println("V97 PASS: pack alignment, 75%-160% head sizing, "+
                           "breathing, 4 headgears, 5 role-specific dialogue sets");
    }
}
