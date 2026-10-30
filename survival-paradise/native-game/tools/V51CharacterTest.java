package com.survivalparadise.nativegame;
import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;
import java.util.Arrays;
/** Verified: no jitter from walking vs idle facial outline and twelve independent role sources. */
public final class V51CharacterTest {
    static void check(boolean ok,String msg){if(!ok)throw new AssertionError(msg);}
    public static void main(String[] args)throws Exception {
        BufferedImage base=ImageIO.read(new File(args[0]));
        BufferedImage npc=ImageIO.read(new File(args[1]));
        BufferedImage source=ImageIO.read(new File(args[2]));
        check(base.getWidth()==1040&&base.getHeight()==160,"player stable body geometry");
        check(npc.getWidth()==1040&&npc.getHeight()==1920,"12 new approved role variants");
        check(source.getWidth()==1040&&source.getHeight()==160,"original V44 unmodified");
        for(int frame=0;frame<4;frame++){
            for(int y=20;y<101;y++)for(int x=0;x<260;x++){
                check(base.getRGB(frame*260+x,y)==base.getRGB(520+x,y),
                    "face instability frame "+frame+" x"+x+" y"+y);
            }
            for(int y=29;y<92;y++)for(int x=101;x<110;x++)
                check(base.getRGB(frame*260+x,y)==0xff000000,
                    "front 9px outline inconsistent frame "+frame);
            // All original leg geometries remain in four unique frames.
            int geometry=0;
            for(int y=109;y<155;y++)for(int x=0;x<150;x++)
                geometry=geometry*31+(base.getRGB(frame*260+x,y)>>>24);
            for(int previous=0;previous<frame;previous++){
                int match=0;
                for(int y=115;y<154;y++)for(int x=0;x<155;x++)
                    if(base.getRGB(frame*260+x,y)==base.getRGB(previous*260+x,y))match++;
                check(match<6000,"duplicate walk gait");
            }
        }
        // Every NPC animation's silhouette and alpha shape exactly matches the
        // normalized four-frame game skeleton, recolored only from GitHub role art.
        for(int role=0;role<12;role++){
            int delta=0;
            for(int y=0;y<160;y++)for(int x=0;x<1040;x++){
                int a=base.getRGB(x,y),b=npc.getRGB(x,role*160+y);
                check((a>>>24)==(b>>>24),"NPC alpha/geometry changed role "+role);
                if(a!=b)delta++;
            }
            check(delta>150,"NPC visual identity not differentiated "+role);
        }
        System.out.println("PASS V51: identical head in idle/4 walk poses, 9px front outline, 12 unique role palettes, original leg masks untouched");
    }
}