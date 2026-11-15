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
    // V144 extended silhouettes remain source-locked to original V133 FIT.
    private final Bitmap[] legacySpritesV144=new Bitmap[3];
    private final int[] legacyBaseV144={3,4,1};
    private Bitmap socksV141;
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
        loadLegacyBootsV144(context);
        socksV141=makeSocksV141(sprites[0]);
    }
    /** Short ankle socks follow the exact same approved five-frame foot anchors.
     * The original boots and PNG pixel data are never modified.
     */
    private static Bitmap makeSocksV141(Bitmap original){
        int w=original.getWidth(),h=original.getHeight();
        int[] rgba=new int[w*h],out=new int[w*h];
        original.getPixels(rgba,0,w,0,0,w,h);
        for(int y=0;y<h;y++)for(int x=0;x<w;x++){
            int i=y*w+x;
            if(y<h*.38f||(rgba[i]>>>24)<128)continue;
            boolean border=false;
            for(int yy=-1;yy<=1&&!border;yy++)for(int xx=-1;xx<=1;xx++){
                int nx=x+xx,ny=y+yy;
                if(nx<0||ny<0||nx>=w||ny>=h||
                   ny<h*.38f||(rgba[ny*w+nx]>>>24)<128){
                    border=true;break;
                }
            }
            out[i]=border?0xff15191c:
                y>h*.85f?0xff687987:
                x>w*.64f?0xffd0d2c5:0xffadb7b1;
        }
        return Bitmap.createBitmap(out,w,h,Bitmap.Config.ARGB_8888);
    }
    private void loadLegacyBootsV144(Context context){
        try(InputStream file=context.getAssets().open("sp_v145_legacy_equipment.zip");
                ZipInputStream zip=new ZipInputStream(file)){
            ZipEntry entry;
            while((entry=zip.getNextEntry())!=null){
                String name=entry.getName();
                if(!name.startsWith("boots/")||!name.endsWith(".png"))continue;
                int i;
                try{i=Integer.parseInt(name.substring(6,8))-5;}
                catch(RuntimeException ignored){continue;}
                if(i<0||i>=3)continue;
                ByteArrayOutputStream bytes=new ByteArrayOutputStream();
                byte[] chunk=new byte[4096];int n;
                while((n=zip.read(chunk))!=-1)bytes.write(chunk,0,n);
                byte[] data=bytes.toByteArray();
                Bitmap bmp=BitmapFactory.decodeByteArray(data,0,data.length);
                if(!validBootCanvasV145(bmp)){
                    java.util.Arrays.fill(legacySpritesV144,null);
                    return;
                }
                legacySpritesV144[i]=bmp;
            }
        }catch(IOException ignored){java.util.Arrays.fill(legacySpritesV144,null);}
        for(Bitmap bmp:legacySpritesV144)if(bmp==null){
            java.util.Arrays.fill(legacySpritesV144,null);return;
        }
    }
    /** User originals have different detailed contours but exactly the V133 canvas. */
    private static boolean validBootCanvasV145(Bitmap bmp){
        if(bmp==null||bmp.getWidth()!=IMAGE_WIDTH||
                bmp.getHeight()!=IMAGE_HEIGHT)return false;
        int[] rgba=new int[IMAGE_WIDTH*IMAGE_HEIGHT];
        bmp.getPixels(rgba,0,IMAGE_WIDTH,0,0,IMAGE_WIDTH,IMAGE_HEIGHT);
        int visible=0;
        for(int pixel:rgba)if((pixel>>>24)>127)visible++;
        return visible>IMAGE_WIDTH*IMAGE_HEIGHT/6;
    }
    static int clampStyle(int v){return Math.max(0,Math.min(COUNT+2,v));}
    private Bitmap spriteV144(int style){
        if(style<0)return socksV141;
        if(style<COUNT)return sprites[clampStyle(style)];
        int id=style-COUNT;
        if(id<0||id>2)return sprites[0];
        return legacySpritesV144[id]!=null?legacySpritesV144[id]:
            sprites[legacyBaseV144[id]];
    }
    android.graphics.drawable.Drawable inventoryIcon(Context context,int style,int dp){
        return ApprovedOutfitArtV139.makeOriginalIcon(context,
            spriteV144(style),dp);
    }
    void draw(Canvas canvas,int frame,int style,float left,float top,float unit,Paint pixels){
        Bitmap bitmap=spriteV144(style);
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
