package com.survivalparadise.nativegame;
public final class V85GroundPickupTest {
 static void ok(boolean b,String m){if(!b)throw new AssertionError(m);}
 public static void main(String[]args){
  GroundPickupsV85 g=new GroundPickupsV85();
  int[] count=new int[3];int near=0;GroundPickupsV85.Item sample=null;
  for(int cy=-15;cy<15;cy++)for(int cx=-15;cx<15;cx++)
  for(int slot=0;slot<3;slot++){
    GroundPickupsV85.Item p=GroundPickupsV85.item(cx,cy,slot,1080,710);
    if(p==null)continue;
    GroundPickupsV85.Item q=GroundPickupsV85.item(cx,cy,slot,1080,710);
    ok(p.x==q.x&&p.y==q.y,"non-deterministic loose ground pickup");
    count[slot]++;if(Math.hypot(p.x-1080,p.y-710)<620){near++;sample=p;}
  }
  ok(count[0]>10&&count[1]>5&&count[2]>3,"missing one ground resource");
  ok(near>3,"camp/forest ground is too barren");
  ok(sample!=null,"missing sample");
  ok(g.nearest(sample.x,sample.y,1f,1080,710)!=null,"cannot pickup by USE");
  ok(g.collect(sample)&&!g.collect(sample),"duplicate pickup");
  GroundPickupsV85 restored=new GroundPickupsV85();restored.decode(g.encode());
  ok(restored.collected(sample.cx,sample.cy,sample.slot),"pickup respawned on Continue");
  ok(restored.nearest(sample.x,sample.y,1f,1080,710)==null,"used pickup remains interactive");
  restored.decode("garbage;0,0;1,2;bad,3");
  ok(restored.collectedCount()==2,"corrupt save parser error");
  restored.clear();ok(restored.collectedCount()==0,"new game did not reset");
  System.out.println("V85 PASS nearby "+near+" pickups: stone "+count[0]+
      ", wood "+count[1]+", scrap "+count[2]+", persistence and no duplication");
 }
}
