package com.survivalparadise.nativegame;
public final class V61FormationTest{
    static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    public static void main(String[] args){
        check(FollowFormationV61.NAMES.length==5,"all modes exposed");
        int n=8,spacing=130;
        for(int mode=0;mode<5;mode++){
            for(int i=0;i<n;i++){
                float x=FollowFormationV61.targetX(2000,1,0,mode,i,n,spacing);
                float y=FollowFormationV61.targetY(500,1,0,mode,i,n,spacing);
                check(Float.isFinite(x)&&Float.isFinite(y),"finite formation slots");
                check(x==FollowFormationV61.targetX(2000,1,0,mode,i,n,spacing),
                      "same slot when revisiting");
                check(Math.hypot(x-2000,y-500)>40,"personal distance");
                for(int j=0;j<i;j++){
                    float xx=FollowFormationV61.targetX(2000,1,0,mode,j,n,spacing);
                    float yy=FollowFormationV61.targetY(500,1,0,mode,j,n,spacing);
                    check(Math.hypot(x-xx,y-yy)>=40,"separate squad members "+mode);
                }
            }
        }
        for(int i=0;i<8;i++){
            float y=FollowFormationV61.targetY(0,1,0,FollowFormationV61.LINE,i,8,spacing);
            float yy=FollowFormationV61.targetY(0,1,0,FollowFormationV61.LINE,0,8,spacing);
            check(i==0||y!=yy,"perpendicular soldier ranks");
        }
        check(FollowFormationV61.targetX(0,1,0,FollowFormationV61.CARAVAN,7,8,spacing)<
              FollowFormationV61.targetX(0,1,0,FollowFormationV61.CARAVAN,0,8,spacing),
              "caravan falls behind player");
        System.out.println("V61 PASS: 5 distinct deterministic formation modes, no identical slots");
    }
}
