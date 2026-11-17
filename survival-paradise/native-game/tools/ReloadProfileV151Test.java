package com.survivalparadise.nativegame;

import java.util.HashSet;

public final class ReloadProfileV151Test {
    private static void check(boolean ok,String reason){
        if(!ok)throw new AssertionError(reason);
    }
    public static void main(String[] args){
        HashSet<String> unique=new HashSet<>();
        for(int weapon=0;weapon<12;weapon++){
            if(weapon==3||weapon==11){
                check(!ReloadProfileV151.canReload(weapon),"non-firearm "+weapon);
                check(ReloadProfileV151.duration(weapon)==0f,"non-firearm delay");
                continue;
            }
            check(ReloadProfileV151.canReload(weapon),"firearm "+weapon);
            check(ReloadProfileV151.duration(weapon)>=1.3f,
                "unrealistically instant reload "+weapon);
            check(unique.add(ReloadProfileV151.propName(weapon)),"duplicate reload prop "+weapon);
            float full=ReloadProfileV151.duration(weapon);
            check(ReloadProfileV151.progress(weapon,full)==0f,"start phase "+weapon);
            check(ReloadProfileV151.progress(weapon,0f)==1f,"end phase "+weapon);
            check(ReloadProfileV151.propVisible(weapon,full*.5f),"prop missing "+weapon);
            check(!ReloadProfileV151.propVisible(weapon,0f),"prop after finish "+weapon);
            check(ReloadProfileV151.tiltDegrees(weapon,full)==0f,"start tilt "+weapon);
            check(ReloadProfileV151.tiltDegrees(weapon,0f)==0f,"end tilt "+weapon);
            float prior=ReloadProfileV151.handX(weapon,full);
            for(int i=1;i<=125;i++){
                float now=ReloadProfileV151.handX(weapon,full*(1-i/125f));
                check(Math.abs(now-prior)<5f,"hand jump "+weapon+" at "+i);
                prior=now;
            }
        }
        check(!ReloadProfileV151.propName(0).equals(ReloadProfileV151.propName(5)),
            "AK must not get handgun magazine");
        check(ReloadProfileV151.propKind(5)==ReloadProfileV151.CURVED_AK,
            "AK magazine must be curved");
        check(ReloadProfileV151.propKind(9)==ReloadProfileV151.BELT_BOX,
            "BKC / LMG needs belt box, not handgun mag");
        check(ReloadProfileV151.propKind(4)==ReloadProfileV151.STANAG,
            "carbine uses STANAG");
        check(ReloadProfileV151.topFeed(7),"shotgun loads from top");
        check(!ReloadProfileV151.topFeed(5),"AK does not top-load shells");
        check(ReloadProfileV151.needsBorrowedHand(0)&&
            ReloadProfileV151.needsBorrowedHand(1)&&
            ReloadProfileV151.needsBorrowedHand(2),
            "handguns need visible spare support hand");
        System.out.println("PASS V151 10 distinct weapon-specific reload prop families and hand paths");
    }
}
