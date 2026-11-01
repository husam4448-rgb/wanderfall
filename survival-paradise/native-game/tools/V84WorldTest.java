package com.survivalparadise.nativegame;

/** Scrap location/persistence, crowbar animation, crafted inventory and manual placement. */
public final class V84WorldTest {
    static void ok(boolean valid,String reason){if(!valid)throw new AssertionError(reason);}
    static final float CX=1080f,CY=710f,W=3200f,H=2200f;
    static SalvageWorldV84.Node find(int kind){
        for(int y=-8;y<8;y++)for(int x=-8;x<8;x++)
        for(int slot=0;slot<SalvageWorldV84.SLOTS;slot++){
            SalvageWorldV84.Node n=SalvageWorldV84.node(x,y,slot,CX,CY,W,H);
            if(n!=null&&n.type==kind)return n;
        }
        throw new AssertionError("Missing wreck type "+kind);
    }
    static void extract(int kind,int fps){
        SalvageWorldV84 w=new SalvageWorldV84();
        SalvageWorldV84.Node n=find(kind);
        HarvestActionV81 action=new HarvestActionV81();
        ok(action.beginScrap(n),"no crowbar action");
        ok(!action.beginScrap(n),"overlapping action");
        ok(!w.exhausted(n.cx,n.cy,n.slot),"instant scrap");
        int impacts=0,frames=0;
        while(action.active&&frames<500){
            if(action.advance(1f/fps))impacts++;
            ok(!w.exhausted(n.cx,n.cy,n.slot),"premature depletion");
            frames++;
        }
        ok(action.finished&&impacts==action.hitsRequired,"missing impacts");
        ok(action.canCompleteScrap(n.x,n.y,SalvageWorldV84.REACH,false),
            "completed loot denied");
        ok(!action.canCompleteScrap(n.x+300,n.y,SalvageWorldV84.REACH,false),
            "distance bypass");
        ok(w.harvest(n)&&!w.harvest(n),"duplicated scrap");
        SalvageWorldV84 restored=new SalvageWorldV84();
        restored.decode(w.encode());
        ok(restored.exhausted(n.cx,n.cy,n.slot),"depleted source respawned");
        ok(restored.nearest(n.x,n.y,1,CX,CY,W,H)==null,"exhausted node targetable");
        action.cancel();ok(action.salvageTarget==null,"tool not reset");
    }
    public static void main(String[]args){
        int near=0;
        for(int y=-2;y<6;y++)for(int x=-2;x<6;x++)
        for(int slot=0;slot<SalvageWorldV84.SLOTS;slot++){
            SalvageWorldV84.Node n=SalvageWorldV84.node(x,y,slot,CX,CY,W,H);
            if(n==null)continue;
            SalvageWorldV84.Node b=SalvageWorldV84.node(x,y,slot,CX,CY,W,H);
            ok(n.x==b.x&&n.y==b.y&&n.type==b.type,"inconsistent scrap spawn");
            if(Math.hypot(n.x-CX,n.y-CY)<1200)near++;
        }
        ok(near>=2,"not enough accessible starting scrap");
        for(int kind=0;kind<3;kind++){
            SalvageWorldV84.Node node=find(kind);
            HarvestActionV81 canceled=new HarvestActionV81();
            canceled.beginScrap(node);canceled.advance(.1f);canceled.cancel();
            ok(!canceled.finished&&canceled.salvageTarget==null,
                "canceled scrap would be awarded");
            for(int fps:new int[]{30,60,90,120})extract(kind,fps);
        }
        CampCraftV83 c=new CampCraftV83();int[] stock={20,12,10,8};
        ok(c.craftToBag(0,stock),"barricade crafting");
        ok(c.objects.isEmpty()&&c.stock[0]==1,"crafted barricade auto-placed");
        ok(stock[0]==16&&stock[1]==10,"barricade cost");
        ok(c.craftToBag(1,stock),"lamp crafting");
        ok(c.objects.isEmpty()&&c.stock[1]==1,"crafted lamp auto-placed");
        CampCraftV83 loaded=new CampCraftV83();
        loaded.decode(c.encode());loaded.decodeStock(c.encodeStock());
        ok(loaded.stock[0]==1&&loaded.stock[1]==1,"crafted stock lost");
        ok(loaded.placeFromBag(0,1120,810),"cannot place stored barricade");
        ok(loaded.stock[0]==0&&loaded.objects.size()==1,"barricade count wrong");
        ok(!loaded.placeFromBag(1,1125,812),"overlapping lamp allowed");
        ok(loaded.stock[1]==1,"invalid placement consumed item");
        ok(loaded.placeFromBag(1,1450,810),"can't place light post");
        ok(loaded.stock[1]==0&&loaded.objects.size()==2,"lamp stock wrong");
        CampCraftV83 persisted=new CampCraftV83();
        persisted.decode(loaded.encode());persisted.decodeStock(loaded.encodeStock());
        ok(persisted.objects.size()==2,"placed structures lost");
        persisted.clear();
        ok(persisted.stock[0]==0&&persisted.objects.size()==0,"new game reset failed");
        System.out.println("V84 PASS "+near+" near-spawn wrecks, 3 salvage sources, crowbar impacts "+
            "30/60/90/120FPS, persisted depletion, stored craftables, placement validation");
    }
}
