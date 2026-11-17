package com.survivalparadise.nativegame;

/**
 * V157 single outdoor building-exclusion contract for natural props, harvest
 * props, salvage, generated pickups, and stationary scenery. This does NOT
 * delete resources or mutate their saved world IDs: a structure merely masks
 * inaccessible pickups until they are no longer inside its masonry.
 *
 * Player, raider and companion motion uses the same fixed-site/neighborhood
 * geometry through GameView.blocked(). Interactive entrances remain outside.
 */
public final class WorldBuildingV157 {
    private WorldBuildingV157(){}
    /** Fast pure-Java test of whether a visual prop would intersect a roof. */
    public static boolean sceneryBlocked(float x,float y,float radius,int industrialSeed){
        if(!Float.isFinite(x)||!Float.isFinite(y))return false;
        float r=Math.max(0f,radius);
        if(NeighborhoodV154.blocked(x,y,r+9f))return true;
        for(ExpeditionSitesV88.Site site:ExpeditionSitesV88.SITES)
            if(ExteriorFootprintV130.blocked(site,x,y,r+9f))return true;
        // Stitched factory buildings and the solid machinery/fence are already
        // traced against the same approved artwork as movement collision.
        if(IndustrialBiomeBridgeV128.bounds(x,y)&&
           IndustrialBiomeBridgeV128.blocked(x,y,r,industrialSeed))
            return true;
        return false;
    }
    /** Check a whole visible object, not only its anchor at ground level. */
    public static boolean sceneryRectBlocked(float left,float top,
                                             float right,float bottom,
                                             int industrialSeed){
        float x=(left+right)*.5f,y=(top+bottom)*.5f;
        float halfW=(right-left)*.5f,halfH=(bottom-top)*.5f;
        // Conservative circumscribed circle means clipped canopies/vehicles
        // disappear before they can overpaint a large roof. Dirt is unaffected.
        return sceneryBlocked(x,y,(float)Math.hypot(halfW,halfH),industrialSeed);
    }
}
