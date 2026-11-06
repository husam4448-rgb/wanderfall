package com.survivalparadise.nativegame;
public final class V130InventorySiteTest {
    static void ok(boolean truth,String msg){if(!truth)throw new AssertionError(msg);}
    public static void main(String[] args){
        int[] order=new int[40],totals=new int[40];
        for(int i=0;i<40;i++)order[i]=i;
        totals[0]=21;totals[1]=5;
        InventorySplitV130 stacks=new InventorySplitV130();
        ok(stacks.split(0,7,order,totals),"first stack split");
        ok(stacks.count(0,order,totals)==14,"source count after split");
        ok(stacks.type(2,order)==0&&stacks.count(2,order,totals)==7,
            "separate UI slot not created");
        ok(stacks.count(0,order,totals)+stacks.count(2,order,totals)==21,
            "stack split duplicated/lost resources");
        ok(stacks.split(2,3,order,totals),"splitting a derived stack");
        ok(stacks.count(2,order,totals)==4&&stacks.count(3,order,totals)==3,
            "sub-stack split");
        ok(stacks.count(0,order,totals)+stacks.count(2,order,totals)+
            stacks.count(3,order,totals)==21,"multiple split totals");
        String saved=stacks.encode();InventorySplitV130 load=new InventorySplitV130();
        load.decode(saved,order,totals);
        ok(load.count(2,order,totals)==4&&load.count(3,order,totals)==3,
            "split inventory save/reload");
        load.consumed(2,2);totals[0]-=2;
        ok(load.count(0,order,totals)+load.count(2,order,totals)+
            load.count(3,order,totals)==19,"partial stack dropping changed totals");
        load.moved(3,6);
        int moved=order[3];System.arraycopy(order,4,order,3,3);order[6]=moved;
        ok(load.type(6,order)==0&&load.count(6,order,totals)==3,
            "dragged split stack misplaced");
        totals[5]=3;
        load.reconcile(order,totals);
        ok(load.type(6,order)==0,"split allocation corrupted on unrelated inventory");
        int sites=0,nearRoad=0,overlaps=0,unsafe=0;
        for(ExpeditionSitesV88.Site s:ExpeditionSitesV88.SITES){
            float[] a=SiteExteriorScaleV130.solid(s);
            ok(a[0]<a[2]&&a[1]<a[3],"invalid building hull");
            ok(!SiteExteriorScaleV130.blocked(s.x,SiteExteriorScaleV130.doorY(s)+22,19),
                "building entrance blocked for "+s.name);
            ok(SiteExteriorScaleV130.blocked((a[0]+a[2])/2f,(a[1]+a[3])/2f,10),
                "building roof not solid for "+s.name);
            float cx=Math.max(a[0],Math.min(1000f,a[2]));
            float cy=Math.max(a[1],Math.min(1060f,a[3]));
            if(Math.hypot(cx-1000,cy-1060)<WorldSafetyV92.CAMP_SAFE_RADIUS)
                unsafe++;
            if(a[0]<1720&&a[2]>1500||
               a[1]<1150&&a[3]>925)nearRoad++;
            for(ExpeditionSitesV88.Site other:ExpeditionSitesV88.SITES){
                if(s==other)continue;
                float[] b=SiteExteriorScaleV130.solid(other);
                if(a[0]<b[2]+25&&a[2]+25>b[0]&&
                   a[1]<b[3]+25&&a[3]+25>b[1])overlaps++;
            }
            if(s.kind!=ExpeditionSitesV88.CLINIC)
                ok(SiteExteriorScaleV130.scale(s.kind)>=1.85f,
                    "small exterior: "+s.name);
            sites++;
        }
        ok(sites==26,"site count changed");
        ok(unsafe==0,"enlarged buildings encroach protected camp: "+unsafe);
        ok(nearRoad==0,"building collides with original highway");
        ok(overlaps==0,"two enlarged buildings clip into each other");
        System.out.println("PASS V130: real split/move/use/drop/reload conservation, "+
            "all "+sites+" scaled roofs, open entrances, zero site/camp/road collisions");
    }
}
