package com.survivalparadise.nativegame;

/** V132 no door is accidentally triggered by the existing INTERACT action. */
public final class V132DoorInteractionTest {
    private static void ok(boolean value,String reason){
        if(!value)throw new AssertionError(reason);
    }
    public static void main(String[] args){
        ok(LegacyControlsV58.USE==6,"INTERACT action ID must stay 6");
        ok(LegacyControlsV58.COUNT==11,"the old HUD controls cannot shift");
        ok("INTERACT".equals(LegacyControlsV58.LABELS[6]),
            "old USE must be visibly labeled INTERACT");
        ok("INTERACT".equals(LegacyControlsV58.NAMES[6]),
            "HUD editor must also label INTERACT");
        int fixed=0;
        for(ExpeditionSitesV88.Site site:ExpeditionSitesV88.SITES){
            float y=site.y+(site.kind==ExpeditionSitesV88.CLINIC?154f:90f);
            ok(ContextualDoorV132.fixedDoor(site.x,y,site.x,site.y,
                site.kind==ExpeditionSitesV88.CLINIC),
                "authored entry must activate the button at its threshold: "+site.name);
            ok(!ContextualDoorV132.fixedDoor(site.x,y+200f,site.x,site.y,
                site.kind==ExpeditionSitesV88.CLINIC),
                "button must disappear beyond this building: "+site.name);
            fixed++;
        }
        ok(fixed==26,"all original fixed enterable sites must remain supported");
        ok(ContextualDoorV132.shelterDoor(500,542,500,500),
            "field-shelter built entrance");
        ok(!ContextualDoorV132.shelterDoor(500,700,500,500),
            "field shelter distance gate");
        ok(ContextualDoorV132.indoorExit(1360,1822.4f,1360,1822.4f),
            "indoor EXIT available at portal");
        ok(!ContextualDoorV132.indoorExit(1360,1500,1360,1822.4f),
            "EXIT cannot appear deep in building");
        ok(ContextualDoorV132.INDUSTRIAL_RADIUS==152f,
            "preserve seed-based factory entrance radius");
        ok(!ContextualDoorV132.visible(false,true,false,false,true,false),
            "no door means no ENTER");
        ok(ContextualDoorV132.visible(false,true,false,false,true,true),
            "ENTER appears only near door");
        ok(!ContextualDoorV132.visible(false,true,true,false,true,true),
            "paused game hides entrance button");
        ok(!ContextualDoorV132.visible(false,true,false,true,true,true),
            "dead player cannot enter");
        ok(!ContextualDoorV132.visible(false,true,false,false,false,true),
            "disabled button must stay hidden");
        ok(ContextualDoorV132.visible(true,false,true,true,false,false),
            "HUD editor must show the button for moving it");
        ok(!ContextualDoorV132.near(Float.NaN,0,0,0,152f),
            "invalid player position cannot create a door");
        System.out.println("PASS V132: all 26 original doors, shelters, factory radius, "+
            "indoor exits, proximity-only visibility, original INTERACT action ID and labels");
    }
}
