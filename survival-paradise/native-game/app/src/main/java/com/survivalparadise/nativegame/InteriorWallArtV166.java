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
    /**
     * Use the existing authored indoor-material atlas as the wall's painted
     * masonry / timber grain instead of a flat solid-color programmer strip.
     * This is a rendering-only treatment; each clip is the exact V163
     * collision wall, so the 164-unit door cuts remain completely open.
     */
    private static int material(int theme){
        switch(theme){
            case 0:case 3:case 7:return InteriorFloorSelectionV166.OAK;
            case 1:case 2:case 8:return InteriorFloorSelectionV166.TERRAZZO;
            case 4:return InteriorFloorSelectionV166.LINO;
            default:return InteriorFloorSelectionV166.CONCRETE;
        }
    }
    /** Painterly textured surface, continuous junctions and inset trim. */
    public static void draw(Canvas c,Paint p,float[][] walls,float inv,
                            int theme,int seed){
        int[] palette=MATERIAL[theme>=0&&theme<8?theme:8];
        int material=material(theme);
        // Base pass first: intersecting perimeter, corner and partition wall
        // segments are not left with individual dark caps at their crossings.
        for(int i=0;i<walls.length;i++){
            float[] q=walls[i];
            float x=q[0]*inv,y=q[1]*inv,w=q[2]*inv,h=q[3]*inv;
            if(w<2||h<2)continue;
            rect(c,p,x+2,y+3,w,h,0x40202927);
            rect(c,p,x,y,w,h,palette[0]);
            c.save();
            c.clipRect(x,y,x+w,y+h);
            if(InteriorFloorArtV166.fill(c,material,
                x+1,y+1,w-2,h-2,seed^theme*739,94f)){
                // Semi-transparent colored wash retains visible authored
                // stone/wood grain without copying the room's floor palette.
                rect(c,p,x+1,y+1,w-2,h-2,
                    0x95000000|(palette[1]&0x00ffffff));
            }else{
                rect(c,p,x+1,y+1,w-2,h-2,palette[1]);
            }
            c.restore();
        }
        // Seam, skirting and wear details remain within physical wall faces.
        for(int i=0;i<walls.length;i++){
            float[] q=walls[i];
            float x=q[0]*inv,y=q[1]*inv,w=q[2]*inv,h=q[3]*inv;
            if(w<2||h<2)continue;
            boolean horizontal=w>=h;
            c.save();c.clipRect(x,y,x+w,y+h);
            if(horizontal){
                rect(c,p,x+2,y+2,w-4,Math.min(3,h*.22f),palette[2]);
                rect(c,p,x+2,y+h-5,w-4,3,palette[3]);
                rect(c,p,x+3,y+h*.54f,w-6,2,0x503b3530);
            }else{
                rect(c,p,x+2,y+2,Math.min(3,w*.22f),h-4,palette[2]);
                rect(c,p,x+w-5,y+2,3,h-4,palette[3]);
                rect(c,p,x+w*.54f,y+3,2,h-6,0x503b3530);
            }
            float length=horizontal?w:h,thickness=horizontal?h:w;
            for(int t=35;t<length-11;t+=61){
                int n=mix(seed^i*1379^t*9137);
                float along=t+Math.floorMod(n,15)-7;
                float a=horizontal?x+along:x+3;
                float b=horizontal?y+3:y+along;
                rect(c,p,a,b,horizontal?2:Math.max(3,thickness-7),
                    horizontal?Math.max(3,thickness-7):2,
                    (n&3)==0?0x88473e35:0x59473e35);
                if((n&7)==2){
                    rect(c,p,horizontal?x+along+5:x+5,
                        horizontal?y+thickness*.34f:y+along+5,
                        horizontal?8:4,horizontal?3:9,palette[2]);
                }
            }
            c.restore();
        }
        // Connect only truly touching *orthogonal* structural segments.
        // Long door openings are never bridged by this visual-only pass.
        for(int i=0;i<walls.length;i++){
            float[] a=walls[i];
            if(a[2]<2||a[3]<2)continue;
            boolean ah=a[2]>=a[3];
            for(int j=i+1;j<walls.length;j++){
                float[] b=walls[j];
                if(b[2]<2||b[3]<2||(b[2]>=b[3])==ah)continue;
                float l=Math.max(a[0],b[0])*inv,
                    t=Math.max(a[1],b[1])*inv;
                float r=Math.min(a[0]+a[2],b[0]+b[2])*inv,
                    bt=Math.min(a[1]+a[3],b[1]+b[3])*inv;
                if(r<l-.25f||bt<t-.25f)continue;
                float jw=Math.max(1f,r-l),jh=Math.max(1f,bt-t);
                rect(c,p,l,t,jw,jh,0x775f615a);
                // A narrow shared cap unifies masonry courses at T-joints
                // without filling any traversable gap.
                rect(c,p,l,t,Math.min(3f,jw),Math.min(3f,jh),
                    palette[2]);
            }
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
