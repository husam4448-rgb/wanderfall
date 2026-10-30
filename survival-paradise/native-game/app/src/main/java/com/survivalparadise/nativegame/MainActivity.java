package com.survivalparadise.nativegame;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ContentValues;
import android.content.SharedPreferences;
import android.content.pm.ActivityInfo;
import android.graphics.Color;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.ArrayAdapter;
import android.widget.TextView;
import android.widget.Toast;
import java.io.OutputStream;
import java.io.File;
import java.io.FileOutputStream;

public final class MainActivity extends Activity {
    GameView game;
    SharedPreferences prefs;
    boolean immersive=true;
    static final String[] LOADOUTS={"Pistol","Revolver","UZI","Flashlight","Tactical carbine",
            "AK rifle","Bullpup","Pump shotgun","Sniper rifle","LMG","Grenade launcher","Red axe"};
    private final int INK=0xffe4f0ed,BG=0xff172b32,ACC=0xff9bc8b1;

    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);
        prefs=getSharedPreferences("survival_paradise_native_v34",MODE_PRIVATE);
        applyImmersive();
        game=new GameView(this);
        setContentView(game);
    }
    void applyImmersive(){
        immersive=prefs==null||prefs.getBoolean("fullscreen",true);
        getWindow().getDecorView().setSystemUiVisibility(immersive?(
             View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY|View.SYSTEM_UI_FLAG_FULLSCREEN|
             View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_LAYOUT_STABLE|
             View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN|View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION):0);
    }
    int setting(String key,int def){return prefs.getInt(key,def);}
    boolean option(String key,boolean def){return prefs.getBoolean(key,def);}
    private TextView text(String s,int sp,boolean bold){
        TextView t=new TextView(this);t.setText(s);t.setTextSize(sp);t.setTextColor(INK);
        if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        t.setPadding(11,10,11,6);return t;
    }
    private LinearLayout column(){
        LinearLayout v=new LinearLayout(this);v.setOrientation(LinearLayout.VERTICAL);
        v.setPadding(12,8,12,14);v.setBackgroundColor(BG);return v;
    }
    private void section(LinearLayout root,String title){
        TextView t=text(title,16,true);t.setTextColor(ACC);t.setPadding(9,15,9,6);root.addView(t);
    }
    private void slider(LinearLayout root,String label,String key,int min,int max,int def,String suffix){
        LinearLayout box=column();
        TextView value=text("",14,false);
        box.addView(value);
        SeekBar bar=new SeekBar(this);bar.setMax(max-min);
        bar.setProgress(Math.max(0,Math.min(max-min,prefs.getInt(key,def)-min)));
        value.setText(label+"   "+(min+bar.getProgress())+suffix);
        box.addView(bar);
        bar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar s,int progress,boolean fromUser){
                int number=min+progress;value.setText(label+"   "+number+suffix);
                if(fromUser){prefs.edit().putInt(key,number).apply();game.reloadSettings();}
            }
            public void onStartTrackingTouch(SeekBar s){}
            public void onStopTrackingTouch(SeekBar s){}
        });
        root.addView(box);
    }
    private void check(LinearLayout root,String title,String key,boolean def){
        CheckBox b=new CheckBox(this);b.setText(title);b.setTextColor(INK);b.setTextSize(15);
        b.setPadding(12,5,8,5);b.setChecked(prefs.getBoolean(key,def));root.addView(b);
        b.setOnCheckedChangeListener((v,on)->{
            prefs.edit().putBoolean(key,on).apply();
            if("fullscreen".equals(key))applyImmersive();
            game.reloadSettings();
        });
    }
    private Button action(LinearLayout root,String title,Runnable run){
        Button b=new Button(this);b.setText(title);b.setAllCaps(false);
        root.addView(b,new LinearLayout.LayoutParams(-1,-2));b.setOnClickListener(v->run.run());return b;
    }
    void settings(){
        game.menuPause(true);
        ScrollView scroll=new ScrollView(this);
        LinearLayout root=column();scroll.addView(root);
        section(root,"SURVIVAL PARADISE  •  GAME SETTINGS");
        root.addView(text("Controls apply to the playable game, and save automatically.",13,false));
        section(root,"PLAYER AND COMBAT");
        slider(root,"Character display size","scale",65,135,100,"%");
        slider(root,"Hand size (independent)","hand",60,145,100,"%");
        slider(root,"Support hand reach","support",-12,24,0," px");
        slider(root,"Simulation speed","speed",50,200,100,"%");
        slider(root,"Survivors (including player)","survivors",1,9,1,"");
        root.addView(text("Equipped weapon",14,true));
        Spinner spinner=new Spinner(this);
        ArrayAdapter<String> adapter=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,LOADOUTS);
        spinner.setAdapter(adapter);
        spinner.setSelection(Math.max(0,Math.min(LOADOUTS.length-1,prefs.getInt("gun",0))));
        root.addView(spinner);
        spinner.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(android.widget.AdapterView<?> parent){}
            public void onItemSelected(android.widget.AdapterView<?> parent,View item,int pos,long id){
                prefs.edit().putInt("gun",pos).apply();
                if(game!=null)game.reloadSettings();
            }
        });
        section(root,"GAMEPLAY AND APPEARANCE");
        check(root,"Show hands","hands",true);
        check(root,"Show weapons","weapons",true);
        check(root,"Grip anchors","anchors",false);
        check(root,"AI hitboxes","hitboxes",false);
        check(root,"Enemy AI","enemyAI",true);
        check(root,"Aiming rotation","aimRotation",true);
        check(root,"Firing recoil + muzzle flashes","recoil",true);
        check(root,"Item drops + inventory","loot",true);
        check(root,"Night lighting","night",false);
        check(root,"Full-screen immersive gameplay","fullscreen",true);
        section(root,"GAME ACTIONS");
        action(root,"Save game now",()->{game.saveProgress();Toast.makeText(this,"Game saved",Toast.LENGTH_SHORT).show();});
        action(root,"Take screenshot",()->captureGame());
        action(root,"Restore default settings",()->{
            prefs.edit().putInt("scale",100).putInt("hand",100).putInt("support",0)
              .putInt("speed",100).putInt("survivors",1).putInt("gun",0)
              .putBoolean("hands",true).putBoolean("weapons",true).putBoolean("anchors",false)
              .putBoolean("hitboxes",false).putBoolean("enemyAI",true).putBoolean("aimRotation",true)
              .putBoolean("recoil",true).putBoolean("loot",true).putBoolean("night",false)
              .putBoolean("fullscreen",true).apply();
            game.reloadSettings();applyImmersive();
            Toast.makeText(this,"Defaults restored. Reopen settings to see the values.",Toast.LENGTH_LONG).show();
        });
        AlertDialog dialog=new AlertDialog.Builder(this).setView(scroll)
          .setPositiveButton("RETURN TO GAME",(d,w)->game.menuPause(false))
          .setOnCancelListener(d->game.menuPause(false)).create();
        dialog.setOnDismissListener(d->game.menuPause(false));
        dialog.show();
        if(dialog.getWindow()!=null)dialog.getWindow().setLayout(
                (int)(getResources().getDisplayMetrics().widthPixels*.70f),-1);
    }
    void captureGame(){
        if(game==null)return;
        try{
            byte[] image=game.capturePNG();
            String name="Survival_Paradise_Native_"+System.currentTimeMillis()+".png";
            if(Build.VERSION.SDK_INT>=29){
                ContentValues cv=new ContentValues();
                cv.put(MediaStore.Images.Media.DISPLAY_NAME,name);
                cv.put(MediaStore.Images.Media.MIME_TYPE,"image/png");
                cv.put(MediaStore.Images.Media.RELATIVE_PATH,Environment.DIRECTORY_PICTURES+"/SurvivalParadise");
                cv.put(MediaStore.Images.Media.IS_PENDING,1);
                Uri uri=getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI,cv);
                if(uri==null)throw new Exception("Cannot create screenshot");
                try(OutputStream out=getContentResolver().openOutputStream(uri)){
                    if(out==null)throw new Exception("Cannot open screenshot");out.write(image);
                }
                ContentValues ready=new ContentValues();ready.put(MediaStore.Images.Media.IS_PENDING,0);
                getContentResolver().update(uri,ready,null,null);
            }else{
                File dir=getExternalFilesDir(Environment.DIRECTORY_PICTURES);
                if(dir==null)dir=getFilesDir();
                try(OutputStream out=new FileOutputStream(new File(dir,name))){out.write(image);}
            }
            Toast.makeText(this,"Screenshot saved",Toast.LENGTH_SHORT).show();
        }catch(Exception e){
            Toast.makeText(this,"Screenshot failed: "+e.getMessage(),Toast.LENGTH_LONG).show();
        }
    }
    @Override public void onBackPressed(){
        if(game!=null&&game.isPlaying()){game.togglePause();return;}super.onBackPressed();
    }
    @Override protected void onPause(){if(game!=null)game.saveProgress();super.onPause();}
}
