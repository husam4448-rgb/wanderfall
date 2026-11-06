package com.survivalparadise.nativegame;

public final class V131InventoryHeadTest {
    private static void ok(boolean b,String why){
        if(!b)throw new AssertionError(why);
    }
    private static void close(float a,float b,String name){
        ok(Math.abs(a-b)<.001f,name+": "+a+" vs "+b);
    }
    public static void main(String[] args){
        String[] names=new String[InventoryCatalogV131.COUNT];
        for(int i=0;i<names.length;i++)names[i]=String.format("ITEM %02d",i);
        ok(InventoryCatalogV131.WEIGHT.length==39,"39 item weights");
        ok(InventoryCatalogV131.weight(36)>InventoryCatalogV131.weight(27),
            "boots should weigh more than caps");
        ok(InventoryCatalogV131.weight(0)==.8f,"preserve scrap mass");
        ok(InventoryCatalogV131.weight(14)==FieldFindsV91Weight.clothWeight,
            "preserve scavenged cloth mass");
        ok(InventoryCatalogV131.compare(29,24,1,names)>0,
            "type sort should put packs before headgear");
        ok(InventoryCatalogV131.compare(31,27,2,names)<0,
            "weight sort should put heavy coat before cap");
        names[24]="Zebra Pack";names[27]="Alpha Cap";
        ok(InventoryCatalogV131.compare(27,24,3,names)<0,
            "alphabetical name sort must ignore original item order");
        for(int type=24;type<39;type++){
            int slot=InventoryCatalogV131.equipmentSlot(type);
            ok(slot>=0&&slot<=5,"invalid equipment slot");
            ok(InventoryCatalogV131.compatible(type,slot),
                "own equipment slot rejected "+type);
            for(int s:new int[]{0,1,2,3,4,5})
                if(s!=slot)ok(!InventoryCatalogV131.compatible(type,s),
                    "incorrect body-part attachment allowed");
        }
        ok(!InventoryCatalogV131.compatible(16,2),
            "cannot equip battery as jacket");
        for(float width:new float[]{360f,480f,720f,1480f}){
            float center=TopHudV76.x(TopHudV76.PAUSE,width)
                +TopHudV76.buttonWidth(TopHudV76.PAUSE,width)*.5f;
            close(center,width*.5f,"top-centered pause");
            for(int a=0;a<TopHudV76.COUNT;a++)for(int b=a+1;
                b<TopHudV76.COUNT;b++){
                float ax=TopHudV76.x(a,width),bx=TopHudV76.x(b,width);
                float ar=ax+TopHudV76.buttonWidth(a,width);
                float br=bx+TopHudV76.buttonWidth(b,width);
                ok(ar<=bx+.01f||br<=ax+.01f,"HUD button overlap");
            }
        }
        float[] standard=HeadCollisionV131.worldBounds(
            500,700,1,-21,-115,28,-60,0);
        float[] mirrored=HeadCollisionV131.worldBounds(
            500,700,-1,-21,-115,28,-60,0);
        close(standard[2]-standard[0],mirrored[2]-mirrored[0],
            "mirrored head collider width");
        float t=HeadCollisionV131.firstHit(400,607,610,607,standard);
        ok(t>0f&&t<1f,"fast projectile must hit real fitted head");
        ok(!Float.isFinite(HeadCollisionV131.firstHit(400,750,610,750,standard)),
            "missed shot incorrectly hits head");
        float[] large=HeadCollisionV131.worldBounds(
            500,700,1,-34,-138,44,-55,0);
        ok((large[2]-large[0])>(standard[2]-standard[0]),
            "larger head slider must widen collision");
        ok((large[3]-large[1])>(standard[3]-standard[1]),
            "larger head slider must increase collider height");
        float[] tilted=HeadCollisionV131.worldBounds(
            500,700,1,-21,-115,28,-60,18);
        ok((tilted[2]-tilted[0])>(standard[2]-standard[0]),
            "tilting head expands forgiving collision region");
        BanditLootV87 bodies=new BanditLootV87();
        BanditLootV87.Bag dead=bodies.spawnCorpse(760,930,2,4,1,-1,147);
        ok(dead!=null&&dead.skinV109==147&&dead.face==-1,
            "dead bandit did not preserve exact living head/skin");
        BanditLootV87 restored=new BanditLootV87();
        restored.decode(bodies.encode());
        ok(restored.bags.size()==1&&restored.bags.get(0).skinV109==147,
            "saved corpse changed character identity");
        restored.decode("17,550,600,2,0,3,0,0,0,0,0");
        ok(restored.bags.size()==1&&!restored.bags.get(0).corpse,
            "pre-V129 bag saves must remain compatible");
        System.out.println("PASS V131: 39 weights, all equipment types, sort modes, top PAUSE, "+
            "fitted mirrored headshot rays and preserved corpse identities");
    }
    // This is the exact unit weight from FieldFindsV91.weight().
    static class FieldFindsV91Weight {static final float clothWeight=.5f;}
}
