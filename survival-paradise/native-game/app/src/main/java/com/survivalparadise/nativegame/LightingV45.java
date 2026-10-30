package com.survivalparadise.nativegame;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.PorterDuff;
import android.graphics.PorterDuffXfermode;
import android.graphics.RadialGradient;
import android.graphics.RectF;
import android.graphics.Shader;
import java.util.ArrayList;
import java.util.List;

/**
 * V45: unified mobile-friendly, low-resolution world lighting compositor.
 * Applied AFTER all world geometry, player, bandits and equipment are rendered.
 * Nothing receives independent brightness: people are dark until lit by a source.
 * A software low-resolution darkness map is scaled over the world (not the HUD).
 * Light sources punch physically localized holes with DST_OUT alpha compositing;
 * flashlight rays stop at building and crate bounding rectangles.
 */
public final class LightingV45 {
    public static final int WARM=0xffffb05b, NEON_BLUE=0xff61ddf6, NEON_PINK=0xffef75ec;
    public static final int TORCH_WHITE=0xfffff2cb;
    private static final int BASE_DARK_RGB=0xff07101b;
    private static final PorterDuffXfermode ERASE=new PorterDuffXfermode(PorterDuff.Mode.DST_OUT);
    private final Paint maskPaint=new Paint(Paint.ANTI_ALIAS_FLAG), renderPaint=new Paint(Paint.FILTER_BITMAP_FLAG);
    private final Paint lightPaint=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint tintedPaint=new Paint(Paint.ANTI_ALIAS_FLAG);
    private Bitmap map;
    private Canvas mapCanvas;
    private int mapW,mapH;
    private float camX,camY,worldW,worldH;
    private final ArrayList<Point> points=new ArrayList<>();
    private final ArrayList<Cone> cones=new ArrayList<>();
    private final Path wedge=new Path();

