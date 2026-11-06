package com.survivalparadise.nativegame;
import java.util.HashSet;
public final class IndustrialOpenWorldV124Test {
    static void check(boolean value,String reason){if(!value)throw new AssertionError(reason);}
    public static void main(String[] args){
        int seed=14901;
        int built=0,empty=0,yards=0,major=0,minor=0;
        HashSet<Integer> family=new HashSet<>();
        HashSet<String> footprints=new HashSet<>();
        for(int y=-20;y<=20;y++)for(int x=-20;x<=20;x++){
            IndustrialOpenWorldV124.Plot p=IndustrialOpenWorldV124.plot(x,y,seed);
            IndustrialOpenWorldV124.Plot q=IndustrialOpenWorldV124.plot(x,y,seed);
            check(p.kind==q.kind&&p.type==q.type&&p.gateSide==q.gateSide,
                "nondeterministic district");
            check(p.x==q.x&&p.y==q.y&&p.doorX==q.doorX,"nondeterministic geometry");
            check(!IndustrialOpenWorldV124.roadAt(p.doorX,p.doorY,seed),
                "entrance unexpectedly on public road");
            family.add(p.kind);
            if(p.type==IndustrialOpenWorldV124.FACILITY){
                built++;footprints.add((int)p.buildingW+":"+(int)p.buildingH);
                check(IndustrialOpenWorldV124.nearestEntrance(
                    p.doorX,p.doorY,110,seed)!=null,"portal missing");
                check(IndustrialOpenWorldV124.blocked(
                    p.buildingX+120,p.buildingY+120,16,seed),"roof not solid");
                check(!IndustrialOpenWorldV124.blocked(
                    p.doorX,p.doorY+55,18,seed),"entrance blocked");
            }else if(p.type==IndustrialOpenWorldV124.YARD)yards++;
            else empty++;
            if(p.developed()){
                check(p.gateSide>=0,"site without road access");
                check(!IndustrialOpenWorldV124.blocked(
                    p.x+558,p.y+1240,18,seed),"yard gate blocked");
            }
            if(IndustrialOpenWorldV124.horizontal(y,x,seed))
                check(IndustrialOpenWorldV124.roadAt(
                    p.x+650,p.y,seed),"horizontal road discontinuity");
            if(IndustrialOpenWorldV124.vertical(x,y,seed))
                check(IndustrialOpenWorldV124.roadAt(
                    p.x,p.y+650,seed),"vertical road discontinuity");
            if(Math.floorMod(y,4)==0){
                major++;
                check(IndustrialOpenWorldV124.horizontal(y,x,seed),"missing arterial H");
            }
            if(Math.floorMod(x,4)==0)
                check(IndustrialOpenWorldV124.vertical(x,y,seed),"missing arterial V");
            else if(IndustrialOpenWorldV124.vertical(x,y,seed))minor++;
            if(y%4!=0 && y%4!=3){
                // All road segments within an arterial cell band agree.
                check(IndustrialOpenWorldV124.vertical(x,y,seed)==
                    IndustrialOpenWorldV124.vertical(x,y+1,seed),
                    "minor street disconnected inside superblock");
            }
        }
        check(built>550&&yards>150&&empty>100,"incorrect land-use distribution");
        check(family.size()==8&&footprints.size()>=4,"district variety");
        check(IndustrialOpenWorldV124.sx(-0.01f)==-1,"negative x sectors");
        check(IndustrialOpenWorldV124.sy(-1400.1f)==-2,"negative y sectors");
        check(IndustrialOpenWorldV124.plot(8,8,seed).kind!=
              IndustrialOpenWorldV124.plot(8,8,seed+17).kind,
              "seeds fail to change district");
        check(IndustrialOpenWorldV124.plot(0,0,seed).enterable(),"start site not enterable");
        System.out.println("PASS V124 industrial open world: facilities="+built+" depots="+yards+
            " vacant="+empty+" road segments="+major+" minor="+minor+
            " kinds="+family.size()+" footprints="+footprints.size());
    }
}
