package com.survivalparadise.nativegame;

/**
 * V124 isolated industrial region. Infinite signed sector coordinates; all
 * decisions depend exclusively on (seed, world coordinate), never on drawing
 * order or the player's travel history. Roads are continuous within arterial
 * superblocks; side streets terminate on an arterial, not empty ground.
 */
public final class IndustrialOpenWorldV124 {
    private IndustrialOpenWorldV124(){}
    public static final int SIZE=IndustrialWorldV123.SECTOR;
    public static final int VACANT=0,YARD=1,FACILITY=2;
    public static final int MINOR_WIDTH=IndustrialWorldV123.MINOR_ROAD;
    public static final int MAJOR_WIDTH=IndustrialWorldV123.ARTERIAL_ROAD;

    public static int sx(float x){return (int)Math.floor(x/(double)SIZE);}
    public static int sy(float y){return (int)Math.floor(y/(double)SIZE);}
    public static boolean vertical(int boundary,int sy,int seed){
        if(Math.floorMod(boundary,4)==0)return true;
        // The value cannot vary in the middle of a four-sector road run.
        int band=Math.floorDiv(sy,4);
        return Math.floorMod(IndustrialWorldV123.hash(boundary,band,seed^0x245A5A27),5)<3;
    }
    public static boolean horizontal(int boundary,int sx,int seed){
        if(Math.floorMod(boundary,4)==0)return true;
        int band=Math.floorDiv(sx,4);
        return Math.floorMod(IndustrialWorldV123.hash(band,boundary,seed^0x6F31925B),5)<3;
    }
    public static int verticalWidth(int boundary){
        return Math.floorMod(boundary,4)==0?MAJOR_WIDTH:MINOR_WIDTH;
    }
    public static int horizontalWidth(int boundary){
        return Math.floorMod(boundary,4)==0?MAJOR_WIDTH:MINOR_WIDTH;
    }
    public static boolean roadAt(float x,float y,int seed){
        int bx=(int)Math.floor(x/(double)SIZE+0.5);
        int by=(int)Math.floor(y/(double)SIZE+0.5);
        return (Math.abs(x-bx*(double)SIZE)<=verticalWidth(bx)*0.5f&&
                vertical(bx,sy(y),seed)) ||
               (Math.abs(y-by*(double)SIZE)<=horizontalWidth(by)*0.5f&&
                horizontal(by,sx(x),seed));
    }
    public static int family(int sx,int sy,int seed){
        int macroX=Math.floorDiv(sx,4), macroY=Math.floorDiv(sy,4);
        int regional=Math.floorMod(IndustrialWorldV123.hash(macroX,macroY,seed^0x14F2B),(8));
        int local=Math.floorMod(IndustrialWorldV123.hash(sx,sy,seed^0x7A17F),6);
        // District families have character; every plot is not randomized alone.
        return Math.floorMod(regional+(local==0?1:local==1?2:0),8);
    }
    /** All built facilities have the actual site entrance V123 can enter. */
    public static final class Plot {
        public final int sx,sy,seed,kind,type,gateSide;
        public final float x,y,buildingX,buildingY,buildingW,buildingH,doorX,doorY;
        public final String name;
        private Plot(int sx,int sy,int seed){
            this.sx=sx;this.sy=sy;this.seed=seed;
            x=sx*(float)SIZE;y=sy*(float)SIZE;
            kind=family(sx,sy,seed);
            name=IndustrialWorldV123.FACILITIES[kind];
            int roll=Math.floorMod(IndustrialWorldV123.hash(sx*37+7,sy*29-2,seed^0x2FEC0),100);
            boolean south=horizontal(sy+1,sx,seed);
            boolean west=vertical(sx,sy,seed);
            boolean east=vertical(sx+1,sy,seed);
            boolean connection=south||west||east;
            // The first plot is a guaranteed playable starting industrial site.
            type=(sx==0&&sy==0)?FACILITY:!connection?VACANT:
                roll<18?VACANT:roll<35?YARD:FACILITY;
            gateSide=south?0:west?1:east?2:-1;
            // Several genuine different footprint sizes, no single repeated box.
            int size=Math.floorMod(IndustrialWorldV123.hash(sx+31,sy+17,seed^0x394A),4);
            buildingW=(kind==3||kind==0)?930:size==0?610:size==1?735:size==2?830:930;
            buildingH=(kind==3||kind==0)?555:size==0?385:size==1?445:size==2?495:555;
            buildingX=x+700-buildingW*.5f;
            buildingY=y+780-buildingH;
            doorX=x+700;
            doorY=y+810;
        }
        public boolean developed(){return type!=VACANT;}
        public boolean enterable(){return type==FACILITY;}
        public String id(){return sx+","+sy;}
    }
    public static Plot plot(int sx,int sy,int seed){
        return new Plot(sx,sy,seed);
    }
    public static Plot at(float x,float y,int seed){
        return plot(sx(x),sy(y),seed);
    }
    public static IndustrialWorldV123.District nearestEntrance(float x,float y,float reach,int seed){
        int cx=sx(x),cy=sy(y);
        IndustrialWorldV123.District best=null;
        float bestDistance=reach*reach;
        for(int iy=cy-1;iy<=cy+1;iy++)for(int ix=cx-1;ix<=cx+1;ix++){
            Plot p=plot(ix,iy,seed);
            if(!p.enterable())continue;
            float dx=x-p.doorX,dy=y-p.doorY,dist=dx*dx+dy*dy;
            if(dist<=bestDistance){
                bestDistance=dist;
                best=IndustrialWorldV123.district(ix,iy,seed);
            }
        }
        return best;
    }
    public static Plot firstStart(int seed){
        Plot p=plot(0,0,seed);
        return p;
    }
    /** Lightweight hit test for actual roofs, yard fencing and stationary assets. */
    public static boolean blocked(float x,float y,float radius,int seed){
        int cx=sx(x),cy=sy(y);
        for(int iy=cy-1;iy<=cy+1;iy++)for(int ix=cx-1;ix<=cx+1;ix++){
            Plot p=plot(ix,iy,seed);
            if(!p.developed())continue;
            if(p.enterable()&&touch(x,y,radius,p.buildingX,p.buildingY,p.buildingW,p.buildingH))return true;
            // Perimeter mesh has one true, broad gate in the south.
            if(touch(x,y,radius,p.x+110,p.y+1206,473,13))return true;
            if(touch(x,y,radius,p.x+830,p.y+1206,438,13))return true;
            if(touch(x,y,radius,p.x+101,p.y+128,13,1091))return true;
            if(touch(x,y,radius,p.x+1265,p.y+128,13,1091))return true;
            // These are the same concrete pads used by outdoor machinery art.
            if(p.type==FACILITY){
                if(touch(x,y,radius,p.x+220,p.y+895,165,115))return true;
                if(touch(x,y,radius,p.x+965,p.y+855,175,126))return true;
            }
            if(p.type==YARD){
                if(touch(x,y,radius,p.x+220,p.y+700,230,170))return true;
                if(touch(x,y,radius,p.x+890,p.y+775,255,160))return true;
            }
        }
        return false;
    }
    private static boolean touch(float x,float y,float r,float px,float py,float w,float h){
        return x+r>px&&x-r<px+w&&y+r>py&&y-r<py+h;
    }
    public static int streetCount(int sx,int sy,int seed){
        int count=0;
        if(horizontal(sy,sx,seed))count++;
        if(horizontal(sy+1,sx,seed))count++;
        if(vertical(sx,sy,seed))count++;
        if(vertical(sx+1,sy,seed))count++;
        return count;
    }
}
