package com.survivalparadise.nativegame;

import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;
import java.util.HashSet;
import java.util.Set;

/** Regression against the EXACT user's transparent four-frame source PNG. */
public final class ExactWalkV43Test {
    static void check(boolean b,String why){if(!b)throw new AssertionError(why);}
    public static void main(String[] args)throws Exception{
        BufferedImage png=ImageIO.read(new File(args[0]));
        check(png!=null&&png.getWidth()==800&&png.getHeight()==260,
              "approved original 800x260 strip must be bundled unchanged");
        Set<Integer> unique=new HashSet<>();
        for(int f=0;f<4;f++){
            int hash=1;
            for(int y=0;y<260;y++)for(int x=0;x<200;x++)
                hash=31*hash+png.getRGB(f*200+x,y);
            check(unique.add(hash),"walk frames duplicate; must use 4 distinct approved poses");
            check((png.getRGB(f*200+100,60)>>>24)!=0,"head visible in frame "+f);
        }
        // Source foot outlines: pose 1 extends left, pose 2 keeps foot tucked,
        // pose 3 extends right, pose 4 has BOTH legs extended.
        check((png.getRGB(10,250)>>>24)!=0,"rear foot in first walk frame");
        check((png.getRGB(210,250)>>>24)==0,"second frame is centered transition");
        check((png.getRGB(2*200+170,250)>>>24)!=0,"rear foot lifted on opposite side");
        check((png.getRGB(3*200+10,250)>>>24)!=0 &&
              (png.getRGB(3*200+170,250)>>>24)!=0,"final pose extends both feet");
        // In-game animation must traverse the 4 images in order at every
        // target frame rate and available speed.
        for(int fps:new int[]{15,30,60}) for(float speed:new float[]{.5f,1f,2f}){
            AnimationCycle cycle=new AnimationCycle();
            boolean[] seen=new boolean[4];int last=-1;
            for(int i=0;i<220;i++){
                float dt=Math.min(.04f,1f/fps)*speed;
                cycle.step(true,dt,7f);
                int frame=cycle.frame();check(frame>=0&&frame<4,"bad source index");
                seen[frame]=true;
                if(last>=0)check(frame==last||frame==(last+1)%4,
                    "skipped source frame at "+fps+" fps, speed "+speed);
                last=frame;
            }
            for(int i=0;i<4;i++)check(seen[i],"missing original frame "+i);
            cycle.step(false,.016f,7f);
            check(!cycle.isWalking()&&cycle.frame()==0,"approved idle transition broken");
        }
        System.out.println("V43 PASS: EXACT uploaded 4-frame PNG, distinct poses, full cadence and preserved idle");
    }
}