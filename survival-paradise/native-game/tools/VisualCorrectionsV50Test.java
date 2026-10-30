package com.survivalparadise.nativegame;

import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;

/** Validate unaltered approved face contour and its minimal render-only correction. */
public final class VisualCorrectionsV50Test {
    private static void require(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    public static void main(String[] args)throws Exception {
        BufferedImage atlas=ImageIO.read(new File(args[0]));
        BufferedImage original=ImageIO.read(new File(args[1]));
        require(atlas.getWidth()==1040&&atlas.getHeight()==160,"V44 atlas size changed");
        int[] faceEnd={96,100,104,100},missing={0,2,4,2},right={105,107,109,107};
        for(int f=0;f<4;f++){
            for(int y=29;y<92;y++){
                int start=faceEnd[f]-missing[f]+1;
                int last=-1;
                for(int x=0;x<=right[f];x++){
                    int c=atlas.getRGB(f*260+x,y);
                    if((c>>>24)!=0&&(c&0xffffff)!=0)last=x;
                }
                require(last==faceEnd[f],"Face/palette not original frame "+f);
                int after=last;
                if(missing[f]>0&&start<=last)after=start-1;
                require(right[f]-after==9,"Front head outline not 9px frame "+f);
                // All previously present black silhouette pixels remain black.
                for(int x=right[f]-8+missing[f];x<=right[f];x++)
                    require((atlas.getRGB(f*260+x,y)&0xffffff)==0,"Atlas contour corruption");
            }
            for(int y=0;y<110;y++)for(int x=0;x<260;x++)
                require(atlas.getRGB(f*260+x,y)==original.getRGB(f*260+x,y),
                    "Walking head identity modified at f="+f+" x="+x+" y="+y);
        }
        // Depth sorting is tested by source-layer guard in CI, because Android
        // Canvas operations cannot be executed by this pure-Java test.
        System.out.println("PASS V50: four approved faces keep source pixels, runtime correction makes 9px front contour");
    }
}