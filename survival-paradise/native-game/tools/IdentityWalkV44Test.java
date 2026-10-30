package com.survivalparadise.nativegame;

import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;
import java.util.HashSet;
import java.util.Set;

/**
 * Strict provenance for Survival Paradise V44.
 * Approved V41 identity MUST be pixel-identical through y=109 in EVERY frame.
 * Only the 10x13 outline's bottom 3 logical rows may determine leg movement.
 * The reference's red shirt, blue pants, skin and hair cannot enter the game.
 */
public final class IdentityWalkV44Test {
    private IdentityWalkV44Test(){}
    static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    public static void main(String[] args)throws Exception{
        BufferedImage base=ImageIO.read(new File(args[0]));
        BufferedImage user=ImageIO.read(new File(args[1]));
        BufferedImage walk=ImageIO.read(new File(args[2]));
        check(base!=null&&base.getWidth()==1040&&base.getHeight()==160,"canonical body dimensions");
        check(user!=null&&user.getWidth()==800&&user.getHeight()==260,"uploaded four-frame reference dimensions");
        check(walk!=null&&walk.getWidth()==1040&&walk.getHeight()==160,"derived walk atlas dimensions");
        Set<Integer> sourcePalette=new HashSet<>();
        for(int y=0;y<160;y++)for(int x=0;x<1040;x++)sourcePalette.add(base.getRGB(x,y));
        for(int y=0;y<160;y++)for(int x=0;x<1040;x++)
            check(sourcePalette.contains(walk.getRGB(x,y)),"unapproved NEW COLOR at "+x+","+y);
        // Preserve all user-approved identity pixels including face and shirt.
        for(int y=0;y<110;y++)for(int x=0;x<1040;x++)
            check(walk.getRGB(x,y)==base.getRGB(x,y),
                  "V41 head, eyes, beard, skin, shirt or outline changed at "+x+","+y);

        final int transparent=0, black=0xff000000, pants=0xff566641, boots=0xff68402b;
        int[] offsets={16,20,24,20};
        Set<Integer> distinct=new HashSet<>();
        for(int frame=0;frame<4;frame++){
            final int origin=frame*260,off=offsets[frame];
            for(int y=110;y<160;y++)for(int x=0;x<260;x++){
                int expected=transparent;
                int row=(y-110)/9;
                int col=(x-off)/9;
                if(y<137 && x>=off && col>=0 && col<10 && row>=0 && row<3){
                    int ref=user.getRGB(frame*200+col*20+10,(row+10)*20+10);
                    if((ref>>>24)!=0){
                        if((ref&0xffffff)==0)expected=black;
                        else if((ref&0xffffff)==0x004aa1)expected=pants;
                        else if((ref&0xffffff)==0x632f00||
                                (ref&0xffffff)==0x6b3312)expected=boots;
                        else throw new AssertionError("unrecognized source reference outline color");
                    }
                }
                check(walk.getRGB(origin+x,y)==expected,
                      "walking geometry did not follow the user outline at frame "
                      +frame+" cell "+x+","+y);
            }
            int hash=1;
            for(int y=0;y<160;y++)for(int x=0;x<260;x++)
                hash=31*hash+walk.getRGB(origin+x,y);
            check(distinct.add(hash),"V44 walk frame duplicate "+frame);
        }
        // No raw reference red shirt or blue trouser colors in derived PNG.
        check(!sourcePalette.contains(0xff820000)&&!sourcePalette.contains(0xff004aa1),
              "unexpected V41 palette overlap with reference");
        System.out.println("V44 PASS: 4 exact silhouette poses, approved V41 face and ALL upper pixels identical, canonical original palette only.");
    }
}
