package com.survivalparadise.nativegame;

import android.graphics.Canvas;
import android.graphics.Paint;

/**
 * Reuses the original authored V165 material pigments for true world-space
 * indoor floors, not the six mono-color prototype rooms. Each V163 room keeps
 * its actual unique polygon-free bounding region and all door geometry.
 */
public final class InteriorMaterialV166 {
    private InteriorMaterialV166(){}
    private static final int[] TINT={
        0x225a402a, // apartment: old oak
        0x203d5d69, // offices: slate blue
        0x1d81775a, // supermarket: worn linoleum
        0x26765b51, // hotel: old warm carpeting
        0x1a7e826f, // school: green-grey tile
        0x253e4e4e, // factory: oil and concrete
        0x27554e42, // warehouse: gritty freight floor
        0x266b5139  // residence: old brown timber
    };
    public static int material(int theme,int room){
        switch(theme){
            case NeighborhoodV154.FACTORY:
            case NeighborhoodV154.WAREHOUSE:
                return SurfaceArtV165.CONCRETE;
            case NeighborhoodV154.OFFICES:
            case NeighborhoodV154.SCHOOL:
            case NeighborhoodV154.MARKET:
                return room%3==0?SurfaceArtV165.CONCRETE:
                    SurfaceArtV165.AGED_PAVEMENT;
            default:return room%5==4?SurfaceArtV165.CONCRETE:
                SurfaceArtV165.AGED_PAVEMENT;
        }
    }
    public static void floor(Canvas c,Paint p,NeighborhoodInteriorV161 room){
        // Underlying aged floor continuity in the actual 1600x1120 V163 map.
        p.setColor(0xff343a37);p.setStyle(Paint.Style.FILL);
        c.drawRect(23f,23f,1577f,1095f,p);
        SurfaceArtV165.rect(c,23f,23f,1554f,1072f,
            SurfaceArtV165.AGED_PAVEMENT,137f,255);
        float scale=ClinicInteriorV89.EXPANSION_V90;
        for(int z=0;z<room.layoutV163.rooms.length;z++){
            float[] b=room.layoutV163.rooms[z];
            float x=b[0]/scale,y=b[1]/scale,
                w=b[2]/scale,h=b[3]/scale;
            if(w<10f||h<10f)continue;
            c.save();
            c.clipRect(x+2,y+2,x+w-2,y+h-2);
            SurfaceArtV165.rect(c,x+2,y+2,w-4,h-4,
                material(room.theme,z),117f+(room.variation%4)*12f,255);
            // Tint affects material, never creates a recognizable placeholder
            // slab. A second subtle real pigment provides local damage.
            int tint=TINT[room.theme];
            p.setStyle(Paint.Style.FILL);p.setColor(tint);
            c.drawRect(x+2,y+2,x+w-2,y+h-2,p);
            for(int i=0;i<4;i++){
                int hash=IndustrialWorldV123.hash(
                    room.building.tileX*41+z*13+i*37,
                    room.building.tileY*29+room.variation+i*19,room.seed);
                float xx=x+45f+Math.floorMod(hash,Math.max(1,(int)w-90));
                float yy=y+37f+Math.floorMod(hash>>>9,Math.max(1,(int)h-74));
                NaturalBrushArtV1652.stamp(c,
                    i%3==0?NaturalGroundV157.DRY:NaturalGroundV157.DIRT,
                    xx,yy,80f+Math.floorMod(hash>>>16,99),
                    45f+Math.floorMod(hash>>>23,70),
                    hash,room.theme==NeighborhoodV154.FACTORY?42:23);
            }
            c.restore();
        }
    }
}
