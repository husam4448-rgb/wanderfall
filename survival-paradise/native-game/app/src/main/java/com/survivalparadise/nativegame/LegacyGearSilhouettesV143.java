package com.survivalparadise.nativegame;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;

/** Non-destructive distinct pixel-art outlines for three pre-V140 legacy
 * equipment families. Generated only from the original approved torso/pants/
 * boot sprites and drawn ONCE on startup, not per frame.
 *
 * The source PNGs, 200 original head images, body anchors, foot geometry and
 * five V133 idle/walk boot positions are never modified. No head accessories.
 */
final class LegacyGearSilhouettesV143 {
    private LegacyGearSilhouettesV143(){}

    private static final int INK=0xff161b20,STITCH=0xffc4b08a;
    private static Paint pixels(int color){
        Paint p=new Paint();p.setAntiAlias(false);p.setFilterBitmap(false);
        p.setColor(color);return p;
    }
    private static void patch(Canvas c,int x,int y,int w,int h,int base){
        if(w<6||h<6)return;
        c.drawRect(x,y,x+w,y+h,pixels(INK));
        c.drawRect(x+2,y+2,x+w-2,y+h-2,pixels(base));
        c.drawRect(x+4,y+4,x+w-4,y+6,pixels(0x60ffffff));
    }
    private static void seam(Canvas c,int x,int y,int x2,int y2,int shade){
        Paint p=pixels(shade);p.setStrokeWidth(3);
        c.drawLine(x,y,x2,y2,p);
        p.setStrokeWidth(1);p.setColor(0x80ddddcb);
        c.drawLine(x+2,y+2,x2+2,y2+2,p);
    }
    static Bitmap torso(Bitmap source,int variant){
        if(source==null||variant<0||variant>2)return source;
        Bitmap output=source.copy(Bitmap.Config.ARGB_8888,true);
        Canvas c=new Canvas(output);
        float sx=output.getWidth()/200f,sy=output.getHeight()/150f;
        c.save();c.scale(sx,sy);
        switch(variant){
            case 0: // canvas work jacket: rectangular tool loops, flap pockets
                patch(c,18,48,27,24,0xff7e6236);
                patch(c,155,48,27,24,0xff7e6236);
                patch(c,31,99,38,33,0xff936b3b);
                patch(c,131,99,38,33,0xff936b3b);
                seam(c,70,20,67,130,0xff53462e);
                seam(c,129,18,133,130,0xff53462e);
                patch(c,90,31,20,20,0xff9c8b58);
                break;
            case 1: // winter overcoat: quilted shoulder pads and cuff mass
                patch(c,6,30,33,34,0xff758b9e);
                patch(c,161,30,33,34,0xff758b9e);
                patch(c,7,95,29,35,0xff60758b);
                patch(c,163,95,29,35,0xff60758b);
                seam(c,40,46,75,116,0xff46586f);
                seam(c,160,46,127,116,0xff46586f);
                patch(c,91,54,19,32,0xff95a9ac);
                break;
            case 2: // genuine plate carrier: raised chest and magazine pouches
                patch(c,57,40,86,45,0xff4c626b);
                patch(c,63,46,74,32,0xff789099);
                patch(c,43,89,35,32,0xff4c5d61);
                patch(c,83,91,34,31,0xff526771);
                patch(c,122,89,35,32,0xff4c5d61);
                patch(c,6,23,33,33,0xff596773);
                patch(c,161,23,33,33,0xff596773);
                seam(c,53,13,76,41,0xffc6b48a);
                seam(c,148,13,124,41,0xffc6b48a);
                break;
        }
        c.restore();
        return output;
    }
    static Bitmap pants(Bitmap source,int variant){
        if(source==null||variant<0||variant>2)return source;
        Bitmap output=source.copy(Bitmap.Config.ARGB_8888,true);
        Canvas c=new Canvas(output);
        c.save();c.scale(output.getWidth()/217f,output.getHeight()/146f);
        switch(variant){
            case 0: // cargo trousers: deep two-flap cargo pouches
                patch(c,5,38,42,49,0xff64704a);
                patch(c,167,38,42,49,0xff64704a);
                patch(c,11,97,29,21,0xff697755);
                patch(c,175,97,29,21,0xff697755);
                seam(c,62,34,57,130,0xff4a533d);
                seam(c,151,34,160,130,0xff4a533d);
                break;
            case 1: // ripstop: sewn thigh webbing and padded knees
                patch(c,13,37,35,21,0xff66764d);
                patch(c,170,37,35,21,0xff66764d);
                seam(c,12,85,89,47,0xffa8a08a);
                seam(c,204,85,126,47,0xffa8a08a);
                patch(c,26,111,53,23,0xff4c5e45);
                patch(c,139,111,53,23,0xff4c5e45);
                break;
            case 2: // tactical reinforced: extended thigh armor and knee guards
                patch(c,6,29,47,51,0xff3d4a5c);
                patch(c,164,29,47,51,0xff3d4a5c);
                patch(c,24,92,56,43,0xff55697e);
                patch(c,137,92,56,43,0xff55697e);
                patch(c,83,23,51,17,0xff677582);
                seam(c,55,17,55,122,0xff99aab9);
                seam(c,161,17,161,122,0xff99aab9);
                break;
        }
        c.restore();return output;
    }
    static Bitmap boots(Bitmap source,int variant){
        if(source==null||variant<0||variant>2)return source;
        Bitmap output=source.copy(Bitmap.Config.ARGB_8888,true);
        Canvas c=new Canvas(output);
        c.save();c.scale(output.getWidth()/68f,output.getHeight()/52f);
        switch(variant){
            case 0: // steel toe: separate toe cap and double heel outsole
                patch(c,31,26,30,13,0xff8d9294);
                patch(c,4,39,57,10,0xff353b3d);
                seam(c,34,18,48,21,STITCH);
                break;
            case 1: // flexible trail: ribbed ankle and gripped outsole
                patch(c,11,10,15,18,0xff8b8568);
                patch(c,5,39,57,9,0xff59654d);
                for(int x=9;x<61;x+=11)
                    c.drawRect(x,45,x+5,49,pixels(INK));
                break;
            case 2: // tactical: raised ankle shroud and reinforced rounded toe
                patch(c,5,5,25,26,0xff525c65);
                patch(c,32,25,30,14,0xff5d6974);
                patch(c,6,40,58,9,0xff282f37);
                seam(c,12,12,26,25,0xff8e9fa8);
                break;
        }
        c.restore();return output;
    }
}
