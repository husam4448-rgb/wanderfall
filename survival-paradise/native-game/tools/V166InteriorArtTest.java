package com.survivalparadise.nativegame;

public final class V166InteriorArtTest {
    private static void check(boolean x,String m){if(!x)throw new AssertionError(m);}
    public static void main(String[] args){
        check(InteriorPropSelectionV166.SPRITES==16,"Atlas cells");
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
        check(InteriorPropSelectionV166.choose(-1,0,0,90,75)==-1,
            "Invalid family");
        System.out.println("PASS V166: existing 16 props, 8 floors, corrected hotel/school semantic roles");
    }
}
