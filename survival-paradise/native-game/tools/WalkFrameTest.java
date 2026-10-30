package com.survivalparadise.nativegame;

import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;

/**
 * V42 native regression: source frame 4 was duplicated; it must now show
 * both legs, pose 3 must lift the rear foot, and every animation frame
 * must play in exact 0,1,2,3 order without skipping.
 */
public final class WalkFrameTest {
    static void require(boolean v,String message){if(!v)throw new AssertionError(message);}

    public static void main(String[] args)throws Exception {
        BufferedImage old=ImageIO.read(new File(args[0]));
        BufferedImage walk=ImageIO.read(new File(args[1]));
        require(walk.getWidth()==1040&&walk.getHeight()==160,"source atlas geometry");
        BufferedImage expected=GenerateWalkV42.restore(old);
        for(int y=0;y<160;y++)for(int x=0;x<1040;x++)
            require(walk.getRGB(x,y)==expected.getRGB(x,y),"derived frame differs from approved-source composition");

        // The screenshot-derived V31 source had a duplicated fourth frame.
        for(int y=0;y<160;y++)for(int x=0;x<260;x++)
            require(old.getRGB(260+x,y)==old.getRGB(780+x,y),"original duplicate provenance");

        // A rear boot lifts and the recovered fourth stance has both boots.
        require((walk.getRGB(2*260+28,132)>>>24)==0,"rear boot lifts in 3rd pose");
        require((walk.getRGB(2*260+95,132)>>>24)>0,"forward foot remains");
        require((walk.getRGB(3*260+25,132)>>>24)>0,"4th pose has extended rear boot");
        require((walk.getRGB(3*260+95,132)>>>24)>0,"4th pose has grounded forward boot");

        // Check 4-frame cadence at realistic mobile 60/30/15fps and the
        // maximum simulation speed (200%). Each pose must be displayed.
        for(float fps:new float[]{60f,30f,15f}){
            for(float speed:new float[]{.5f,1f,2f}){
                AnimationCycle c=new AnimationCycle();
                boolean[] seen=new boolean[4];
                int last=-1;
                for(int n=0;n<220;n++){
                    c.step(true,Math.min(.04f,1f/fps)*speed,7f);
                    int f=c.frame();
                    require(f>=0&&f<4,"invalid frame");
                    seen[f]=true;
                    if(last>=0)require(f==last||f==(last+1)%4,
                        "skipped walk frame at "+fps+" FPS speed "+speed+": "+last+"->"+f);
                    last=f;
                }
                for(int i=0;i<4;i++)
                    require(seen[i],"missing pose "+i+" at "+fps+" FPS speed "+speed);
                c.step(false,.016f,7f);
                require(c.frame()==0&&!c.isWalking(),"idle reset disturbed");
            }
        }
        // The V41 body atlas stays bundled separately for the approved idle.
        require(old.getRGB(2*260+28,132)!=walk.getRGB(2*260+28,132),
                "V42 walking restoration must not overwrite original planted-idle source");

        System.out.println("V42 WALK REGRESSION PASS: all four unique poses, raised boot, no frame skips, idle unchanged");
    }
}
