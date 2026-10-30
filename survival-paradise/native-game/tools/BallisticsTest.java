package com.survivalparadise.nativegame;
public class BallisticsTest{
 static void check(boolean yes,String msg){if(!yes)throw new AssertionError(msg);}
 static void near(float got,float want,float eps,String msg){check(Math.abs(got-want)<eps,msg+" "+got+" vs "+want);}
 public static void main(String[]args){
  check(Ballistics.SPEED[0]>2000&&Ballistics.SPEED[8]>3900&&Ballistics.SPEED[10]<Ballistics.SPEED[0],"weapon velocity bands");
  float[] r=Ballistics.muzzle(1000,1100,1,1,0,.76f,147,79,103,76,0);
  float[] l=Ballistics.muzzle(1000,1100,-1,-1,0,.76f,147,79,103,76,0);
  near(r[0]-1000,1000-l[0],.01f,"left/right barrel mirror");
  near(r[1],l[1],.01f,"barrel height");
  float[] up=Ballistics.muzzle(1000,1100,1,0,-1,.76f,147,79,103,76,0);
  float[] down=Ballistics.muzzle(1000,1100,1,0,1,.76f,147,79,103,76,0);
  check(up[1]<r[1]&&down[1]>r[1],"vertical aiming for full 180-deg arc");
  near(Ballistics.segmentCircle(0,0,100,0,49,0,1),.48f,.0001f,"swept target");
  near(Ballistics.segmentBox(0,0,100,0,45,-2,55,2),.45f,.0001f,"swept cover");
  check(Float.isInfinite(Ballistics.segmentCircle(0,0,100,0,50,60,1)),"miss target");

  // V36 regression: hand grip must never drift farther than one small torso reach
  // from its parent, regardless of weapon, side, recoil or aim angle.
  float[] angles={-1.55f,-1.15f,-.7f,-.25f,0f,.25f,.7f,1.15f,1.55f};
  float px=1234f,py=567f,s=.76f;
  float rootX=(Ballistics.TORSO_X-70f)*s;
  float rootY=(Ballistics.TORSO_Y-136f)*s;
  for(int facing:new int[]{1,-1}){
    for(float angle:angles){
      float dx=facing*(float)Math.cos(angle),dy=(float)Math.sin(angle);
      float actual=Ballistics.angle(dx,dy,facing);
      near(actual,angle,.0001f,"world aim must match visual rotation");
      float[] grip=Ballistics.rigGrip(px,py,facing,dx,dy,s,0f);
      float torsoWorldX=px+facing*rootX,torsoWorldY=py+rootY;
      float reach=(float)Math.hypot(grip[0]-torsoWorldX,grip[1]-torsoWorldY);
      float expected=(float)Math.hypot(Ballistics.GRIP_X-Ballistics.TORSO_X,
                                     Ballistics.GRIP_Y-Ballistics.TORSO_Y)*s;
      near(reach,expected,.001f,"rigid hand-body reach");
      check(reach<=9.5f,"hand too distant from torso");
      for(int weapon=0;weapon<12;weapon++){
        float[] mx={147,171,154,129,220,215,213,225,238,228,216,183};
        float[] my={79,73,75,88,75,78,72,80,74,72,71,92};
        float[] srcX={103,103,103,97,102,101,101,101,101,102,101,102};
        float[] srcY={76,75,76,78,77,77,77,77,77,77,77,81};
        float[] muzzle=Ballistics.rigMuzzle(px,py,facing,dx,dy,s,mx[weapon],my[weapon],srcX[weapon],srcY[weapon],0f);
        float barrel=(float)Math.hypot(muzzle[0]-grip[0],muzzle[1]-grip[1]);
        float expectedBarrel=(float)Math.hypot(mx[weapon]-srcX[weapon],my[weapon]-srcY[weapon])*s;
        near(barrel,expectedBarrel,.001f,"barrel rigid to hand contact");
      }
    }
  }

  System.out.println("V36 torso-anchored weapon-rig regression checks PASS");
 }
}
