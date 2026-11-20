package com.survivalparadise.nativegame;

public final class V166InteriorArtTest {
    private static void check(boolean x,String m){if(!x)throw new AssertionError(m);}
    public static void main(String[] args){
        check(InteriorPropSelectionV166.SPRITES==160,
            "Original 16 + specialized 16 + story 16 + ensemble 16");
        check(InteriorPropSelectionV166.CELL==256,"Atlas dimensions");
        for(int theme=0;theme<NeighborhoodV154.TYPES;theme++){
            int seen=0;
            for(int i=0;i<60;i++){
                int kind=i%6;
                float width=68+i%55,height=57+i%39;
                int sprite=InteriorPropSelectionV166.choose(
                    theme,kind,i,width,height);
                check(InteriorPropSelectionV166.valid(sprite),"Index invalid");
                check(sprite/2==theme,"Wrong family");
                check(sprite==InteriorPropSelectionV166.choose(
                    theme,kind,i,width,height),"Index unstable");
                seen|=1<<(sprite%2);

            }
            check(seen==3,"Missing visual variant for family "+theme);
        }
        // All direct-role furniture must remain visually plausible for its
        // actual room. A successful Android run does not certify art quality.
        // Regression: the former hotel reception used supermarket checkout #5.
        for(int room=0;room<6;room++){
            for(int variation=0;variation<4;variation++){
                for(int slot=0;slot<48;slot++){
                    int hotel=InteriorRoomArchetypeV166.sprite(3,room,variation,slot);
                    int school=InteriorRoomArchetypeV166.sprite(4,room,variation,slot);
                    check(InteriorPropSelectionV166.valid(hotel),"Hotel role invalid");
                    check(InteriorPropSelectionV166.valid(school),"School role invalid");
                    check(hotel!=4&&hotel!=5,"Supermarket furniture in hotel");
                    if(room==0) {
                        int kind=InteriorFurnitureCatalogV166.kind(hotel);
                        if(kind>=0)check(kind!=4&&kind!=5&&kind!=14,
                            "Hotel reception contains sink, dining set or cooler");
                    }
                    check(school!=10&&school!=11,
                        "Factory machine in classroom/laboratory");
                }
            }
        }
        for(int station=0;station<90;station++)
            for(int variation=0;variation<4;variation++){
                int hotel=InteriorRoomArchetypeV166.shared(3,station,variation);
                int school=InteriorRoomArchetypeV166.shared(4,station,variation);
                check(hotel!=4&&hotel!=5,
                    "Supermarket checkout in hotel lobby");
                int hotelKind=InteriorFurnitureCatalogV166.kind(hotel);
                check(hotelKind!=4&&hotelKind!=5&&hotelKind!=14,
                    "Hotel commons contain sink, dining set or refrigerator");
                check(school!=10&&school!=11,
                    "Factory machinery in school commons");
            }
        // Existing exact original atlas indices remain immutable, while
        // direct role tags 32..47 select the specialized atlas 16..31.
        for(int sprite=16;sprite<32;sprite++){
            check(InteriorPropSelectionV166.valid(sprite),"Special invalid");
            check(InteriorPropSelectionV166.choose(3,sprite+16,0,150,90)
                ==sprite,"Special direct-role mapping changed");
            check(InteriorRoomArchetypeV166.width(sprite)>55,
                "Special width missing");
            check(InteriorRoomArchetypeV166.height(sprite)>55,
                "Special height missing");
        }
        check(InteriorPropSelectionV166.valid(64)&&
            InteriorPropSelectionV166.valid(159)&&
            !InteriorPropSelectionV166.valid(160),
            "V166 extended furniture indices invalid");
        boolean[] categories=new boolean[16];
        for(int theme=0;theme<8;theme++){
            for(int room=0;room<6;room++)
                for(int variation=0;variation<4;variation++)
                    for(int slot=0;slot<20;slot++){
                        int sprite=InteriorRoomArchetypeV166.sprite(
                            theme,room,variation,slot);
                        check(InteriorPropSelectionV166.valid(sprite),
                            "Semantic role invalid");
                        if(sprite>=16&&sprite<32)categories[sprite-16]=true;
                        if(theme==3)
                            check(sprite!=4&&sprite!=5&&sprite!=26&&sprite!=27,
                                "Retail checkout in hotel");
                        if(theme==4)
                            check(sprite!=10&&sprite!=11&&sprite!=28&&sprite!=29,
                                "Industrial machinery in school");
                    }
            for(int station=0;station<80;station++){
                int sprite=InteriorRoomArchetypeV166.shared(theme,station,0);
                check(InteriorPropSelectionV166.valid(sprite),
                    "Common area role invalid");
                if(sprite>=16&&sprite<32)categories[sprite-16]=true;
                if(theme==3)
                    check(sprite!=4&&sprite!=5&&sprite!=26&&sprite!=27,
                        "Retail equipment in hotel commons");
                if(theme==4)
                    check(sprite!=10&&sprite!=11&&sprite!=28&&sprite!=29,
                        "Heavy machinery in school commons");
            }
        }
        // Every newly authored set-piece index is reachable in some
        // actual room/shared area; none is a dead asset or a random prop.
        boolean[] newScenes=new boolean[16];
        boolean[] ensembles=new boolean[16];
        for(int theme=0;theme<8;theme++){
            for(int room=0;room<6;room++)
                for(int variation=0;variation<4;variation++)
                    for(int slot=0;slot<21;slot++){
                        int sprite=InteriorRoomArchetypeV166.sprite(
                            theme,room,variation,slot);
                        if(sprite>=32&&sprite<48)newScenes[sprite-32]=true;
                        if(sprite>=48&&sprite<64)ensembles[sprite-48]=true;
                    }
            for(int station=0;station<12;station++){
                int sprite=InteriorRoomArchetypeV166.shared(theme,station,0);
                if(sprite>=32&&sprite<48)newScenes[sprite-32]=true;
                        if(sprite>=48&&sprite<64)ensembles[sprite-48]=true;
            }
        }
        for(int i=0;i<16;i++){
            check(InteriorPropSelectionV166.choose(2,i+48,0,100,100)==i+32,
                "New 32..47 direct role tag changed");
            check(InteriorRoomArchetypeV166.width(i+32)>50,
                "Missing new set-piece dimensions");
        }
        // Complete semantic set pieces use only existing authored sprites.
        for(int group=48;group<64;group++){
            int[][] recipe=InteriorScenePlanV166.parts(group);
            check(recipe.length>=2,"Single-object ensemble");
            check(InteriorPropSelectionV166.choose(2,group+16,0,140,100)==group,
                "Direct grouping role changed");
            for(int[] part:recipe){
                check(part.length==5,"Invalid scene component");
                check(part[0]>=0&&part[0]<48,"Recursive/invalid child");
                check(part[1]>=0&&part[2]>=0&&part[3]>0&&part[4]>0,
                    "Invalid part bounds");
                check(part[1]+part[3]<=1000&&part[2]+part[4]<=1000,
                    "Set piece overhangs collision footprint");
            }
        }
        // Semantic coverage: 12 *distinct* functional objects for every
        // building type, selected by named room instead of density tricks.
        for(int theme=0;theme<8;theme++){
            boolean[] seen=new boolean[12];
            for(int room=0;room<6;room++){
                java.util.HashSet<Integer> roomSprites=new java.util.HashSet<>();
                for(int slot=0;slot<8;slot++){
                    int sprite=InteriorRoomArchetypeV166.directional(
                        theme,room,0,slot);
                    check(InteriorFurnitureCatalogV166.valid(sprite),
                        "Non-directional furniture in role library");
                    check(InteriorFurnitureCatalogV166.kind(sprite)>=0,
                        "Missing actual furnishing model");
                    check(InteriorFurnitureCatalogV166.width(sprite)>=90f &&
                          InteriorFurnitureCatalogV166.height(sprite)>=77f,
                        "Miniature in functional furnishing library");
                    roomSprites.add(sprite);
                    seen[sprite-64-theme*12]=true;
                }
                // A coherent classroom or bedroom has six true functional
                // furnishing types; forcing seven introduced printers, file
                // cabinets and dining equipment into inappropriate rooms.
                check(roomSprites.size()>=6,
                    "Room lacks six distinct functional furniture models");
            }
            // The real room layout matters more than the raw number of
            // different prop IDs. Explicitly reject unsuitable classroom,
            // domestic kitchen and sleeping-room objects.
            for(int room=0;room<6;room++)for(int slot=0;slot<8;slot++){
                int sprite=InteriorRoomArchetypeV166.directional(
                    theme,room,0,slot);
                int kind=InteriorFurnitureCatalogV166.kind(sprite);
                if(theme==4&&(room==0||room==1))
                    check(kind!=5&&kind!=10&&kind!=28,
                        "Classroom polluted by dining table, files or printer");
                if(theme==0&&(room==1||room==4))
                    check(kind!=3&&kind!=4&&kind!=5&&kind!=10,
                        "Apartment bedroom has kitchen, dining or filing equipment");
                if(theme==7&&room==1)
                    check(kind!=3&&kind!=4&&kind!=31,
                        "Residence bedroom has cooker, dining set or kitchen island");
                if(theme==7&&room==2)
                    check(kind!=0&&kind!=6&&kind!=30,
                        "Residence kitchen has sofa, office desk or dresser");
            }
            int variety=0;
            for(boolean s:seen)if(s)variety++;
            check(variety>=10,"Theme lacks substantial object variety: "+theme);
        }
        check(InteriorRoomArchetypeV166.legacy(0,0,true,0)==30,
            "Clinic bed replaced");
        check(InteriorRoomArchetypeV166.legacy(1,0,true,1)==31,
            "Clinic trolley replaced");
        check(InteriorPropSelectionV166.choose(-1,0,0,90,75)==-1,
            "Invalid family");
        System.out.println("PASS V166: 64 legacy and 96 new directional role sprites; contextual selection and identity");
    }
}
