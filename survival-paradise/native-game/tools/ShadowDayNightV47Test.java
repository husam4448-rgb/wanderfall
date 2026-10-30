package com.survivalparadise.nativegame;
public final class ShadowDayNightV47Test {
    static void check(boolean ok,String msg){if(!ok)throw new AssertionError(msg);}
    public static void main(String[] args){
        ShadowGeometryV47.Blocker head=new ShadowGeometryV47.Blocker(90,-20,110,20);
        check(ShadowGeometryV47.blocks(head,0,0,200,0),"character head must cast rear shadow");
        check(!ShadowGeometryV47.blocks(head,0,0,80,0),"light-facing side stays lit");
        check(!ShadowGeometryV47.blocks(head,0,0,100,0),"lit actor front surface not darkened");
        check(!ShadowGeometryV47.blocks(head,100,0,200,0),"self-held flashlight doesn't shadow itself");
        check(!ShadowGeometryV47.blocks(head,0,0,200,100),"off-axis light isn't blocked");
        ShadowGeometryV47.Blocker wall=new ShadowGeometryV47.Blocker(50,30,80,70);
        check(ShadowGeometryV47.blocks(wall,0,50,130,50),"building casts behind shadow");
        check(!ShadowGeometryV47.blocks(wall,0,0,130,0),"wall not blocking clear ray");
        ShadowGeometryV47.Blocker[] shadows={head,wall};
        check(ShadowGeometryV47.blocksAny(shadows,2,0,0,200,0),"multiple blockers");
        GameClockV47 c=new GameClockV47(12*60);
        c.configure(36);check(c.nightFraction()==0,"noon is daylight");
        c.jumpToHour(22);check(c.nightFraction()==1,"night is dark");
        c.jumpToHour(6);check(c.nightFraction()>0 && c.nightFraction()<1,"dawn is gradual");
        c.jumpToHour(18.5f);check(c.nightFraction()>0 && c.nightFraction()<1,"dusk is gradual");
        c.jumpToHour(23.99f);int day=c.day();for(int i=0;i<12;i++)c.advance(.25f);
        check(c.day()==day+1 && c.minute()<4,"midnight automatically advances to next day");
        c.configure(12);c.setClock(1,2);for(int i=0;i<3;i++)c.advance(.25f);
        check(c.minute()>0.9f,"custom day duration advances time");
        System.out.println("V47 PASS: actor shadows, wall shadows, unshadowed fronts, smooth solar cycle, persisted clock");
    }
}