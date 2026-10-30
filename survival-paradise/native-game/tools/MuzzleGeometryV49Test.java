package com.survivalparadise.nativegame;

import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;

/** V49 verify all projectile origins are on the actual displayed muzzle axis. */
public final class MuzzleGeometryV49Test {
    static void check(boolean ok,String m){if(!ok)throw new AssertionError(m);}
    public static void main(String[] args)throws Exception{
        BufferedImage atlas=ImageIO.read(new File(args[0]));
        check(atlas!=null&&atlas.getWidth()==3120&&atlas.getHeight()==480,"Original approved 12-weapon atlas");
        final int[] expectedY={62,58,67,88,67,66,68,66,69,56,69,92};
        final int[] oldY={79,73,75,88,75,78,72,80,74,72,71,92};
        for(int weapon=0;weapon<11;weapon++){
            int x=Math.round(MuzzleGeometryV49.X[weapon]);
            int y=Math.round(MuzzleGeometryV49.Y[weapon]);
            check(y==expectedY[weapon],"muzzle vertical regression "+weapon);
            if(weapon==3)continue; // Flashlight emits a beam, never a projectile.
            int worldX=weapon*260+x;
            // Muzzle source x is at the first empty image column immediately
            // right of opaque barrel: no offset beneath the image.
            check((atlas.getRGB(worldX,y)>>>24)==0,"muzzle endpoint should be outside barrel at "+weapon);
            int hit=0;
            for(int yy=Math.max(0,y-3);yy<=y+3;yy++)
                if((atlas.getRGB(worldX-2,yy)>>>24)>96)hit++;
            check(hit>0,"barrel pixel not on calibrated centerline "+weapon);
            check(Math.abs(y-oldY[weapon])>=2||weapon==10,
                  "uncorrected muzzle origin for weapon "+weapon);
            for(int facing:new int[]{-1,1}){
                float[] barrel=Ballistics.rigMuzzle(500,500,facing,facing,0,.76f,x,y,103,76,0);
                check(Float.isFinite(barrel[0])&&Float.isFinite(barrel[1]),"invalid transformed muzzle");
            }
        }
        System.out.println("V49 PASS: muzzle fire/light positions measured against original alpha gear atlas");
    }
}
