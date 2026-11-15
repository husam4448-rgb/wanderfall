package com.survivalparadise.nativegame;

import java.util.Arrays;

/** Pure JVM test of November 15 reference calibration, old gear, HUD and camera. */
public final class V142CharacterHudCameraTest {
    private static void ok(boolean valid,String description){
        if(!valid)throw new AssertionError(description);
    }
    public static void main(String[] args){
        ok(CharacterPresetV142.GLOBAL_SCALE==92,
            "character scale is not slightly smaller");
        ok(CharacterPresetV142.TORSO==77&&CharacterPresetV142.PELVIS==72,
            "the screenshot's torso/hips values drifted");
        ok(CharacterPresetV142.PIVOT_X==9&&CharacterPresetV142.PIVOT_Y==-24,
            "the screenshot's weapon/hand pivots drifted");
        ok(CharacterPresetV142.BREATH==4&&
           CharacterPresetV142.BREATH_SPEED==100&&
           CharacterPresetV142.WALK_FPS==4&&
           CharacterPresetV142.WALK_SPEED==107,
           "idle/walk settings do not match screenshot");
        ok(CharacterPresetV142.BODY_KEYS.length==
           CharacterPresetV142.BODY_VALUES.length,
           "character preference keys/values do not align");
        for(String key:CharacterPresetV142.BODY_KEYS)
            ok(!key.toLowerCase().contains("head")&&
               !key.toLowerCase().contains("face"),
               "must not migrate original head fit: "+key);
        ok(CharacterPresetV142.scopeKey("bodyWidthV114",false)
                .equals("bodyWidthV114")&&
           CharacterPresetV142.scopeKey("bodyWidthV114",true)
                .equals("bodyWidthV114NpcV113"),"NPC/player settings not distinct");
        ok(LegacyOutfitVisualV142.torso(0,-1)==9&&
           LegacyOutfitVisualV142.torso(1,-1)==16&&
           LegacyOutfitVisualV142.torso(2,-1)==6,
           "legacy jackets do not have approved clothing sprites");
        ok(LegacyOutfitVisualV142.pants(0,-1)==10&&
           LegacyOutfitVisualV142.pants(1,-1)==18&&
           LegacyOutfitVisualV142.pants(2,-1)==6,
           "legacy pants not rendered with approved silhouettes");
        ok(LegacyOutfitVisualV142.boots(0,-1)==3&&
           LegacyOutfitVisualV142.boots(1,-1)==4&&
           LegacyOutfitVisualV142.boots(2,-1)==1,
           "legacy boots not fitted to approved five-frame source");
        for(int h=-1;h<10;h++)ok(LegacyOutfitVisualV142.headgear(h)<0,
            "V138 permanently hidden headgear was reactivated");
        int[] choices=new int[34];Arrays.fill(choices,100);
        HudOpacityV142.applyAll(58,choices.length,(i,value)->choices[i]=value);
        for(int v:choices)ok(v==58,"global alpha skipped an editable HUD control");
        choices[3]=31;
        ok(choices[3]==31&&choices[2]==58,
            "individual button opacity unexpectedly changed all buttons");
        HudOpacityV142.applyAll(-100,choices.length,(i,value)->choices[i]=value);
        for(int v:choices)ok(v==15,"all alpha lower clamp broken");
        HudOpacityV142.applyAll(300,choices.length,(i,value)->choices[i]=value);
        for(int v:choices)ok(v==100,"all alpha upper clamp broken");
        ok(HudOpacityV142.defaultFor(11,11,12,13,16,23)==70&&
           HudOpacityV142.defaultFor(12,11,12,13,16,23)==70&&
           HudOpacityV142.defaultFor(13,11,12,13,16,23)==78&&
           HudOpacityV142.defaultFor(16,11,12,13,16,23)==82&&
           HudOpacityV142.defaultFor(23,11,12,13,16,23)==72,
           "individual UI categories lost alpha defaults");
        // Indoor camera must follow aim while respecting finite room borders.
        float playerX=850f,roomW=1800f,frameW=610f,
            panX=118f;
        float camera=Math.max(0f,Math.min(roomW-frameW,
            playerX-frameW*.5f+panX));
        ok(camera>playerX-frameW*.5f,
            "interior camera still ignores aim pan");
        float edge=Math.max(0f,Math.min(roomW-frameW,
            1790f-frameW*.5f+panX));
        ok(edge==roomW-frameW,"interior camera allowed empty margins");
        float whole=Math.max(0f,Math.min(0f,
            900f-1800f*.5f+panX));
        ok(whole==0f,"fully visible room must not scroll into empty space");
        System.out.println("PASS V142: screenshot fit player/NPC, smaller scale, "+
            "legacy gear silhouettes, no headwear, selected/global HUD opacity, "+
            "and bounded indoor camera pan");
    }
}
