package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;

/**
 * Weapon-specific tiny PIXEL ART for reload props, painted only while reloading.
 * The immutable V109 head/body and original V31 weapon atlas are never edited.
 * Coordinates are source atlas units, within the existing torso-centered rig.
 */
final class ReloadArtV151 {
    private static final int OUTLINE=0xff101718;
    private static final int STEEL=0xff3a4447;
    private static final int LIGHT=0xff85918c;
    private static final int BRASS=0xffe6bf67;
    private static final int DARK_BRASS=0xff916a2b;
    private static final int OLIVE=0xff5f6548;
    private static final int CLAY=0xffa46b40;
    private final Paint p=new Paint(0);

    private void rect(Canvas c,float x,float y,float w,float h,int color){
        p.setStyle(Paint.Style.FILL);p.setColor(color);
        c.drawRect(x,y,x+w,y+h,p);
    }
    private void rim(Canvas c,int x,int y,int w,int h,int fill){
        rect(c,x-1,y-1,w+2,h+2,OUTLINE);
        rect(c,x,y,w,h,fill);
    }
    private void brassTop(Canvas c,int x,int y,int width){
        rect(c,x,y,width,3,BRASS);
        rect(c,x,y+3,width,2,DARK_BRASS);
    }

    /** Gun-local attachment, rendered just BEFORE the original support hand. */
    void drawHeldAmmo(Canvas c,int weapon,float remaining,float sourceScale){
        if(!ReloadProfileV151.propVisible(weapon,remaining))return;
        float hx=ReloadProfileV151.handX(weapon,remaining);
        float hy=ReloadProfileV151.handY(weapon,remaining);
        c.save();
        c.translate((hx-70f)*sourceScale,(hy-136f)*sourceScale);
        c.scale(sourceScale,sourceScale);
        switch(ReloadProfileV151.propKind(weapon)){
            case ReloadProfileV151.SLIM_PISTOL:
                // 9 mm pistol: narrow, straight, single grip-length metal magazine.
                rim(c,-4,-24,9,25,0xff424b4a);
                rect(c,-3,-21,2,20,LIGHT);
                rect(c,3,-19,1,19,0xff222a2c);
                brassTop(c,-3,-28,7);
                break;
            case ReloadProfileV151.SPEEDLOADER:
                // Six independent brass cartridges grouped in a revolver speedloader.
                rim(c,-9,-20,18,17,0xff303a3b);
                for(int i=0;i<6;i++){
                    int x=-6+(i%3)*5,y=-17+(i/3)*8;
                    rect(c,x,y,3,6,BRASS);
                    rect(c,x,y+4,3,2,DARK_BRASS);
                }
                rect(c,-2,-22,5,4,LIGHT); // loader release knob
                break;
            case ReloadProfileV151.UZI_BOX:
                // SMG: long, straight double-stack stick; NEVER a pistol magazine.
                rim(c,-6,-35,12,35,0xff404949);
                rect(c,-4,-33,2,30,LIGHT);
                for(int y=-26;y<-2;y+=7)rect(c,-5,y,10,2,0xff273135);
                brassTop(c,-4,-39,9);
                break;
            case ReloadProfileV151.STANAG:
                // Carbine: ribbed STANAG body with angled floorplate.
                rim(c,-8,-29,16,28,0xff424b4f);
                rect(c,-7,-27,2,24,0xff889590);
                for(int y=-22;y<-4;y+=5)rect(c,-4,y,10,2,0xff293739);
                rect(c,-9,-3,18,4,0xff282f31);
                brassTop(c,-6,-33,12);
                break;
            case ReloadProfileV151.CURVED_AK:
                // AK: unmistakably CURVED 7.62 magazine, not a box or pistol clip.
                // Graduated offsets create a banana-shaped bottom, matching
                // this game's AK art rather than a straight pistol box.
                rim(c,-11,-29,14,8,0xff293032);
                rim(c,-9,-21,16,8,0xff303538);
                rim(c,-5,-13,18,8,0xff343a3b);
                rim(c,0,-5,19,8,0xff2c3436);
                rim(c,7,3,19,7,0xff2a3032);
                for(int i=0;i<5;i++){
                    rect(c,-8+i*4,-27+i*8,2,6,0xff727b75);
                }
                brassTop(c,-8,-34,12);
                break;
            case ReloadProfileV151.BULLPUP_BOX:
                // Compact rear-mounted black polymer magazine, distinctly shorter.
                rim(c,-7,-20,14,20,0xff3e403a);
                rect(c,-5,-18,3,15,0xffa39b7f);
                rect(c,-4,-8,10,3,0xff252a2b);
                brassTop(c,-5,-24,10);
                break;
            case ReloadProfileV151.TOP_SHELLS:
                // User-approved TOP feed: a red 12 gauge cartridge with brass head.
                rim(c,-4,-20,9,24,0xff9a3030);
                rect(c,-3,-18,2,16,0xffd65a4c);
                brassTop(c,-4,-23,9);
                rect(c,-4,0,9,3,0xff683b2e);
                break;
            case ReloadProfileV151.PRECISION_BOX:
                // Sniper: matte steel 7.62 precision box with wide base and lips.
                rim(c,-8,-24,16,24,0xff464d45);
                rect(c,-7,-21,2,19,0xff8b9b7c);
                rect(c,4,-22,2,17,0xff292f2c);
                rim(c,-9,-2,18,4,0xff2b3333);
                brassTop(c,-6,-28,12);
                break;
            case ReloadProfileV151.BELT_BOX:
                // BKC/LMG: belt box plus articulated ammunition links; NO handgun mag.
                rim(c,-15,-16,30,25,0xff575d43);
                rect(c,-12,-13,24,3,0xff939b6e);
                rect(c,-11,-7,22,12,0xff424935);
                rect(c,-13,5,26,2,OUTLINE);
                for(int i=0;i<5;i++){
                    int x=-13+i*6,y=-29+(i%2)*3;
                    rect(c,x-1,y-1,5,11,OUTLINE);
                    rect(c,x,y,3,8,BRASS);
                    rect(c,x,y+6,3,3,DARK_BRASS);
                }
                break;
            case ReloadProfileV151.GRENADE_ROUNDS:
                // 40 mm launcher shells: THREE chunky rounds, not rifle magazines.
                for(int i=0;i<3;i++){
                    int x=-17+i*12;
                    rim(c,x,-21,9,22,0xff657047);
                    rect(c,x+1,-18,7,6,0xffa8a06d);
                    brassTop(c,x,-4,9);
                    rect(c,x+2,-23,5,3,0xff293a32);
                }
                break;
            default:break;
        }
        c.restore();
    }

