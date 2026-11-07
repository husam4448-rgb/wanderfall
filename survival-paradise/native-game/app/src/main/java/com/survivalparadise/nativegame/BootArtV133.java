package com.survivalparadise.nativegame;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.RectF;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/** V133 approved toe-right boots: identical art across all animation frames.
 * Position/rotation comes from the user-approved V132 five-frame fitting JSON.
 * Left facing is mirrored by the calling character's Canvas.
 */
final class BootArtV133 {
    static final String[] NAMES={
        "Classic Brown","Combat Boots","Desert Boots","Reinforced Work Boots","Trail Boots"
    };
    private static final String[] FILES={
        "00_Classic_Brown.png","01_Combat.png","02_Desert.png",
        "03_Reinforced_Work.png","04_Trail.png"
    };
    static final int COUNT=FILES.length;
    static final int IMAGE_WIDTH=68,IMAGE_HEIGHT=52;
    // [idle,walk1,walk2,walk3,walk4][rear,front][x,y,clockwise_degrees]
    static final int[][][] FIT={
        {{40,242,0},{115,242,0}},
        {{38,239,6},{113,236,26}},
        {{38,239,18},{134,217,-45}},
        {{15,230,51},{120,242,-8}},
        {{23,236,39},{119,243,0}}
    };
    private final Bitmap[] sprites=new Bitmap[COUNT];
    private final Rect src=new Rect(0,0,IMAGE_WIDTH,IMAGE_HEIGHT);
    private final RectF dst=new RectF();

    BootArtV133(Context context) throws IOException {
        try(InputStream input=context.getAssets().open("sp_v133_boots.zip");
            ZipInputStream zip=new ZipInputStream(input)){
            ZipEntry entry;
            while((entry=zip.getNextEntry())!=null){
                if(entry.isDirectory())continue;
                int index=-1;
                for(int i=0;i<COUNT;i++)if(FILES[i].equals(entry.getName())){index=i;break;}
                if(index<0)continue;
                ByteArrayOutputStream buffer=new ByteArrayOutputStream();
                byte[] bytes=new byte[4096];int n;
                while((n=zip.read(bytes))!=-1)buffer.write(bytes,0,n);
                byte[] data=buffer.toByteArray();
                Bitmap bitmap=BitmapFactory.decodeByteArray(data,0,data.length);
                if(bitmap==null||bitmap.getWidth()!=IMAGE_WIDTH||bitmap.getHeight()!=IMAGE_HEIGHT)
                    throw new IOException("Invalid V133 boot: "+entry.getName());
                sprites[index]=bitmap;
            }
        }
        for(int i=0;i<COUNT;i++)if(sprites[i]==null)
            throw new IOException("Missing V133 boot style "+FILES[i]);
    }
    static int clampStyle(int v){return Math.max(0,Math.min(COUNT-1,v));}
    void draw(Canvas canvas,int frame,int style,float left,float top,float unit,Paint pixels){
        Bitmap bitmap=sprites[clampStyle(style)];
        int f=Math.max(0,Math.min(4,frame));
        for(int foot=0;foot<2;foot++){
            int[] pos=FIT[f][foot];
            float cx=left+(pos[0]+IMAGE_WIDTH*.5f)*unit;
            float cy=top+(pos[1]+IMAGE_HEIGHT*.5f)*unit;
            canvas.save();
            canvas.translate(cx,cy);
            canvas.rotate(pos[2]);
            dst.set(-IMAGE_WIDTH*.5f*unit,-IMAGE_HEIGHT*.5f*unit,
                IMAGE_WIDTH*.5f*unit,IMAGE_HEIGHT*.5f*unit);
            canvas.drawBitmap(bitmap,src,dst,pixels);
            canvas.restore();
        }
    }
}
