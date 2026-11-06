package com.survivalparadise.nativegame;
import java.util.HashSet;
public final class IndustrialFitV125Test {
    static void ok(boolean condition,String message){
        if(!condition)throw new AssertionError(message);
    }
    public static void main(String[] args){
        int n=0;
        for(int seed:new int[]{14901,1,-17,43,2026,981123}){
            for(int sy=-12;sy<=12;sy++)for(int sx=-12;sx<=12;sx++){
                IndustrialOpenWorldV124.Plot plot=IndustrialOpenWorldV124.plot(sx,sy,seed);
                if(!plot.enterable())continue;
                n++;
                float left=plot.buildingX-12, right=plot.buildingX+plot.buildingW+12;
                float top=plot.buildingY-22,bottom=plot.buildingY+plot.buildingH+24;
                ok(left>=plot.x+200 && right<=plot.x+1200,
                    "factory overlaps the street/curb at x");
                ok(top>=plot.y+187 && bottom<plot.y+990,
                    "factory overlaps street/curb at y");
                ok(!IndustrialOpenWorldV124.roadAt(plot.doorX,plot.doorY,seed),
                    "factory entrance drawn on roadway");
                ok(!IndustrialOpenWorldV124.blocked(
                    plot.doorX,plot.doorY+50,22,seed),"building entrance inaccessible");
                ok(!IndustrialOpenWorldV124.blocked(
                    plot.x+700,plot.y+1240,21,seed),"yard gate inaccessible");
                IndustrialWorldV123.District district=
                    IndustrialOpenWorldV124.nearestEntrance(plot.doorX,plot.doorY,100,seed);
                ok(district!=null&&district.sx==sx&&district.sy==sy,
                    "door mismatched to its seed-specific interior");
                ok(district.doorX==plot.doorX&&district.doorY==plot.doorY,
                    "visual doorway and activation do not align");
            }
            float[][] home=new float[5][];
            for(int i=0;i<5;i++){
                home[i]=IndustrialCampV125.home(i,seed);
                ok(IndustrialCampV125.clear(home[i][0],home[i][1],seed),
                   "camp NPC inside a wall, facade, rack or driveway");
                ok(IndustrialCampV125.patrolAllowed(
                    home[i][0],home[i][1],seed),"patrol disabled on valid anchor");
                for(int j=0;j<i;j++){
                    float dx=home[i][0]-home[j][0],dy=home[i][1]-home[j][1];
                    ok(dx*dx+dy*dy>70*70,"industrial roles overlap each other");
                }
            }
            ok(IndustrialCampV125.clear(IndustrialCampV125.FIRES[0][0],
                IndustrialCampV125.FIRES[0][1],seed),"campfire clips machine or wall");
        }
        System.out.println("PASS V125: "+n+
            " facade/road setbacks, doors, saved site ids; industrial NPC clearances");
    }
}
