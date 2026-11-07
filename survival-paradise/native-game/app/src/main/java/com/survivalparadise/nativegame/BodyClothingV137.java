package com.survivalparadise.nativegame;

/**
 * V137 universal, pixel-locked Walk 2 body. Shared by all 200 heads, idle
 * and the four walking frames. Only colored INNER pixels change with equipped
 * torso/leg clothing. Black contour never changes between clothing variants.
 *
 * Approved source: V109 original body_walk.png, frame 2, 200 x 260 pixels.
 * Separate V133 boots and V109/V5 fitted heads must never be recolored here.
 */
final class BodyClothingV137 {
    static final int WIDTH=200, HEIGHT=260;
    static final int BLACK=0xff000000;
    static final int RED=0xff820000;
    static final int BLUE=0xff004aa1;
    static final int[] TOP={0xff70664a,0xff4a606c,0xff343d45};
    static final int[] PANTS={0xff8d7856,0xff51674c,0xff3b444e};
    static final int UNDER_LEFT=60,UNDER_RIGHT=140;
    static final int UNDER_TOP=220,UNDER_BOTTOM=236; // 16px, slightly thinner than side contour

    private BodyClothingV137(){}

    static int styleKey(int torsoStyle,int pantStyle){
        return (normalized(torsoStyle)+1)*4+normalized(pantStyle)+1;
    }
    static int normalized(int style){return style>=0&&style<3?style:-1;}

    static void apply(int[] pixels,int width,int height,
                      int torsoStyle,int pantStyle){
        if(width!=WIDTH||height!=HEIGHT||pixels==null||
           pixels.length!=WIDTH*HEIGHT)
            throw new IllegalArgumentException("V137 locked 200x260 body only");
        torsoStyle=normalized(torsoStyle);
        pantStyle=normalized(pantStyle);
        // Preserve ALL existing black silhouette pixels and transparency above
        // y220. Red region belongs to torso, blue strip belongs to trousers.
        for(int y=160;y<220;y++)for(int x=0;x<WIDTH;x++){
            int at=y*WIDTH+x,src=pixels[at];
            if(y<200&&(src==RED||src==BLUE)){
                pixels[at]=torsoPixel(torsoStyle,x,y);
            }else if(y>=200&&src==BLUE){
                pixels[at]=pantsPixel(pantStyle,x,y);
            }
        }
        // Canonical underside: 80px wide, centered on the same x100 axis as
        // pants; 16px tall versus the old 20px. No external outline overlay.
        for(int y=UNDER_TOP;y<240;y++)for(int x=UNDER_LEFT;x<UNDER_RIGHT;x++)
            pixels[y*WIDTH+x]=0;
        for(int y=UNDER_TOP;y<UNDER_BOTTOM;y++)for(int x=UNDER_LEFT;x<UNDER_RIGHT;x++)
            pixels[y*WIDTH+x]=BLACK;
    }

    private static int torsoPixel(int kind,int x,int y){
        if(kind<0)return RED;
        int base=TOP[kind];
        if(kind==0){ // canvas work jacket: restrained stitched seams/pockets
            if(y>=184&&y<190&&(x>=55&&x<80||x>=120&&x<145))
                return 0xff625b44;
            if(y<180&&x>=90&&x<95)return 0xff8a805c;
        }else if(kind==1){ // weatherproof field coat
            if(y>=184&&y<188)return 0xff607984;
            if(x>=99&&x<103)return 0xff384c58;
        }else{ // plate carrier: block armor panels, never an overlay
            if(y>=163&&y<178&&x>=61&&x<139)
                return 0xff626b70;
            if(y>=182&&y<192&&x>=82&&x<119)
                return 0xff4a555b;
        }
        return base;
    }

    private static int pantsPixel(int kind,int x,int y){
        if(kind<0)return BLUE;
        int base=PANTS[kind];
        if(kind==0){ // cargo trousers
            if(y>=207&&y<210&&(x<90||x>=110))return 0xffa18a64;
        }else if(kind==1){ // subtle ripstop weave
            if((x+y)%13<2)return 0xff61765a;
        }else{ // reinforced tactical panels
            if(x>=94&&x<107||y>=213&&y<216)return 0xff515b64;
        }
        return base;
    }
}
