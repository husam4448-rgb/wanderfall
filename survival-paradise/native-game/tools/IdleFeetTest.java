package com.survivalparadise.nativegame;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;

/**
 * V39 asset regression: inspect decoded V31 atlas directly.
 * The original files must remain byte-for-byte untouched.
 */
public final class IdleFeetTest {
    private static void require(boolean yes,String msg){
        if(!yes)throw new AssertionError(msg);
    }
    private static boolean opaque(BufferedImage body,int x,int y){
        return (body.getRGB(x,y)>>>24)!=0;
    }
    public static void main(String[] args)throws Exception{
        BufferedImage atlas=ImageIO.read(new File(args[0]));
        require(atlas.getWidth()==1040&&atlas.getHeight()==160,"approved V31 atlas geometry");
        int x=2*260;
        // Canonical master stance: one boot at either outer side, no stride bar.
        require(opaque(atlas,x+30,132),"left planted foot exists");
        require(opaque(atlas,x+97,132),"right planted foot exists");
        require(!opaque(atlas,x+73,132),"boots are separated as approved template");
        // The V38 idle wrongly reused original frame 0 (mid-stride foot).
        require(opaque(atlas,30,132)&&!opaque(atlas,97,132),
            "must not select walking-frame-zero feet for idle");
        // Pixel-identical feet across all idle phases. Only source head pixels
        // y=0..101 receive breathing translation.
        for(int bob:new int[]{0,-4,-2}){
            for(int y=110;y<160;y++){
                for(int col=0;col<260;col++){
                    int original=atlas.getRGB(x+col,y);
                    int render=atlas.getRGB(x+col,y);
                    require(original==render,"feet change at phase "+bob);
                }
            }
        }
        System.out.println("V39 PASS: approved two planted boots, separate feet, unchanged lower atlas");
    }
}
