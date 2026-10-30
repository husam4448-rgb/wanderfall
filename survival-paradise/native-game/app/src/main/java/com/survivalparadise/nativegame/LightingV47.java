package com.survivalparadise.nativegame;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RadialGradient;
import android.graphics.RectF;
import android.graphics.Shader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * V47 occlusion-aware software lightmap: opaque darkness everywhere except
 * actual world-space point lights and occlusion-tested hand flashlight cones.
 * The mask is composited AFTER every scene/character/weapon sprite and BEFORE
 * the HUD, preventing sprites from glowing in isolation.
 *
 * V45's DST_OUT + bitmap shader path is deliberately not used: it can render
 * differently on OEM accelerated canvases. V46 explicitly calculates every
 * output pixel's alpha and uploads an ARGB_8888 bitmap without Xfermodes.
 */
public final class LightingV47 {
    public static final int WARM=0xffffb05b, NEON_BLUE=0xff61ddf6, NEON_PINK=0xffef75ec;
    private static final int DARK_RGB=0x00101a23;
    private final Paint mapPaint=new Paint(Paint.FILTER_BITMAP_FLAG);
    private final Paint tintPaint=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final ArrayList<Point> points=new ArrayList<>();
    private final ArrayList<Beam> beams=new ArrayList<>();
    private final ArrayList<ShadowGeometryV47.Blocker> blockers=new ArrayList<>();
    private ShadowGeometryV47.Blocker[] activeBlockers=new ShadowGeometryV47.Blocker[0];
    private int activeCount;
    private Bitmap tintBitmap;
    private int[] tintPixels;
    private final Paint tintMapPaint=new Paint(Paint.FILTER_BITMAP_FLAG);
    private Bitmap bitmap;
    private int[] pixels;
    private int width,height;
    private float resolutionFactor=1f;
    private final RectF screenDst=new RectF();
    /** A larger factor saves per-pixel occlusion work on low-end Android devices. */
    public void setPixelScale(float factor){
        resolutionFactor=Math.max(.85f,Math.min(2.5f,factor));
    }
    public int pixelCount(){return width*height;}
    private float left,top,screenWidth,screenHeight,stepX,stepY;
    private int darkness;

    private static final class Point {
        final float x,y,radius,power; final int color;
        Point(float x,float y,float radius,float power,int color){
            this.x=x;this.y=y;this.radius=radius;this.power=power;this.color=color;
        }
    }
    private static final class Beam {
        final float x,y,dx,dy,reach;
        Beam(float x,float y,float dx,float dy,float reach){
            this.x=x;this.y=y;float norm=Math.max(.0001f,(float)Math.hypot(dx,dy));
            this.dx=dx/norm;this.dy=dy/norm;this.reach=reach;
        }
    }
    public void clear(){points.clear();beams.clear();blockers.clear();}
    public void occludeRect(float x0,float y0,float x1,float y1){
        if(x1>x0&&y1>y0)blockers.add(new ShadowGeometryV47.Blocker(x0,y0,x1,y1));
    }
    private void prepareBlockers(float srcX,float srcY,float radius){
        activeCount=0;
        if(activeBlockers.length<blockers.size())
            activeBlockers=new ShadowGeometryV47.Blocker[blockers.size()+16];
        for(ShadowGeometryV47.Blocker b:blockers){
            float dx=Math.max(b.left-srcX,Math.max(0f,srcX-b.right));
            float dy=Math.max(b.top-srcY,Math.max(0f,srcY-b.bottom));
            if(dx*dx+dy*dy<=radius*radius)activeBlockers[activeCount++]=b;
        }
    }
    private boolean shadowed(float sx,float sy,float x,float y){
        return ShadowGeometryV47.blocksAny(activeBlockers,activeCount,sx,sy,x,y);
    }
    public void point(float x,float y,float radius,float power,int color){
        if(radius>1&&power>0)points.add(new Point(x,y,radius,Math.min(1,power),color));
    }
    public void flashlight(float x,float y,float dx,float dy,float reach){
        if(reach>0)beams.add(new Beam(x,y,dx,dy,reach));
    }
    public int sourceCount(){return points.size()+beams.size();}

