package com.survivalparadise.nativegame;

/**
 * V102: pixel-identical native gas-mask palette authored on the locked V31
 * 9x9 head-cell lattice. Head-only variant, not a positioned equipment sprite.
 * Original black contour, original alpha and original eye colors are immutable.
 * No pixel below y=91 or outside the actual head is ever changed.
 */
public final class GasMaskPaletteV102 {
    private GasMaskPaletteV102(){}
    private static final int NONE=-1;
    private static final int[][] COLORS={
        {0xff171a1e, 0xff373e3b, 0xff24272c, 0xff24272c, 0xff373e3b, 0xff5b675e, 0xff373e3b, 0xff24272c},
        {0xff24272c, 0xff373e3b, 0xff24272c, 0xff444c42, 0xff373e3b, 0xff373e3b, 0xff24272c, 0xff24272c},
        {0xff24272c, 0xff373e3b, 0xff24272c, 0xff24272c, 0xff24272c, 0xff24272c, 0xff373e3b, 0xff24272c},
        {0xff24272c, 0xff5b675e, NONE, NONE, 0xff171a1e, 0xff24272c, NONE, NONE},
        {0xff171a1e, 0xff24272c, 0xff373e3b, 0xff24272c, 0xff444c42, 0xff24272c, 0xff24272c, 0xff171a1e},
        {0xff7f898b, 0xffa8aeb0, 0xff24272c, 0xff24272c, 0xff7f898b, 0xff24272c, 0xffa8aeb0, 0xff7f898b},
        {0xff24272c, 0xff7f898b, 0xff24272c, 0xff171a1e, 0xff24272c, 0xff171a1e, 0xff7f898b, 0xff24272c}
    };
    public static int recolor(int x,int y,int original){
        if(x<33||x>104||y<29||y>91)return original;
        if((original>>>24)==0 || (original&0x00ffffff)==0)return original;
        // The two approved eyes, white sclera and turquoise irises, are exact.
        if(y>=56&&y<65 && ((x>=51&&x<69)||(x>=87&&x<105)))return original;
        int cellX=(x-33)/9,cellY=(y-29)/9;
        int fill=COLORS[cellY][cellX];
        if(fill==NONE)return original;
        return (original&0xff000000)|(fill&0x00ffffff);
    }
}
