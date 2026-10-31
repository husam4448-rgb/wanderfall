package com.survivalparadise.nativegame;
public final class V72WeaponCameraTest{
    static void ok(boolean b,String msg){if(!b)throw new AssertionError(msg);}
    static void near(float actual,float desired,String msg){
        ok(Math.abs(actual-desired)<.01f,msg+": "+actual+" expected "+desired);
    }
    public static void main(String[] args){
        int[] expected={320,320,320,250,520,520,520,400,720,560,440,160};
        for(int w=0;w<12;w++)ok(WeaponCameraV72.weaponMaximum(w)==expected[w],
            "weapon maximum "+w);
        ok(WeaponCameraV72.weaponMaximum(0)<WeaponCameraV72.weaponMaximum(4),
            "short firearm vs rifle");
        ok(WeaponCameraV72.weaponMaximum(4)<WeaponCameraV72.weaponMaximum(8),
            "rifle vs sniper");
        near(WeaponCameraV72.distance(0,72,1480,720,1),230.4f,
            "short pistol default ~2x former 65px");
        near(WeaponCameraV72.distance(4,72,1480,720,1),374.4f,
            "rifle default longer");
        near(WeaponCameraV72.distance(8,100,1480,900,1),720f,
            "sniper maximum doubled again to 720 world pixels");
        near(WeaponCameraV72.distance(8,100,1480,720,1),705f,
            "screen-height guard remains symmetric");
        near(WeaponCameraV72.distance(8,0,1480,720,1),0,
            "0% disables camera pan");
        near(WeaponCameraV72.distance(8,100,1480,720,2),352f,
            "zoom affects symmetric viewport guard");
        for(int w=0;w<12;w++){
            float radius=WeaponCameraV72.distance(w,100,1480,720,1);
            float[] left=WeaponCameraV72.circle(-1000,0,radius);
            float[] right=WeaponCameraV72.circle(1000,0,radius);
            float[] top=WeaponCameraV72.circle(0,-1000,radius);
            float[] bottom=WeaponCameraV72.circle(0,1000,radius);
            float[] diagonal=WeaponCameraV72.circle(1000,1000,radius);
            near(-left[0],radius,"left "+w);
            near(right[0],radius,"right "+w);
            near(-top[1],radius,"up "+w);
            near(bottom[1],radius,"down "+w);
            near((float)Math.hypot(diagonal[0],diagonal[1]),radius,"diagonal "+w);
        }
        System.out.println("V73 PASS: expanded weapon pan caps, viewport limits, equal four-axis circular panning");
    }
}