    private void ensure(float w,float h){
        int minWidth=Math.max(96,Math.round(180f/resolutionFactor));
        int maxWidth=Math.max(minWidth,Math.round(440f/resolutionFactor));
        int minHeight=Math.max(66,Math.round(110f/resolutionFactor));
        int maxHeight=Math.max(minHeight,Math.round(280f/resolutionFactor));
        int newWidth=Math.max(minWidth,Math.min(maxWidth,Math.round(w/(3.3f*resolutionFactor))));
        int newHeight=Math.max(minHeight,Math.min(maxHeight,Math.round(h*newWidth/Math.max(1f,w))));
        if(bitmap!=null&&width==newWidth&&height==newHeight)return;
        if(bitmap!=null)bitmap.recycle();
        if(tintBitmap!=null)tintBitmap.recycle();
        width=newWidth;height=newHeight;
        bitmap=Bitmap.createBitmap(width,height,Bitmap.Config.ARGB_8888);
        tintBitmap=Bitmap.createBitmap(width,height,Bitmap.Config.ARGB_8888);
        pixels=new int[width*height];
        tintPixels=new int[width*height];
    }
    private void uncover(int i,float amount){
        int oldAlpha=pixels[i]>>>24;
        int alpha=LightMathV46.shadowAlpha(darkness,amount);
        if(alpha<oldAlpha)pixels[i]=(alpha<<24)|DARK_RGB;
    }
    private void tint(int index,float strength,int color){
        int a=Math.round(38*strength);
        if(a<=0)return;
        int previous=tintPixels[index]>>>24;
        if(a<=previous)return;
        tintPixels[index]=(a<<24)|(color&0x00ffffff);
    }
    private int ix(float x){return (int)Math.floor((x-left)/stepX);}
    private int iy(float y){return (int)Math.floor((y-top)/stepY);}
    private void pointMask(Point light){
        prepareBlockers(light.x,light.y,light.radius);
        int minX=Math.max(0,ix(light.x-light.radius));
        int maxX=Math.min(width-1,ix(light.x+light.radius)+1);
        int minY=Math.max(0,iy(light.y-light.radius));
        int maxY=Math.min(height-1,iy(light.y+light.radius)+1);
        float r2=light.radius*light.radius;
        for(int y=minY;y<=maxY;y++){
            float dy=top+(y+.5f)*stepY-light.y;
            for(int x=minX;x<=maxX;x++){
                float dx=left+(x+.5f)*stepX-light.x;
                float d2=dx*dx+dy*dy;
                if(d2>=r2)continue;
                float px=left+(x+.5f)*stepX,py=top+(y+.5f)*stepY;
                if(activeCount>0&&shadowed(light.x,light.y,px,py))continue;
                float strength=LightMathV46.pointStrength(dx,dy,light.radius,light.power);
                int index=y*width+x;
                uncover(index,strength);
                tint(index,strength,light.color);
            }
        }
    }
    private void coneMask(Beam beam,List<GameView.Cover> walls){
        prepareBlockers(beam.x,beam.y,beam.reach);
        final float HALF=.50f; // 57-degree full flashlight cone
        // Every ray sees the SAME building, tree and character silhouettes.
        // Test per lit lightmap pixel, not just a 67-ray wall approximation.
        int minX=Math.max(0,ix(beam.x-beam.reach));
        int maxX=Math.min(width-1,ix(beam.x+beam.reach)+1);
        int minY=Math.max(0,iy(beam.y-beam.reach));
        int maxY=Math.min(height-1,iy(beam.y+beam.reach)+1);
        final float cosHalf=(float)Math.cos(HALF);
        for(int y=minY;y<=maxY;y++){
            float dy=top+(y+.5f)*stepY-beam.y;
            for(int x=minX;x<=maxX;x++){
                float dx=left+(x+.5f)*stepX-beam.x;
                float r2=dx*dx+dy*dy;
                if(r2>beam.reach*beam.reach)continue;
                float d=(float)Math.sqrt(r2);
                if(d<2){uncover(y*width+x,.99f);continue;}
                float forward=(dx*beam.dx+dy*beam.dy)/d;
                if(forward<cosHalf)continue;
                float side=(beam.dx*dy-beam.dy*dx)/d;
                float px=left+(x+.5f)*stepX,py=top+(y+.5f)*stepY;
                if(activeCount>0&&shadowed(beam.x,beam.y,px,py))continue;
                float strength=LightMathV46.flashlightStrength(dx,dy,beam.dx,beam.dy,beam.reach);
                uncover(y*width+x,strength);
            }
        }
        // Bright source, on the flashlight head only, does NOT make the whole character glow.
        pointMask(new Point(beam.x,beam.y,35,.97f,0xffffefcc));
    }
    public void render(Canvas scene,float camX,float camY,float w,float h,
                       int nightDarkness,List<GameView.Cover> covers){
        ensure(w,h);
        left=camX;top=camY;screenWidth=w;screenHeight=h;
        stepX=w/width;stepY=h/height;
        darkness=Math.max(0,Math.min(248,nightDarkness));
        Arrays.fill(pixels,(darkness<<24)|DARK_RGB);
        Arrays.fill(tintPixels,0);
        for(Point point:points)pointMask(point);
        for(Beam beam:beams)coneMask(beam,covers);
        bitmap.setPixels(pixels,0,width,0,0,width,height);
        mapPaint.setAlpha(255);
        screenDst.set(left,top,left+w,top+h);
        scene.drawBitmap(bitmap,null,screenDst,mapPaint);
        // Shadows also occlude colored reflections; a radial overlay drawn
        // without ray tests would otherwise brighten actors and walls in shade.
        tintBitmap.setPixels(tintPixels,0,width,0,0,width,height);
        scene.drawBitmap(tintBitmap,null,screenDst,tintMapPaint);
    }
    public void release(){
        if(bitmap!=null){bitmap.recycle();bitmap=null;}
        if(tintBitmap!=null){tintBitmap.recycle();tintBitmap=null;}
        pixels=null;tintPixels=null;
    }
}