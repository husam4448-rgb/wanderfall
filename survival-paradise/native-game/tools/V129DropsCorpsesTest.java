package com.survivalparadise.nativegame;

public final class V129DropsCorpsesTest {
    private static void ok(boolean v,String message){
        if(!v)throw new AssertionError(message);
    }
    public static void main(String[] args){
        DroppedItemsV129 ground=new DroppedItemsV129();
        final float now=DroppedItemsV129.time(3,600f);
        DroppedItemsV129.Stack outdoors=ground.drop(6,27,925f,1055f,
            "world",now,2);
        DroppedItemsV129.Stack indoors=ground.drop(30,1,450f,500f,
            "industrial:14901:2:0",now,1);
        ok(outdoors!=null&&indoors!=null,"real stacks must spawn");
        ok(ground.nearest(925,1055,"world",110)==outdoors,"outdoor pickup");
        ok(ground.nearest(450,500,"world",110)==null,"indoor stack leaked outdoors");
        ok(ground.nearest(450,500,"industrial:14901:2:0",110)==indoors,
            "indoor scene identity");
        ok(ground.drop(5,0,120,80,"world",now,2)==null,"zero quantity allowed");
        ok(ground.drop(40,1,120,80,"world",now,2)==null,"invalid item allowed");
        String saved=ground.encode();
        DroppedItemsV129 loaded=new DroppedItemsV129();
        loaded.decode(saved);
        ok(loaded.stacks.size()==2,"dropped items did not restore");
        ok(loaded.stacks.get(0).quantity==27,"quantity changed on reload");
        ok(loaded.stacks.get(1).type==30,"gear type lost");
        loaded.expire(now+1439f);
        ok(loaded.stacks.size()==2,"stacks expired too early");
        loaded.expire(now+1441f);
        ok(loaded.stacks.size()==1&&loaded.stacks.get(0).type==6,
            "one-day stack should expire before two-day");
        loaded.expire(now+2881f);
        ok(loaded.stacks.isEmpty(),"two-day expiry failed");
        loaded.decode(saved);
        ok(loaded.take(loaded.stacks.get(0))&&loaded.stacks.size()==1,
            "recovery not removing exactly one stack");
        loaded.decode("garbage;99,40,-1,NaN,1,100,world");
        ok(loaded.stacks.isEmpty(),"bad save data should be rejected");
        BanditLootV87 bodies=new BanditLootV87();
        BanditLootV87.Bag dead=bodies.spawnCorpse(650,770,5,2,1,-1);
        ok(dead!=null&&dead.corpse&&dead.face==-1,"corpse metadata");
        int[] loot=bodies.takeAll(dead);
        ok(loot[BanditLootV87.AMMO]>0,"NPC carries no ammo");
        ok(bodies.contains(dead)&&dead.empty(),"searched body vanished");
        String persisted=bodies.encode();
        BanditLootV87 restored=new BanditLootV87();
        restored.decode(persisted);
        ok(restored.bags.size()==1&&restored.bags.get(0).corpse&&
            restored.bags.get(0).empty(),"empty corpse did not persist");
        BanditLootV87.Bag cache=restored.spawn(100,200,3,2,0);
        ok(cache!=null&&!cache.corpse,"supply cache became corpse");
        restored.takeAll(cache);
        ok(!restored.contains(cache),"old supply cache must be removed when looted");
        BanditLootV87 old=new BanditLootV87();
        old.decode("17,550,600,2,0,3,0,0,0,0,0");
        ok(old.bags.size()==1&&!old.bags.get(0).corpse,
            "legacy V87 saved supply bag incompatible");
        System.out.println("PASS V129: quantity, 39 items, drop/recover, "+
            "indoor/outdoor isolation, 1-2 day expiry, persistent corpses and V87 migration");
    }
}
