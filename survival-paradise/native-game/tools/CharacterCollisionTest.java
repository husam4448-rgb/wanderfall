package com.survivalparadise.nativegame;

import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;

public final class CharacterCollisionTest {
    static void check(boolean value,String what) {
        if(!value)throw new AssertionError(what);
    }
    static void near(float got,float expected,float eps,String what) {
        check(Math.abs(got-expected)<eps,what+": "+got+" vs "+expected);
    }
    public static void main(String[] args)throws Exception{
        BufferedImage atlas=ImageIO.read(new File(args[0]));
        check(atlas.getWidth()==1040 && atlas.getHeight()==160,"unchanged V31 atlas dimensions");
        CharacterCollision.PixelMask mask=(x,y)->((atlas.getRGB(x,y)>>>24)&255)>0;
        float centerX=500,centerY=500,s=CharacterCollision.BASE_SCALE;
        // Top of approved character is ~88 px ABOVE the foot anchor;
        // old radius-30 circle centered only 28 px up missed these head shots.
        float topHeadY=centerY+(24-136)*s;
        float eyeY=centerY+(51-136)*s;
        float chestY=centerY+(108-136)*s;
        float bootsY=centerY+(130-136)*s;
        for(int facing:new int[]{1,-1}) {
            for(float breath:new float[]{0f,-4f}) {
                float adjustedTop=topHeadY+breath*s;
                for(float headY:new float[]{adjustedTop,eyeY+breath*s}) {
                    float hit=CharacterCollision.firstHit(390,headY,610,headY,
                        centerX,centerY,facing,0,false,breath,1f,mask);
                    check(Float.isFinite(hit),"head damage must register for facing "+facing+" breath "+breath);
                }
                check(Float.isFinite(CharacterCollision.firstHit(390,chestY,610,chestY,
                    centerX,centerY,facing,0,false,breath,1f,mask)),"torso hit");
                check(Float.isFinite(CharacterCollision.firstHit(390,bootsY,610,bootsY,
                    centerX,centerY,facing,0,false,breath,1f,mask)),"boots stay inside visible silhouette");
            }
            for(int frame=0;frame<4;frame++) {
                float hit=CharacterCollision.firstHit(390,eyeY,610,eyeY,centerX,centerY,
                    facing,frame,true,0f,1f,mask);
                check(Float.isFinite(hit),"walking frame "+frame+" head hit");
            }
        }
        // No bogus hits far above/below/outside the transparent sprite.
        for(float yy:new float[]{centerY-115,centerY+19}) {
            float miss=CharacterCollision.firstHit(390,yy,610,yy,
               centerX,centerY,1,0,false,0f,1f,mask);
            check(Float.isInfinite(miss),"shot outside character should miss");
        }
        check(Float.isInfinite(CharacterCollision.firstHit(620,eyeY,690,eyeY,
               centerX,centerY,1,0,false,0f,1f,mask)),"ray beside head misses");
        // Extremely fast projectiles must not tunnel through a small target.
        check(Float.isFinite(CharacterCollision.firstHit(-1000,topHeadY,2000,topHeadY,
               centerX,centerY,-1,0,false,0f,1f,mask)),"3000px swept high-speed headshot");
        // Horizontal symmetry without raising gun vertically on a facing flip.
        for(float dy:new float[]{-.9f,-.4f,0f,.4f,.9f}) {
            float dx=(float)Math.sqrt(1-dy*dy);
            float right=Ballistics.angle(dx,dy,1);
            float left=Ballistics.angle(-dx,dy,-1);
            near(right,left,1e-6f,"identical mirror pitch at elevation "+dy);
            near(Ballistics.angle(-dx,dy,1),right,1e-6f,"stale facing cannot force rifle upright");
            float[] muzzleR=Ballistics.rigMuzzle(500,500,1,dx,dy,s,215,78,101,77,0f);
            float[] muzzleL=Ballistics.rigMuzzle(500,500,-1,-dx,dy,s,215,78,101,77,0f);
            near(muzzleR[0]-500,500-muzzleL[0],.002f,"barrel x mirrors");
            near(muzzleR[1],muzzleL[1],.002f,"barrel height persists across flip");
        }
        System.out.println("V41 PASS: real alpha head/body/feet hits, 4 walking poses, mirrored 360 aim, fast bullets");
    }
}
