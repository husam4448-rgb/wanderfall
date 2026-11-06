package com.survivalparadise.nativegame;

/**
 * V126 actual silhouette collision traced from the four approved transparent
 * industrial facade source PNGs. Every 32x32 bit corresponds to actual artwork
 * opacity, not a guessed building rectangle. Same source-to-world transform is
 * used for both drawing and collision.
 */
public final class IndustrialFacadeShapeV126 {
    private IndustrialFacadeShapeV126(){}
    private static final int GRID=32;
    // Packed 32 horizontal occupancy bits for each of 32 source-image rows.
    private static final String[] SOURCE={
        "000000000000000000000000000000000003c000000ff000103ffe0011ffff8017ffffe01ffffff03ffffffc3ffffffc3ffffffc3ffffffc7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe0c03802e000000000000000000000000",
        "0000000000000000000100000007c000001ff800003ffc0001ffff3003fffff00ffffff01ffffffc3ffffffc3ffffffe3ffffffe3ffffffc3ffffffe7ffffffc7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe3ffffffe3ffffffc3ffffffc3ffffffc3ffffffc3ffffffc3ffffffe3ffffffe3ffffffe0000000000000000",
        "0000000000000000000180000007e000001ff800007ffe0001ffff0007ffffc00ffffff03ffffffc3ffffffc3ffffffc3ffffffc3ffffffc3ffffffc3ffffffc7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe3ffffffc3ffffffc3ffffffc3ffffffc3ffffffc3ffffffc3ffffffc7ffffffc3ffffffc0000000000000000",
        "000000000000000000000000000000000003c000003ffc0203ffff821ffffffa1ffffffa3ffffffe3ffffffe3ffffffe3ffffffe3ffffffe7ffffffe7ffffffe7ffffffe7ffffffe3ffffffe3ffffffe7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe7ffffffe000003f000000000000000000000000000000000"
    };
    private static final int[][] SHAPE=load();
    private static int[][] load(){
        int[][] out=new int[SOURCE.length][GRID];
        for(int i=0;i<SOURCE.length;i++){
            if(SOURCE[i].length()!=GRID*8)
                throw new IllegalStateException("V126 alpha mask missing rows");
            for(int y=0;y<GRID;y++){
                int n=0;
                for(int j=y*8;j<(y+1)*8;j++)
                    n=(n<<4)|Character.digit(SOURCE[i].charAt(j),16);
                out[i][y]=n;
            }
        }
        return out;
    }
    /** Approved facades: 0 double factory, 1 single, 2 shed, 3 warehouse. */
    public static int facade(int kind){
        if(kind==4||kind==6)return 1;
        if(kind==5)return 2;
        if(kind==3||kind==7)return 3;
        return 0;
    }
    public static boolean opaque(int facade,int x,int y){
        return facade>=0&&facade<SHAPE.length&&x>=0&&x<GRID&&y>=0&&y<GRID
            &&(SHAPE[facade][y]&(1<<(GRID-1-x)))!=0;
    }
    public static boolean buildingBlocks(IndustrialOpenWorldV124.Plot p,
                                         float x,float y,float radius){
        if(!p.enterable())return false;
        return overlaps(facade(p.kind),x,y,radius,
            p.buildingX-12f,p.buildingY-22f,p.buildingW+24f,p.buildingH+46f);
    }
    public static boolean overlaps(int facade,float x,float y,float radius,
                                   float left,float top,float width,float height){
        if(facade<0||facade>=SHAPE.length||width<=0||height<=0||radius<0)return false;
        if(x+radius<=left||x-radius>=left+width||
           y+radius<=top||y-radius>=top+height)return false;
        int x0=Math.max(0,(int)Math.floor((x-radius-left)*GRID/width));
        int x1=Math.min(GRID-1,(int)Math.floor((x+radius-left)*GRID/width));
        int y0=Math.max(0,(int)Math.floor((y-radius-top)*GRID/height));
        int y1=Math.min(GRID-1,(int)Math.floor((y+radius-top)*GRID/height));
        float cw=width/GRID,ch=height/GRID;
        for(int gy=y0;gy<=y1;gy++){
            int bits=SHAPE[facade][gy];
            if(bits==0)continue;
            float cy1=top+gy*ch,cy2=cy1+ch;
            float dy=Math.max(cy1-y,Math.max(0,y-cy2));
            for(int gx=x0;gx<=x1;gx++){
                if((bits&(1<<(GRID-1-gx)))==0)continue;
                float cx1=left+gx*cw,cx2=cx1+cw;
                float dx=Math.max(cx1-x,Math.max(0,x-cx2));
                if(dx*dx+dy*dy<=radius*radius)return true;
            }
        }
        return false;
    }
}
