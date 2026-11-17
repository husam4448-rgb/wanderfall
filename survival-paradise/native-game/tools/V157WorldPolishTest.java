package com.survivalparadise.nativegame;

/** Source-only terrain, building solidity, swept movement and clutter mask QA. */
public final class V157WorldPolishTest {
    private static void yes(boolean v,String error){
        if(!v)throw new AssertionError(error);
    }
    public static void main(String[] args){
        int seed=14901;
        for(ExpeditionSitesV88.Site s:ExpeditionSitesV88.SITES){
            float doorY=s.y+ExteriorFootprintV130.anchor(s);
            float left=s.x-ExteriorFootprintV130.width(s);
            float right=s.x+ExteriorFootprintV130.width(s);
            float top=doorY-ExteriorFootprintV130.height(s);
            // All four cardinal directions and the front center are solid.
            yes(ExteriorFootprintV130.blocked(s,s.x,doorY-50f,10f),
                "front door can be walked through "+s.name);
            yes(ExteriorFootprintV130.blocked(s,left+10f,doorY-380f,8f),
                "west wall can be walked through "+s.name);
            yes(ExteriorFootprintV130.blocked(s,right-10f,doorY-380f,8f),
                "east wall can be walked through "+s.name);
            yes(ExteriorFootprintV130.blocked(s,s.x,top+10f,8f),
                "north wall can be walked through "+s.name);
            yes(!ExteriorFootprintV130.blocked(s,s.x,doorY+42f,20f),
                "outside scene-transition entrance blocked "+s.name);
            yes(WorldBuildingV157.sceneryBlocked(s.x,doorY-500f,45f,seed),
                "clutter may be painted on roof "+s.name);
            yes(!SweptWorldCollisionV157.clear(
                (x,y,r)->ExteriorFootprintV130.blocked(s,x,y,r),
                s.x,doorY+65f,s.x,doorY-600f,16f),
                "fast player tunneling through building "+s.name);
        }
        int count=0;
        boolean[] variants=new boolean[NeighborhoodV154.TYPES];
        for(int y=-4;y<=4;y++)for(int x=-4;x<=4;x++)
            for(int slot=0;slot<NeighborhoodV154.COLS*NeighborhoodV154.ROWS;slot++){
                NeighborhoodV154.Building b=NeighborhoodV154.get(x,y,slot);
                if(b==null)continue;
                count++;variants[b.kind]=true;
                float cx=b.left+b.width*.5f,cy=b.top+b.height*.5f;
                yes(b.blocked(cx,cy,12f),"empty neighborhood walls");
                yes(WorldBuildingV157.sceneryBlocked(cx,cy,30f,seed),
                    "neighborhood clutter projected through facade");
                yes(!SweptWorldCollisionV157.clear(
                    NeighborhoodV154::blocked,
                    b.left-100f,cy,b.right()+100f,cy,18f),
                    "raider tunneling across city walls");
            }
        yes(count>175,"fewer than 175 buildings in 9x9 districts: "+count);
        for(int i=0;i<variants.length;i++)yes(variants[i],"missing district type "+i);
        // Source-only rendering model: patches are not axis-aligned repeating
        // tiles; all parameter values stay stable between reloads.
        int organic=0,dirt=0,grass=0;
        for(int y=-7;y<=7;y++)for(int x=-7;x<=7;x++)
            for(int slot=0;slot<NaturalGroundV157.PER_CELL;slot++){
                NaturalGroundV157.Patch a=NaturalGroundV157.patch(x,y,slot);
                NaturalGroundV157.Patch b=NaturalGroundV157.patch(x,y,slot);
                yes(a.x==b.x&&a.y==b.y&&a.rx==b.rx&&a.ry==b.ry&&
                    a.kind==b.kind&&a.variation==b.variation,
                    "ground rerolled when chunk unloaded");
                yes(a.rx>=86f&&a.ry>=57f&&a.rotation>=0f,
                    "terrain patch scale invalid");
                float first=NaturalGroundV157.wobble(a,0);
                boolean varies=false;
                for(int v=1;v<14;v++)
                    if(Math.abs(first-NaturalGroundV157.wobble(a,v))>.04f)
                        varies=true;
                yes(varies,"polygon looks like an artificial oval grid");
                organic++;if(a.kind==NaturalGroundV157.DIRT)dirt++;
                if(a.kind==NaturalGroundV157.GRASS)grass++;
            }
        yes(organic>500&&dirt>50&&grass>50,
            "organic terrain lacks visible dirt/grass diversity");
        SweptWorldCollisionV157.Test thinWall=
            (x,y,r)->Math.abs(x)<=9f+r&&Math.abs(y)<60f;
        yes(!SweptWorldCollisionV157.clear(
            thinWall,-90f,0f,90f,0f,12f),
            "thin wall tunneled through under high delta time");
        yes(SweptWorldCollisionV157.clear(
            thinWall,-90f,90f,90f,90f,12f),
            "invisible collision on clear outdoor route");
        yes(!WorldBuildingV157.sceneryBlocked(1080f,710f,12f,seed),
            "starting camp became solid");
        System.out.println("PASS V157: "+ExpeditionSitesV88.SITES.length+
            " four-sided landmarks; "+count+" solid neighborhood blocks; "+
            organic+" deterministic organic ground patches; masked clutter, "+
            "swept player/NPC movement and preserved outdoor interaction landing");
    }
}
