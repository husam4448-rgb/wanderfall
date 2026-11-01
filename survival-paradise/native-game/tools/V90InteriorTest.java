package com.survivalparadise.nativegame;
public final class V90InteriorTest {
 static void ok(boolean x,String msg){if(!x)throw new AssertionError(msg);}
 public static void main(String[]args){
  ClinicInteriorV89 map=new ClinicInteriorV89();
  ok(ClinicInteriorV89.WIDTH>=2600&&ClinicInteriorV89.HEIGHT>=1800,
      "not enlarged for full screen");
  float s=ClinicInteriorV89.EXPANSION_V90;
  ok(ClinicInteriorV89.ENTRANCE_X>1150,"entry not relocated");
  ok(!map.blocked(ClinicInteriorV89.ENTRANCE_X,
      ClinicInteriorV89.ENTRANCE_Y,18),"entrance blocked");
  ok(!map.blocked(800*s,568*s,18),"widened main hall blocked");
  ok(!map.blocked(280*s,300*s,18),"triage blocked");
  ok(!map.blocked(790*s,280*s,18),"surgery blocked");
  ok(!map.blocked(1350*s,280*s,18),"lab blocked");
  ok(!map.blocked(300*s,830*s,18),"pharmacy blocked");
  ok(!map.blocked(1300*s,970*s,18),"recovery blocked");
  ok(map.blocked(530*s,215*s,9),"room wall missing");
  ClinicVisionV90 v=new ClinicVisionV90();
  v.trace(800*s,565*s,1,0,map);
  ok(v.blockedRays>0,"vision ignores clinic walls");
  ok(v.visible(800*s,565*s,1,0,820*s,565*s,map),
      "forward corridor not visible");
  ok(!v.visible(800*s,565*s,1,0,760*s,565*s,map),
      "rear vision not concealed");
  ClinicActorsV90 enemies=new ClinicActorsV90(map);
  ok(enemies.actors.length>=7,"missing indoor enemy/friendly actors");
  boolean hasZombie=false,hasFeral=false,hasRaider=false,hasFriendly=false;
  for(ClinicActorsV90.Actor a:enemies.actors){
    ok(!map.blocked(a.x,a.y,13),"actor spawned inside wall/furniture");
    if(a.type==ClinicActorsV90.ZOMBIE)hasZombie=true;
    if(a.type==ClinicActorsV90.FERAL)hasFeral=true;
    if(a.type==ClinicActorsV90.RAIDER)hasRaider=true;
    if(!a.hostile())hasFriendly=true;
  }
  ok(hasZombie&&hasFeral&&hasRaider&&hasFriendly,
      "indoor factions incomplete");
  ClinicActorsV90.Actor enemy=enemies.actors[0];
  ok(enemies.hit(enemy,900)&&!enemy.active,"invulnerable indoor enemy");
  String saved=enemies.encode();
  ClinicActorsV90 continued=new ClinicActorsV90(map);continued.decode(saved,map);
  ok(!continued.actors[0].active,"dead enemy respawn after Continue");
  continued.decode("garbage",map);
  ok(continued.actors[0].active,"corrupted save destroys encounter template");
  ClinicInteriorV89.Storage item=map.storages[0];
  int n=map.take(item,1);
  ok(n>0&&map.take(item,1)==0,"loot dupes");
  ClinicInteriorV89 restored=new ClinicInteriorV89();
  restored.decode(map.encode());
  ok(restored.storages[0].amount[1]==0,"old clinic loot save lost");
  System.out.println("V90 PASS full-screen widened 2720x1904 clinic, occluded vision, zombies/animals/hostiles/friendlies, actor/loot persistence");
 }
}
