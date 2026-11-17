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
        // Explicit manifest distinguishes newly stripped bodies from V87/V129
        // legacy corpses. It persists even after the last item was taken.
        public boolean gearManifestV141=false;
        public long nutsV143=0; // immutable coin value until explicitly looted
        public int variant=0,face=1,skinV109=-1;
        public final int[] count=new int[ITEMS];
        /** Index 0 maps to stable item ID 39. Versioned, sparse save encoding. */
        public final int[] extra=new int[58];
        /** Six independent ammo families; old 58 gear cells stay immutable. */
        public final int[] ammoExtraV143=new int[6];
        public int itemCount(int kind){
            if(kind>=ITEMS+extra.length&&
               kind<ITEMS+extra.length+ammoExtraV143.length)
                return ammoExtraV143[kind-ITEMS-extra.length];
            if(kind>=ITEMS+extra.length+ammoExtraV143.length&&
               kind<ITEMS+extra.length+ammoExtraV143.length+3){
                int denomination=kind-(ITEMS+extra.length+
                    ammoExtraV143.length);
                return denomination==NutWalletV143.IRON?(int)(nutsV143%100):
                    denomination==NutWalletV143.SILVER_COIN?
                        (int)(nutsV143%10000/100):(int)(nutsV143/10000);
            }
            return kind>=0&&kind<ITEMS?count[kind]:
                kind>=ITEMS&&kind<ITEMS+extra.length?extra[kind-ITEMS]:0;
        }
        public boolean hasExtra(){for(int n:extra)if(n>0)return true;return false;}
        Bag(int id,float x,float y){this.id=id;this.x=x;this.y=y;}
        public boolean empty(){
            for(int n:count)if(n>0)return false;
            if(nutsV143>0||hasExtra())return false;
            for(int n:ammoExtraV143)if(n>0)return false;
            return true;
        }
        public int total(){
            int n=0;for(int c:count)n+=c;for(int c:extra)n+=c;
            for(int c:ammoExtraV143)n+=c;
            for(int d=0;d<3;d++)n+=itemCount(ITEMS+extra.length+
                ammoExtraV143.length+d);
            return n;
        }
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
    public int takeExtra(Bag bag,int index){
        if(!contains(bag)||index<0||index>=58)return 0;
        int n=bag.extra[index];if(n<=0)return 0;
        bag.extra[index]=0;
        if(bag.empty()&&!bag.corpse)bags.remove(bag);
        return n;
    }
    public int takeNutsV143(Bag bag,int denomination){
        if(!contains(bag)||denomination<0||denomination>2)return 0;
        int amount=bag.itemCount(ITEMS+bag.extra.length+
            bag.ammoExtraV143.length+denomination);
        if(amount<=0)return 0;
        bag.nutsV143-=(long)amount*NutWalletV143.unit(denomination);
        if(bag.empty()&&!bag.corpse)bags.remove(bag);
        return amount;
    }
    public long takeAllNutsV143(Bag bag){
        if(!contains(bag))return 0;
        long total=bag.nutsV143;bag.nutsV143=0;
        if(bag.empty()&&!bag.corpse)bags.remove(bag);
        return total;
    }
    public int takeAmmoV143(Bag bag,int familyIndex){
        if(!contains(bag)||familyIndex<0||familyIndex>=6)return 0;
        int amount=bag.ammoExtraV143[familyIndex];
        if(amount<1)return 0;
        bag.ammoExtraV143[familyIndex]=0;
        if(bag.empty()&&!bag.corpse)bags.remove(bag);
        return amount;
    }
    public int[] takeAllExtra(Bag bag){
        int[] out=new int[58];
        if(!contains(bag))return out;
        System.arraycopy(bag.extra,0,out,0,out.length);
        java.util.Arrays.fill(bag.extra,0);
        if(bag.empty()&&!bag.corpse)bags.remove(bag);
        return out;
    }
    public int[] takeAll(Bag bag){
        int[] taken=new int[ITEMS];
        if(!contains(bag))return taken;
        System.arraycopy(bag.count,0,taken,0,ITEMS);
        for(int i=0;i<ITEMS;i++)bag.count[i]=0;
        if(!bag.corpse)bags.remove(bag);
        return taken;
    }
    private static boolean bagHasAmmoV143(Bag bag){
        for(int n:bag.ammoExtraV143)if(n>0)return true;
        return false;
    }
    /**
     * One-time pre-V153 fixed-site cache relocation. Only the original static
     * outdoor supplies bags are moved, identified by their exact authored
     * world coordinates. Corpse/normal drop locations and ALL item quantities,
     * gear, ammunition, currency and IDs are preserved.
     */
    public int migrateFixedSiteCachesV153(){
        int moved=0;
        for(int index=0;index<bags.size();index++){
            Bag old=bags.get(index);
            if(old.corpse)continue;
            for(int i=0;i<ExpeditionSitesV88.SITES.length;i++){
                float originalX=ExpeditionSitesV88.LEGACY_X[i]+115f;
                float originalY=ExpeditionSitesV88.LEGACY_Y[i]+91f;
                if(Math.abs(old.x-originalX)>1.1f||
                   Math.abs(old.y-originalY)>1.1f)continue;
                ExpeditionSitesV88.Site site=ExpeditionSitesV88.SITES[i];
                if(Math.abs(site.x+115f-old.x)<1f&&
                   Math.abs(site.y+91f-old.y)<1f)break;
                Bag shifted=new Bag(old.id,site.x+120f,
                    site.y+ExteriorFootprintV130.anchor(site)+36f);
                shifted.corpse=old.corpse;
                shifted.gearManifestV141=old.gearManifestV141;
                shifted.nutsV143=old.nutsV143;
                shifted.variant=old.variant;shifted.face=old.face;
                shifted.skinV109=old.skinV109;
                System.arraycopy(old.count,0,shifted.count,0,old.count.length);
                System.arraycopy(old.extra,0,shifted.extra,0,old.extra.length);
                System.arraycopy(old.ammoExtraV143,0,shifted.ammoExtraV143,0,
                    old.ammoExtraV143.length);
                bags.set(index,shifted);
                moved++;
                break;
            }
        }
        return moved;
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
            if(bag.gearManifestV141||bag.hasExtra()||bag.nutsV143>0||
               bagHasAmmoV143(bag)){
                out.append(",x");
                for(int i=0;i<bag.extra.length;i++)if(bag.extra[i]>0)
                    out.append('|').append(i).append(':').append(bag.extra[i]);
            }
            if(bagHasAmmoV143(bag)){
                out.append(",a");
                for(int i=0;i<bag.ammoExtraV143.length;i++)
                    if(bag.ammoExtraV143[i]>0)
                        out.append('|').append(i).append(':')
                            .append(bag.ammoExtraV143[i]);
            }
            if(bag.nutsV143>0)out.append(",n").append(bag.nutsV143);
        }
        return out.toString();
    }
    public void decode(String data){
        clear();if(data==null||data.isEmpty())return;
        for(String entry:data.split(";")){
            if(bags.size()>=MAX_BAGS)break;
            String[] p=entry.split(",");
            if(p.length!=ITEMS+3&&p.length!=ITEMS+6&&
               p.length!=ITEMS+7&&p.length!=ITEMS+8&&
               p.length!=ITEMS+9&&p.length!=ITEMS+10)continue;
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
                    if(p.length>=ITEMS+7){
                        int skin=Integer.parseInt(p[ITEMS+6]);
                        bag.skinV109=skin>=1&&skin<=200?skin:-1;
                    }
                    if(p.length>=ITEMS+8){
                        String[] entries=p[ITEMS+7].split("\\|",-1);
                        if(entries.length<1||!"x".equals(entries[0]))continue;
                        boolean valid=true;
                        for(int k=1;k<entries.length;k++){
                            String[] pair=entries[k].split(":",-1);
                            if(pair.length!=2){valid=false;break;}
                            int extraId=Integer.parseInt(pair[0]),n=Integer.parseInt(pair[1]);
                            if(extraId<0||extraId>=bag.extra.length||n<1||n>9999||
                               bag.extra[extraId]!=0){valid=false;break;}
                            bag.extra[extraId]=n;
                        }
                        if(!valid)continue;
                        bag.gearManifestV141=true;
                    }
                    if(p.length>=ITEMS+9){
                        // Versioned optional suffixes: ammo 'a' and wallet 'n'.
                        boolean seenAmmo=false,seenMoney=false;
                        for(int field=ITEMS+8;field<p.length;field++){
                            String value=p[field];
                            if(value.startsWith("a")&&!seenAmmo){
                                seenAmmo=true;
                                String[] entries=value.split("\\|",-1);
                                if(!"a".equals(entries[0])){invalid=true;break;}
                                for(int k=1;k<entries.length;k++){
                                    String[] parts=entries[k].split(":",-1);
                                    if(parts.length!=2){invalid=true;break;}
                                    int ammoIndex=Integer.parseInt(parts[0]),
                                        quantity=Integer.parseInt(parts[1]);
                                    if(ammoIndex<0||ammoIndex>=6||quantity<1||
                                       quantity>9999||bag.ammoExtraV143[ammoIndex]!=0){
                                        invalid=true;break;
                                    }
                                    bag.ammoExtraV143[ammoIndex]=quantity;
                                }
                            }else if(value.startsWith("n")&&!seenMoney){
                                seenMoney=true;
                                long amount=Long.parseLong(value.substring(1));
                                if(amount<1||amount>NutWalletV143.MAX){
                                    invalid=true;break;
                                }
                                bag.nutsV143=amount;
                            }else{invalid=true;break;}
                        }
                        if(invalid)continue;
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
