package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;

/**
 * V123 first native environmental gameplay pass. Source art is planned for the
 * later sprite-atlas pass; this scalable geometric scene exposes real collision,
 * room openings and reversible deterministic sectors instead of a flat mockup.
 */
public final class IndustrialSceneV123 {
    private IndustrialSceneV123(){}
    private static void r(Canvas c,Paint p,float x,float y,float w,float h,int color){
        p.setColor(color);p.setStyle(Paint.Style.FILL);
        c.drawRect(x,y,x+w,y+h,p);
    }
    private static void line(Canvas c,Paint p,float x,float y,float xx,float yy,float size,int color){
        p.setColor(color);p.setStrokeWidth(size);c.drawLine(x,y,xx,yy,p);
    }
    private static void machine(Canvas c,Paint p,float x,float y,float w,float h,int color,int mode){
        r(c,p,x-7,y-7,w+14,h+14,0xff1b262a);
        r(c,p,x,y,w,h,color);
        r(c,p,x+11,y+11,w-22,h-24,0xff35454a);
        r(c,p,x+19,y+20,w-38,Math.max(7,h/3),0xff718081);
        r(c,p,x+26,y+h*.59f,w-52,9,0xff181e20);
        for(int i=0;i<4;i++){
            r(c,p,x+14+i*(w-30)/4f,y+h-18,Math.max(6,(w-50)/8f),8,
              (i+mode)%2==0?0xffb68a38:0xff263339);
        }
        r(c,p,x+w*.14f,y+14,8,8,0xffda8d32);
        r(c,p,x+w*.81f,y+14,8,8,0xffd7b15f);
    }
    private static void rack(Canvas c,Paint p,float x,float y,float w,float h,int seed){
        r(c,p,x,y,w,h,0xff202c2f);
        r(c,p,x+7,y+7,w-14,h-14,0xff776952);
        for(int i=0;i<3;i++){
            float yy=y+15+i*(h-30)/3f;
            r(c,p,x+14,yy,w-28,10,0xff263b3b);
            for(int j=0;j<3;j++)
                r(c,p,x+17+j*(w-38)/3f,yy+3,(w-58)/3f,12,
                    ((seed+i+j)&1)==0?0xffa1774b:0xff617070);
        }
        r(c,p,x+6,y+5,9,h-10,0xffb08033);
        r(c,p,x+w-15,y+5,9,h-10,0xffb08033);
    }
    private static void metal(Canvas c,Paint p,float x,float y,float w,float h){
        r(c,p,x-4,y-4,w+8,h+8,0xff1d2c2d);
        r(c,p,x,y,w,h,0xff806f59);
        for(int i=0;i<6;i++){
            float yy=y+8+i*(h-14)/6f;
            r(c,p,x+7,yy,w-14,Math.max(3,h/23),0xffaab0a2);
            r(c,p,x+11,yy+4,w-22,2,0xff4c5d5f);
        }
    }
    private static void ground(Canvas c,Paint p,int sx,int sy,int seed){
        float x=sx*(float)IndustrialWorldV123.SECTOR;
        float y=sy*(float)IndustrialWorldV123.SECTOR;
        r(c,p,x,y,1400,1400,0xff565954);
        for(int k=0;k<10;k++){
            int h=IndustrialWorldV123.hash(sx*13+k,sy*19-k,seed);
            float xx=x+Math.floorMod(h,1350);
            float yy=y+Math.floorMod(h>>>10,1350);
            r(c,p,xx,yy,34+Math.floorMod(h>>>20,70),11,0x55434a45);
        }
        r(c,p,x-IndustrialWorldV123.roadWidth(sx)/2f,y-5,
          IndustrialWorldV123.roadWidth(sx),1410,0xff252e30);
        r(c,p,x-5,y-IndustrialWorldV123.roadWidth(sy)/2f,
          1410,IndustrialWorldV123.roadWidth(sy),0xff252e30);
        for(int k=0;k<14;k++){
            r(c,p,x-3,y+40+k*95,6,48,0xffb49c62);
            r(c,p,x+40+k*95,y-3,48,6,0xffb49c62);
        }
    }
    private static void building(Canvas c,Paint p,IndustrialWorldV123.District d){
        float x=d.x,y=d.y;
        // Concrete forecourt and four distinct building profiles.
        r(c,p,x+120,y+160,845,655,0xff454e4e);
        r(c,p,x+145,y+184,793,548,0xff142227);
        r(c,p,x+157,y+196,770,510,0xff656d68);
        int[] roof={0xff687378,0xff79685e,0xff6e6359,0xff52656a};
        r(c,p,x+170,y+205,741,500,roof[d.kind%4]);
        for(int i=0;i<9;i++)
            r(c,p,x+183+i*81,y+215,34,467,0x44502017);
        for(int i=0;i<6;i++){
            r(c,p,x+195+i*115,y+245,70,9,0xff3b4749);
            r(c,p,x+195+i*115,y+258,70,7,0xffb58e5f);
        }
        r(c,p,x+227,y+287,635,65,0xff343f43);
        r(c,p,x+232,y+291,626,14,0xff87908a);
        for(int j=0;j<5;j++)
            r(c,p,x+244+j*125,y+300,95,27,0xff596569);
        r(c,p,x+444,y+610,192,93,0xff1c2c30);
        r(c,p,x+454,y+620,174,82,0xff77746a);
        for(int i=0;i<6;i++)r(c,p,x+462,y+630+i*10,155,4,0xff323f42);
        // Accessible USE portal, not a painted-over collision wall.
        r(c,p,d.doorX-76,d.doorY-8,152,19,0xff172a2c);
        r(c,p,d.doorX-70,d.doorY-4,140,13,0xffb99e63);
        r(c,p,d.doorX-58,d.doorY+12,116,30,0xffb4a277);
        r(c,p,d.doorX-55,d.doorY+19,110,6,0xff263b3c);
        // Storage stacks and machinery occupy consistent bounded pads.
        for(int i=0;i<4;i++){
            float px=d.materialX(i),py=d.materialY(i);
            metal(c,p,px-68,py-34,136,62);
        }
        machine(c,p,x+175,y+930,150,110,0xff78533c,d.kind);
        machine(c,p,x+945,y+845,170,120,0xff565c58,d.kind+1);
        machine(c,p,x+970,y+1080,170,120,0xff805c43,d.kind+2);
        rack(c,p,x+745,y+945,190,83,d.kind);
        // Industrial yard chainlink fence with real wide gates in the south wall.
        r(c,p,x+90,y+1220,400,12,0xff364345);
        r(c,p,x+590,y+1220,685,12,0xff364345);
        for(int i=0;i<11;i++){
            if(i==4||i==5)continue;
            r(c,p,x+120+i*107,y+1212,9,31,0xffa38757);
        }
        r(c,p,x+90,y+165,14,1065,0xff4b5758);
        r(c,p,x+1274,y+165,14,1065,0xff4b5758);
    }
    public static void outdoors(Canvas c,Paint p,float camX,float camY,
                                float vw,float vh,int seed){
        int x0=IndustrialWorldV123.sector(camX)-1,x1=IndustrialWorldV123.sector(camX+vw)+1;
        int y0=IndustrialWorldV123.sector(camY)-1,y1=IndustrialWorldV123.sector(camY+vh)+1;
        for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++)
            ground(c,p,x,y,seed);
        for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++)
            building(c,p,IndustrialWorldV123.district(x,y,seed));
    }
    public static boolean outsideBlocked(float x,float y,float radius,int seed){
        int cx=IndustrialWorldV123.sector(x),cy=IndustrialWorldV123.sector(y);
        for(int sy=cy-1;sy<=cy+1;sy++)for(int sx=cx-1;sx<=cx+1;sx++){
            float bx=sx*(float)IndustrialWorldV123.SECTOR;
            float by=sy*(float)IndustrialWorldV123.SECTOR;
            if(x+radius>bx+170 && x-radius<bx+911 &&
               y+radius>by+205 && y-radius<by+706)return true;
            // Machinery and steel stacks are physically solid. Yard paths are free.
            if(x+radius>bx+175 && x-radius<bx+325 &&
               y+radius>by+930 && y-radius<by+1040)return true;
            if(x+radius>bx+945 && x-radius<bx+1115 &&
               y+radius>by+845 && y-radius<by+965)return true;
        }
        return false;
    }
    public static void indoors(Canvas c,Paint p,IndustrialInteriorV123 room){
        int seed=room.district.seed;
        int kind=room.district.kind;
        r(c,p,0,0,2720,1904,0xff253137);
        r(c,p,36,36,2648,1825,kind==2?0xff605e57:0xff5e6969);
        for(int i=0;i<40;i++)r(c,p,36+i*68,38,2,1820,0x33515a58);
        for(int i=0;i<27;i++)r(c,p,36,36+i*68,2648,2,0x33515a58);
        // Cross-shaped main avenues and room access are always left open.
        r(c,p,1080,38,560,1822,0xff80817a);
        r(c,p,536,820,1644,210,0xff777b77);
        for(int y=160;y<1700;y+=135)r(c,p,1354,y,12,61,0xffc1a365);
        for(float[] wall:IndustrialInteriorV123.WALLS){
            r(c,p,wall[0]-4,wall[1]-4,wall[2]+8,wall[3]+8,0xff17252a);
            r(c,p,wall[0],wall[1],wall[2],wall[3],0xff68605a);
            r(c,p,wall[0]+4,wall[1]+3,Math.max(3,wall[2]-8),5,0xffad8969);
        }
        for(int i=0;i<IndustrialInteriorV123.MACHINES.length;i++){
            float[] q=IndustrialInteriorV123.MACHINES[i];
            if(i<6)machine(c,p,q[0],q[1],q[2],q[3],kind==2?0xff82563d:0xff4c595c,i);
            else if(i<14)rack(c,p,q[0],q[1],q[2],q[3],seed+i);
            else metal(c,p,q[0],q[1],q[2],q[3]);
        }
        // Each wing opening gets a striped physical doorway and direction cue.
        for(int i=0;i<3;i++){
            float y=i==0?315:i==1?810:1315;
            for(float x:new float[]{510,2180}){
                r(c,p,x-15,y,58,14,0xffba8b39);
                r(c,p,x-15,y+145,58,11,0xffba8b39);
            }
        }
        for(int i=0;i<14;i++){
            ClinicInteriorV89.Storage s=room.storages[i];
            r(c,p,s.x-31,s.y-18,62,36,0xff1c292b);
            r(c,p,s.x-26,s.y-13,52,27,s.empty()?0xff58615b:0xff9a754a);
            r(c,p,s.x-20,s.y-7,40,5,0xffd1b782);
        }
        // Explicit unblocked threshold on the actual V90 exit coordinate.
        r(c,p,1235,1858,250,22,0xffc0a36a);
        for(int i=0;i<8;i++)r(c,p,1241+i*30,1858,15,15,0xff243235);
    }
}
