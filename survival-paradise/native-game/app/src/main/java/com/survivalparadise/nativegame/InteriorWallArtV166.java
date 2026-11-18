package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;

/**
 * V166 architecture treatment. All painted wall footprints derive from the
 * collision segments; door jambs are decorations at the *ends* of segments,
 * not bars crossing traversable openings. Coordinates are in logical V89 units.
 */
public final class InteriorWallArtV166 {
    private InteriorWallArtV166(){}
    private static final int[][] MATERIAL={
        {0xff302f2e,0xff897b69,0xffb8a58b,0xff5c4c40,0xffd4c4a8}, // apartments
        {0xff29343a,0xff74838a,0xffb1b9ac,0xff40565d,0xffd6c6a3}, // office
        {0xff303937,0xff8f9b89,0xffd6d0ad,0xff55695e,0xffc8ad77}, // market
        {0xff312e30,0xff928276,0xffc1b4a4,0xff5b4544,0xffd6bd9b}, // hotel
        {0xff303939,0xff8f9990,0xffc1c6ac,0xff596b63,0xffcfb786}, // school
        {0xff252d31,0xff677579,0xffa5a59a,0xff47565b,0xffb68d58}, // factory
        {0xff272c30,0xff69706b,0xffa8a89a,0xff495050,0xffc29962}, // depot
        {0xff352f2c,0xff897564,0xffbbab8c,0xff635142,0xffd2b991}, // home
        {0xff253c3d,0xff869d96,0xffd9ded0,0xff55746d,0xffd8c3a0}  // clinic
    };
    private static void rect(Canvas c,Paint p,float x,float y,float w,float h,int argb){
        if(w<=0||h<=0)return;
        p.setStyle(Paint.Style.FILL);p.setColor(argb);
        c.drawRect(x,y,x+w,y+h,p);
    }
    private static int mix(int x){
        x^=x>>>16;x*=0x7feb352d;x^=x>>>15;x*=0x846ca68b;
        return x^(x>>>16);
    }
    /** Draw material, relief, trims, discrete seams, wear and contact shadows. */
    public static void draw(Canvas c,Paint p,float[][] walls,float inv,
                            int theme,int seed){
        int[] palette=MATERIAL[theme>=0&&theme<8?theme:8];
        for(int i=0;i<walls.length;i++){
            float[] q=walls[i];
            float x=q[0]*inv,y=q[1]*inv,w=q[2]*inv,h=q[3]*inv;
            if(w<2||h<2)continue;
            boolean horizontal=w>=h;
            // Shadow and detail clip to their *physical* wall footprint.
            // Contact shadow can project onto floors by at most two pixels.
            rect(c,p,x+2,y+2,w,h,0x33222b2a);
            c.save();c.clipRect(x,y,x+w,y+h);
            rect(c,p,x,y,w,h,palette[0]);
            rect(c,p,x+2,y+2,w-4,h-4,palette[1]);
            if(horizontal){
                rect(c,p,x+2,y+2,w-4,Math.min(4,h*.24f),palette[2]);
                rect(c,p,x+2,y+h-5,w-4,3,palette[3]);
                rect(c,p,x+3,y+h*.53f,w-6,2,0x443b3530);
            }else{
                rect(c,p,x+2,y+2,Math.min(4,w*.24f),h-4,palette[2]);
                rect(c,p,x+w-5,y+2,3,h-4,palette[3]);
                rect(c,p,x+w*.53f,y+3,2,h-6,0x443b3530);
            }
            float length=horizontal?w:h, thickness=horizontal?h:w;
            for(int t=27;t<length-8;t+=48){
                int n=mix(seed^i*1379^t*9137);
                float along=t+Math.floorMod(n,15)-7;
                // Uneven mortar seams, repaint chips and subtle exposed brick.
                float a=horizontal?x+along:x+3;
                float b=horizontal?y+3:y+along;
                float cw=horizontal?2:Math.max(3,thickness-6);
                float ch=horizontal?Math.max(3,thickness-7):2;
                rect(c,p,a,b,cw,ch,(n&3)==0?palette[3]:0x4c473e35);
                if((n&7)==2){
                    float cx=horizontal?x+along+5:x+5;
                    float cy=horizontal?y+thickness*.34f:y+along+5;
                    rect(c,p,cx,cy,horizontal?8:4,horizontal?3:9,palette[2]);
                    rect(c,p,cx+2,cy+2,horizontal?4:2,horizontal?2:5,palette[3]);
                }
                if((n&15)==8){
                    float xx=horizontal?x+along-12:x+thickness*.55f;
                    float yy=horizontal?y+thickness*.55f:y+along-12;
                    rect(c,p,xx,yy,horizontal?15:2,horizontal?2:15,palette[3]);
                }
            }
            c.restore();
        }
    }
    /**
     * Reveal the *actual* open 164-unit V163 door cut with side jambs and
     * slim recessed threshold; no solid crossbar, no added collision.
     */
    public static void doorway(Canvas c,Paint p,float centerX,float centerY,
                               boolean wallVertical,int theme){
        int[] pal=MATERIAL[theme>=0&&theme<8?theme:8];
        if(wallVertical){
            for(int side=-1;side<=1;side+=2){
                float yy=centerY+side*82f;
                rect(c,p,centerX-1,yy-7,22,14,pal[0]);
                rect(c,p,centerX+2,yy-5,16,8,pal[4]);
                rect(c,p,centerX+7,yy-3,7,4,pal[3]);
            }
            rect(c,p,centerX+5,centerY-68,2,136,0x44483f37);
        }else{
            for(int side=-1;side<=1;side+=2){
                float xx=centerX+side*82f;
                rect(c,p,xx-7,centerY-1,14,22,pal[0]);
                rect(c,p,xx-5,centerY+2,8,16,pal[4]);
                rect(c,p,xx-3,centerY+7,4,7,pal[3]);
            }
            rect(c,p,centerX-68,centerY+5,136,2,0x44483f37);
        }
    }
}