    /** Short firearm-specific moving receiver details, separate from held ammo. */
    void drawMechanism(Canvas c,int weapon,float remaining,float sourceScale){
        if(!ReloadProfileV151.propVisible(weapon,remaining))return;
        float progress=ReloadProfileV151.progress(weapon,remaining);
        c.save();c.scale(sourceScale,sourceScale);
        switch(weapon){
            case ReloadProfileV151.REVOLVER:
                // Opened cylinder with six visible chamber rims.
                rim(c,42,-77,14,12,STEEL);
                for(int i=0;i<6;i++)
                    rect(c,44+(i%3)*4,-75+(i/3)*6,2,3,DARK_BRASS);
                break;
            case ReloadProfileV151.SHOTGUN:
                // Top loading slot is above receiver; each shell visibly feeds down.
                rim(c,49,-82,16,4,0xff22282a);
                rect(c,51,-82,12,1,LIGHT);
                break;
            case ReloadProfileV151.SNIPER:
                // Bolt carrier slides back and is then driven forward.
                rect(c,53+(progress<.52f?-8:0),-70,15,3,OUTLINE);
                rect(c,54+(progress<.52f?-8:0),-69,13,1,LIGHT);
                break;
            case ReloadProfileV151.BELT_FED_LMG:
                // Open receiver cover exposes linked belt guides.
                rim(c,53,-92,24,4,OLIVE);
                for(int i=0;i<4;i++)rect(c,57+i*5,-88,3,5,BRASS);
                break;
            case ReloadProfileV151.GRENADE_LAUNCHER:
                // Cylinder / cassette visually open at the loading window.
                rim(c,57,-77,17,9,OLIVE);
                for(int i=0;i<3;i++)rect(c,59+i*5,-75,3,5,DARK_BRASS);
                break;
            default:break;
        }
        c.restore();
    }
}
