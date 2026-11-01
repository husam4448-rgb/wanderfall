package com.survivalparadise.nativegame;
public final class V88WorldTest {
 static void yes(boolean b,String s){if(!b)throw new AssertionError(s);}
 public static void main(String[]args){
  yes(ExpeditionSitesV88.SITES.length>=10,"too few places to visit");
  for(int i=0;i<ExpeditionSitesV88.SITES.length;i++){
   ExpeditionSitesV88.Site a=ExpeditionSitesV88.SITES[i];
   yes(a.name.length()>5,"missing site label");
   yes(ExpeditionSitesV88.nearest(a.x,a.y,1)==a,"landmark search failed");
   int[] l=ExpeditionSitesV88.supplies(i);int sum=0;for(int q:l)sum+=q;
   yes(sum>=3,"location lacks supplies");
   for(int j=0;j<i;j++){
    ExpeditionSitesV88.Site b=ExpeditionSitesV88.SITES[j];
    yes(Math.hypot(a.x-b.x,a.y-b.y)>250,"sites overlap");
   }
  }
  yes(BanditBrainV88.state(650,78,false)==BanditBrainV88.PATROL,"idle patrol");
  yes(BanditBrainV88.state(470,78,false)==BanditBrainV88.CHASE,"chase");
  yes(BanditBrainV88.state(220,78,false)==BanditBrainV88.STRAFE,"strafe");
  yes(BanditBrainV88.state(220,78,true)==BanditBrainV88.GUARD,"cover");
  yes(BanditBrainV88.state(220,20,false)==BanditBrainV88.RETREAT,"low-health retreat");
  yes(!BanditBrainV88.shouldShoot(BanditBrainV88.STRAFE,200,0,false),"fires through wall");
  yes(BanditBrainV88.shouldShoot(BanditBrainV88.STRAFE,200,0,true),"never shoots");
  yes(!BanditBrainV88.shouldShoot(BanditBrainV88.CHASE,200,0,true),"shoots while chasing");
  yes(BanditBrainV88.moveX(BanditBrainV88.RETREAT,1,0,1)==-1,"retreat direction");
  yes(BanditBrainV88.moveY(BanditBrainV88.STRAFE,1,0,1)==1,"strafing direction");
  System.out.println("V88 PASS ten explorable landmarks with supplies and AI patrol/chase/strafe/retreat/cover states");
 }
}
