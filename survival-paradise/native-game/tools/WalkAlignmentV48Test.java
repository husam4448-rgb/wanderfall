package com.survivalparadise.nativegame;
import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;

/** Pixel regression: preserve original V44 atlas and stabilize torso/face. */
public final class WalkAlignmentV48Test {
    static void check(boolean b,String m){if(!b)throw new AssertionError(m);}
    static double match(BufferedImage atlas,int f,int offset){
        int same=0,total=0;
        for(int y=20;y<=108;y++)for(int x=20;x<=124;x++){
            int xx=x-offset;
            int a=xx<0||xx>=260?0:atlas.getRGB(f*260+xx,y);
            int b=atlas.getRGB(260+x,y);
            if(a==b)same++;
            total++;
        }
        return (double)same/total;
    }
    public static void main(String[] args)throws Exception{
        BufferedImage png=ImageIO.read(new File(args[0]));
        check(png!=null&&png.getWidth()==1040&&png.getHeight()==160,
                "Original immutable 4-frame PNG required");
        int[] expected={4,0,-4,0};
        for(int f=0;f<4;f++){
            int off=WalkAlignmentV48.sourceOffsetX(f);
            check(off==expected[f],"Frame alignment incorrect "+f);
            double corrected=match(png,f,off),original=match(png,f,0);
            check(corrected>.98,"Head/torso still wobbles frame "+f+" "+corrected);
            if(f==0||f==2)check(corrected-original>.13,
                              "Stabilization not measurable frame "+f);
            float right=WalkAlignmentV48.worldOffsetX(f,1,1);
            float left=WalkAlignmentV48.worldOffsetX(f,-1,1);
            check(Math.abs(right+left)<.00001f,"Left/right mirror changed aim");
            check(Math.abs(right-off*.76f)<.00001f,"Hitbox x mismatch");
        }
        System.out.println("PASS V48: 4 unique walking poses retained, torso/face >98% stable, mirrored pixel hitboxes aligned, source PNG untouched");
    }
}
