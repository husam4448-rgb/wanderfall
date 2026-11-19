package com.survivalparadise.nativegame;

public final class V166InteriorArtTest {
    private static void check(boolean x,String m){if(!x)throw new AssertionError(m);}
    public static void main(String[] args){
        check(InteriorPropSelectionV166.SPRITES==32,
            "Combined 16 original + 16 specialized art cells");
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
        check(!InteriorPropSelectionV166.valid(32),
            "Invalid sprite accepted");
        boolean[] categories=new boolean[16];
        for(int theme=0;theme<8;theme++){
            for(int room=0;room<6;room++)
                for(int variation=0;variation<4;variation++)
                    for(int slot=0;slot<20;slot++){
                        int sprite=InteriorRoomArchetypeV166.sprite(
                            theme,room,variation,slot);
                        check(InteriorPropSelectionV166.valid(sprite),
                            "Semantic role invalid");
                        if(sprite>=16)categories[sprite-16]=true;
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
                if(sprite>=16)categories[sprite-16]=true;
                if(theme==3)
                    check(sprite!=4&&sprite!=5&&sprite!=26&&sprite!=27,
                        "Retail equipment in hotel commons");
                if(theme==4)
                    check(sprite!=10&&sprite!=11&&sprite!=28&&sprite!=29,
                        "Heavy machinery in school commons");
            }
        }
        for(int sprite=0;sprite<14;sprite++)
            check(categories[sprite],"Specialized room sprite never assigned: "+sprite);
        check(InteriorRoomArchetypeV166.legacy(0,0,true,0)==30,
            "Clinic bed replaced");
        check(InteriorRoomArchetypeV166.legacy(1,0,true,1)==31,
            "Clinic trolley replaced");
        check(InteriorPropSelectionV166.choose(-1,0,0,90,75)==-1,
            "Invalid family");
        System.out.println("PASS V166: 32 themed sprites; correct hotel/school, clinic and original identity");
    }
}
