package com.survivalparadise.nativegame;
public final class V73CameraHudTest {
    static void near(float a,float b,float eps,String msg){
        if(Math.abs(a-b)>eps)throw new AssertionError(msg+": "+a+" != "+b);
    }
    static void ok(boolean b,String msg){if(!b)throw new AssertionError(msg);}
    public static void main(String[] args){
        near(CameraHudV73.zoom(45f),.45f,.0001f,"minimum zoom");
        near(CameraHudV73.zoom(70f),.70f,.0001f,"old minimum remains supported");
        near(CameraHudV73.zoom(100f),1f,.0001f,"normal zoom");
        near(CameraHudV73.zoom(180f),1.8f,.0001f,"maximum zoom");
        near(CameraHudV73.zoom(-20f),.45f,.0001f,"zoom clamp");
        near(CameraHudV73.zoom(400f),1.8f,.0001f,"zoom high clamp");
        near(CameraHudV73.opacity(0),15,0,"HUD still accessible");
        near(CameraHudV73.opacity(15),15,0,"minimum global fade");
        near(CameraHudV73.opacity(50),50,0,"mid HUD");
        near(CameraHudV73.opacity(100),100,0,"fully visible HUD");
        near(CameraHudV73.alpha(100),255,0,"opaque compositor");
        ok(CameraHudV73.alpha(15)<45,"fade is immersive");
        int[] firearms={0,1,2,4,5,6,7,8,9,10};
        for(int gun:firearms){
            int max=WeaponCameraV72.weaponMaximum(gun);
            ok(max>=320,"expanded ballistic class look-around "+gun);
            float z=CameraHudV73.zoom(45f);
            int visible=WeaponCameraV72.visibleMaximum(gun,1480f,720f,z);
            ok(visible==max,"zoom-out unlocks full circular camera range "+gun);
            float right=WeaponCameraV72.circle(10000,0,max)[0];
            float up=WeaponCameraV72.circle(0,-10000,max)[1];
            near(right,-up,.001f,"equal horizontal and vertical look-around "+gun);
        }
        ok(WeaponCameraV72.weaponMaximum(0)<WeaponCameraV72.weaponMaximum(4),
            "rifle pans farther than pistol");
        ok(WeaponCameraV72.weaponMaximum(4)<WeaponCameraV72.weaponMaximum(8),
            "sniper pans farthest");
        System.out.println("V73 PASS: 45% world zoom, HUD fade, enhanced weapon pan with equal circle");
    }
}