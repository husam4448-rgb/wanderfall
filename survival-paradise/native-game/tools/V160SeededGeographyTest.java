package com.survivalparadise.nativegame;

/**
 * Seed diversity, natural transition, persisted version and harvest-art QA.
 * All checks are pure JVM and intentionally do not modify any save.
 */
public final class V160SeededGeographyTest {
    static void yes(boolean ok,String error){if(!ok)throw new AssertionError(error);}
    private static int delta(int a,int b){
        return Math.max(Math.max(
            Math.abs(((a>>>16)&255)-((b>>>16)&255)),
            Math.abs(((a>>>8)&255)-((b>>>8)&255))),
            Math.abs((a&255)-(b&255)));
    }
    public static void main(String[] args){
        int[] seeds={14901,87011,-999,0,20261117,113,9042026,777777};
        WorldGeographyV160[] worlds=new WorldGeographyV160[seeds.length];
        String[] serialized=new String[seeds.length];
        for(int i=0;i<seeds.length;i++){
            final int[] stage={-1};
            final int index=i;
            worlds[i]=WorldGeographyV160.prepare(seeds[i],(progress,label)->{
                yes(progress>=stage[0]&&progress<=100,
                    "loading phase not monotonic "+index);
                yes(label!=null&&!label.isEmpty(),"empty terrain phase");
                stage[0]=progress;
            });
            yes(stage[0]==100,"world not fully generated");
            serialized[i]=worlds[i].encode();
            yes(WorldGeographyV160.decode(serialized[i],seeds[i])!=null,
                "saved world climate could not reload");
            yes(WorldGeographyV160.decode(serialized[i],seeds[i]+1)==null,
                "foreign-world seed accepted");
            yes(WorldGeographyV160.decode(serialized[i]+"x",seeds[i])==null,
                "invalid world fingerprint accepted");
            yes(WorldGeographyV160.decode("",seeds[i])==null,
                "legacy world mysteriously became re-seeded");
            WorldGeographyV160 loaded=WorldGeographyV160.decode(
                serialized[i],seeds[i]);
            yes(loaded!=null,"invalid decode");
            int unique=0;boolean[] categories=new boolean[6];
            for(int x=-8;x<=8;x++)for(int y=-8;y<=8;y++){
                float xx=x*2900f+291f,yy=y*3450f+133f;
                int b=worlds[i].biomeAt(xx,yy);
                yes(b>=0&&b<6,"invalid biome type");
                if(!categories[b]){categories[b]=true;unique++;}
                yes(loaded.biomeAt(xx,yy)==b&&
                    loaded.colorAt(xx,yy)==worlds[i].colorAt(xx,yy),
                    "restarting the game changed geographic position");
            }
            yes(unique>=3,"seed has no distinct natural regions "+seeds[i]);
            // The historical starter camp remains pixel-perfect in all
            // V160 natural world maps regardless of biome climate.
            yes(worlds[i].colorAt(1080f,710f)==
                WorldChunkModel.groundColorAt(1080f,710f,1080,710),
                "starter camp appearance modified");
            // V160 changes resource POSITION and TYPE, not the cell+slot
            // harvested-state identity; legacy saves use null as before.
            for(int cx=-17;cx<=17;cx+=7)
                for(int cy=-11;cy<=11;cy+=5)
                    for(int slot=0;slot<ResourceWorldV80.SLOTS;slot++){
                        int h=ResourceWorldV80.seed(cx,cy,slot,worlds[i]);
                        ResourceWorldV80.Node node=ResourceWorldV80.node(
                            cx,cy,slot,1080,710,3200,2200,worlds[i]);
                        if(node==null)continue;
                        yes(node.seed==h,"resource sprite/loot hash mismatch");
                        int kind=slot==3?ResourceWorldV80.BUSH:
                            slot==2&&node.x>=0&&node.x<=3200&&
                            node.y>=0&&node.y<=2200?4:
                            worlds[i].prop(node.x,node.y,h);
                        yes(node.kind==kind,"harvestable item mismatches rendered type");
                    }
        }
        int changedBiomes=0,changedColors=0,changedResources=0,
            sampled=0;
        for(int x=-15;x<=15;x++)for(int y=-11;y<=11;y++){
            float wx=x*1770f+143f,wy=y*1890f+387f;
            sampled++;
            if(worlds[0].biomeAt(wx,wy)!=worlds[1].biomeAt(wx,wy))
                changedBiomes++;
            if(delta(worlds[0].colorAt(wx,wy),
                     worlds[1].colorAt(wx,wy))>=8)changedColors++;
            int cx=Math.floorDiv((int)wx,ResourceWorldV80.CELL),
                cy=Math.floorDiv((int)wy,ResourceWorldV80.CELL);
            if(ResourceWorldV80.seed(cx,cy,0,worlds[0])!=
               ResourceWorldV80.seed(cx,cy,0,worlds[1]))
                changedResources++;
        }
        yes(changedBiomes>sampled/6,
            "new seeds mostly reproduce identical biome maps");
        yes(changedColors>sampled/3,
            "new seed changes only labels without changing real terrain colors");
        yes(changedResources>sampled/2,
            "new seed does not change material location");
        // Neighboring pixels, including raster-chunk edges, must not show
        // hard-coded 72px discontinuities.
        for(int s=0;s<seeds.length;s++)
            for(int i=-16;i<=16;i++){
                float boundary=i*WorldChunkModel.CHUNK_SIZE;
                int left=worlds[s].colorAt(boundary-.025f,3911f);
                int right=worlds[s].colorAt(boundary+.025f,3911f);
                yes(delta(left,right)<=2,"hard visible chunk seam");
            }
        int alteredCivilization=0;
        for(int i=0;i<seeds.length;i++){
            WorldCivilizationV159.Plan newPlan=
                WorldCivilizationV159.generate(seeds[i],null,worlds[i]);
            WorldCivilizationV159.Plan restored=
                WorldCivilizationV159.decode(newPlan.encode(),seeds[i]);
            yes(restored!=null&&
                restored.encode().equals(newPlan.encode()),
                "seeded world settlement not persistent");
            yes(newPlan.parcels.length>10,
                "terrain erased all human settlements");
            yes(newPlan.atTile(0,0)==null,"seeded city paved the original camp");
            yes(newPlan.variedBuildingsV160&&restored.variedBuildingsV160,
                "seed-specific architecture mode lost in the save");
            WorldCivilizationV159.Plan legacyPlan=
                WorldCivilizationV159.generate(seeds[i],null);
            yes(!legacyPlan.variedBuildingsV160&&
                !WorldCivilizationV159.decode(legacyPlan.encode(),
                    seeds[i]).variedBuildingsV160,
                "V159 existing save unexpectedly moved its buildings");
            int changedArchitecture=0,buildingCount=0;
            for(WorldCivilizationV159.Parcel plot:newPlan.parcels){
                for(int slot=0;slot<NeighborhoodV154.COLS*NeighborhoodV154.ROWS;slot++){
                    NeighborhoodV154.Building old=NeighborhoodV154.get(
                        plot.tx,plot.ty,slot);
                    NeighborhoodV154.Building building=NeighborhoodV154.get(
                        plot.tx,plot.ty,slot,newPlan);
                    NeighborhoodV154.Building saved=NeighborhoodV154.get(
                        plot.tx,plot.ty,slot,restored);
                    if(old==null){yes(building==null,"invented invalid building");continue;}
                    buildingCount++;
                    yes(building!=null&&saved!=null,"seed deleted locked building slot");
                    yes(building.left==saved.left&&building.width==saved.width&&
                        building.height==saved.height&&building.kind==saved.kind,
                        "actual building changed coordinates on Continue");
                    yes(NeighborhoodV154.blocked(
                        building.left+building.width*.5f,
                        building.top+building.height*.5f,15f,newPlan),
                        "seed-specific roof is visually present but intangible");
                    yes(NeighborhoodV154.safe(building),
                        "seeded building overlaps historic highway or landmarks");
                    if(old.left!=building.left||old.top!=building.top||
                       old.kind!=building.kind||old.width!=building.width)
                        changedArchitecture++;
                }
            }
            yes(buildingCount>=20&&changedArchitecture>=buildingCount/2,
                "all seed worlds reuse the same building art/geometry");
            if(i>0){
                WorldCivilizationV159.Plan first=
                    WorldCivilizationV159.generate(seeds[0],null,worlds[0]);
                if(!first.encode().equals(newPlan.encode()))
                    alteredCivilization++;
            }
        }
        yes(alteredCivilization==seeds.length-1,
            "seed variance did not reach civilization plot layouts");
        System.out.println("PASS V160: "+seeds.length+
            " seeds tested, biome differences="+changedBiomes+"/"+sampled+
            ", terrain palette differences="+changedColors+"/"+sampled+
            ", resource coordinate differences="+changedResources+"/"+sampled+
            "; 6 biome IDs, continuous chunk borders, old-world save isolation"+
            " and validated climate-adapted civilization plots");
    }
}
