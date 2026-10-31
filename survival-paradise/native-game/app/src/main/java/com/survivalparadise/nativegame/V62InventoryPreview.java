package com.survivalparadise.nativegame;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.view.View;

/** Inventory paper-doll: renders the real immutable approved idle sprites and live weapon gear.
 * All equipment is drawn as overlays; never edits the locked pixel-art skeleton. */
public final class V62InventoryPreview extends View {
    private final GameView game;
    private final Paint paint=new Paint();
    public V62InventoryPreview(Context context,GameView game){
        super(context);this.game=game;
        setLayerType(View.LAYER_TYPE_SOFTWARE,null);
    }
    @Override protected void onDraw(Canvas canvas){
        super.onDraw(canvas);
        int w=getWidth(),h=getHeight();
        canvas.drawColor(0xff211d19);
        paint.setColor(0xff3d3228);canvas.drawOval(w*.14f,h*.79f,w*.86f,h*.96f,paint);
        paint.setColor(0xffac8954);paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(3f);canvas.drawOval(w*.14f,h*.79f,w*.86f,h*.96f,paint);
        paint.setStyle(Paint.Style.FILL);
        // The exact approved idle atlas and current equipped firearm/torch are
        // rendered through GameView.character; head/torso art is never reconstructed.
        // Fit the complete approved survivor and weapon within this panel. Never
        // enlarge by the world/character zoom or crop the face/equipment.
        float factor=Math.min(w/210f,h/150f)*.92f/Math.max(.65f,game.scale);
        canvas.save();
        canvas.translate(w*.55f,h*.81f);
        canvas.scale(factor,factor);
        float breath=(float)(-2+2*Math.sin(System.nanoTime()/350_000_000.0));
        game.character(canvas,0,0,game.gun,game.face,2,breath,0f,0f,true,false,-1);
        canvas.restore();
        paint.setColor(0xffd9bd83);paint.setTextSize(Math.max(11f,Math.min(16f,w*.036f)));
        canvas.drawText("SURVIVOR • LIVE GEAR",w*.07f,h*.10f,paint);
        canvas.drawText("IDLE / LIVE GEAR",w*.14f,h*.15f,paint);
        postInvalidateDelayed(95);
    }
}
