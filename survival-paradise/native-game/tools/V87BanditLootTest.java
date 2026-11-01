package com.survivalparadise.nativegame;
public final class V87BanditLootTest {
    static void ok(boolean b,String s){if(!b)throw new AssertionError(s);}
    public static void main(String[]args){
        BanditLootV87 model=new BanditLootV87();
        BanditLootV87.Bag first=model.spawn(1100,820,3,2,1);
        ok(first!=null&&first.total()>=3,"empty bandit bag");
        ok(first.count[BanditLootV87.MEDKIT]==1,"bandit loot types incorrect");
        ok(model.nearest(1100,820,100)==first,"USE can't select nearest bag");
        ok(model.nearest(1500,820,100)==null,"remote looting allowed");
        String encoded=model.encode();
        BanditLootV87 restored=new BanditLootV87();restored.decode(encoded);
        ok(restored.bags.size()==1,"save/continue loses bandit loot");
        BanditLootV87.Bag saved=restored.bags.get(0);
        int scrap=restored.take(saved,BanditLootV87.SCRAP);
        ok(scrap>0&&restored.take(saved,BanditLootV87.SCRAP)==0,"stack duplicates");
        ok(restored.bags.size()==1,"partial loot prematurely removed bag");
        BanditLootV87 loaded=new BanditLootV87();loaded.decode(restored.encode());
        ok(loaded.bags.size()==1&&loaded.bags.get(0).count[BanditLootV87.SCRAP]==0,
            "partially looted bag respawns items");
        int[] remaining=loaded.takeAll(loaded.bags.get(0));
        int sum=0;for(int n:remaining)sum+=n;
        ok(sum>=1&&loaded.bags.isEmpty(),"LOOT ALL leaves or duplicates contents");
        ok(loaded.takeAll(saved)[0]==0,"invalid bag reference allowed to loot");
        ok(loaded.encode().isEmpty(),"empty bags persisted");
        loaded.decode("bad;1,0,0,-1,0,0,0,0,0,0,0;0,20,20,1,1,1,1,1,1,1,1");
        ok(loaded.bags.isEmpty(),"corrupted loot accepted");
        for(int i=0;i<BanditLootV87.MAX_BAGS;i++)
            ok(loaded.spawn(i*30f,200,i+1,4,i%2)!=null,"max reached early");
        ok(loaded.spawn(9999,200,1,1,0)==null,"unbounded loot bag allocation");
        loaded.clear();ok(loaded.bags.isEmpty(),"New Game does not reset bags");
        System.out.println("V87 PASS loot bags, saved partial loot, LOOT ALL, no duplication, distance, max cap");
    }
}
