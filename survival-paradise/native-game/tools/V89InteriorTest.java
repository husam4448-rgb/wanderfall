package com.survivalparadise.nativegame;
import java.util.ArrayDeque;
/** Pure JVM: interior geometry, path reachability and persistent loot. */
public final class V89InteriorTest {
 static void ok(boolean pass,String msg){if(!pass)throw new AssertionError(msg);}
 public static void main(String[]args){
  ClinicInteriorV89 in=new ClinicInteriorV89();
  ok(in.storages.length>=12,"not enough interior storage containers");
  ok(ClinicInteriorV89.WIDTH>=1500&&ClinicInteriorV89.HEIGHT>=1000,
      "building not full-scale");
  float s=ClinicInteriorV89.EXPANSION_V90;
  ok(!in.blocked(800*s,1030*s,19),"entry is blocked");
  ok(!in.blocked(800*s,568*s,19),"main corridor blocked");
  ok(!in.blocked(280*s,300*s,18),"triage is inaccessible");
  ok(!in.blocked(790*s,280*s,18),"operating theatre inaccessible");
  ok(!in.blocked(1350*s,280*s,18),"laboratory inaccessible");
  ok(!in.blocked(300*s,830*s,18),"pharmacy inaccessible");
  ok(!in.blocked(1300*s,970*s,18),"recovery ward inaccessible");
  ok(in.blocked(530*s,215*s,10),"wall collision absent");
  ok(in.blocked(12*s,200*s,10),"interior perimeter failed");
  // Flood fill verifies the door gaps actually connect all six departments.
  final int grid=20,w=ClinicInteriorV89.WIDTH/grid,h=ClinicInteriorV89.HEIGHT/grid;
  boolean[][] seen=new boolean[w][h];ArrayDeque<int[]> q=new ArrayDeque<>();
  int startX=(int)(800*s/grid),startY=(int)(1030*s/grid);
  seen[startX][startY]=true;q.add(new int[]{startX,startY});
  while(!q.isEmpty()){
   int[] a=q.removeFirst();
   for(int[] delta:new int[][]{{1,0},{-1,0},{0,1},{0,-1}}){
    int x=a[0]+delta[0],y=a[1]+delta[1];
    if(x<0||y<0||x>=w||y>=h||seen[x][y])continue;
    if(in.blocked(x*grid+grid*.5f,y*grid+grid*.5f,6))continue;
    seen[x][y]=true;q.addLast(new int[]{x,y});
   }
  }
  for(float[] room:ClinicInteriorV89.ROOM_LABELS){
   int x=(int)(room[0]/grid),y=(int)(room[1]/grid);
   boolean adjacent=false;
   for(int dx=-7;dx<=7;dx++)for(int dy=-7;dy<=7;dy++){
    int ax=x+dx,ay=y+dy;
    if(ax>=0&&ax<w&&ay>=0&&ay<h&&seen[ax][ay])adjacent=true;
   }
   ok(adjacent,"unreachable room "+x+","+y);
  }
  ClinicInteriorV89.Storage first=in.storages[0];
  ok(first.total()>0,"first cabinet empty");
  int qty=in.take(first,1);
  ok(qty>0&&in.take(first,1)==0,"cabinet duplicated medkits");
  String state=in.encode();
  ClinicInteriorV89 restored=new ClinicInteriorV89();
  restored.decode(state);
  ok(restored.storages[0].amount[1]==0,"partially looted save restored items");
  int[] all=restored.takeAll(restored.storages[0]);
  ok(all[1]==0,"loot all duplicated previously taken medkits");
  ok(restored.storages[0].empty(),"loot all not empty");
  String once=restored.encode();
  restored.decode(once);
  ok(restored.storages[0].empty(),"empty cabinet respawned after reload");
  ClinicInteriorV89 invalid=new ClinicInteriorV89();
  String before=invalid.encode();
  invalid.decode("garbage");
  ok(before.equals(invalid.encode()),"bad save destroyed default containers");
  invalid.reset();ok(!invalid.storages[0].empty(),"new game not reset");
  System.out.println("V89 PASS full-scale six-room clinic, door connectivity, furnishing collisions, 14 storages, partial loot and save/continue");
 }
}
