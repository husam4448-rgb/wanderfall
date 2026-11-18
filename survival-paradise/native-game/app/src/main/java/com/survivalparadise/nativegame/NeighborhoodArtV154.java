package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;

/**
 * Distinct world-scale architecture for abandoned neighborhoods.
 * Painted in world coordinates, from a pure immutable geometry model.
 * These extra blocks are sealed scenery; the 26 authored V153 landmarks
 * remain the working enterable locations and keep their original loot IDs.
 */
public final class NeighborhoodArtV154 {
    private NeighborhoodArtV154(){}
    private static final int OUTLINE=0xff172429, CONCRETE=0xff777a73;
    private static void box(Canvas c,Paint p,float x,float y,float w,float h,int color){
        if(w<=0||h<=0)return;
        p.setStyle(Paint.Style.FILL);p.setColor(color);
        c.drawRect(x,y,x+w,y+h,p);
    }
    private static int shade(int color,int amount){
        int r=Math.max(0,Math.min(255,((color>>16)&255)+amount));
        int g=Math.max(0,Math.min(255,((color>>8)&255)+amount));
        int b=Math.max(0,Math.min(255,(color&255)+amount));
        return 0xff000000|(r<<16)|(g<<8)|b;
    }
    private static final int[] ROOFS={
        0xff736f68,0xff516d71,0xff8a8068,0xff6d7680,
        0xff7b8071,0xff685e53,0xff687278,0xff806d5c
    };
    private static final int[] WALLS={
        0xff7d7a72,0xff53666c,0xffa49374,0xff897e70,
        0xff777f6f,0xff665f55,0xff6e7471,0xff9b816b
    };
    private static final int[] ACCENTS={
        0xffc19d74,0xff86b6ba,0xffc5aa63,0xffc4b6a2,
        0xffaebea4,0xffc0915d,0xffadab8e,0xffae8e71
    };
    private static String name(int kind){
        switch(kind){
            case NeighborhoodV154.APARTMENTS:return "RESIDENTIAL";
            case NeighborhoodV154.OFFICES:return "OFFICES";
            case NeighborhoodV154.MARKET:return "SUPERMARKET";
            case NeighborhoodV154.HOTEL:return "HOTEL";
            case NeighborhoodV154.SCHOOL:return "SCHOOL";
            case NeighborhoodV154.FACTORY:return "PRODUCTION";
            case NeighborhoodV154.WAREHOUSE:return "DISTRIBUTION";
            default:return "HOUSING";
        }
    }
    private static void windows(Canvas c,Paint p,NeighborhoodV154.Building b,
                                int left,int right,int top,int bottom,boolean night){
        float ww=b.width;
        int count=b.kind==NeighborhoodV154.MARKET?6:9;
        float gap=(ww-left-right)/(float)count;
        for(int i=0;i<count;i++){
            float xx=b.left+left+i*gap+9f;
            float inner=Math.max(42f,gap-25f);
            boolean lit=night&&Math.floorMod(i+b.variation*5+b.slot,5)==0;
            int glass=lit?0xffdcc18b:0xff688b91;
            box(c,p,xx,b.bottom()-bottom,inner,top,OUTLINE);
            box(c,p,xx+5,b.bottom()-bottom+6,inner-10,top-11,glass);
            box(c,p,xx+inner*.5f-3,b.bottom()-bottom+6,6,top-11,
                0xff364b4e);
            box(c,p,xx+6,b.bottom()-bottom+top*.55f,inner-12,4,
                0xffb2b5a1);
        }
    }
    private static void roofDetails(Canvas c,Paint p,NeighborhoodV154.Building b,
                                    int roof,int trim){
        float x=b.left,y=b.top,w=b.width,h=b.height;
        float useH=h-222f;
        switch(b.kind){
            case NeighborhoodV154.APARTMENTS:
                // Two long apartment wings with terraces and roof ducts.
                for(int i=0;i<3;i++){
                    float yy=y+96+i*(useH-125f)/3f;
                    box(c,p,x+70,yy,w-140,44,shade(roof,-16));
                    box(c,p,x+83,yy+8,w-166,9,trim);
                    for(int j=0;j<6;j++)
                        box(c,p,x+94+j*(w-190)/6f,yy+19,75,16,
                            0xff34474b);
                }
                box(c,p,x+70,y+useH-96,w-140,22,shade(trim,-20));
                break;
            case NeighborhoodV154.OFFICES:
                for(int i=0;i<5;i++){
                    float xx=x+78+i*(w-156)/5f;
                    box(c,p,xx,y+65,22,useH-102,0xff223b43);
                    box(c,p,xx+29,y+70,120,useH-130,0xff719da1);
                    for(int j=0;j<4;j++)
                        box(c,p,xx+29,y+120+j*(useH-180)/4f,
                            121,12,0xff344b54);
                }
                box(c,p,x+w*.42f,y+85,w*.16f,180,0xff405c60);
                break;
            case NeighborhoodV154.MARKET:
                for(int i=0;i<6;i++){
                    float xx=x+85+i*(w-170)/6f;
                    box(c,p,xx,y+82,(w-186)/6f,useH-160,
                        i%2==0?0xffa1957b:0xff7b8a80);
                    box(c,p,xx+16,y+105,(w-210)/6f,30,0xff485d60);
                }
                for(int i=0;i<8;i++)
                    box(c,p,x+63+i*(w-126)/8f,y+useH-95,
                        (w-160)/8f,30,i%2==0?trim:shade(trim,-38));
                break;
            case NeighborhoodV154.HOTEL:
                for(int j=0;j<3;j++){
                    float yy=y+74+j*(useH-85)/3f;
                    box(c,p,x+75,yy,w-150,70,shade(roof,-25));
                    box(c,p,x+88,yy+8,w-176,16,trim);
                    for(int i=0;i<8;i++)
                        box(c,p,x+110+i*(w-220)/8f,yy+35,76,25,
                            0xffb4b19b);
                }
                break;
            case NeighborhoodV154.SCHOOL:
                box(c,p,x+66,y+62,w-132,useH-138,shade(roof,19));
                box(c,p,x+109,y+111,w-218,useH-244,0xff46585a);
                // Fully enclosed central skylight / hall, not an open
                // collision-free courtyard that would become an invisible wall.
                box(c,p,x+124,y+127,w-248,useH-275,0xff96aaa1);
                for(int i=0;i<8;i++)
                    box(c,p,x+149+i*(w-300)/8f,y+145,8,useH-310,
                        0xff37575a);
                break;
            case NeighborhoodV154.FACTORY:
                for(int i=0;i<7;i++){
                    float xx=x+50+i*(w-100)/7f;
                    box(c,p,xx,y+66,(w-124)/7f,useH-112,
                        i%2==0?shade(roof,18):shade(roof,-22));
                    box(c,p,xx+6,y+82,30,useH-147,0xffa5ac9d);
                    box(c,p,xx+43,y+92,9,useH-167,0xff303e40);
                }
                break;
            case NeighborhoodV154.WAREHOUSE:
                for(int i=0;i<21;i++){
                    float xx=x+40+i*(w-80)/21f;
                    box(c,p,xx,y+50,12,useH-90,
                        i%3==0?0xffa2a598:0xff4d5f63);
                }
                box(c,p,x+142,y+110,w-284,70,0xff26363d);
                for(int i=0;i<5;i++)
                    box(c,p,x+160+i*(w-320)/5f,y+126,90,40,trim);
                break;
            case NeighborhoodV154.RESIDENCES:
                for(int i=0;i<7;i++){
                    float xx=x+45+i*(w-90)/7f;
                    box(c,p,xx,y+65,(w-112)/7f,useH-135,
                        i%2==0?shade(roof,12):shade(roof,-20));
                    box(c,p,xx+16,y+105,34,75,0xffb6a18a);
                    box(c,p,xx+18,y+210,65,15,0xff3e5451);
                }
                break;
            default:break;
        }
        // Stable rooftop vents: not interactive items or world collision.
        for(int i=0;i<3;i++){
            float xx=x+110+i*(w-220)/3f;
            box(c,p,xx,y+useH-48,62,43,OUTLINE);
            box(c,p,xx+6,y+useH-41,50,29,shade(trim,-28));
        }
    }
    private static void pavement(Canvas c,Paint p,NeighborhoodV154.Building b){
        float x=b.left,y=b.top,w=b.width,bottom=b.bottom();
        box(c,p,x-52,y-39,w+104,b.height+220f,0x4a363c38);
        box(c,p,x-42,y-30,w+84,b.height+185f,0xff706c61);
        // Weathered service apron and curb on the actual door side.
        box(c,p,x+31,bottom+19,w-62,86,0xff878478);
        box(c,p,x+45,bottom+26,w-90,15,0xffa9a08d);
        for(int i=0;i<9;i++){
            float bx=x+74+i*(w-148)/9f;
            box(c,p,bx,bottom+66,4,35,0xff595c56);
        }
        // This pavement has no collision, unlike the masonry roof.
    }
    private static void building(Canvas c,Paint p,NeighborhoodV154.Building b,
                                 boolean night){
        float x=b.left,y=b.top,w=b.width,h=b.height,bottom=b.bottom();
        int roof=shade(ROOFS[b.kind],(b.variation%5-2)*5);
        int wall=shade(WALLS[b.kind],(b.variation%4-2)*6);
        int trim=ACCENTS[b.kind];
        pavement(c,p,b);
        // Raised exterior profile: dark offset shadow, roof parapet and a
        // south-facing multi-story front spanning the width of the building.
        box(c,p,x+27,y+34,w+17,h+25,0x5d101919);
        box(c,p,x-14,y-14,w+28,h+27,OUTLINE);
        box(c,p,x,y,w,h,wall);
        box(c,p,x+15,y+13,w-30,h-191f,roof);
        box(c,p,x+25,y+21,w-50,14,shade(roof,30));
        box(c,p,x+25,y+38,12,h-236,shade(roof,-28));
        roofDetails(c,p,b,roof,trim);
        // Tall, legible front face: multiple window bays, structural pillars
        // and a recessed blocked doorway. Never display a false ENTER prompt.
        box(c,p,x,bottom-182,w,182,shade(wall,-22));
        box(c,p,x+13,bottom-174,w-26,159,wall);
        box(c,p,x+14,bottom-178,w-28,15,shade(wall,35));
        windows(c,p,b,60,60,62,151,night);
        for(int i=0;i<8;i++)
            box(c,p,x+72+i*(w-144)/8f,bottom-170,8,158,
                shade(wall,-40));
        float doorX=b.doorX;
        box(c,p,doorX-83,bottom-163,166,164,OUTLINE);
        box(c,p,doorX-70,bottom-151,140,145,0xff394749);
        box(c,p,doorX-58,bottom-142,116,132,0xff222e31);
        for(int i=0;i<5;i++)
            box(c,p,doorX-57,bottom-128+i*23,114,8,0xff7b6a58);
        box(c,p,doorX-107,bottom-188,214,26,trim);
        // Broken signage / service address: distinct place function.
        p.setColor(0xffece2bd);
        p.setTextSize(19f);
        p.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
        c.drawText(name(b.kind),doorX-99,bottom-168,p);
        box(c,p,doorX-79,bottom+21,158,49,0xffaba18a);
        box(c,p,doorX-72,bottom+28,144,10,0xffccc1a2);
        box(c,p,doorX-46,bottom+76,92,12,0xff5e665d);
    }
    private static void roads(Canvas c,Paint p,int tx,int ty){
        boolean hasBuilding=false;
        for(int slot=0;slot<NeighborhoodV154.COLS*NeighborhoodV154.ROWS;slot++)
            if(NeighborhoodV154.get(tx,ty,slot)!=null){hasBuilding=true;break;}
        if(!hasBuilding)return;
        float x=tx*(float)NeighborhoodV154.TILE_W;
        float y=ty*(float)NeighborhoodV154.TILE_H;
        float[] vertical={1750f,3550f};
        float[] horizontal={2190f,4250f};
        // V162: draw all road surfaces BEFORE their lane markings.
        // Both carriageways use one asphalt substrate at four-way crossings.
        for(float xx:vertical){
            box(c,p,x+xx-116,y+200,232,4195,0xff64665e);
            box(c,p,x+xx-99,y+201,198,4192,0xff373d3f);
            SurfaceArtV165.rect(c,x+xx-99,y+201,198,4192,
                SurfaceArtV165.ASPHALT,355f,213);
        }
        for(float yy:horizontal){
            box(c,p,x+140,y+yy-111,5120,222,0xff67675e);
            box(c,p,x+142,y+yy-97,5116,194,0xff373d3f);
            SurfaceArtV165.rect(c,x+142,y+yy-97,5116,194,
                SurfaceArtV165.ASPHALT,355f,213);
        }
        for(float xx:vertical)for(float yy:horizontal)
            {
                box(c,p,x+xx-116,y+yy-111,232,222,0xff373d3f);
                SurfaceArtV165.rect(c,x+xx-116,y+yy-111,232,222,
                    SurfaceArtV165.ASPHALT,355f,213);
            }
        // V165.1 organic shoulder strips remain inside each road segment;
        // do not draw fake soil seams across real intersections.
        for(float xx:vertical){
            float[][] seg={{205f,2076f},{2304f,4136f},{4364f,4390f}};
            for(float[] v:seg)
                RoadShoulderArtV1651.vertical(c,x+xx-99f,x+xx+99f,
                    y+v[0],y+v[1]);
        }
        for(float yy:horizontal){
            float[][] seg={{142f,1636f},{1864f,3436f},{3664f,5258f}};
            for(float[] h:seg)
                RoadShoulderArtV1651.horizontal(c,x+h[0],x+h[1],
                    y+yy-97f,y+yy+97f);
        }
        // Kerbs only on free-standing vertical road edges; never through the
        // asphalt intersection where a perpendicular road connects.
        for(float xx:vertical){
            float[][] segments={{205f,2076f},{2304f,4136f},{4364f,4390f}};
            for(float[] segment:segments){
                box(c,p,x+xx-111,y+segment[0],7,segment[1]-segment[0],
                    0xffa2997c);
                box(c,p,x+xx+104,y+segment[0],7,segment[1]-segment[0],
                    0xffa2997c);
            }
            for(int dash=0;dash<33;dash++){
                float cy=230f+dash*126f;
                if((cy+58f>2079f&&cy<2301f)||
                   (cy+58f>4139f&&cy<4361f))continue;
                box(c,p,x+xx-3,y+cy,6,58,0xffb0a079);
            }
        }
        // Yellow lane dashes stop on both sides of the crossing.
        for(float yy:horizontal){
            for(int dash=0;dash<35;dash++){
                float cx=176f+dash*145f;
                boolean intersection=false;
                for(float xx:vertical)
                    if(cx+69f>xx-121f&&cx<xx+121f)
                        intersection=true;
                if(!intersection)box(c,p,x+cx,y+yy-3f,69,6,0xffb4a078);
            }
        }
    }
    public static void draw(Canvas c,Paint p,float camX,float camY,
                            float viewW,float viewH,boolean night){
        draw(c,p,camX,camY,viewW,viewH,night,null);
    }
    /** New worlds render only the seed-selected town clusters. Old saves
     * pass null to retain the exact historical V154 building map.
     */
    public static void draw(Canvas c,Paint p,float camX,float camY,
                            float viewW,float viewH,boolean night,
                            WorldCivilizationV159.Plan plan){
        int tx0=NeighborhoodV154.tileX(camX-170),
            tx1=NeighborhoodV154.tileX(camX+viewW+170);
        int ty0=NeighborhoodV154.tileY(camY-170),
            ty1=NeighborhoodV154.tileY(camY+viewH+170);
        for(int ty=ty0;ty<=ty1;ty++)for(int tx=tx0;tx<=tx1;tx++)
            if(NeighborhoodV154.district(tx,ty)&&
               (plan==null||plan.atTile(tx,ty)!=null))
                roads(c,p,tx,ty);
        NeighborhoodV154.visible(camX,camY,viewW,viewH,plan,
            b->building(c,p,b,night));
    }
}
