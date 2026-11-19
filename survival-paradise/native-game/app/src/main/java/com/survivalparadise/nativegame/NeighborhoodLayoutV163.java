package com.survivalparadise.nativegame;

import java.util.ArrayList;

/**
 * V163 genuinely distinct, seeded floor plans. Six topologies with per-site
 * geometry, room widths, door anchors, furniture, supplies and encounter points.
 * Pure Java: the same walls drive drawing, collision, LOS and NPC navmesh.
 * Save identities and all 14 container indexes stay V161-compatible.
 */
public final class NeighborhoodLayoutV163 {
    public static final int PLAN_COUNT=6;
    private static final float S=ClinicInteriorV89.EXPANSION_V90;
    public final int plan,signature;
    public final float[][] walls,furniture,rooms,labels,doors,caches,encounters;
    private final ArrayList<float[]> barriers=new ArrayList<>();
    private final ArrayList<float[]> objects=new ArrayList<>();
    private final ArrayList<Zone> zones=new ArrayList<>();
    private final int theme,variation,seed;

    private static final class Zone {
        final float x1,y1,x2,y2,dx,dy,side;
        final boolean vertical;
        Zone(float x1,float y1,float x2,float y2,
             float dx,float dy,boolean vertical,float side){
            this.x1=x1;this.y1=y1;this.x2=x2;this.y2=y2;
            this.dx=dx;this.dy=dy;this.vertical=vertical;this.side=side;
        }
    }
    private static float min(float a,float b){return Math.min(a,b);}
    private static float max(float a,float b){return Math.max(a,b);}
    private static float clamp(float x,float lo,float hi){
        return max(lo,min(hi,x));
    }
    private static float[] scaled(float[] a){
        float[] out=a.clone();
        for(int i=0;i<a.length;i++)out[i]*=S;
        return out;
    }
    private static float[][] pack(ArrayList<float[]> input){
        float[][] out=new float[input.size()][];
        for(int i=0;i<out.length;i++)out[i]=scaled(input.get(i));
        return out;
    }
    private void wall(float x,float y,float w,float h){
        if(w>2f&&h>2f)barriers.add(new float[]{x,y,w,h});
    }
    private void hGap(float x1,float x2,float y,float door){
        float radius=82f;
        wall(x1,y,max(0,door-radius-x1),19);
        wall(door+radius,y,max(0,x2-door-radius),19);
    }
    private void vGap(float y1,float y2,float x,float door){
        float radius=82f;
        wall(x,y1,19,max(0,door-radius-y1));
        wall(x,door+radius,19,max(0,y2-door-radius));
    }
    private void zone(float x1,float y1,float x2,float y2,
                      float dx,float dy,boolean vertical,float side){
        zones.add(new Zone(x1,y1,x2,y2,dx,dy,vertical,side));
    }
    /**
     * Geometric solid placement shared by chambers and circulation spaces.
     * Test the true collision walls and the saved container/door anchors.
     * Never alter the 14 persistent loot-container positions.
     */
    private boolean putFurnishing(int sprite,float x,float y,float w,float h,
                                  ArrayList<float[]> supplies){
        if(sprite<0||x<35f||y<48f||x+w>1565f||y+h>1059f)return false;
        // Keep the original 98-unit south door and its approach open.
        if(x<945f&&x+w>655f&&y<1095f&&y+h>866f)return false;
        for(float[] wall:barriers){
            if(x<wall[0]+wall[2]+10f&&x+w>wall[0]-10f&&
               y<wall[1]+wall[3]+10f&&y+h>wall[1]-10f)return false;
        }
        float cx=x+w*.5f,cy=y+h*.5f;
        for(Zone z:zones){
            if(Math.hypot(cx-z.dx,cy-z.dy)<155f)return false;
        }
        for(float[] cache:supplies){
            if(x<cache[0]+54f&&x+w>cache[0]-54f&&
               y<cache[1]+54f&&y+h>cache[1]-54f)return false;
        }
        for(float[] obj:objects){
            if(x<obj[1]+obj[3]+22f&&x+w>obj[1]-22f&&
               y<obj[2]+obj[4]+22f&&y+h>obj[2]-22f)return false;
        }
        // Existing V161 collision and deterministic room signatures continue
        // to derive from these same rectangles.
        objects.add(new float[]{16+sprite,x,y,w,h});
        return true;
    }
    /**
     * Curate complete functional work/living clusters before adding small
     * scattered support furniture. Anchors are relative to actual rooms,
     * and every piece uses the same collision, portal and loot clearances as
     * the old V163 model; no decorative fake loot or new saved objects.
     */
    /**
     * Put a complete themed ensemble against an actual ROOM WALL first.
     * The old 13% inward anchors excluded every large scene from small
     * chambers. Human-furnished rooms use corners and perimeter stations;
     * retain central player paths and the saved 14 cabinet interactions.
     */
    private void composeRoomScene(int room,ArrayList<float[]> supplies){
        Zone z=zones.get(room);
        final int[][] anchors={
            {0,0},{1000,0},{0,1000},{1000,1000},
            {500,0},{500,1000},{0,500},{1000,500},
            {220,210},{780,210},{220,790},{780,790},
            {500,300},{150,500},{850,500}
        };
        int staged=0;
        float area=(z.x2-z.x1)*(z.y2-z.y1);
        int aim=area>210000f?5:area>120000f?4:3;
        for(int slot=0;slot<anchors.length&&staged<aim;slot++){
            int sprite=InteriorRoomArchetypeV166.sprite(
                theme,room,variation,slot);
            if(sprite<0)continue;
            float width=InteriorRoomArchetypeV166.width(sprite);
            float height=InteriorRoomArchetypeV166.height(sprite);
            float scale=area<120000f?.80f:area<185000f?.89f:1f;
            width*=scale;height*=scale;
            float spanX=z.x2-z.x1-52f-width;
            float spanY=z.y2-z.y1-52f-height;
            if(spanX<=0||spanY<=0)continue;
            int n=hash(room*587+slot*13,theme*97+slot*19);
            float x=z.x1+26f+anchors[slot][0]*spanX/1000f+
                    Math.floorMod(n>>>9,5)-2f;
            float y=z.y1+26f+anchors[slot][1]*spanY/1000f+
                    Math.floorMod(n>>>17,5)-2f;
            float cx=x+width*.5f,cy=y+height*.5f;
            float midX=(z.x1+z.x2)*.5f,midY=(z.y1+z.y2)*.5f;
            // The solid composition may reach toward the centre but must
            // not cover the exact standing / navigation cell at room centre.
            float centreMargin=sprite>=48?16f:58f;
            if(x<midX+centreMargin&&x+width>midX-centreMargin&&
               y<midY+centreMargin&&y+height>midY-centreMargin)continue;
            // A clear corridor still connects door opening to room centre.
            float passage=sprite>=48?53f:75f;
            if(z.vertical){
                float left=Math.min(z.dx,midX),right=Math.max(z.dx,midX);
                if(x<right+passage&&x+width>left-passage&&
                   y<z.dy+passage&&y+height>z.dy-passage)continue;
            }else{
                float top=Math.min(z.dy,midY),bottom=Math.max(z.dy,midY);
                if(y<bottom+passage&&y+height>top-passage&&
                   x<z.dx+passage&&x+width>z.dx-passage)continue;
            }
            if(putFurnishing(sprite,x,y,width,height,supplies))staged++;
        }
    }
    /**
     * Circulation and shared-purpose spaces were never part of the six V163
     * rooms. Previously this left reception halls, sales floors and school
     * commons completely empty. Place functional grouped equipment on their
     * edges while preserving a broad continuous route to every room door.
     */
    private void furnishCommons(ArrayList<float[]> supplies){
        // A deterministic full-floor search, rather than 24 southern-edge
        // anchors. Broad atria and public areas previously contained only
        // one or two fixtures because the old candidate list missed them.
        // Keep all functional props solid and navigation-aware. The 81-cell
        // permutation visits every floor region with stable seed variation.
        final int aim=theme==NeighborhoodV154.SCHOOL||
            theme==NeighborhoodV154.HOTEL||
            theme==NeighborhoodV154.MARKET?14:10;
        int count=0;
        for(int j=0;j<81&&count<aim&&objects.size()<84;j++){
            int index=Math.floorMod(j*47+Math.floorMod(signature,81),81);
            int col=index%9,row=index/9;
            int h=hash(571+index*13,theme*181+index*7);
            int sprite=InteriorRoomArchetypeV166.shared(
                theme,index,variation);
            float w=InteriorRoomArchetypeV166.width(sprite);
            float hh=InteriorRoomArchetypeV166.height(sprite);
            // Fixed proportional scale, never stretch/flatten source art.
            float scale=index%4==0?.84f:1f;
            w*=scale;hh*=scale;
            float cx=110f+col*171f+(Math.floorMod(h>>>12,15)-7);
            float cy=108f+row*110f+(Math.floorMod(h>>>19,15)-7);
            float x=cx-w*.5f,y=cy-hh*.5f;
            // The south entry must remain an unmistakable walkable path.
            if(x<910f&&x+w>690f&&y+h>830f)continue;
            boolean inRoom=false;
            for(Zone z:zones){
                // Check ENTIRE object extent; a center-only test allowed
                // props to spill across room walls into neighboring spaces.
                if(x<z.x2+9f&&x+w>z.x1-9f&&
                   y<z.y2+9f&&y+hh>z.y1-9f){
                    inRoom=true;break;
                }
            }
            if(inRoom)continue;
            if(putFurnishing(sprite,x,y,w,hh,supplies))count++;
        }
    }
    private int hash(int a,int b){
        return IndustrialWorldV123.hash(a*31+signature,b*71+variation,seed);
    }
    public NeighborhoodLayoutV163(NeighborhoodV154.Building building,int worldSeed){
        theme=building.kind;variation=building.variation;seed=worldSeed;
        signature=IndustrialWorldV123.hash(building.tileX*97+building.slot*11,
            building.tileY*131+building.slot*23,worldSeed^0x163D5);
        plan=Math.floorMod(signature,PLAN_COUNT);
        // Identical perimeter and original bottom entrance across all layouts.
        wall(0,0,1600,23);wall(0,0,23,1120);wall(1577,0,23,1120);
        wall(0,1095,751,25);wall(849,1095,751,25);
        // V166: tie every partition to a continuous structural perimeter.
        // The second south course deliberately shares the 98-unit exit gap.
        // These are real collision walls, never visual-only doorway covers.
        wall(23,23,1554,21);
        wall(23,1070,728,25);wall(849,1070,728,25);
        switch(plan){
            case 0:horizontal();break;
            case 1:vertical();break;
            case 2:cross();break;
            case 3:atrium();break;
            case 4:openWorkshop();break;
            default:splitSpine();break;
        }
        if(zones.size()!=6)throw new IllegalStateException("Expected six reachable rooms");
        ArrayList<float[]> roomRects=new ArrayList<>(),texts=new ArrayList<>(),
            portals=new ArrayList<>(),supplies=new ArrayList<>(),spawn=new ArrayList<>();
        // Position every chest by a real door, not by the abandoned V89 room grid.
        for(int i=0;i<zones.size();i++){
            Zone z=zones.get(i);
            roomRects.add(new float[]{z.x1,z.y1,z.x2-z.x1,z.y2-z.y1});
            texts.add(new float[]{z.x1+32f,z.y1+53f});
            portals.add(new float[]{z.dx,z.dy});
            for(int j=0;j<2;j++){
                float offset=j==0?-49f:49f;
                float sx=z.vertical?z.dx+z.side*105f:z.dx+offset;
                float sy=z.vertical?z.dy+offset:z.dy+z.side*105f;
                supplies.add(new float[]{clamp(sx,z.x1+38f,z.x2-38f),
                    clamp(sy,z.y1+36f,z.y2-36f)});
            }
            float ex=(z.x1+z.x2)/2f,ey=(z.y1+z.y2)/2f;
            // NPCs occupy actual rooms and are moved away from doors and props.
            spawn.add(new float[]{ex,ey});
        }
        // Two additional container anchors preserve V161 14-box save format.
        for(int i:new int[]{0,5}){
            Zone z=zones.get(i);
            float sx=z.vertical?z.dx+z.side*157f:z.dx+150f;
            float sy=z.vertical?z.dy+125f:z.dy+z.side*150f;
            supplies.add(new float[]{clamp(sx,z.x1+55f,z.x2-55f),
                clamp(sy,z.y1+55f,z.y2-55f)});
        }
        // V166 functional furnishing: authored sprites selected by ROOM use,
        // wall-oriented placements, collision-tested against doors and loot.
        // No more six slots of arbitrary building-wide objects.
        final int[][] anchors={
            {0,0},{1000,0},{0,1000},{1000,1000},
            {450,0},{550,1000},{0,450},{1000,550},
            {250,0},{750,1000},{0,780},{1000,240},
            {210,1000},{780,0},{0,230},{1000,790},
            // Secondary wall niches and paired work surfaces, not a
            // uniform checkerboard of randomly positioned machinery.
            {500,200},{500,800},{200,500},{800,500},
            {330,330},{670,330},{330,670},{670,670},
            {120,330},{880,670},{120,670},{880,330},
            {330,120},{670,880},{330,880},{670,120}
        };
        for(int index=0;index<6;index++){
            Zone z=zones.get(index);
            float area=(z.x2-z.x1)*(z.y2-z.y1);
            composeRoomScene(index,supplies);
            int target=area>270000f?9:area>160000f?7:5;
            int placed=0;
            // First honor human-authored perimeter stations. Then probe
            // seeded interior niches on a 9x9 lattice, avoiding the former
            // early exit when every candidate near a cabinet/door was used.
            for(int candidate=0;candidate<anchors.length+81&&placed<target;candidate++){
                int n=hash(index*73+candidate,theme*107+candidate);
                int ax,ay;
                if(candidate<anchors.length){
                    int[] anchor=anchors[
                        (candidate+Math.floorMod(n>>>11,3))%anchors.length];
                    ax=anchor[0];ay=anchor[1];
                }else{
                    int id=Math.floorMod(
                        (candidate-anchors.length)*47+Math.floorMod(signature,81),
                        81);
                    ax=(id%9)*125;ay=(id/9)*125;
                }
                int sprite=InteriorRoomArchetypeV166.sprite(
                    theme,index,variation,candidate+5);
                if(sprite<0)continue;
                float w=InteriorRoomArchetypeV166.width(sprite);
                float h=InteriorRoomArchetypeV166.height(sprite);
                float spanX=z.x2-z.x1-72f-w,spanY=z.y2-z.y1-72f-h;
                if(spanX<1||spanY<1)continue;
                float x=z.x1+36f+ax*spanX/1000f;
                float y=z.y1+36f+ay*spanY/1000f;
                x=clamp(x+(Math.floorMod(n>>>17,13)-6),z.x1+30f,z.x2-w-30f);
                y=clamp(y+(Math.floorMod(n>>>23,13)-6),z.y1+30f,z.y2-h-30f);
                float cx=x+w*.5f,cy=y+h*.5f;
                // All six layouts share the original south-facing spawn/exit.
                // Protect a broad approach, not only the tiny 98px door gap.
                if(x<940f&&x+w>660f&&y<1095f&&y+h>880f)continue;
                // Entrance clearances and central routes are collision-safe.
                if(Math.hypot(cx-z.dx,cy-z.dy)<166f)continue;
                if(Math.abs(cx-(z.x1+z.x2)*.5f)<53f&&
                   Math.abs(cy-(z.y1+z.y2)*.5f)<80f)continue;
                boolean overlaps=false;
                for(float[] cache:supplies){
                    if(Math.abs(cx-cache[0])<101f&&
                       Math.abs(cy-cache[1])<93f){overlaps=true;break;}
                }
                if(overlaps)continue;
                for(float[] q:objects){
                    if(x<q[1]+q[3]+26f&&x+w>q[1]-26f&&
                       y<q[2]+q[4]+26f&&y+h>q[2]-26f){
                        overlaps=true;break;
                    }
                }
                if(overlaps)continue;
                // Direct atlas sprite tag 16..31; original types still decode.
                objects.add(new float[]{16+sprite,x,y,w,h});
                placed++;
            }
        }
        furnishCommons(supplies);
        walls=pack(barriers);
        ArrayList<float[]> scaledObjects=new ArrayList<>();
        for(float[] o:objects){
            float[] out=o.clone();
            for(int k=1;k<5;k++)out[k]*=S;
            scaledObjects.add(out);
        }
        furniture=scaledObjects.toArray(new float[0][]);
        rooms=pack(roomRects);
        labels=pack(texts);
        doors=pack(portals);
        caches=pack(supplies);
        encounters=pack(spawn);
    }
    /** Three north / three south rooms surrounding a broad horizontal spine. */
    private void horizontal(){
        float cut1=clamp(525+Math.floorMod(hash(1,1),161)-80,450,595);
        float cut2=clamp(1055+Math.floorMod(hash(2,2),161)-80,985,1140);
        float top=480+Math.floorMod(hash(3,3),65),bottom=620+Math.floorMod(hash(4,4),65);
        float[] xx={23,cut1,cut2,1577};
        wall(cut1,44,19,top-44);wall(cut2,44,19,top-44);
        wall(cut1,bottom,19,1070-bottom);wall(cut2,bottom,19,1070-bottom);
        for(int i=0;i<3;i++){
            float mid=(xx[i]+xx[i+1])/2f;
            hGap(xx[i],xx[i+1],top,mid);
            hGap(xx[i],xx[i+1],bottom,mid);
            zone(xx[i]+22,45,xx[i+1]-20,top,mid,top,false,-1);
            zone(xx[i]+22,bottom+20,xx[i+1]-20,1070,mid,bottom+19,false,1);
        }
    }
    /** Long vertical hall with three pairs of independent side rooms. */
    private void vertical(){
        float west=685+Math.floorMod(hash(1,9),81),east=925+Math.floorMod(hash(2,9),81);
        float first=320+Math.floorMod(hash(3,9),85),second=698+Math.floorMod(hash(4,9),85);
        float[] yy={44,first,second,1070};
        for(int i=0;i<3;i++){
            float cy=(yy[i]+yy[i+1])/2f;
            vGap(yy[i],yy[i+1],west,cy);
            vGap(yy[i],yy[i+1],east,cy);
            zone(24,yy[i]+3,west,yy[i+1]-3,west,cy,true,-1);
            zone(east+20,yy[i]+3,1577,yy[i+1]-3,east+19,cy,true,1);
        }
        for(float divider:new float[]{first,second}){
            wall(23,divider,west-23,20);
            wall(east,divider,1577-east,20);
        }
    }
    /** A T cross with three upper rooms and uneven lower side wings. */
    private void cross(){
        float x1=510+Math.floorMod(hash(7,2),80),x2=1010+Math.floorMod(hash(9,2),80);
        float y1=385+Math.floorMod(hash(6,2),56),y2=y1+165;
        float left=695+Math.floorMod(hash(8,2),65),right=895+Math.floorMod(hash(10,2),65);
        float below=795+Math.floorMod(hash(11,2),66);
        float[] xx={23,x1,x2,1577};
        for(int i=0;i<3;i++){
            float mid=(xx[i]+xx[i+1])/2f;
            hGap(xx[i],xx[i+1],y1,mid);
            zone(xx[i]+20,44,xx[i+1]-20,y1,mid,y1,false,-1);
        }
        wall(x1,44,19,y1-44);wall(x2,44,19,y1-44);
        vGap(y2,below,left,(y2+below)/2f);
        vGap(below,1070,left,(below+1070)/2f);
        vGap(y2,1070,right,(y2+1070)/2f);
        wall(23,below,left-23,20);
        zone(24,y2+3,left,below-3,left,(y2+below)/2f,true,-1);
        zone(24,below+24,left,1070,left,(below+1070)/2f,true,-1);
        zone(right+22,y2+3,1577,1070,right,(y2+1070)/2f,true,1);
    }
    /** Wide open atrium with six suites on its two sides. */
    private void atrium(){
        float west=485+Math.floorMod(hash(1,17),66),east=1090+Math.floorMod(hash(2,17),66);
        float y1=358+Math.floorMod(hash(3,17),53),y2=730+Math.floorMod(hash(4,17),52);
        float[] yy={44,y1,y2,1070};
        for(int i=0;i<3;i++){
            float cy=(yy[i]+yy[i+1])/2f;
            vGap(yy[i],yy[i+1],west,cy);
            vGap(yy[i],yy[i+1],east,cy);
            zone(24,yy[i]+3,west,yy[i+1]-3,west,cy,true,-1);
            zone(east+20,yy[i]+3,1577,yy[i+1]-3,east+19,cy,true,1);
        }
        for(float y:new float[]{y1,y2}){
            wall(23,y,west-23,20);wall(east,y,1577-east,20);
        }
    }
    /** Production/depot open floor, three small bays and three rear wings. */
    private void openWorkshop(){
        float top=325+Math.floorMod(hash(1,23),85);
        float west=465+Math.floorMod(hash(2,23),95),east=1070+Math.floorMod(hash(3,23),95);
        float divider=840+Math.floorMod(hash(4,23),70);
        float[] xx={23,west,1055,1577};
        for(int i=0;i<3;i++){
            float mid=(xx[i]+xx[i+1])/2f;
            hGap(xx[i],xx[i+1],top,mid);
            zone(xx[i]+20,44,xx[i+1]-20,top,mid,top,false,-1);
        }
        wall(west,44,19,top-44);wall(1055,44,19,top-44);
        vGap(660,divider,west,(660+divider)/2f);
        vGap(divider,1070,west,(divider+1070)/2f);
        vGap(660,1070,east,(660+1070)/2f);
        wall(23,divider,west-23,20);
        zone(24,660,west,divider,west,(660+divider)/2f,true,-1);
        zone(24,divider+20,west,1070,west,(divider+1070)/2f,true,-1);
        zone(east+20,660,1577,1070,east,(660+1070)/2f,true,1);
    }
    /** Tall central spine, two pairs of high rooms, two lower wings. */
    private void splitSpine(){
        float west=700+Math.floorMod(hash(1,29),65),east=885+Math.floorMod(hash(2,29),65);
        float split=348+Math.floorMod(hash(3,29),68),cross=675+Math.floorMod(hash(4,29),65);
        float[] yy={44,split,cross};
        for(int i=0;i<2;i++){
            float cy=(yy[i]+yy[i+1])/2f;
            vGap(yy[i],yy[i+1],west,cy);
            vGap(yy[i],yy[i+1],east,cy);
            zone(24,yy[i]+3,west,yy[i+1]-3,west,cy,true,-1);
            zone(east+20,yy[i]+3,1577,yy[i+1]-3,east+19,cy,true,1);
        }
        wall(23,split,west-23,20);wall(east,split,1577-east,20);
        float cy=cross+100f;
        hGap(23,west,cross,(23+west)/2f);
        hGap(east,1577,cross,(east+1577)/2f);
        wall(west,cross,19,1070-cross);
        wall(east,cross,19,1070-cross);
        zone(24,cross+20,west,1070,(23+west)/2f,cross+19,false,1);
        zone(east+20,cross+20,1577,1070,(east+1577)/2f,cross+19,false,1);
    }
    public boolean doorVertical(int room){
        return room>=0&&room<zones.size()&&zones.get(room).vertical;
    }
    public boolean blocked(float worldX,float worldY,float radius){
        if(worldX-radius<23*S||worldX+radius>1577*S||
           worldY-radius<23*S||worldY+radius>1095*S)return true;
        for(float[] q:walls)
            if(worldX+radius>q[0]&&worldX-radius<q[0]+q[2]&&
               worldY+radius>q[1]&&worldY-radius<q[1]+q[3])return true;
        for(float[] q:furniture)
            if(worldX+radius>q[1]+4&&worldX-radius<q[1]+q[3]-4&&
               worldY+radius>q[2]+4&&worldY-radius<q[2]+q[4]-4)
                return true;
        return false;
    }
}
