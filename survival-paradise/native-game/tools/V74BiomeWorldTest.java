package com.survivalparadise.nativegame;

public final class V74BiomeWorldTest {
    static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
    static int diff(int a,int b){
        return Math.abs(((a>>16)&255)-((b>>16)&255))+
               Math.abs(((a>>8)&255)-((b>>8)&255))+
               Math.abs((a&255)-(b&255));
    }
    public static void main(String[]args){
        int[] found=new int[6];
        final int base=0xff53664b;
        check(BiomeWorldV74.tint(1080,710,base,1080,710)==base,"V73 spawn color changed");
        int n=0,changed=0;
        for(int y=-64000;y<=64000;y+=1152)for(int x=-64000;x<=64000;x+=1152){
            int type=BiomeWorldV74.biome(x,y);
            check(type>=0&&type<6,"biome index");
            found[type]++;
            int h=WorldChunkModel.hash(x/72,y/72);
            int prop=BiomeWorldV74.prop(x,y,h);
            check(prop>=0&&prop<7,"sprite atlas index");
            check(prop==BiomeWorldV74.prop(x,y,h),"revisit changed prop");
            int tint=BiomeWorldV74.tint(x,y,base,1080,710);
            check(tint>>>24==255,"opaque terrain");
            if(tint!=base)changed++;
            int a=WorldChunkModel.groundColorAt(x-.05f,y,1080,710);
            int b=WorldChunkModel.groundColorAt(x+.05f,y,1080,710);
            check(diff(a,b)<=4,"tile seam discontinuity");
            n++;
        }
        for(int i=0;i<6;i++)check(found[i]>0,"missing biome "+i);
        check(changed>n/2,"environment color not integrated");
        check(WorldChunkModel.tileDetail(-11,33)==WorldChunkModel.hash(-11,33),
              "V73 terrain hash changed");
        System.out.println("V74 PASS "+n+" samples / six biomes / seven props / locked hub");
    }
}
