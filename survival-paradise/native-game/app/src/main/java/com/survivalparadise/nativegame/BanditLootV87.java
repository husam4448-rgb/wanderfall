package com.survivalparadise.nativegame;

import java.util.ArrayList;

/** Bandit equipment bags, independent of old timed ground drops. Persistent, no expiry. */
public final class BanditLootV87 {
    public static final int SCRAP=0,MEDKIT=1,AMMO=2,FOOD=3,WATER=4,
        WOOD=5,STONE=6,FIBER=7,ITEMS=8,MAX_BAGS=4096;
    public static final float USE_RADIUS=138f;
    public static final String[] NAMES={"Scrap","Medkit","Ammo","Food","Water",
        "Wood","Stone","Fiber"};
    public static final class Bag {
        public final int id;
        public final float x,y;
        public boolean corpse=false;
        public int variant=0,face=1,skinV109=-1;
        public final int[] count=new int[ITEMS];
        Bag(int id,float x,float y){this.id=id;this.x=x;this.y=y;}
        public boolean empty(){for(int n:count)if(n>0)return false;return true;}
        public int total(){int n=0;for(int c:count)n+=c;return n;}
    }
    public final ArrayList<Bag> bags=new ArrayList<>();
    private int nextId=1;
    public void clear(){bags.clear();nextId=1;}
    public Bag spawn(float x,float y,int kills,int wave,int variant){
        if(!Float.isFinite(x)||!Float.isFinite(y))return null;
        if(bags.size()>=MAX_BAGS)return null;
        Bag bag=new Bag(nextId++,x,y);
        // An individual bag always contains 2–4 recognizable types.
        bag.count[SCRAP]=1+Math.floorMod(kills+variant,3);
        bag.count[AMMO]=1+Math.floorMod(wave+kills,2);
        if(kills%3==0)bag.count[MEDKIT]=1;
        else if(kills%3==1)bag.count[FOOD]=1;
        else bag.count[WATER]=1;
        if((kills+variant)%4==0)bag.count[FIBER]=2;
        if((kills+wave)%5==0)bag.count[WOOD]=2;
        bags.add(bag);return bag;
    }
    public Bag spawnCorpse(float x,float y,int kills,int wave,int variant,int face){
        return spawnCorpse(x,y,kills,wave,variant,face,-1);
    }
    /** Keep the exact original NPC skin ID, never derive a new head on death. */
    public Bag spawnCorpse(float x,float y,int kills,int wave,int variant,int face,int skinV109){
        Bag bag=spawn(x,y,kills,wave,variant);
        if(bag!=null){
            bag.corpse=true;bag.variant=variant;bag.face=face<0?-1:1;
            bag.skinV109=skinV109>=1&&skinV109<=200?skinV109:-1;
        }
        return bag;
    }
    public Bag nearest(float x,float y,float range){
        Bag best=null;float dmin=range*range;
        for(Bag bag:bags){
            if(bag.empty())continue;
            float dx=bag.x-x,dy=bag.y-y,d=dx*dx+dy*dy;
            if(d<=dmin){best=bag;dmin=d;}
        }
        return best;
    }
    public boolean contains(Bag bag){return bag!=null&&bags.contains(bag);}
    /** Take a whole icon stack only once; remove bag on the final transfer. */
    public int take(Bag bag,int kind){
        if(!contains(bag)||kind<0||kind>=ITEMS)return 0;
        int amount=bag.count[kind];
        if(amount<=0)return 0;
        bag.count[kind]=0;
        if(bag.empty()&&!bag.corpse)bags.remove(bag);
        return amount;
    }
    public int[] takeAll(Bag bag){
        int[] taken=new int[ITEMS];
        if(!contains(bag))return taken;
        System.arraycopy(bag.count,0,taken,0,ITEMS);
        for(int i=0;i<ITEMS;i++)bag.count[i]=0;
        if(!bag.corpse)bags.remove(bag);
        return taken;
    }
    public String encode(){
        StringBuilder out=new StringBuilder(bags.size()*52);
        for(Bag bag:bags){
            if(bag.empty()&&!bag.corpse)continue;
            if(out.length()>0)out.append(';');
            out.append(bag.id).append(',').append(Math.round(bag.x)).
                append(',').append(Math.round(bag.y));
            for(int n:bag.count)out.append(',').append(n);
            out.append(',').append(bag.corpse?1:0).append(',')
               .append(bag.variant).append(',').append(bag.face)
               .append(',').append(bag.skinV109);
        }
        return out.toString();
    }
    public void decode(String data){
        clear();if(data==null||data.isEmpty())return;
        for(String entry:data.split(";")){
            if(bags.size()>=MAX_BAGS)break;
            String[] p=entry.split(",");
            if(p.length!=ITEMS+3&&p.length!=ITEMS+6&&p.length!=ITEMS+7)continue;
            try{
                int id=Integer.parseInt(p[0]);
                float x=Float.parseFloat(p[1]),y=Float.parseFloat(p[2]);
                if(id<1||!Float.isFinite(x)||!Float.isFinite(y)||
                   Math.abs(x)>2000000||Math.abs(y)>2000000)continue;
                boolean duplicate=false;
                for(Bag b:bags)if(b.id==id){duplicate=true;break;}
                if(duplicate)continue;
                Bag bag=new Bag(id,x,y);
                boolean invalid=false;
                for(int i=0;i<ITEMS;i++){
                    int n=Integer.parseInt(p[i+3]);
                    if(n<0||n>999){invalid=true;break;}
                    bag.count[i]=n;
                }
                if(p.length>=ITEMS+6){
                    bag.corpse=Integer.parseInt(p[ITEMS+3])==1;
                    bag.variant=Integer.parseInt(p[ITEMS+4]);
                    bag.face=Integer.parseInt(p[ITEMS+5])<0?-1:1;
                    if(p.length==ITEMS+7){
                        int skin=Integer.parseInt(p[ITEMS+6]);
                        bag.skinV109=skin>=1&&skin<=200?skin:-1;
                    }
                }
                if(!invalid&&(!bag.empty()||bag.corpse)){
                    bags.add(bag);
                    nextId=Math.max(nextId,id+1);
                }
            }catch(NumberFormatException ignored){/* corrupted save segment */}
        }
    }
}
