package com.survivalparadise.nativegame;
import java.util.ArrayList;
/** Persistent field-crafting structures. Runtime uses the same world coordinates as V80. */
public final class CampCraftV83 {
 public static final int BARRICADE=0,LIGHT_POST=1,WATER_COLLECTOR=2,FIELD_SHELTER=3,MAX=32,WOOD=0,STONE=1,FIBER=2,SCRAP=3;
 public static final int[][] COST={{4,2,0,0},{2,0,2,1},{3,2,3,1},{5,0,4,1}};
 public static final class Structure {
  public final int kind;public final float x,y;
  Structure(int k,float x,float y){kind=k;this.x=x;this.y=y;}
 }
 public final ArrayList<Structure> objects=new ArrayList<>();
 public String error="";
 public void clear(){objects.clear();java.util.Arrays.fill(stock,0);error="";}
 public boolean near(float x,float y){
  for(Structure v:objects){float dx=x-v.x,dy=y-v.y;if(dx*dx+dy*dy<96f*96f)return true;}
  return false;
 }
 public boolean craft(int kind,float x,float y,int[] inv){
  if(kind<0||kind>=COST.length){error="Unknown recipe";return false;}
  if(!Float.isFinite(x)||!Float.isFinite(y)||Math.abs(x)>2000000f||Math.abs(y)>2000000f){
   error="Invalid position";return false;}
  if(objects.size()>=MAX){error="Maximum 32 structures";return false;}
  if(near(x,y)){error="Too close to another structure";return false;}
  if(inv==null||inv.length<4){error="Missing inventory";return false;}
  for(int i=0;i<4;i++)if(inv[i]<COST[kind][i]){error="Insufficient materials";return false;}
  for(int i=0;i<4;i++)inv[i]-=COST[kind][i];
  objects.add(new Structure(kind,x,y));error="";return true;
 }

 /** V84: crafting yields portable backpack items rather than placing immediately. */
 public final int[] stock=new int[4];
 public boolean craftToBag(int kind,int[] resources){
  if(kind<0||kind>=COST.length){error="Unknown recipe";return false;}
  if(resources==null||resources.length<4){error="Missing resources";return false;}
  if(stock[kind]>=99){error="Bag stack full";return false;}
  for(int i=0;i<4;i++)if(resources[i]<COST[kind][i]){
   error="Insufficient materials";return false;
  }
  for(int i=0;i<4;i++)resources[i]-=COST[kind][i];
  stock[kind]++;error="";return true;
 }
 public boolean placeFromBag(int kind,float x,float y){
  if(kind<0||kind>=COST.length||stock[kind]<1){error="No crafted item in backpack";return false;}
  if(!Float.isFinite(x)||!Float.isFinite(y)){error="Invalid position";return false;}
  if(objects.size()>=MAX){error="Maximum 32 structures";return false;}
  if(near(x,y)){error="Too close to another structure";return false;}
  objects.add(new Structure(kind,x,y));stock[kind]--;error="";return true;
 }
 public String encodeStock(){return stock[0]+","+stock[1]+","+stock[2]+","+stock[3];}
 public void decodeStock(String data){
  java.util.Arrays.fill(stock,0);
  if(data==null)return;String[] p=data.split(",");
  // V84/V87 had 2 stored structure types; keep their save files importable.
  if(p.length!=2&&p.length!=4)return;
  try{
   for(int i=0;i<p.length;i++){
    int n=Integer.parseInt(p[i]);if(n<0||n>99){java.util.Arrays.fill(stock,0);return;}
    stock[i]=n;
   }
  }catch(NumberFormatException ignored){java.util.Arrays.fill(stock,0);}
 }
 public String encode(){
  StringBuilder b=new StringBuilder();
  for(Structure v:objects){if(b.length()>0)b.append(';');
   b.append(v.kind).append(',').append(Math.round(v.x)).append(',').append(Math.round(v.y));}
  return b.toString();
 }
 public void decode(String raw){
  clear();if(raw==null||raw.isEmpty())return;
  for(String token:raw.split(";")){
   if(objects.size()>=MAX)break;String[] p=token.split(",");
   if(p.length!=3)continue;
   try{
    int kind=Integer.parseInt(p[0]);float x=Float.parseFloat(p[1]),y=Float.parseFloat(p[2]);
    if((kind>=0&&kind<COST.length)&&Float.isFinite(x)&&Float.isFinite(y)&&
       Math.abs(x)<=2000000f&&Math.abs(y)<=2000000f&&!near(x,y))
      objects.add(new Structure(kind,x,y));
   }catch(NumberFormatException ignored){}
  }
 }
}
