package com.survivalparadise.nativegame;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;
import javax.imageio.ImageIO;

/**
 * V42 approved walk-frame recovery.
 *
 * The V31 prototype body atlas contains four source slots but 1 and 3 have
 * IDENTICAL pixels. The user-approved 4-pose reference has a raised rear boot
 * in pose 3 and both boots extended in pose 4. V42 composes those lower-body
 * details using ONLY original approved V31 palette/boot pixels. The head,
 * torso, colors, silhouettes elsewhere, and the original PNG remain unchanged.
 * The recovered walk atlas is a separate bundled asset, not a replacement of
 * the canonical original. No generated illustration or interpolated pixels.
 */
public final class GenerateWalkV42 {
    private GenerateWalkV42(){}

    private static void check(boolean value,String message){
        if(!value)throw new IllegalStateException("V42 recovery validation failed: "+message);
    }

    public static BufferedImage restore(BufferedImage source){
        check(source!=null&&source.getWidth()==1040&&source.getHeight()==160,
                "approved atlas dimensions 1040x160");
        final int FRAME_WIDTH=260;
        // Explicitly identify duplicate source pose before substituting anything.
        for(int y=0;y<160;y++)for(int x=0;x<260;x++){
            check(source.getRGB(FRAME_WIDTH+x,y)==source.getRGB(3*FRAME_WIDTH+x,y),
                    "source frame four is not the known duplicated source; do not overwrite");
        }
        BufferedImage out=new BufferedImage(1040,160,BufferedImage.TYPE_INT_ARGB);
        for(int y=0;y<160;y++)for(int x=0;x<1040;x++)
            out.setRGB(x,y,source.getRGB(x,y));

        final int third=2*FRAME_WIDTH, fourth=3*FRAME_WIDTH;
        // Pose 3: rear foot lifted above the ground; remove ONLY its old
        // bottom 9-pixel boot row, leaving its existing raised brown boot intact.
        for(int y=128;y<=136;y++)for(int x=24;x<=41;x++)
            out.setRGB(third+x,y,0);

        // Pose 4: the V31 slot was a duplicate of pose 2, not the canonical
        // rear-leg extension. Restore only y>=110 from *approved source pixels*.
        // Everything above pants stays identical to the old V31 frame.
        for(int y=110;y<=136;y++)for(int x=0;x<125;x++)
            out.setRGB(fourth+x,y,0);
        // Existing continuous six-pixel V13 trousers band + black outlines.
        for(int y=110;y<=118;y++)for(int x=33;x<=104;x++)
            out.setRGB(fourth+x,y,source.getRGB(third+x,y));
        // Rear boot extends backward, from original approved pose 1.
        for(int y=119;y<=136;y++)for(int x=16;x<=33;x++)
            out.setRGB(fourth+x,y,source.getRGB(x,y));
        // Forward boot stays grounded, from approved pose 3.
        for(int y=119;y<=136;y++)for(int x=87;x<=104;x++)
            out.setRGB(fourth+x,y,source.getRGB(third+x,y));

        // Original upper-body pixels may never be altered.
        for(int f=0;f<4;f++){
            int limit=f<2?160:f==2?128:110;
            for(int y=0;y<limit;y++)for(int x=0;x<260;x++)
                check(out.getRGB(f*260+x,y)==source.getRGB(f*260+x,y),
                     "unchanged approved upper frame "+f+" at "+x+","+y);
        }
        // No NEW colors are introduced: every visible pixel comes from source.
        Set<Integer> approvedColors=new HashSet<>();
        for(int y=0;y<160;y++)for(int x=0;x<1040;x++)
            approvedColors.add(source.getRGB(x,y));
        for(int y=0;y<160;y++)for(int x=0;x<1040;x++)
            check(approvedColors.contains(out.getRGB(x,y)),
                 "new/unapproved pixel color at "+x+","+y);
        // All four poses must now be visually distinct.
        for(int a=0;a<4;a++)for(int b=a+1;b<4;b++){
            boolean differs=false;
            for(int y=0;y<160&&!differs;y++)for(int x=0;x<260;x++){
                if(out.getRGB(a*260+x,y)!=out.getRGB(b*260+x,y)){
                    differs=true;break;
                }
            }
            check(differs,"walking poses "+(a+1)+" and "+(b+1)+" duplicate");
        }
        check((out.getRGB(third+28,132)>>>24)==0,"raised rear foot was not lifted");
        check((out.getRGB(third+95,132)>>>24)!=0,"leading foot lost");
        check((out.getRGB(fourth+25,132)>>>24)!=0,"backward rear boot absent");
        check((out.getRGB(fourth+95,132)>>>24)!=0,"forward boot absent");
        return out;
    }

    public static void main(String[] args)throws IOException {
        if(args.length!=2)throw new IllegalArgumentException("Usage: GenerateWalkV42 original_body.png corrected_walk.png");
        BufferedImage old=ImageIO.read(new File(args[0]));
        BufferedImage recovered=restore(old);
        File output=new File(args[1]);
        File parent=output.getParentFile();
        if(parent!=null&&!parent.exists()&&!parent.mkdirs())
            throw new IOException("Cannot create asset directory: "+parent);
        if(!ImageIO.write(recovered,"png",output))
            throw new IOException("PNG encoder unavailable");
        System.out.println("V42 WALK RECOVERY PASS: 4 distinct approved-source poses; original V31 PNG unchanged");
    }
}
