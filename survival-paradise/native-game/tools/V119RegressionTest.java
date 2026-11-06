package com.survivalparadise.nativegame;

/** Deterministic TALK drag, exact footprint and natural firearm-FX tests. */
public final class V119RegressionTest {
    private static void check(boolean value,String message){
        if(!value)throw new AssertionError(message);
    }
    private static void close(float a,float b,String label){
        check(Math.abs(a-b)<.001f,label+": "+a+" vs "+b);
    }
    public static void main(String[] args){
        final int legacy=11,talk=15;
        check(!HudDragV119.isLegacyAction(talk,legacy),"TALK must not enter legacy defaultX/Y");
        check(HudDragV119.isSeparateControl(talk,legacy),"TALK separate");
        check(HudDragV119.isLegacyAction(0,legacy),"FIRE remains legacy");
        check(HudDragV119.isLegacyAction(legacy-1,legacy),"ZOOM remains legacy");
        float buttonLeft=384f,buttonTop=191f;
        float pointerX=411f,pointerY=209f;
        float grabX=HudDragV119.grabOffset(pointerX,buttonLeft);
        float grabY=HudDragV119.grabOffset(pointerY,buttonTop);
        close(buttonLeft+HudDragV119.horizontalOffset(pointerX,grabX,buttonLeft,105,800),
            buttonLeft,"TALK does not jump horizontally on drag start");
        close(buttonTop+HudDragV119.verticalOffset(pointerY,grabY,buttonTop,44,500),
            buttonTop,"TALK does not jump vertically on drag start");
        int x=HudDragV119.horizontalOffset(500,grabX,buttonLeft,105,800);
        int y=HudDragV119.verticalOffset(300,grabY,buttonTop,44,500);
        check(x==89&&y==91,"TALK moves with pointer and keeps original finger offset");
        check(HudDragV119.horizontalOffset(-300,grabX,buttonLeft,105,800)==-384,
            "TALK horizontal safe bound");
        check(HudDragV119.verticalOffset(1500,grabY,buttonTop,44,500)==265,
            "TALK vertical safe bound");
        for(int gun=0;gun<12;gun++)
            check(GunEffectsV119.firearm(gun)==(gun!=3&&gun!=11),
                "Only guns have muzzle and bullet art, gun="+gun);
        check(GunEffectsV119.FLASH_SECONDS>=.12f&&GunEffectsV119.FLASH_SECONDS<=.20f,
            "V130 firearm muzzle light perceptible but not continuous");
        check(GunEffectsV119.BULLET_TRAIL_LENGTH<=14f,"bullet streak is short");
        check(GunEffectsV119.muzzleLength(1,0)<=10f,"pistol short flash");
        check(GunEffectsV119.muzzleLength(1,7)<=13f,"shotgun short flash");
        check(GunEffectsV119.muzzleHalfWidth(1)<=4f,"thin natural flash");
        close(GunEffectsV119.alpha(-1),0f,"expired flash invisible");
        close(GunEffectsV119.alpha(1),1f,"flash opacity clamped");
        System.out.println("V119: TALK drag isolated from legacy defaults, stable grab and bounds; short firearm-only effects: PASS");
    }
}
