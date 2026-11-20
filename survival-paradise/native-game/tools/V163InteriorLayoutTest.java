package com.survivalparadise.nativegame;

import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.HashSet;

/** V163: prove walls, collision, room topology, seed identity and saves. */
public final class V163InteriorLayoutTest {
    private static void check(boolean ok,String detail){
        if(!ok)throw new AssertionError(detail);
    }
    private static boolean[] reachable(ClinicNavV90 nav){
        boolean[] seen=new boolean[nav.w*nav.h];
        ArrayDeque<Integer> q=new ArrayDeque<>();
        int x=(int)(ClinicInteriorV89.ENTRANCE_X/ClinicNavV90.CELL),
            y=(int)(ClinicInteriorV89.ENTRANCE_Y/ClinicNavV90.CELL);
        int initial=y*nav.w+x;
        check(nav.free[initial],"Entry blocked in nav grid");
        q.add(initial);seen[initial]=true;
        int[] dx={-1,1,0,0},dy={0,0,-1,1};
        while(!q.isEmpty()){
            int id=q.removeFirst(),cx=id%nav.w,cy=id/nav.w;
            for(int k=0;k<4;k++){
                int nx=cx+dx[k],ny=cy+dy[k];
                if(nx<0||ny<0||nx>=nav.w||ny>=nav.h)continue;
                int next=ny*nav.w+nx;
                if(nav.free[next]&&!seen[next]){seen[next]=true;q.addLast(next);}
            }
        }
        return seen;
    }
    private static boolean nearby(boolean[] seen,ClinicNavV90 nav,float x,float y){
        int ix=(int)(x/ClinicNavV90.CELL),iy=(int)(y/ClinicNavV90.CELL);
        for(int dy=-3;dy<=3;dy++)for(int dx=-3;dx<=3;dx++){
            int a=ix+dx,b=iy+dy;
            if(a<0||b<0||a>=nav.w||b>=nav.h)continue;
            if(seen[b*nav.w+a])return true;
        }
        return false;
    }
    public static void main(String[] args){
        HashSet<Integer> topology=new HashSet<>(),geometry=new HashSet<>();
        int tested=0,lootPreserved=0,allProps=0,minProps=Integer.MAX_VALUE,maxProps=0;
        int composedGroups=0,roomMin=Integer.MAX_VALUE,roomsBelowSix=0;
        int downward=0,sideways=0,roomsNoDown=0,roomsNoSide=0;
        int directional=0,nonSolidFake=0,miniatures=0,sparseLog=0;
        int[] histogram=new int[11];
        java.util.HashSet<Integer> furnishedRoles=new java.util.HashSet<>();
        for(int seed:new int[]{14901,87011,31526,58923}){
            WorldGeographyV160 earth=WorldGeographyV160.prepare(seed,null);
            WorldCivilizationV159.Plan plan=WorldCivilizationV159.generate(
                seed,null,earth);
            for(WorldCivilizationV159.Parcel parcel:plan.parcels){
                for(int slot=0;slot<NeighborhoodV154.COLS*NeighborhoodV154.ROWS;slot++){
                    NeighborhoodV154.Building b=NeighborhoodV154.get(
                        parcel.tx,parcel.ty,slot,plan);
                    if(b==null)continue;
                    NeighborhoodInteriorV161 room=new NeighborhoodInteriorV161(b,seed);
                    NeighborhoodLayoutV163 layout=room.layoutV163;
                    check(layout.walls.length>12,"Missing physical room partitions");
                    check(layout.rooms.length==6&&layout.doors.length==6,
                        "Room/door topology not generated");
                    // Density evidence is counted from actual seeded object
                    // rectangles, not the number of attempted placements.
                    int nProps=layout.furniture.length;
                    for(float[] q:layout.furniture){
                        if((int)q[0]>=64&&(int)q[0]<80)composedGroups++;
                        if(q.length>6&&q[6]==1f)nonSolidFake++;
                        int art=(int)q[0]-16;
                        if(InteriorFurnitureCatalogV166.valid(art)){
                            directional++;
                            furnishedRoles.add(art);
                            if(q[3]/ClinicInteriorV89.EXPANSION_V90<49f||
                               q[4]/ClinicInteriorV89.EXPANSION_V90<42f)
                                miniatures++;
                        }
                    }
                    for(int roomIndex=0;roomIndex<layout.rooms.length;roomIndex++){
                        float[] roomBox=layout.rooms[roomIndex];
                        int roomProps=0,frontCount=0,sideCount=0;
                        for(float[] q:layout.furniture){
                            if(q[1]>=roomBox[0]&&q[2]>=roomBox[1]&&
                               q[1]+q[3]<=roomBox[0]+roomBox[2]&&
                               q[2]+q[4]<=roomBox[1]+roomBox[3]){
                                roomProps++;
                                if(q.length>5){
                                    if((int)q[5]==0){downward++;frontCount++;}
                                    if((int)q[5]==90||(int)q[5]==270){
                                        sideways++;sideCount++;
                                    }
                                }
                            }
                        }
                        roomMin=Math.min(roomMin,roomProps);
                        histogram[Math.min(roomProps,10)]++;
                        if(frontCount==0)roomsNoDown++;
                        if(sideCount==0)roomsNoSide++;
                        if(roomProps<6)roomsBelowSix++;
                        if(roomProps<3&&sparseLog++<24)
                            System.out.println("NEEDS_FURNITURE seed="+seed+
                                " theme="+room.theme+" plan="+layout.plan+
                                " room="+roomIndex+" size="+
                                (int)(roomBox[2]/ClinicInteriorV89.EXPANSION_V90)+
                                "x"+(int)(roomBox[3]/ClinicInteriorV89.EXPANSION_V90)+
                                " solid="+roomProps);
                    }
                    allProps+=nProps;
                    minProps=Math.min(minProps,nProps);
                    maxProps=Math.max(maxProps,nProps);
                    check(layout.caches.length==14&&room.storages.length==14,
                        "Container save indices changed");
                    check(!room.blocked(ClinicInteriorV89.ENTRANCE_X,
                        ClinicInteriorV89.ENTRANCE_Y,12f),"Blocked entrance");
                    check(!room.blocked(ClinicInteriorV89.EXIT_X,
                        ClinicInteriorV89.EXIT_Y,12f),"Blocked exit");
                    ClinicNavV90 nav=new ClinicNavV90(room);
                    boolean[] seen=reachable(nav);
                    for(float[] z:layout.rooms){
                        float midX=z[0]+z[2]/2,midY=z[1]+z[3]/2;
                        check(nearby(seen,nav,midX,midY),
                            "Unreachable room in topology "+layout.plan);
                    }
                    for(float[] door:layout.doors)
                        check(nearby(seen,nav,door[0],door[1]),
                            "Door inaccessible in topology "+layout.plan);
                    for(ClinicInteriorV89.Storage item:room.storages)
                        check(nearby(seen,nav,item.x,item.y),
                            "Container inaccessible: seed="+seed+" theme="+room.theme+
                            " topology="+layout.plan+" cache="+item.x+","+item.y);
                    int signature=Arrays.deepHashCode(layout.walls);
                    geometry.add(signature);
                    topology.add(layout.plan);
                    String saved=room.encode();
                    NeighborhoodInteriorV161 reentered=new NeighborhoodInteriorV161(b,seed);
                    reentered.decode(saved);
                    check(saved.equals(reentered.encode()),
                        "Container contents changed on re-entry");
                    check(Arrays.deepEquals(layout.furniture,
                            reentered.sceneFurniture()),
                        "Same building regenerated a different furniture plan");
                    check(Arrays.deepEquals(layout.walls,reentered.sceneWalls()),
                        "Same building regenerated a different interior");
                    check(Arrays.deepEquals(room.decorV166,reentered.decorV166),
                        "Ambient decorations differ after re-entry");
                    // No floor decals are preferable to loose paper/bolt
                    // scatter, especially on industrial concrete floors.
                    if(room.theme==NeighborhoodV154.FACTORY||
                       room.theme==NeighborhoodV154.WAREHOUSE)
                        check(room.decorV166.length==0,
                            "Industrial floor uses fake cosmetic clutter");
                    for(float[] d:room.decorV166){
                        check(d.length==5&&d[3]>0f&&d[4]>0f,
                            "Invalid walk-through decoration");
                        for(float[] furnishing:layout.furniture){
                            check(d[1]+d[3]<=furnishing[1]||
                                  d[1]>=furnishing[1]+furnishing[3]||
                                  d[2]+d[4]<=furnishing[2]||
                                  d[2]>=furnishing[2]+furnishing[4],
                                  "Ambient detail overlaps solid furniture");
                        }
                    }
                    lootPreserved++;tested++;
                    if(tested>85&&topology.size()==NeighborhoodLayoutV163.PLAN_COUNT)break;
                }
                if(tested>85&&topology.size()==NeighborhoodLayoutV163.PLAN_COUNT)break;
            }
        }
        System.out.println("V166_DENSITY_METRICS buildings="+tested+
            " roomMin="+roomMin+" belowSix="+roomsBelowSix+
            " missingSide="+roomsNoSide+" missingFront="+roomsNoDown+
            " directional="+directional+" totalFurniture="+allProps+
            " histogram0to10plus="+java.util.Arrays.toString(histogram));
        check(tested>=20,"Too few buildings inspected");
        // Count of decals or small wall-notes is never a quality criterion.
        check(nonSolidFake==0,"Fake wall-note objects still in layout");
        check(miniatures==0,"Miniature furniture generated to pad counts");
        check(directional>tested*8,"New directional props not actually used");
        check(furnishedRoles.size()>=55,"Insufficient furniture vocabulary in layouts");
        check(roomMin>=3,"Room needs at least three substantial furniture objects");
        check(roomsBelowSix<=tested*4,
            "Too many rooms have fewer than six distinct furniture objects: "+roomsBelowSix);
        check(roomsNoSide<=tested*2,
            "Too many rooms lack side-facing furniture: "+roomsNoSide);
        // Structural semantics must be enforced per named room, not only by
        // the building theme. Warehouses must not look like open-plan offices.
        for(int theme=0;theme<8;theme++)for(int idx=0;idx<6;idx++)
            for(int variation=0;variation<4;variation++)
                for(int slot=0;slot<16;slot++){
                    int sprite=InteriorRoomArchetypeV166.directional(theme,idx,variation,slot);
                    check(InteriorRoomArchetypeV166.isRoomFurniture(theme,idx,variation,sprite),
                        "Incompatible furnishing in room "+theme+"/"+idx);
                    int kind=InteriorFurnitureCatalogV166.kind(sprite);
                    int actual=idx;
                    if((variation&1)!=0){
                        if(actual==1)actual=2;else if(actual==2)actual=1;
                    }
                    if((variation&2)!=0){
                        if(actual==4)actual=5;else if(actual==5)actual=4;
                    }
                    if(theme==6&&actual<5)check(kind!=6,
                        "Office desk placed in warehouse stock or handling area");
                    if(theme==2&&actual<5)check(kind!=6,
                        "Office desk placed in shop floor or market storage");
                    if(theme==0&&actual==2)check(kind!=0&&kind!=6,
                        "Bed or computer workstation in apartment kitchen");
                    if(theme==0&&actual==3)
                        check(kind!=0&&kind!=1&&kind!=3&&kind!=5&&kind!=6,
                            "Inappropriate living/dining furniture in apartment utility");
                    if(theme==3&&(actual==2||actual==5))
                        check(kind!=5&&kind!=14,
                            "Dining table or supermarket cooler in hotel service room");
                    if(theme==4&&(actual==0||actual==1))
                        check(kind!=5,"Generic dining table in classroom");
                }

        check(topology.size()==NeighborhoodLayoutV163.PLAN_COUNT,
            "Floor plans are not sufficiently diverse: "+topology);
        check(geometry.size()>15,"Different buildings reused indistinguishable wall layouts");
        check(lootPreserved==tested,"Lost a saved loot container");
        System.out.println("PASS V163: "+tested+" buildings, "+
            topology.size()+" layout families, "+geometry.size()+
            " distinct wall sets, reachable doors and preserved loot; "+
            "furniture min/mean/max="+minProps+"/"+(allProps/tested)+"/"+maxProps+
            "; complete scene ensembles="+composedGroups+
            "; individual props per room minimum="+roomMin+
            "; rooms below six="+roomsBelowSix+
            "; front/side orientations="+downward+"/"+sideways+
            "; rooms missing down-facing="+roomsNoDown+
            "; rooms missing side-facing="+roomsNoSide);
    }
}
