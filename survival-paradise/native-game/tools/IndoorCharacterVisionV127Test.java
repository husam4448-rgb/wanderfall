package com.survivalparadise.nativegame;
public final class IndoorCharacterVisionV127Test {
    private static void ok(boolean good,String why){
        if(!good)throw new AssertionError(why);
    }
    private static class OpenRoom extends ClinicInteriorV89 {
        @Override public boolean blocked(float x,float y,float r){return false;}
    }
    private static final class WallRoom extends OpenRoom {
        @Override public boolean blocked(float x,float y,float r){
            return x+r>520&&x-r<550&&y+r>200&&y-r<600;
        }
    }
    private static boolean see(ClinicInteriorV89 map,float x,float feet){
        return IndoorCharacterVisionV127.visible(new ClinicVisionV90(),
            map,400f,400f,1f,0f,x,feet);
    }
    public static void main(String[] args){
        ClinicInteriorV89 open=new OpenRoom(),wall=new WallRoom();
        ok(see(open,650,460),"actor in cone should be visible");
        ok(see(open,453,440),"nearby actor should remain visible");
        ok(!see(open,180,460),"actor behind player visible outside cone");
        ok(!see(open,400,780),"actor far to the side visible outside cone");
        ok(!see(open,1300,460),"actor beyond range should not be visible");
        ok(!see(wall,650,460),"actor behind industrial wall must be occluded");
        ok(see(wall,460,460),"actor in front of wall should be visible");
        ClinicVisionV90 cone=new ClinicVisionV90();
        cone.trace(400f,400f,1f,0f,wall);
        ok(cone.blockedRays>0,"vision rays must respect building walls");
        // Rotation should rotate actor visibility; no horizontal-only NPC view.
        ok(IndoorCharacterVisionV127.visible(cone,open,
            400f,400f,0f,-1f,400f,220f),"north-facing FOV missing");
        ok(!IndoorCharacterVisionV127.visible(cone,open,
            400f,400f,0f,-1f,650f,460f),"north view leaks east NPC");
        System.out.println("PASS V127: indoor NPC/companion angular FOV, range, near vision, wall occlusion and heading");
    }
}
