package com.survivalparadise.nativegame;

import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;

/** Pixel-by-pixel and identity regression for the user's approved animated sheets. */
public final class V56ApprovedCharacterTest {
    static void check(boolean good,String what){if(!good)throw new AssertionError(what);}
    static int argb(BufferedImage image,int x,int y){return image.getRGB(x,y);}
    public static void main(String[] args)throws Exception{
        BufferedImage approvedWalk=ImageIO.read(new File(args[0]));
        BufferedImage originalIdle=ImageIO.read(new File(args[1]));
        BufferedImage roleWalk=ImageIO.read(new File(args[2]));
        BufferedImage roleIdle=ImageIO.read(new File(args[3]));
        check(approvedWalk.getWidth()==1040&&approvedWalk.getHeight()==160,"approved 4-frame walk");
        check(originalIdle.getWidth()==1040&&originalIdle.getHeight()==160,"original unmodified idle");
        check(roleWalk.getWidth()==1040&&roleWalk.getHeight()==1920,"12 role walk atlases");
        check(roleIdle.getWidth()==260&&roleIdle.getHeight()==1920,"12 role idle atlases");
        final int sourceSkin=0xfff2c69e;
        int skinTotal=0;
        // Every walking frame uses the exact 4-frame approved V44 sprite art:
        // frame source upper geometry and palette are unchanged from V31.
        for(int frame=0;frame<4;frame++){
            int skinPixels=0;
            for(int y=0;y<110;y++)for(int x=0;x<260;x++){
                int wx=frame*260+x;
                check(argb(approvedWalk,wx,y)==argb(originalIdle,wx,y),
                      "Walking identity differs from approved upper body frame "+frame+" pixel "+x+","+y);
                if(argb(approvedWalk,wx,y)==sourceSkin)skinPixels++;
            }
            check(skinPixels>=8,"Skin swatch missing in walking frame "+frame);
            skinTotal+=skinPixels;
        }
        for(int role=0;role<12;role++){
            int bodyRow=role*160;
            int[] roleSkin=new int[4];
            for(int frame=0;frame<4;frame++){
                for(int y=0;y<160;y++)for(int x=0;x<260;x++){
                    int wx=frame*260+x;
                    check((argb(roleWalk,wx,bodyRow+y)>>>24)==
                          (argb(approvedWalk,wx,y)>>>24),
                          "Walking silhouette modified in role "+role+" frame "+frame);
                }
                for(int y=0;y<110;y++)for(int x=0;x<260;x++){
                    int wx=frame*260+x;
                    // Every V31/V44 walking frame upper body is the preserved
                    // source art recolored by a stable, role-specific palette.
                    if(argb(originalIdle,wx,y)==sourceSkin)
                        roleSkin[frame]=argb(roleWalk,wx,bodyRow+y);
                }
                check(roleSkin[frame]!=0,"Role skin missing "+role+"/"+frame);
            }
            for(int frame=1;frame<4;frame++)
                check(roleSkin[frame]==roleSkin[0],"Skin changes during walk "+role+"/"+frame);
            for(int y=0;y<160;y++)for(int x=0;x<260;x++){
                int expected=argb(originalIdle,520+x,y);
                check((argb(roleIdle,x,bodyRow+y)>>>24)==(expected>>>24),
                      "Idle silhouette changed "+role+" "+x+","+y);
                if(y<110)
                    check(argb(roleIdle,x,bodyRow+y)==
                          argb(roleWalk,520+x,bodyRow+y),
                          "Idle differs from walking face/shirt "+role+" "+x+","+y);
            }
        }
        // Walking remains an actual four-position animation, not one redrawn still.
        int[] different=new int[4];
        for(int frame=0;frame<4;frame++)
            for(int y=112;y<150;y++)for(int x=0;x<160;x++)
                different[frame]=31*different[frame]+(argb(approvedWalk,frame*260+x,y)>>>24);
        check(different[0]!=different[1]&&different[1]!=different[2]&&
              different[2]!=different[3],"Leg animation poses collapsed");
        System.out.println("V56 STRICT PASS: approved 4-frame walking, original idle, "+
            skinTotal+" skin pixels; 12 NPC palette-identical idle/walk pairs");
    }
}