    public static final class Point {
        public final float x,y,radius,power;
        public final int color;
        Point(float x,float y,float radius,float power,int color){this.x=x;this.y=y;this.radius=radius;this.power=power;this.color=color;}
    }
    public static final class Cone {
        public final float x,y,dx,dy,length,spread;
        public Cone(float x,float y,float dx,float dy,float length,float spread){
            this.x=x;this.y=y;float l=(float)Math.hypot(dx,dy);if(l<.0001f)l=1;
            this.dx=dx/l;this.dy=dy/l;this.length=length;this.spread=spread;
        }
    }
    public void clear(){points.clear();cones.clear();}
    public void point(float x,float y,float radius,float strength,int color){
        if(radius>1&&strength>0)points.add(new Point(x,y,radius,Math.min(1f,strength),color));
    }
    public void flashlight(float x,float y,float dx,float dy,float length){
        if(length>0)cones.add(new Cone(x,y,dx,dy,length,(float)Math.toRadians(30)));
    }
    public int sourceCount(){return points.size()+cones.size();}
    public static boolean inBeam(float srcX,float srcY,float dirX,float dirY,float px,float py,
                                 float length,float halfAngle){
        float dx=px-srcX,dy=py-srcY,d=(float)Math.hypot(dx,dy);
        if(d>length||d<.001f)return d<length;
        float norm=(float)Math.hypot(dirX,dirY);
        if(norm<.001f)return false;
        float dot=(dx*dirX+dy*dirY)/(d*norm);
        return dot>=(float)Math.cos(halfAngle);
    }
    public static float visibilityRadius(float x,float y,float dx,float dy,float distance,
                                        List<GameView.Cover> occluders){
        float max=distance;
        float x1=x+dx*distance,y1=y+dy*distance;
        for(GameView.Cover c:occluders){
            float r=LightGeometryV45.rayBox(x,y,dx,dy,distance,c.x-3,c.y-3,c.x+c.w+3,c.y+c.h+3);
            max=Math.min(max,r);
        }
        return max;
    }
    private void ensure(float width,float height){
        // ~3.5 world pixels per lightmap cell. 240..520 px width on phones.
        int w=Math.max(200,Math.min(520,Math.round(width/3.2f)));
        int h=Math.max(120,Math.min(350,Math.round(height*w/Math.max(1,width))));
        if(map!=null&&mapW==w&&mapH==h)return;
        if(map!=null)map.recycle();
        mapW=w;mapH=h;
        map=Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);
        mapCanvas=new Canvas(map);
    }
    private boolean visible(float x,float y,float radius){
        return x+radius>camX&&x-radius<camX+worldW&&y+radius>camY&&y-radius<camY+worldH;
    }
    private void radial(float x,float y,float radius,float power){
        if(!visible(x,y,radius))return;
        float alpha=power;
        int inner=Color.argb((int)(255*alpha),255,255,255);
        int middle=Color.argb((int)(185*alpha),255,255,255);
        lightPaint.setShader(new RadialGradient(x,y,radius,
             new int[]{inner,middle,0x00ffffff},new float[]{0,.24f,1f},Shader.TileMode.CLAMP));
        mapCanvas.drawCircle(x,y,radius,lightPaint);
        lightPaint.setShader(null);
    }
    private void cone(Cone c,List<GameView.Cover> walls){
        if(!visible(c.x,c.y,c.length))return;
        float center=(float)Math.atan2(c.dy,c.dx);
        // Three low-overdraw passes form a soft falloff: wide penumbra, medium
        // beam and bright core. Each ray stops at opaque building or crate.
        final float[] widths={1f,.63f,.27f};
        final int[] alphas={92,106,175};
        final int rayCount=32;
        for(int pass=0;pass<3;pass++){
            float half=c.spread*widths[pass];
            for(int i=0;i<rayCount;i++){
                float a0=center-half+2*half*i/rayCount;
                float a1=center-half+2*half*(i+1)/rayCount;
                float am=(a0+a1)*.5f;
                float dx=(float)Math.cos(am),dy=(float)Math.sin(am);
                float len=visibilityRadius(c.x,c.y,dx,dy,c.length,walls);
                if(len<4)continue;
                float x0=c.x+(float)Math.cos(a0)*len,y0=c.y+(float)Math.sin(a0)*len;
                float x1=c.x+(float)Math.cos(a1)*len,y1=c.y+(float)Math.sin(a1)*len;
                wedge.reset();wedge.moveTo(c.x,c.y);wedge.lineTo(x0,y0);
                wedge.lineTo(x1,y1);wedge.close();
                lightPaint.setShader(new LinearGradient(c.x,c.y,c.x+dx*len,c.y+dy*len,
                    new int[]{Color.argb(alphas[pass],255,255,255),
                    Color.argb(alphas[pass]/2,255,255,255),0x00ffffff},
                    new float[]{0,.47f,1f},Shader.TileMode.CLAMP));
                mapCanvas.drawPath(wedge,lightPaint);
            }
        }
        lightPaint.setShader(null);
        radial(c.x,c.y,47,.83f);
    }
    /** Canvas is already translated into world space and drawWorld has completed. */
    public void render(Canvas world,float cameraX,float cameraY,float width,float height,
                       int darkness,List<GameView.Cover> walls){
        ensure(width,height);camX=cameraX;camY=cameraY;worldW=width;worldH=height;
        map.eraseColor(BASE_DARK_RGB & 0x00ffffff | (Math.max(0,Math.min(250,darkness))<<24));
        mapCanvas.save();
        mapCanvas.scale(mapW/Math.max(1,width),mapH/Math.max(1,height));
        mapCanvas.translate(-camX,-camY);
        lightPaint.setStyle(Paint.Style.FILL);lightPaint.setXfermode(ERASE);
        for(Point p:points)radial(p.x,p.y,p.radius,p.power);
        for(Cone c:cones)cone(c,walls);
        lightPaint.setXfermode(null);
        mapCanvas.restore();
        RectF dst=new RectF(camX,camY,camX+worldW,camY+worldH);
        world.drawBitmap(map,null,dst,renderPaint);
        // Colored reflected light tints EVERYTHING inside it, including actors.
        for(Point p:points){
            if(!visible(p.x,p.y,p.radius))continue;
            int color=p.color;
            int center=Color.argb((int)(42*p.power),Color.red(color),Color.green(color),Color.blue(color));
            tintedPaint.setShader(new RadialGradient(p.x,p.y,p.radius,
               new int[]{center,0x00000000},null,Shader.TileMode.CLAMP));
            world.drawCircle(p.x,p.y,p.radius,tintedPaint);
        }
        tintedPaint.setShader(null);
    }
    public void release(){if(map!=null){map.recycle();map=null;mapCanvas=null;}}
}