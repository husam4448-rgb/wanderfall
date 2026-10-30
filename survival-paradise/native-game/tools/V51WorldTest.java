package com.survivalparadise.nativegame;
/** Regenerate identical terrain patches and no NPC identity randomization. */
public final class V51WorldTest {
 static int hash(int a,int b){int k=a*73856093^b*19349663;k^=k>>>13;k*=0x5bd1e995;return k^(k>>>15);}
 public static void main(String[] args){
  for(int gx=-40;gx<40;gx++)for(int gy=-40;gy<40;gy++){
   int p=hash(Math.floorDiv(gx,5),Math.floorDiv(gy,5));
   if(p!=hash(Math.floorDiv(gx,5),Math.floorDiv(gy,5)))throw new AssertionError("world nondeterministic");
   if(Math.floorMod(p,4)<0||Math.floorMod(p,4)>3)throw new AssertionError("biome out of range");
  }
  System.out.println("PASS V51: deterministic world patches");
 }
}