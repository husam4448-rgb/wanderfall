package com.survivalparadise.nativegame;
public final class V118RegressionTest {
  static void check(boolean b,String msg){if(!b)throw new AssertionError(msg);}
  public static void main(String[] args){
    for(int w=0;w<12;w++)check(GunEffectsV118.firearm(w)==(w!=3&&w!=11),"gun effect type "+w);
    check(CompanionOrdersV118.spacing(1)==70,"minimum formation standoff");
    check(CompanionOrdersV118.spacing(1000)==450,"maximum formation standoff");
    check(CompanionOrdersV118.mayMove(false)&&!CompanionOrdersV118.mayMove(true),"stay/follow command");
    check(CompanionOrdersV118.mayShoot(false)&&!CompanionOrdersV118.mayShoot(true),"hold/fire command");
    for(int form=0;form<5;form++)for(int i=0;i<5;i++){
      float x=CompanionOrdersV118.targetX(0,1,0,form,i,5,210);
      float y=CompanionOrdersV118.targetY(0,1,0,form,i,5,210);
      check(Float.isFinite(x)&&Float.isFinite(y),"finite formation positions");
    }
    check(GunEffectsV118.lifeFraction(2,1)==1f,"flash clamp");
    check(GunEffectsV118.lifeFraction(-1,1)==0f,"expired flash invisible");
    System.out.println("V118 companion move/fire independent and firearm-only visual effects: PASS");
  }
}
