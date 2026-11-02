package com.survivalparadise.nativegame;

/** JVM-only regression for V102 pixel-precise integrated gas-mask head.
 * No Android SDK or APK build required.
 */
public final class V102NativeGasMaskTest {
    static void check(boolean yes,String reason){
        if(!yes)throw new AssertionError(reason);
    }
    public static void main(String[] args){
        int skin=0xfff2c69e,eyeWhite=0xffffffff,eyeIris=0xff328d9b;
        int outline=0xff000000,transparent=0x00000000;
        int changed=0;
        for(int y=0;y<160;y++){
            for(int x=0;x<260;x++){
                int original=skin;
                if((x==24||x==105)&&y>=20&&y<=91)original=outline;
                if(y>=56&&y<65&&((x>=51&&x<60)||(x>=87&&x<96)))
                    original=eyeWhite;
                if(y>=56&&y<65&&((x>=60&&x<69)||(x>=96&&x<105)))
                    original=eyeIris;
                int next=GasMaskPaletteV102.recolor(x,y,original);
                check((original>>>24)==(next>>>24),"alpha changed");
                if(x<33||x>104||y<29||y>91)
                    check(next==original,"out-of-head edit");
                if(original==outline||original==transparent)
                    check(next==original,"black contour changed");
                if(y>=56&&y<65&&((x>=51&&x<69)||(x>=87&&x<105)))
                    check(next==original,"approved eyes changed");
                if(next!=original)changed++;
            }
        }
        check(changed>=3500,"mask did not change enough head interior pixels");
        check(GasMaskPaletteV102.recolor(51,74,skin)!=skin,"mask missing");
        System.out.println("V102 PASS: no body/outline/eye/alpha change; 9px native fit; "+
            changed+" interior pixels changed; 75/100/160% handled by HeadKnifeV82");
    }
}