package com.survivalparadise.nativegame;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.drawable.Drawable;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * Approved legacy inventory icons loaded from the user's exact V145 PNGs.
 * V92 kind values 6..14 are 3 torsos, 3 trousers and 3 boots.
 * Head-equipment inventory icons (kinds 3..5) stay intact and never affect
 * character rendering. The old V95 geometric icons remain as safe fallback.
 */
final class ApprovedLegacyIconsV145 {
    private ApprovedLegacyIconsV145() {}
    private static final String ZIP="sp_v145_legacy_equipment.zip";
    private static final String[] FILES={
        "torsos/20_canvas_work_jacket.png",
        "torsos/21_weatherproof_field_coat.png",
        "torsos/22_plate_carrier.png",
        "pants/20_cargo_trousers.png",
        "pants/21_ripstop_trousers.png",
        "pants/22_tactical_trousers.png",
        "boots/05_steel_toe_work_boots.png",
        "boots/06_trail_boots.png",
        "boots/07_tactical_combat_boots.png"
    };
    private static final Bitmap[] ART=new Bitmap[9];
    private static boolean attempted=false;
    static synchronized Drawable drawable(Context context,int kind,int dp){
        if(kind<6||kind>14)return null;
        if(!attempted)load(context);
        Bitmap original=ART[kind-6];
        return ApprovedOutfitArtV139.makeOriginalIcon(context,original,dp);
    }
    private static void load(Context context){
        attempted=true;
        try(InputStream input=context.getAssets().open(ZIP);
            ZipInputStream zip=new ZipInputStream(input)){
            ZipEntry entry;
            while((entry=zip.getNextEntry())!=null){
                if(entry.isDirectory())continue;
                int id=-1;
                for(int i=0;i<FILES.length;i++)
                    if(FILES[i].equals(entry.getName())){id=i;break;}
                if(id<0)continue;
                ByteArrayOutputStream buffer=new ByteArrayOutputStream();
                byte[] chunk=new byte[4096];
                int n;
                while((n=zip.read(chunk))!=-1)buffer.write(chunk,0,n);
                byte[] data=buffer.toByteArray();
                Bitmap bitmap=BitmapFactory.decodeByteArray(data,0,data.length);
                if(bitmap!=null)ART[id]=bitmap;
            }
        }catch(IOException ignored){
            // V95 legacy icons remain available if archive is missing.
        }
    }
}
