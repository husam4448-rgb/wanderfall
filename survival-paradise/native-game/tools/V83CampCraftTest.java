package com.survivalparadise.nativegame;
public final class V83CampCraftTest {
 static void ok(boolean b,String s){if(!b)throw new AssertionError(s);}
 public static void main(String[]args){
  CampCraftV83 c=new CampCraftV83();int[] inv={12,4,6,3};
  ok(c.craft(0,1080,710,inv),"craft barricade");
  ok(inv[0]==8&&inv[1]==2,"barricade costs");
  ok(!c.craft(1,1081,713,inv),"overlap must be rejected");
  ok(inv[0]==8&&inv[2]==6,"rejected craft spent material");
  ok(c.craft(1,1280,710,inv),"craft lamp");
  ok(inv[0]==6&&inv[2]==4&&inv[3]==2,"lamp costs");
  String raw=c.encode();CampCraftV83 copy=new CampCraftV83();copy.decode(raw);
  ok(copy.objects.size()==2,"save/load persistence");
  ok(copy.objects.get(0).kind==0&&copy.objects.get(1).kind==1,"kind persistence");
  copy.decode("0,-5000,2000;bad;8,1,1;1,-4870,2000;0,-5000,2000");
  ok(copy.objects.size()==2,"invalid/duplicate save not ignored");
  copy.clear();ok(copy.objects.size()==0,"new game must clear structures");
  int[] zeros={0,0,0,0};ok(!copy.craft(0,2,3,zeros),"free crafting");
  for(int i=0;i<CampCraftV83.MAX;i++){
   int[] huge={20,20,20,20};
   ok(copy.craft(0,i*150,0,huge),"cap premature");
  }
  ok(!copy.craft(0,9000,0,new int[]{20,20,20,20}),"limit bypass");
  System.out.println("V83 PASS camp crafting, collision spacing, limited structures, save/load");
 }
}
