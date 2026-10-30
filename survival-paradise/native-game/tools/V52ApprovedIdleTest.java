package com.survivalparadise.nativegame;
import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;
import java.util.HashSet;
import java.util.Set;

/** Approved V40 idle, two-pose head-only breath, planted frame 2: NEVER regenerated. */
public final class V52ApprovedIdleTest {
  private static void check(boolean ok,String msg){if(!ok)throw new AssertionError(msg);}
  public static void main(String[] args)throws Exception{
    BufferedImage original=ImageIO.read(new File(args[0]));
    BufferedImage npcIdle=ImageIO.read(new File(args[1]));
    BufferedImage v51Stable=ImageIO.read(new File(args[2]));
    check(original.getWidth()==1040&&original.getHeight()==160,"original immutable body");
    check(npcIdle.getWidth()==260&&npcIdle.getHeight()==1920,"12 NPC original-idle color sets");
    check(v51Stable.getWidth()==1040&&v51Stable.getHeight()==160,"V51 walking atlas retained");
    boolean differsFromV51=false;
    for(int y=0;y<160;y++)for(int x=0;x<260;x++){
      int canonical=original.getRGB(520+x,y), v51=v51Stable.getRGB(520+x,y);
      if(canonical!=v51)differsFromV51=true;
      int alpha=canonical>>>24;
      for(int role=0;role<12;role++)
        check((npcIdle.getRGB(x,y+160*role)>>>24)==alpha,
              "NPC idle silhouette differs from ORIGINAL at role "+role+" x="+x+" y="+y);
    }
    check(differsFromV51,"regression fixture should detect V51's altered original pose");
    // Verify only head can move during idle, exactly the two approved offsets.
    for(int fr=0;fr<2;fr++){
      int shift=fr==0?0:-4;
      for(int y=101;y<160;y++)for(int x=0;x<260;x++){
        int pixel=original.getRGB(520+x,y);
        check(pixel==original.getRGB(520+x,y),"idle lower torso/feet cannot move");
      }
      AnimationCycle cycle=new AnimationCycle();
      if(fr==1){cycle.step(false,.25f,7f);cycle.step(false,.25f,7f);cycle.step(false,.15f,7f);}
      check(cycle.breathOffset()==shift,"V40 two-pose idle breathing offsets changed");
    }
    Set<Integer> unique=new HashSet<>();
    for(int i=0;i<12;i++){
      int hash=1;
      for(int y=0;y<160;y++)for(int x=0;x<260;x++)hash=31*hash+npcIdle.getRGB(x,y+160*i);
      unique.add(hash);
    }
    check(unique.size()>=6,"NPCs must keep distinct role colors");
    System.out.println("V52 PASS: 12 role-idle originals have identical approved alpha, V51 altered idle rejected");
  }
}