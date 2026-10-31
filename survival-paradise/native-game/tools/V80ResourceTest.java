package com.survivalparadise.nativegame;

/** Determinism, sparse world persistence, travel, reuse and near-camp availability. */
public final class V80ResourceTest {
    private static void ok(boolean yes,String msg){if(!yes)throw new AssertionError(msg);}
    private static final float CX=1080f,CY=710f,W=3200f,H=2200f;

    public static void main(String[] args){
        ResourceWorldV80 store=new ResourceWorldV80();
        int found=0,forest=0,stone=0,fiber=0,nearCamp=0;
        ResourceWorldV80.Node nearest=null;
        for(int y=-12;y<12;y++)for(int x=-12;x<12;x++)for(int k=0;k<4;k++){
            ResourceWorldV80.Node n=ResourceWorldV80.node(x,y,k,CX,CY,W,H);
            if(n==null)continue;
            found++;
            if(n.resource()==ResourceWorldV80.WOOD)forest++;
            if(n.resource()==ResourceWorldV80.STONE)stone++;
            if(n.resource()==ResourceWorldV80.FIBER)fiber++;
            float d=(float)Math.hypot(n.x-CX,n.y-CY);
            if(d<1000f){nearCamp++;nearest=n;}
            if(k<3 && !(n.x>=0&&n.x<=W&&n.y>=0&&n.y<=H)){
                int expectedSeed=WorldChunkModel.hash(x*7+k,y*11-k);
                ok(n.seed==expectedSeed,"V74 sprite seed changed");
                ok(n.kind==BiomeWorldV74.prop(n.x,n.y,n.seed),"V74 biomes changed");
            }
            ResourceWorldV80.Node again=ResourceWorldV80.node(x,y,k,CX,CY,W,H);
            ok(again.seed==n.seed&&again.x==n.x&&again.y==n.y,
               "resource drift after chunk re-entry");
        }
        ok(found>200&&forest>0&&stone>0&&fiber>0,"all biomes/resources populated");
        ok(nearCamp>0,"no gatherable resources within walking distance of camp");
        ok(nearest!=null,"missing test resource");
        ResourceWorldV80.Node touch=store.nearest(nearest.x,nearest.y,1f,CX,CY,W,H);
        ok(touch!=null,"USE cannot detect exact resource anchor");
        ok(store.harvest(touch),"harvest failed");
        ok(!store.harvest(touch),"resource duplicated after first harvest");
        ok(store.exhausted(touch.cx,touch.cy,touch.slot),"depleted marker not stored");
        String serialized=store.encode();
        ResourceWorldV80 restored=new ResourceWorldV80();
        restored.decode(serialized);
        ok(restored.exhausted(touch.cx,touch.cy,touch.slot),"lost depleted node on load");
        ok(restored.depletedNodes()==1,"unexpected node count");
        for(int i=0;i<50;i++)restored.node(i,-i,0,CX,CY,W,H); // leaving/reentering
        ok(restored.exhausted(touch.cx,touch.cy,touch.slot),"resource regenerated after travel");
        ok(restored.nearest(touch.x,touch.y,1f,CX,CY,W,H)==null,
           "exhausted resource still usable");
        restored.decode("bad;1,2,16;1,2,3;-4,-9,4;");
        ok(restored.exhausted(1,2,0)&&restored.exhausted(1,2,1),
           "multi-node cell mask missing");
        ok(restored.exhausted(-4,-9,2),"negative-coordinate persistence");
        restored.clear();
        ok(restored.depletedCells()==0,"new game does not reset gathering");
        System.out.println("V80 PASS world nodes="+found+" wood="+forest+
            " stone="+stone+" fiber="+fiber+" nearSpawn="+nearCamp);
    }
}
