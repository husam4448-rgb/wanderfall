package com.survivalparadise.nativegame;
public final class V70AimZonesTest {
    static void ok(boolean yes,String why){if(!yes)throw new AssertionError(why);}
    static void near(float a,float b,String why){ok(Math.abs(a-b)<.001f,why+" got="+a+" want="+b);}
    public static void main(String[] args){
        near(AimZonesV70.extendFactor(.1f),0f,"tiny tilt never extends");
        near(AimZonesV70.extendFactor(.45f),0f,"normal aim never extends");
        near(AimZonesV70.extendFactor(.62f),0f,"aim-only boundary");
        near(AimZonesV70.extendFactor(.76f),.5f,"mid outer ring half extension velocity");
        near(AimZonesV70.extendFactor(.90f),1f,"max extension velocity");
        near(AimZonesV70.panFactor(.50f),0,"center never pans");
        near(AimZonesV70.panFactor(.89f),0,"extending aim never pans");
        near(AimZonesV70.panFactor(.90f),0,"panning starts ONLY in outermost 10%");
        near(AimZonesV70.panFactor(.95f),.5f,"pan phase gentle ramp");
        near(AimZonesV70.panFactor(1f),1f,"far rim max camera pan");
        near(AimZonesV70.reach(4600,325,5000,.30f,650,.016f),325f,
             "normal aim instantly resets to rest, no accumulated drift");
        near(AimZonesV70.reach(325,325,5000,.60f,650,.016f),325f,
             "near center no forward movement");
        float slow=AimZonesV70.reach(325,325,5000,.76f,650,.016f);
        near(slow,325f+650f*.5f*.016f,"linear velocity not accelerating");
        near(AimZonesV70.reach(slow,325,5000,.76f,650,.016f),
             slow+650f*.5f*.016f,"constant extension speed per frame");
        near(AimZonesV70.reach(4999,325,5000,1f,650,.016f),5000,
             "crosshair never passes actual bullet endpoint");
        float cap=65;
        near(AimZonesV70.panX(1,0,cap,1),cap,"right pan radius");
        near(AimZonesV70.panX(-1,0,cap,1),-cap,"left pan radius");
        near(AimZonesV70.panY(0,1,cap,1),cap,"down pan radius");
        near(AimZonesV70.panY(0,-1,cap,1),-cap,"up pan radius");
        float dx=AimZonesV70.panX(1,1,cap,1),dy=AimZonesV70.panY(1,1,cap,1);
        near((float)Math.hypot(dx,dy),cap,"diagonal cannot exceed circular radius");
        near(AimZonesV70.panX(1,0,cap,.80f),0f,"nonpan aiming does not move camera");
        near(AimZonesV70.panY(0,1,cap,.80f),0f,"nonpan aiming does not move camera vertically");
        near(AimZonesV70.panX(1,0,cap,0),0f,"release has no panning");
        near(AimZonesV70.reach(300,190,2665,0,650,.016f),190,
             "release resets weapon-specific snapback distance");
        System.out.println("V70 PASS: three separate zones, zero drift near center, equal circular four-direction panning");
    }
}
