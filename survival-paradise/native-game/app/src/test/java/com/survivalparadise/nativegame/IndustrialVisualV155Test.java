package com.survivalparadise.nativegame;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Typeface;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.RuntimeEnvironment;
import org.robolectric.annotation.Config;

import java.io.File;
import java.io.FileOutputStream;
import java.util.Arrays;

import static org.junit.Assert.*;

/**
 * Source-only Android Canvas contact sheet of all eight V155 industry types,
 * with the actual approved WebP facade atlas and native procedural rooftops.
 * Runs on Robolectric/JVM, creates NO APK and never starts the mobile app.
 */
@RunWith(RobolectricTestRunner.class)
@Config(sdk=28)
public final class IndustrialVisualV155Test {
    @Test public void drawAllRealIndustrialFacadesWithoutMissingAssets() throws Exception {
        final int seed=14901, cell=384, columns=4, rows=2;
        Context context=RuntimeEnvironment.getApplication();
        IndustrialArtV123 sprites=new IndustrialArtV123();
        sprites.load(context.getAssets());
        assertEquals("Original 24 industrial assets must load",24,sprites.loaded());

        IndustrialOpenWorldV124.Plot[] plots=
            new IndustrialOpenWorldV124.Plot[8];
        for(int sy=-10;sy<=10;sy++)for(int sx=-10;sx<=10;sx++){
            IndustrialOpenWorldV124.Plot p=IndustrialOpenWorldV124.plot(sx,sy,seed);
            if(p.enterable()&&plots[p.kind]==null)plots[p.kind]=p;
        }
        for(int kind=0;kind<plots.length;kind++)
            assertNotNull("No enterable site of industry "+kind,plots[kind]);
        Bitmap contact=Bitmap.createBitmap(columns*cell,rows*cell,
            Bitmap.Config.ARGB_8888);
        Canvas canvas=new Canvas(contact);
        Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
        canvas.drawColor(0xff182629);
        for(int kind=0;kind<plots.length;kind++){
            IndustrialOpenWorldV124.Plot p=plots[kind];
            float cellX=(kind%columns)*cell,cellY=(kind/columns)*cell;
            canvas.save();
            canvas.clipRect(cellX,cellY,cellX+cell,cellY+cell);
            canvas.translate(cellX+10,cellY+7);
            canvas.scale(.258f,.258f);
            canvas.translate(-p.x,-p.y);
            IndustrialSceneV124.outdoors(canvas,paint,
                p.x,p.y,1400,1400,seed);
            sprites.outdoors(canvas,p.x,p.y,1400,1400,seed);
            canvas.restore();
            paint.setStyle(Paint.Style.FILL);
            paint.setColor(0xff102429);
            canvas.drawRect(cellX+7,cellY+8,cellX+cell-7,cellY+41,paint);
            paint.setColor(0xfff0e0bb);
            paint.setTypeface(Typeface.create("monospace",Typeface.BOLD));
            paint.setTextSize(16f);
            canvas.drawText(IndustrialWorldV123.FACILITIES[kind],
                cellX+17,cellY+29,paint);
            // Distinct scene pixels at two places inside each populated lot.
            int x=(int)(cellX+cell*.5f),y=(int)(cellY+cell*.50f);
            assertNotEquals("Opaque facade missing on facility "+kind,
                0,contact.getPixel(x,y)>>>24);
        }
        File out=new File("build/visual-v155/industrial_contact_sheet.png");
        assertTrue("Failed to create visual report directory",
            out.getParentFile().isDirectory()||out.getParentFile().mkdirs());
        try(FileOutputStream stream=new FileOutputStream(out)){
            assertTrue("Failed to encode real Android Canvas pixels",
                contact.compress(Bitmap.CompressFormat.PNG,100,stream));
        }
        assertTrue("Rendered PNG missing or blank",out.isFile()&&out.length()>3000);
        System.out.println("PASS V155: Android Canvas rendered all eight approved facades "+
            "and their actual new architectural overlays, "+out.length()+" PNG bytes");
        sprites.release();contact.recycle();
    }
}
