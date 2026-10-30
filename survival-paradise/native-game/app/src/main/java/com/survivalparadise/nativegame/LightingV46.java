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
 * V46 deterministic software lightmap: opaque darkness everywhere except
 * actual world-space point lights and occlusion-tested hand flashlight cones.
 * The mask is composited AFTER every scene/character/weapon sprite and BEFORE
 * the HUD, preventing sprites from glowing in isolation.
 *
 * V45's DST_OUT + bitmap shader path is deliberately not used: it can render
 * differently on OEM accelerated canvases. V46 explicitly calculates every
 * output pixel's alpha and uploads an ARGB_8888 bitmap without Xfermodes.
 */
public final class LightingV46 {
    public static final int WARM=0xffffb05b, NEON_BLUE=0xff61ddf6, NEON_PINK=0xffef75ec;
    private static final int DARK_RGB=0x00101a23;
    private final Paint mapPaint=new Paint(Paint.FILTER_BITMAP_FLAG);
    private final Paint tintPaint=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final ArrayList<Point> points=new ArrayList<>();
    private final ArrayList<Beam> beams=new ArrayList<>();
    private Bitmap bitmap;
    private int[] pixels;
    private int width,height;
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
    public void clear(){points.clear();beams.clear();}
    public void point(float x,float y,float radius,float power,int color){
        if(radius>1&&power>0)points.add(new Point(x,y,radius,Math.min(1,power),color));
    }
    public void flashlight(float x,float y,float dx,float dy,float reach){
        if(reach>0)beams.add(new Beam(x,y,dx,dy,reach));
    }
    public int sourceCount(){return points.size()+beams.size();}

    private void ensure(float w,float h){
        int newWidth=Math.max(180,Math.min(440,Math.round(w/3.3f)));
        int newHeight=Math.max(110,Math.min(280,Math.round(h*newWidth/Math.max(1,w))));
        if(bitmap!=null&&width==newWidth&&height==newHeight)return;
        if(bitmap!=null)bitmap.recycle();
        width=newWidth;height=newHeight;
        bitmap=Bitmap.createBitmap(width,height,Bitmap.Config.ARGB_8888);
        pixels=new int[width*height];
    }
    private void uncover(int i,float amount){
        int oldAlpha=pixels[i]>>>24;
        int alpha=LightMathV46.shadowAlpha(darkness,amount);
        if(alpha<oldAlpha)pixels[i]=(alpha<<24)|DARK_RGB;
    }
    private int ix(float x){return (int)Math.floor((x-left)/stepX);}
    private int iy(float y){return (int)Math.floor((y-top)/stepY);}
    private void pointMask(Point light){
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
                float strength=LightMathV46.pointStrength(dx,dy,light.radius,light.power);
                uncover(y*width+x,strength);
            }
        }
    }
    private void coneMask(Beam beam,List<GameView.Cover> walls){
        final float HALF=.50f; // 57-degree full flashlight cone
        final int RAYS=67;
        final float[] rayReach=new float[RAYS];
        float start=(float)Math.atan2(beam.dy,beam.dx);
        for(int i=0;i<RAYS;i++){
            float a=start-HALF+(2f*HALF*i)/(RAYS-1);
            float ux=(float)Math.cos(a),uy=(float)Math.sin(a);
            float distance=beam.reach;
            for(GameView.Cover box:walls){
                distance=Math.min(distance,LightGeometryV45.rayBox(beam.x,beam.y,ux,uy,
                    beam.reach,box.x-3,box.y-3,box.x+box.w+3,box.y+box.h+3));
            }
            rayReach[i]=distance;
        }
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
                float relative=(float)Math.atan2(side,forward)/HALF;
                int ray=Math.max(0,Math.min(RAYS-1,
                     Math.round((relative+1f)*.5f*(RAYS-1))));
                if(d>rayReach[ray]-1.5f)continue; // actual shadow behind walls
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
        for(Point point:points)pointMask(point);
        for(Beam beam:beams)coneMask(beam,covers);
        bitmap.setPixels(pixels,0,width,0,0,width,height);
        mapPaint.setAlpha(255);
        scene.drawBitmap(bitmap,null,new RectF(left,top,left+w,top+h),mapPaint);
        // Tinted reflected illumination, blended over both actors and architecture.
        for(Point q:points){
            if(q.x+q.radius<camX||q.x-q.radius>camX+w||q.y+q.radius<camY||q.y-q.radius>camY+h)continue;
            int c=q.color;
            int center=Color.argb(Math.max(0,Math.min(75,Math.round(58*q.power))),
                Color.red(c),Color.green(c),Color.blue(c));
            tintPaint.setShader(new RadialGradient(q.x,q.y,q.radius,
                new int[]{center,0x00000000},null,Shader.TileMode.CLAMP));
            scene.drawCircle(q.x,q.y,q.radius,tintPaint);
            tintPaint.setShader(null);
        }
    }
    public void release(){
        if(bitmap!=null){bitmap.recycle();bitmap=null;}
        pixels=null;
    }
}