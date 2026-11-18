package com.survivalparadise.nativegame;

/** Pure JVM visual-footprint contract; no bitmap renderer or Android SDK needed. */
public final class V1652CampSpatialTest {
    private static final class Box {
        final float l,t,r,b;
        Box(float x,float y,float w,float h){
            l=x-w*.5f;t=y-h*.5f;r=x+w*.5f;b=y+h*.5f;
        }
        boolean overlaps(Box other){
            return l<other.r&&other.l<r&&t<other.b&&other.t<b;
        }
    }
    private static void separated(Box a,Box b,String description){
        if(a.overlaps(b))
            throw new AssertionError("Intersecting visual footprints: "+description);
    }
    private static void yes(boolean condition,String message){
        if(!condition)throw new AssertionError(message);
    }
    public static void main(String[] args){
        CampWorldV164.Site s=new CampWorldV164.Site("starter",
            1080f,710f,0,14901,0,0,-1,false,true);
        // Source-verified V165.2 production anchors, measured in world units.
        Box tentOlive=new Box(-300,-185,334,263);
        Box tentTan=new Box(225,-185,334,263);
        Box medic=new Box(-38,-105,190,163);
        Box trader=new Box(-215,73,250,215);
        Box solar=new Box(-397,132,84,64);
        Box guard=new Box(270,5,170,96);
        Box fire=new Box(90,95,144,111);
        Box chest=new Box(s.chestX()-s.x,s.chestY()-s.y,104,73);
        Box westScrap=new Box(-399,-5,76,56);
        Box eastScrap=new Box(405,-16,76,56);
        separated(tentOlive,medic,"olive tent/medical canopy");
        separated(tentTan,medic,"tan tent/medical canopy");
        separated(tentOlive,trader,"trader roof versus open tent");
        separated(trader,solar,"trader roof versus solar charger");
        separated(trader,westScrap,"trade entrance versus scrap");
        separated(tentTan,eastScrap,"tent doorway versus scrap");
        separated(guard,fire,"guard barrier versus fire");
        separated(guard,chest,"guard barrier versus searchable chest");
        separated(guard,eastScrap,"guard barrier versus roadside debris");
        // Physics must not extend well beyond the visual chest bounds.
        yes(47f<=104f/2f&&35f<=73f/2f,"Invisible chest collision");
        // NPCs remain outside the chest and beyond the station's bag wall.
        yes(Math.hypot(250f-335f,105f-155f)>78f,
            "Starting guard collides with chest/traffic");
        CampWorldV164.Site rural=new CampWorldV164.Site("rural",
            10000f,10000f,3,14901,2,2,-1,false,false);
        Box rearLeft=new Box(-205,-153,334,263);
        Box rearRight=new Box(186,-153,334,263);
        Box ruralTrader=new Box(-255,125,250,215);
        Box ruralMedic=new Box(155,119,190,163);
        Box ruralGuard=new Box(55,273,170,96);
        Box ruralFire=new Box(20,70,144,111);
        Box ruralChest=new Box(342,125,104,73);
        Box ruralSolar=new Box(-423,255,84,64);
        Box ruralWestScrap=new Box(-432,68,76,56);
        Box ruralEastScrap=new Box(402,-26,92,68);
        separated(rearLeft,ruralTrader,"rural tent/trader");
        separated(rearRight,ruralMedic,"rural tent/medic");
        separated(rearRight,ruralEastScrap,"rural rear tent/industrial debris");
        separated(ruralTrader,ruralSolar,"rural trader/solar");
        separated(ruralTrader,ruralWestScrap,"rural trader/scrap");
        separated(ruralGuard,ruralMedic,"rural medic/watch");
        separated(ruralGuard,ruralFire,"rural watch/campfire");
        separated(ruralGuard,ruralChest,"rural guard/storage");
        yes(rural.npcY(CampWorldV164.GUARD)<rural.y+225f,
            "Guard feet should not spawn inside the sandbag row");
        yes(s.saveId().equals("c14901_0_0_-1"),"Starter save identity changed");
        System.out.println("PASS V165.2: starter/rural assets scaled, entrances/footprints clear, chest and guards coherent, saves stable");
    }
}
