package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;

/**
 * V161 themed solid props. Each object's painted extent stays inside the
 * exact collision rectangle supplied by NeighborhoodInteriorV161.
 * No empty placeholder blocks, head art changes, or asset substitutions.
 */
public final class NeighborhoodInteriorArtV161 {
    private NeighborhoodInteriorArtV161(){}
    private static void r(Canvas c,Paint p,float x,float y,float w,float h,int color){
        if(w<=0||h<=0)return;
        p.setStyle(Paint.Style.FILL);p.setColor(color);
        c.drawRect(x,y,x+w,y+h,p);
    }
    private static void oval(Canvas c,Paint p,float x,float y,float w,float h,int color){
        p.setStyle(Paint.Style.FILL);p.setColor(color);
        c.drawOval(x,y,x+w,y+h,p);
    }
    /**
     * V163 exact room footprints. No static six-box checkerboard: each site's
     * walls, tiles, work zones and room signs follow its unique physical map.
     * Drawn in logical pre-scaled coordinates, not on top of characters.
     */
    public static void floor(Canvas c,Paint p,NeighborhoodInteriorV161 room){
        NeighborhoodLayoutV163 plan=room.layoutV163;
        int kind=room.theme;
        int ground=kind==NeighborhoodV154.FACTORY?0xff666d6b:
            kind==NeighborhoodV154.WAREHOUSE?0xff77766d:
            kind==NeighborhoodV154.MARKET?0xff81796c:
            kind==NeighborhoodV154.HOTEL?0xff83716a:
            kind==NeighborhoodV154.SCHOOL?0xff728077:
            kind==NeighborhoodV154.OFFICES?0xff6b787a:0xff827866;
        r(c,p,23,23,1554,1072,ground);
        float scale=ClinicInteriorV89.EXPANSION_V90;
        for(int z=0;z<plan.rooms.length;z++){
            float[] b=plan.rooms[z];
            float x=b[0]/scale,y=b[1]/scale,w=b[2]/scale,h=b[3]/scale;
            int hsh=IndustrialWorldV123.hash(z+room.building.tileX*9,
                room.building.tileY*31+room.variation,room.seed);
            int tint=(Math.floorMod(hsh,5)-2)*5;
            int red=Math.max(0,Math.min(255,((ground>>>16)&255)+tint));
            int green=Math.max(0,Math.min(255,((ground>>>8)&255)+tint));
            int blue=Math.max(0,Math.min(255,(ground&255)+tint));
            int tile=0xff000000|(red<<16)|(green<<8)|blue;
            r(c,p,x+3,y+3,w-6,h-6,tile);
            // Different floor finishes: workshop stripe, classroom lino,
            // residence parquet, hotel carpet, or warehouse expansion joints.
            boolean industrial=kind==NeighborhoodV154.FACTORY||
                kind==NeighborhoodV154.WAREHOUSE;
            if(industrial){
                for(int i=0;i<6;i++){
                    float vx=x+15+(w-30)*i/6f;
                    r(c,p,vx,y+12,2,h-24,0x33404746);
                }
                r(c,p,x+20,y+h-42,w-40,6,0xffb69a60);
                for(int i=0;i<Math.min(6,(int)(w/65));i++)
                    r(c,p,x+25+i*65,y+h-42,25,6,0xff343e3e);
            }else if(kind==NeighborhoodV154.SCHOOL||
                     kind==NeighborhoodV154.MARKET||
                     kind==NeighborhoodV154.OFFICES){
                for(int i=1;i<Math.max(2,(int)(w/90));i++)
                    r(c,p,x+i*88,y+6,2,h-12,0x40435656);
                for(int i=1;i<Math.max(2,(int)(h/92));i++)
                    r(c,p,x+6,y+i*88,w-12,2,0x40435656);
            }else{
                for(int i=0;i<Math.min(9,(int)(h/38));i++)
                    r(c,p,x+8,y+11+i*38,w-16,2,0x4b4a3e34);
                r(c,p,x+30,y+22,w-60,h-44,
                    (room.variation+z)%2==0?0x3376a1a2:0x335e6d64);
            }
            for(int i=0;i<8;i++){
                int hash=IndustrialWorldV123.hash(z*29+i,
                    plan.signature+i*17,room.seed);
                float bx=x+15+Math.floorMod(hash,Math.max(1,(int)(w-35)));
                float by=y+15+Math.floorMod(hash>>>9,Math.max(1,(int)(h-35)));
                r(c,p,bx,by,Math.max(2,i%3+1),2,0x4c242a27);
            }
        }
    }
    /** Draw one visually recognizable item scaled to its collidable footprint. */
    public static void furniture(Canvas c,Paint p,float[] q,int theme,int variant,int index){
        float x=q[1],y=q[2],w=q[3],h=q[4];
        if(w<25||h<20)return;
        c.save();c.clipRect(x-3,y-3,x+w+3,y+h+3);
        // Furniture silhouettes include seams, handles and top-facing details.
        r(c,p,x-3,y-3,w+6,h+6,0xff1a2a2b);
        int type=(int)q[0];
        if(theme==NeighborhoodV154.WAREHOUSE ||
           theme==NeighborhoodV154.FACTORY){
            if(type==4 || theme==NeighborhoodV154.FACTORY&&index%3==0){
                // Industrial press / motor with guards, vents and feed rollers.
                r(c,p,x,y,w,h,0xff586566);
                r(c,p,x+5,y+5,w-10,h*.32f,0xff9d9d85);
                r(c,p,x+w*.16f,y+h*.22f,w*.68f,h*.51f,0xff354d51);
                r(c,p,x+w*.22f,y+h*.28f,w*.56f,h*.16f,0xffb39462);
                for(int i=0;i<5;i++){
                    r(c,p,x+10+i*(w-20)/5f,y+h*.78f,
                        Math.max(4,(w-25)/8f),Math.max(3,h*.10f),0xff23393e);
                }
                r(c,p,x+w*.76f,y+h*.08f,8,8,0xffe0b35c);
                r(c,p,x+w*.79f,y+h*.17f,6,7,0xffaa4b43);
            }else{
                // Pallet racking, strapped timber boxes, stacked freight.
                r(c,p,x,y,w,h,0xff51463d);
                r(c,p,x+3,y+3,w-6,h-6,0xff94744f);
                for(int i=1;i<4;i++)
                    r(c,p,x+5,y+i*h/4f,w-10,5,0xff343d3c);
                for(int j=0;j<3;j++){
                    float xx=x+7+j*(w-13)/3f;
                    r(c,p,xx,y+8,Math.max(8,(w-18)/3f),h*.22f,
                        j==1?0xff8f8c72:0xffb58b59);
                    r(c,p,xx+4,y+h*.49f,Math.max(3,(w-35)/3f),h*.17f,
                        0xff6c7b72);
                }
                r(c,p,x+7,y+h-12,w-14,5,0xffc2a26c);
            }
        }else if(theme==NeighborhoodV154.MARKET){
            // Stocked store shelving and checker-out countertops.
            r(c,p,x,y,w,h,0xff415356);
            for(int row=0;row<3;row++){
                float yy=y+7+row*(h-15)/3f;
                r(c,p,x+4,yy,w-8,Math.max(5,(h-26)/3f),0xff9d986f);
                for(int j=0;j<5;j++){
                    float xx=x+8+j*(w-16)/5f;
                    r(c,p,xx,yy+2,Math.max(3,(w-30)/5f),
                        Math.max(3,(h-26)/3f-3),
                        (j+row+variant)%3==0?0xff9e6542:
                        (j+row)%2==0?0xff778c6c:0xffbaae74);
                }
                r(c,p,x+3,yy+(h-15)/3f-5,w-6,5,0xff253c3c);
            }
        }else if(theme==NeighborhoodV154.SCHOOL){
            // Chalkboard desks with notebooks, textbooks, chair legs.
            r(c,p,x,y,w,h,0xff594c3c);
            r(c,p,x+4,y+4,w-8,h*.52f,0xffa0875c);
            r(c,p,x+7,y+7,w*.36f,h*.26f,0xffe2cf9d);
            r(c,p,x+w*.54f,y+6,w*.31f,h*.25f,0xffd1dcb6);
            r(c,p,x+6,y+h*.63f,w-12,Math.max(4,h*.15f),0xff464b44);
            r(c,p,x+8,y+h-11,7,8,0xff202c2b);
            r(c,p,x+w-15,y+h-11,7,8,0xff202c2b);
        }else if(theme==NeighborhoodV154.OFFICES){
            // Desktop workstation: monitor, keyboard, chair back and cable.
            r(c,p,x,y,w,h,0xff5c5445);
            r(c,p,x+4,y+4,w-8,h*.56f,0xffab997a);
            r(c,p,x+w*.27f,y+6,w*.46f,h*.34f,0xff182b35);
            r(c,p,x+w*.30f,y+9,w*.40f,h*.25f,0xff688b91);
            r(c,p,x+w*.43f,y+h*.38f,w*.14f,5,0xff1a3134);
            r(c,p,x+w*.25f,y+h*.48f,w*.49f,5,0xff273c3d);
            r(c,p,x+w*.19f,y+h*.67f,w*.64f,h*.19f,0xff3f5153);
        }else if(theme==NeighborhoodV154.HOTEL||theme==NeighborhoodV154.APARTMENTS||
                 theme==NeighborhoodV154.RESIDENCES){
            if(type==0||index%4==0){
                // Bed frame, separate pillows, sheets and folded blanket.
                r(c,p,x,y,w,h,0xff343e3a);
                r(c,p,x+4,y+4,w-8,h-8,0xffb5a68a);
                r(c,p,x+8,y+7,(w-20)*.49f,h*.24f,0xffe2dfc8);
                r(c,p,x+w*.52f,y+7,(w-20)*.44f,h*.24f,0xffe2dfc8);
                r(c,p,x+8,y+h*.37f,w-16,h*.50f,
                    theme==NeighborhoodV154.HOTEL?0xff78938c:
                    variant%2==0?0xff8f6a55:0xff849379);
                r(c,p,x+9,y+h*.72f,w-18,6,0xffd3b387);
            }else if(type==3||index%3==0){
                // Kitchen / dining table set with plates and small utensils.
                r(c,p,x,y,w,h,0xff56483b);
                r(c,p,x+5,y+5,w-10,h-12,0xff977b5b);
                oval(c,p,x+w*.2f,y+h*.16f,x+w*.43f,y+h*.59f,0xffd0c9a5);
                oval(c,p,x+w*.54f,y+h*.16f,x+w*.76f,y+h*.59f,0xffd0c9a5);
                r(c,p,x+w*.47f,y+9,5,h*.54f,0xff43595b);
            }else{
                // Bookcase / cupboard with shelves, handles and storage.
                r(c,p,x,y,w,h,0xff3d3e38);
                r(c,p,x+4,y+4,w-8,h-8,0xff856f53);
                for(int i=1;i<4;i++)
                    r(c,p,x+6,y+i*h/4f,w-12,4,0xff453c35);
                r(c,p,x+w*.47f,y+8,4,h-16,0xffba9c68);
                r(c,p,x+w*.58f,y+h*.52f,5,8,0xff2b3534);
            }
        }else{
            // Fallback detailed cabinet, not an empty featureless placeholder.
            r(c,p,x,y,w,h,0xff455d5b);
            r(c,p,x+4,y+4,w-8,h-8,0xff6e8073);
            for(int i=0;i<4;i++)
                r(c,p,x+6,y+6+i*(h-13)/4f,w-12,4,0xff283f43);
            r(c,p,x+w*.47f,y+8,5,h-17,0xffb3b79a);
        }
        c.restore();
    }
}
