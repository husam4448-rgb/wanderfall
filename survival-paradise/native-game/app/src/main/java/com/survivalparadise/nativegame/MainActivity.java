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
import android.view.WindowInsets;
import android.view.WindowInsetsController;
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
    CharacterPreviewV118 activeCharacterPreviewV118;
    boolean immersive=true;
    static final String[] LOADOUTS={"Pistol","Revolver","UZI","Flashlight","Tactical carbine",
            "AK rifle","Bullpup","Pump shotgun","Sniper rifle","LMG","Grenade launcher","Red axe"};
    private final int INK=0xffe4f0ed,BG=0xff172b32,ACC=0xff9bc8b1;

    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);
        prefs=getSharedPreferences("survival_paradise_native_v34",MODE_PRIVATE);
        // V46 migration: default to NIGHT once, so light sources are visible
        // on existing V45 installations too. DAY is always one tap away.
        if(!prefs.getBoolean("v46_lighting_migrated",false)){
            prefs.edit().putBoolean("night",true)
                .putBoolean("lampOn",true)
                .putBoolean("v46_lighting_migrated",true).apply();
        }
        // Upgrade prior V59 default light resolution only once; preserve user-
        // selected values other than the old, unmodified 150% default.
        if(!prefs.getBoolean("v60_lighting_migrated",false)){
            SharedPreferences.Editor migration=prefs.edit();
            if(prefs.getInt("lightResolution",150)==150)
                migration.putInt("lightResolution",220);
            migration.putBoolean("fastPointLights",true)
                     .putBoolean("staticLightCache",true)
                     .putBoolean("v60_lighting_migrated",true).apply();
        }
        // One-time V72 HUD preset, without modifying world/equipment saves.
        if(!prefs.getBoolean("v72_reference_hud_migrated",false)){
            SharedPreferences.Editor hud=prefs.edit();
            for(int id=0;id<LegacyControlsV58.COUNT+4;id++){
                hud.remove("uiX"+id).remove("uiY"+id).remove("uiSize"+id)
                    .remove("uiAlpha"+id).remove("uiEnabled"+id);
            }
            hud.remove("movePadSize").remove("aimPadSize")
                .putBoolean("editControls",false)
                .putBoolean("classicAimCameraV71",true)
                .putInt("cameraPanPercentV72",72)
                .putBoolean("v72_reference_hud_migrated",true).apply();
        }
        // V121 screenshot profile, only where preferences are unset.
        if(!prefs.getBoolean(ScreenshotSettingsV121.CHARACTER_MARKER,false))
            ScreenshotSettingsV121.applyCharacters(prefs,false);
        applyImmersive();
        game=new GameView(this);
        setContentView(game);
    }
    static final int EXPORT_SAVE_V85=851,IMPORT_SAVE_V85=852,EXPORT_FIT_V108=1081;
    /** Android system file picker stores a portable save outside app-private data. */
    void exportGameSaveV85(){
        game.saveProgress();
        android.content.Intent pick=new android.content.Intent(
            android.content.Intent.ACTION_CREATE_DOCUMENT);
        pick.addCategory(android.content.Intent.CATEGORY_OPENABLE);
        pick.setType("application/json");
        pick.putExtra(android.content.Intent.EXTRA_TITLE,"SurvivalParadise_Save_V85.json");
        startActivityForResult(pick,EXPORT_SAVE_V85);
    }

    /** Save the character-only calibration as portable JSON through Android's file picker. */
    void exportCharacterFittingV108(){
        android.content.Intent pick=new android.content.Intent(
            android.content.Intent.ACTION_CREATE_DOCUMENT);
        pick.addCategory(android.content.Intent.CATEGORY_OPENABLE);
        pick.setType("application/json");
        pick.putExtra(android.content.Intent.EXTRA_TITLE,
            "SurvivalParadise_CharacterFit_V108.json");
        startActivityForResult(pick,EXPORT_FIT_V108);
    }
    void importGameSaveV85(){
        new AlertDialog.Builder(this).setTitle("Restore game save")
            .setMessage("This replaces the current save and settings with the chosen backup. Continue?")
            .setNegativeButton("Cancel",null)
            .setPositiveButton("Choose backup",(d,w)->{
                android.content.Intent pick=new android.content.Intent(
                    android.content.Intent.ACTION_OPEN_DOCUMENT);
                pick.addCategory(android.content.Intent.CATEGORY_OPENABLE);
                pick.setType("application/json");
                startActivityForResult(pick,IMPORT_SAVE_V85);
            }).show();
    }
    /** Lossless typed SharedPreferences format with explicit app/version marker. */
    String encodeSaveV85() throws org.json.JSONException{
        org.json.JSONObject object=new org.json.JSONObject();
        object.put("format","survival-paradise-save-v85");
        object.put("package","com.survivalparadise.nativegame");
        org.json.JSONObject data=new org.json.JSONObject();
        for(java.util.Map.Entry<String,?> item:prefs.getAll().entrySet()){
            Object value=item.getValue();
            if(value==null)continue;
            org.json.JSONObject typed=new org.json.JSONObject();
            if(value instanceof String)typed.put("kind","s");
            else if(value instanceof Boolean)typed.put("kind","b");
            else if(value instanceof Integer)typed.put("kind","i");
            else if(value instanceof Long)typed.put("kind","l");
            else if(value instanceof Float)typed.put("kind","f");
            else continue;
            typed.put("value",value);
            data.put(item.getKey(),typed);
        }
        object.put("prefs",data);
        return object.toString();
    }
    void restoreSaveV85(String content) throws Exception{
        org.json.JSONObject object=new org.json.JSONObject(content);
        if(!"survival-paradise-save-v85".equals(object.getString("format"))||
           !"com.survivalparadise.nativegame".equals(object.getString("package")))
            throw new IllegalArgumentException("Unsupported game-save format");
        org.json.JSONObject data=object.getJSONObject("prefs");
        if(!data.has("hasSave"))throw new IllegalArgumentException("No game save in backup");
        SharedPreferences.Editor ed=prefs.edit().clear();
        java.util.Iterator<String> keys=data.keys();
        while(keys.hasNext()){
            String key=keys.next();
            org.json.JSONObject typed=data.getJSONObject(key);
            String t=typed.getString("kind");
            if("s".equals(t))ed.putString(key,typed.getString("value"));
            else if("b".equals(t))ed.putBoolean(key,typed.getBoolean("value"));
            else if("i".equals(t))ed.putInt(key,typed.getInt("value"));
            else if("l".equals(t))ed.putLong(key,typed.getLong("value"));
            else if("f".equals(t))ed.putFloat(key,(float)typed.getDouble("value"));
        }
        if(!ed.commit())throw new IllegalStateException("Save write failed");
        game.hasSave=prefs.getBoolean("hasSave",false);
        game.reloadSettings();
        if(game.hasSave)game.continueGame();
        else game.newGame();
        game.invalidate();
    }
    @Override protected void onActivityResult(int request,int result,android.content.Intent data){
        super.onActivityResult(request,result,data);
        if(result!=RESULT_OK||data==null||data.getData()==null)return;
        if(request!=EXPORT_SAVE_V85&&request!=IMPORT_SAVE_V85&&request!=EXPORT_FIT_V108)return;
        try{

            if(request==EXPORT_FIT_V108){
                try(java.io.OutputStream stream=getContentResolver().openOutputStream(
                    data.getData(),"w")){
                    if(stream==null)throw new java.io.IOException("Storage unavailable");
                    byte[] json=CharacterFitV108.exportJson(prefs).toString(2)
                        .getBytes(java.nio.charset.StandardCharsets.UTF_8);
                    stream.write(json);stream.flush();
                }
                Toast.makeText(this,"Character fitting JSON exported",
                    Toast.LENGTH_LONG).show();
            }else if(request==EXPORT_SAVE_V85){
                try(java.io.OutputStream stream=getContentResolver().openOutputStream(
                    data.getData(),"w")){
                    if(stream==null)throw new java.io.IOException("Storage unavailable");
                    stream.write(encodeSaveV85().getBytes(java.nio.charset.StandardCharsets.UTF_8));
                    stream.flush();
                }
                Toast.makeText(this,"Save exported outside the game",Toast.LENGTH_LONG).show();
            }else{
                byte[] resultBytes;
                try(java.io.InputStream stream=getContentResolver().openInputStream(data.getData());
                    java.io.ByteArrayOutputStream buffer=new java.io.ByteArrayOutputStream()){
                    if(stream==null)throw new java.io.IOException("Backup unavailable");
                    byte[] chunk=new byte[8192];int n;
                    while((n=stream.read(chunk))!=-1){
                        if(buffer.size()+n>1500000)throw new java.io.IOException("Backup exceeds size limit");
                        buffer.write(chunk,0,n);
                    }
                    resultBytes=buffer.toByteArray();
                }
                restoreSaveV85(new String(resultBytes,java.nio.charset.StandardCharsets.UTF_8));
                Toast.makeText(this,"Game save restored",Toast.LENGTH_LONG).show();
            }
        }catch(Exception ex){
            Toast.makeText(this,"Save transfer failed: "+ex.getMessage(),
                Toast.LENGTH_LONG).show();
        }
    }

    void applyImmersive(){
        immersive=prefs==null||prefs.getBoolean("fullscreen",true);
        View decor=getWindow().getDecorView();
        if(Build.VERSION.SDK_INT>=30){
            // Samsung / Android 11+: bars can stay visible after pulling down
            // the notification shade unless insets are hidden on focus regain.
            getWindow().setDecorFitsSystemWindows(!immersive);
            WindowInsetsController controller=getWindow().getInsetsController();
            if(controller!=null){
                if(immersive){
                    controller.setSystemBarsBehavior(
                        WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
                    controller.hide(WindowInsets.Type.statusBars()|
                                    WindowInsets.Type.navigationBars());
                }else{
                    controller.show(WindowInsets.Type.statusBars()|
                                    WindowInsets.Type.navigationBars());
                }
            }
        }
        int flags=View.SYSTEM_UI_FLAG_LAYOUT_STABLE;
        if(immersive){
            flags|=View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY|
                   View.SYSTEM_UI_FLAG_FULLSCREEN|
                   View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|
                   View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN|
                   View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION;
        }
        decor.setSystemUiVisibility(flags);
        if(immersive)getWindow().addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
        else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
    }
    private void restoreFullscreenAfterShade(){
        if(!immersive)return;
        View decor=getWindow().getDecorView();
        decor.postDelayed(()->{
            if(!isFinishing()&&hasWindowFocus()&&immersive)applyImmersive();
        },180);
    }
    @Override public void onWindowFocusChanged(boolean hasFocus){
        super.onWindowFocusChanged(hasFocus);
        if(!hasFocus){if(game!=null)game.releaseControls();}
        else restoreFullscreenAfterShade();
    }
    @Override protected void onResume(){
        super.onResume();
        restoreFullscreenAfterShade();
    }
    int setting(String key,int def){return prefs.getInt(key,def);}
    boolean option(String key,boolean def){return prefs.getBoolean(key,def);}
    private TextView text(String s,int sp,boolean bold){
        TextView t=new TextView(this);t.setText(s);
        t.setTextSize(sp*Math.max(.75f,Math.min(1.55f,prefs.getInt("menuTextSize",100)/100f)));
        t.setTextColor(INK);
        if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        t.setPadding(7,4,7,3);return t;
    }
    private LinearLayout column(){
        LinearLayout v=new LinearLayout(this);v.setOrientation(LinearLayout.VERTICAL);
        v.setPadding(8,4,8,6);v.setBackgroundColor(BG);return v;
    }
    private void section(LinearLayout root,String title){
        TextView t=text(title,15,true);t.setTextColor(ACC);t.setPadding(7,7,7,3);root.addView(t);
    }
    private int dp118(float value){
        return Math.round(value*getResources().getDisplayMetrics().density);
    }
    private Button stepButton118(String symbol){
        Button b=new Button(this);b.setText(symbol);b.setAllCaps(false);
        b.setTextSize(16);b.setPadding(0,0,0,0);
        b.setMinWidth(0);b.setMinHeight(0);
        b.setMinimumWidth(0);b.setMinimumHeight(0);
        return b;
    }
    private void slider(LinearLayout root,String label,String key,int min,int max,int def,String suffix){
        LinearLayout box=column();
        int density=prefs.getInt("menuRowSpacing",100);
        box.setPadding(5,Math.max(1,density/38),5,Math.max(1,density/38));
        TextView caption=text("",13,false);
        box.addView(caption);
        int current=Math.max(min,Math.min(max,prefs.getInt(key,def)));
        caption.setText(label+"  "+current+suffix);
        boolean vertical=label.toLowerCase(java.util.Locale.US).contains("vertical");
        final Runnable redraw=()->{if(activeCharacterPreviewV118!=null)
            activeCharacterPreviewV118.invalidate();};
        if(vertical){
            // Y-position sliders physically travel UP/DOWN, not sideways.
            LinearLayout control=new LinearLayout(this);
            control.setOrientation(LinearLayout.VERTICAL);
            control.setGravity(Gravity.CENTER_HORIZONTAL);
            final VerticalSliderV118 v=new VerticalSliderV118(this,min,max,current,
                (number,user)->{
                    caption.setText(label+"  "+number+suffix);
                    if(user){prefs.edit().putInt(key,number).apply();
                        game.reloadSettings();redraw.run();}
                });
            Button plus=stepButton118("+"),minus=stepButton118("−");
            control.addView(plus,new LinearLayout.LayoutParams(dp118(48),dp118(30)));
            control.addView(v,new LinearLayout.LayoutParams(dp118(48),dp118(114)));
            control.addView(minus,new LinearLayout.LayoutParams(dp118(48),dp118(30)));
            plus.setOnClickListener(view->v.setValue(v.getValue()+1,true));
            minus.setOnClickListener(view->v.setValue(v.getValue()-1,true));
            box.addView(control,new LinearLayout.LayoutParams(dp118(70),-2));
        }else{
            LinearLayout control=new LinearLayout(this);
            control.setOrientation(LinearLayout.HORIZONTAL);
            control.setGravity(Gravity.CENTER_VERTICAL);
            Button minus=stepButton118("−"),plus=stepButton118("+");
            SeekBar bar=new SeekBar(this);bar.setMax(max-min);
            bar.setMinimumHeight(dp118(22));bar.setPadding(0,0,0,0);
            bar.setScaleY(prefs.getInt("menuSliderSize",100)/100f);
            bar.setProgress(current-min);
            int button=dp118(38);
            control.addView(minus,new LinearLayout.LayoutParams(button,dp118(35)));
            control.addView(bar,new LinearLayout.LayoutParams(0,dp118(35),1f));
            control.addView(plus,new LinearLayout.LayoutParams(button,dp118(35)));
            bar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
                public void onProgressChanged(SeekBar seek,int p,boolean user){
                    int number=min+p;caption.setText(label+"  "+number+suffix);
                    if(user){prefs.edit().putInt(key,number).apply();
                        game.reloadSettings();redraw.run();}
                }
                public void onStartTrackingTouch(SeekBar seek){}
                public void onStopTrackingTouch(SeekBar seek){}
            });
            minus.setOnClickListener(view->{
                bar.setProgress(Math.max(0,bar.getProgress()-1));
                int number=min+bar.getProgress();prefs.edit().putInt(key,number).apply();
                game.reloadSettings();redraw.run();
            });
            plus.setOnClickListener(view->{
                bar.setProgress(Math.min(max-min,bar.getProgress()+1));
                int number=min+bar.getProgress();prefs.edit().putInt(key,number).apply();
                game.reloadSettings();redraw.run();
            });
            box.addView(control,new LinearLayout.LayoutParams(
                Math.min(dp118(230),Math.max(dp118(165),
                    getResources().getDisplayMetrics().widthPixels/2)),dp118(37)));
        }
        root.addView(box);
    }
    /** The slider's actual maximum follows the currently equipped weapon.
     * Save percentage rather than absolute pixels so swapping guns can
     * increase/decrease pan reach without resetting the user's preference. */
    private void weaponPanSlider(LinearLayout root){
        int weapon=game==null?0:game.gun;
        int maximum=WeaponCameraV72.visibleMaximum(weapon,
            game==null?1480f:game.viewW,game==null?720f:game.viewH,
            game==null?1f:Math.max(.01f,game.zoom));
        int percent=prefs.getInt("cameraPanPercentV72",72);
        LinearLayout box=column();box.setPadding(6,3,6,3);
        TextView caption=text("",14,false);box.addView(caption);
        SeekBar bar=new SeekBar(this);bar.setMax(Math.max(1,maximum));
        bar.setProgress(Math.round(maximum*percent/100f));
        caption.setText("CIRCULAR CAMERA PAN — "+LOADOUTS[weapon]+
            "   "+bar.getProgress()+" / "+maximum+" px");
        bar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar v,int p,boolean fromUser){
                caption.setText("CIRCULAR CAMERA PAN — "+LOADOUTS[weapon]+
                    "   "+Math.min(maximum,p)+" / "+maximum+" px");
                if(fromUser){
                    prefs.edit().putInt("cameraPanPercentV72",
                        maximum>0?Math.round(p*100f/maximum):0).apply();
                    game.reloadSettings();
                }
            }
            public void onStartTrackingTouch(SeekBar v){}
            public void onStopTrackingTouch(SeekBar v){}
        });
        LinearLayout control=new LinearLayout(this);
        control.setOrientation(LinearLayout.HORIZONTAL);
        control.setGravity(Gravity.CENTER_VERTICAL);
        Button minus=stepButton118("−"),plus=stepButton118("+");
        control.addView(minus,new LinearLayout.LayoutParams(dp118(38),dp118(35)));
        control.addView(bar,new LinearLayout.LayoutParams(0,dp118(35),1f));
        control.addView(plus,new LinearLayout.LayoutParams(dp118(38),dp118(35)));
        final Runnable persist=()->{
            int p=bar.getProgress();
            prefs.edit().putInt("cameraPanPercentV72",
                maximum>0?Math.round(p*100f/maximum):0).apply();
            game.reloadSettings();
        };
        minus.setOnClickListener(v->{bar.setProgress(Math.max(0,bar.getProgress()-1));
            persist.run();});
        plus.setOnClickListener(v->{bar.setProgress(Math.min(maximum,bar.getProgress()+1));
            persist.run();});
        box.addView(control,new LinearLayout.LayoutParams(dp118(235),dp118(38)));
        root.addView(box);
        root.addView(text("Extended camera pan follows your weapon; reopen Settings after swapping. Equal circular range in all directions. Zoom out for wider look-around.",11,false));
    }
    private void check(LinearLayout root,String title,String key,boolean def){
        CheckBox b=new CheckBox(this);b.setText(title);b.setTextColor(INK);b.setTextSize(13);
        b.setPadding(8,1,5,1);b.setChecked(prefs.getBoolean(key,def));root.addView(b);
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
    private void testTravel(float dx,float dy,String message){
        if(game!=null&&game.debugTeleport(dx,dy))
            Toast.makeText(this,message,Toast.LENGTH_SHORT).show();
        else
            Toast.makeText(this,"Start or continue a game before traveling",Toast.LENGTH_SHORT).show();
    }
    private void resizeSettingsWindow(AlertDialog dialog,int widthPct,int heightPct){
        if(dialog==null||dialog.getWindow()==null)return;
        int sw=getResources().getDisplayMetrics().widthPixels;
        int sh=getResources().getDisplayMetrics().heightPixels;
        int w=Math.min(sw,Math.max(sw*65/100,sw*widthPct/100));
        int h=Math.min(sh,Math.max(sh*65/100,sh*heightPct/100));
        dialog.getWindow().setLayout(w,h);
    }
    private void jumpButton(LinearLayout bar,String label,Runnable task){
        Button b=new Button(this);b.setText(label);b.setAllCaps(false);
        b.setTextSize(11);b.setMinHeight(0);b.setMinimumHeight(0);
        bar.addView(b,new LinearLayout.LayoutParams(0,-2,1f));
        b.setOnClickListener(v->task.run());
    }
    /** Compact one-column section navigation outside the settings scroll area. */
    private Button sideNavButton(LinearLayout nav,String title,Runnable click){
        Button button=new Button(this);
        button.setText(title);button.setAllCaps(false);button.setTextSize(11);
        button.setMinHeight(0);button.setMinimumHeight(0);
        button.setPadding(4,0,4,0);
        button.setTextColor(0xffd7e4de);
        button.setBackgroundColor(0xff2e4c50);
        int height=Math.max(31,Math.round(34*getResources().getDisplayMetrics().density));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,height);
        lp.bottomMargin=Math.max(2,Math.round(getResources().getDisplayMetrics().density*3));
        nav.addView(button,lp);button.setOnClickListener(v->click.run());
        return button;
    }
    // Separate from game settings: the actual HUD has its own layout editor.
    void hudEditor(){
        game.menuPause(true);
        // Compact newly acquired loot into the first available cells, adjacent
        // to existing stacks, before opening the inventory window.
        game.organizeBagV131(Math.max(0,Math.min(3,
            prefs.getInt("bagSortV131",0))));
        LinearLayout shell=column();
        section(shell,"HUD BUTTON EDITOR  •  V121 SCREENSHOT DEFAULTS");
        shell.addView(text("ALL HUD controls can be edited: top buttons, joysticks, status bars, resource/clock, FPS, squad, inventory and quickbar. Choose one, adjust with +/- or use ON-SCREEN DRAG.",12,false));
        ScrollView scroll=new ScrollView(this);
        scroll.setFillViewport(false);
        LinearLayout root=column();
        scroll.addView(root);
        section(root,"GLOBAL HUD VISIBILITY");
        slider(root,"Global HUD opacity","hudOpacityV73",15,100,100,"%");
        slider(root,"Top button background opacity","topButtonOpacityV76",0,65,22,"%");
        check(root,"Show FPS diagnostics","testPerf",false);
        check(root,"Compact performance readout","compactDebugV76",true);
        root.addView(text("Fades all HUD panels, controls, hotbar and status bars. Aim reticle and HUD editor remain visible.",11,false));
        section(root,"BUTTON SELECTION");
        Spinner picker=new Spinner(this);
        String[] choicesV87=new String[GameView.EDITOR_ITEMS];
        for(int item=0;item<choicesV87.length;item++)
            choicesV87[item]=game.controlName(item);
        picker.setAdapter(new ArrayAdapter<String>(this,
            android.R.layout.simple_spinner_dropdown_item,choicesV87));
        root.addView(picker);
        LinearLayout options=column();
        root.addView(options);
        int lastSelectedV87=prefs.getInt("selectedButton",0);
        picker.setSelection(Math.max(0,Math.min(GameView.EDITOR_ITEMS-1,lastSelectedV87)));
        picker.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(android.widget.AdapterView<?> parent){}
            public void onItemSelected(android.widget.AdapterView<?> parent,View item,int index,long id){
                int control=index;
                String title=game.controlName(control);
                prefs.edit().putInt("selectedButton",control).apply();
                options.removeAllViews();
                check(options,"Enable "+title,
                    "uiEnabled"+control,index>=LegacyControlsV58.COUNT||
                        LegacyControlsV58.defaultEnabled(index));
                slider(options,"SIZE","uiSize"+control,60,180,
                    index>=LegacyControlsV58.COUNT?100:
                    LegacyControlsV58.defaultScale(index),"%");
                slider(options,"OPACITY","uiAlpha"+control,30,100,100,"%");
                slider(options,"HORIZONTAL POSITION","uiX"+control,-420,420,0,"");
                slider(options,"VERTICAL POSITION","uiY"+control,-310,310,0,"");
            }
        });
        section(root,"LAYOUT ACTIONS");
        final AlertDialog[] active=new AlertDialog[1];
        action(root,"EDIT BUTTONS ON THE GAME SCREEN",()->{
            prefs.edit().putBoolean("editControls",true).apply();
            game.reloadSettings();
            if(active[0]!=null)active[0].dismiss();
            Toast.makeText(this,"Drag a button to reposition it. Open HUD EDIT to finish.",
                    Toast.LENGTH_LONG).show();
        });
        action(root,"FINISH EDITING / LOCK BUTTONS",()->{
            prefs.edit().putBoolean("editControls",false).apply();
            game.reloadSettings();
            if(active[0]!=null)active[0].dismiss();
        });
        action(root,"RESTORE ALL BUTTON DEFAULTS (SCREENSHOT V121)",()->{
            ScreenshotSettingsV121.applyHud(prefs,game.viewW,true);
            game.reloadSettings();
            if(active[0]!=null)active[0].dismiss();
            Toast.makeText(this,"V121 screenshot HUD restored",Toast.LENGTH_SHORT).show();
        });
        shell.addView(scroll,new LinearLayout.LayoutParams(-1,0,1f));
        AlertDialog dialog=new AlertDialog.Builder(this).setView(shell)
            .setPositiveButton("RETURN TO GAME",(d,w)->{})
            .create();
        active[0]=dialog;
        dialog.setOnDismissListener(d->{
            game.menuPause(false);restoreFullscreenAfterShade();
        });
        dialog.show();
        dialog.setCancelable(true);
        dialog.setCanceledOnTouchOutside(true);
        resizeSettingsWindow(dialog,98,96);
    }

    private void makeWindowMovable(AlertDialog dialog,View handle,
                                   int widthPct,int heightPct,String key){
        if(dialog==null||dialog.getWindow()==null)return;
        android.view.Window window=dialog.getWindow();
        window.setGravity(Gravity.TOP|Gravity.LEFT);
        int screenW=getResources().getDisplayMetrics().widthPixels;
        int screenH=getResources().getDisplayMetrics().heightPixels;
        int w=screenW*Math.max(60,Math.min(100,widthPct))/100;
        int h=screenH*Math.max(58,Math.min(98,heightPct))/100;
        WindowManager.LayoutParams init=window.getAttributes();
        init.width=w;init.height=h;
        init.x=Math.max(0,Math.min(screenW-w,prefs.getInt(key+"X",(screenW-w)/2)));
        init.y=Math.max(0,Math.min(screenH-h,prefs.getInt(key+"Y",(screenH-h)/2)));
        window.setAttributes(init);
        final float[] grab=new float[4];
        handle.setOnTouchListener((v,e)->{
            switch(e.getActionMasked()){
                case android.view.MotionEvent.ACTION_DOWN:
                    grab[0]=e.getRawX();grab[1]=e.getRawY();
                    grab[2]=window.getAttributes().x;grab[3]=window.getAttributes().y;
                    return true;
                case android.view.MotionEvent.ACTION_MOVE:
                    WindowManager.LayoutParams p=window.getAttributes();
                    p.x=Math.max(0,Math.min(screenW-p.width,Math.round(grab[2]+e.getRawX()-grab[0])));
                    p.y=Math.max(0,Math.min(screenH-p.height,Math.round(grab[3]+e.getRawY()-grab[1])));
                    window.setAttributes(p);return true;
                case android.view.MotionEvent.ACTION_UP:
                    prefs.edit().putInt(key+"X",window.getAttributes().x)
                        .putInt(key+"Y",window.getAttributes().y).apply();return true;
                case android.view.MotionEvent.ACTION_CANCEL:return true;
            }
            return false;
        });
    }
    /** V88 buttons retain the V62 palette but their measured height equals width. */
    /** V134 universal flat square cell: no gradients, lift or inconsistent inset. */
    private SquareItemSlotV88 v88SquareSlot(String title,boolean equipped){
        SquareItemSlotV88 button=new SquareItemSlotV88(this);
        button.setAllCaps(false);button.setText(title);button.setTextSize(9);
        button.setTextColor(0xffe5d9bd);
        button.setPadding(1,1,1,1);
        button.setMinHeight(0);button.setMinimumHeight(0);
        button.setMinWidth(0);button.setMinimumWidth(0);
        android.graphics.drawable.GradientDrawable bg=
            new android.graphics.drawable.GradientDrawable();
        bg.setColor(0xff293633);
        bg.setCornerRadius(0);
        bg.setStroke(Math.max(1,Math.round(getResources().
            getDisplayMetrics().density)),0xff687b72);
        button.setBackground(bg);
        return button;
    }

    private Button v62Slot(String title,boolean equipped){
        Button button=new Button(this);
        button.setAllCaps(false);button.setText(title);button.setTextSize(9);
        button.setTextColor(0xffe1cfac);
        button.setPadding(3,2,3,2);
        button.setMinHeight(0);button.setMinimumHeight(0);
        button.setMinWidth(0);button.setMinimumWidth(0);
        android.graphics.drawable.GradientDrawable bg=
            new android.graphics.drawable.GradientDrawable(
                android.graphics.drawable.GradientDrawable.Orientation.TL_BR,
                equipped?new int[]{0xff554335,0xff2c2521}:
                new int[]{0xff40342b,0xff201d1c});
        bg.setCornerRadius(5);
        bg.setStroke(2,equipped?0xffaa854d:0xff665747);
        button.setBackground(bg);
        return button;
    }

    /**
     * V87 dual-inventory bandit loot. Tap to select then LOOT, drag its icon
     * over PLAYER INVENTORY, or LOOT ALL. Only this bag's selected stacks move.
     */
    interface LootCountV95 { int at(int kind); }
    /** Android drag-and-drop. A touch MOVE starts a real drag, not a fake UP test. */
    void attachLootSourceV95(View source,int kind,int[] selected,
        Runnable[] refresh,LootCountV95 counts){
        final float[] from=new float[2];
        final boolean[] dragging={false};
        float threshold=8f*getResources().getDisplayMetrics().density;
        source.setOnTouchListener((v,e)->{
            switch(e.getActionMasked()){
                case android.view.MotionEvent.ACTION_DOWN:
                    if(counts.at(kind)<1)return true;
                    from[0]=e.getRawX();from[1]=e.getRawY();
                    dragging[0]=false;selected[0]=kind;
                    if(refresh[0]!=null)refresh[0].run();
                    return true;
                case android.view.MotionEvent.ACTION_MOVE:
                    if(!dragging[0]&&counts.at(kind)>0&&
                        Math.hypot(e.getRawX()-from[0],e.getRawY()-from[1])>threshold){
                        android.content.ClipData transfer=android.content.ClipData
                            .newPlainText("sp-loot-v95",Integer.toString(kind));
                        dragging[0]=v.startDragAndDrop(transfer,
                            new View.DragShadowBuilder(v),null,0);
                    }
                    return true;
                case android.view.MotionEvent.ACTION_UP:
                case android.view.MotionEvent.ACTION_CANCEL:
                    dragging[0]=false;return true;
                default:return true;
            }
        });
    }
    /** Attach to EACH receiving cell and its scroll frame for reliable drops. */
    View.OnDragListener lootDropV95(int[] selected,Runnable[] claim,int limit){
        return (target,event)->{
            int action=event.getAction();
            if(action==android.view.DragEvent.ACTION_DRAG_STARTED){
                return event.getClipDescription()!=null&&
                    event.getClipDescription().hasMimeType(
                        android.content.ClipDescription.MIMETYPE_TEXT_PLAIN);
            }
            if(action==android.view.DragEvent.ACTION_DROP){
                try{
                    String content=event.getClipData().getItemAt(0).getText().toString();
                    int type=Integer.parseInt(content);
                    if(type>=0&&type<limit){
                        selected[0]=type;
                        claim[0].run();return true;
                    }
                }catch(Exception ignored){}
                return false;
            }
            return true;
        };
    }
    /** V134: identical flat, edge-to-edge square slot geometry for both loot panes. */
    private SquareItemSlotV88[] lootGridV134(LinearLayout target,int total){
        final int columns=5;
        SquareItemSlotV88[] slots=new SquareItemSlotV88[total];
        for(int row=0;row<(total+columns-1)/columns;row++){
            LinearLayout line=new LinearLayout(this);
            line.setOrientation(LinearLayout.HORIZONTAL);
            target.addView(line,new LinearLayout.LayoutParams(-1,-2));
            for(int col=0;col<columns&&row*columns+col<total;col++){
                int position=row*columns+col;
                SquareItemSlotV88 tile=v88SquareSlot("",false);
                tile.setGravity(Gravity.CENTER);
                tile.setTextSize(8f);
                tile.setPadding(1,1,1,1);
                tile.setTag(-1);
                LinearLayout.LayoutParams params=
                    new LinearLayout.LayoutParams(0,-2,1f);
                int margin=Math.max(1,Math.round(getResources().
                    getDisplayMetrics().density));
                params.setMargins(margin,margin,margin,margin);
                line.addView(tile,params);
                slots[position]=tile;
            }
        }
        return slots;
    }
    /** V134: source and destination tiles draw the same item icon and label. */
    private android.graphics.drawable.Drawable lootIconV134(int type){
        if(type>=24&&type<39)
            return GearItemIconsV95.drawable(this,type-24,18);
        if(type>=14&&type<24)
            return FieldItemIconsV91.drawable(getResources(),type-14,18);
        return game.itemIconsV84.drawable(getResources(),
            type==10?ItemIconsV84.WATER_COLLECTOR:
            type==11?ItemIconsV84.FIELD_SHELTER:
            type==12?ItemIconsV84.BANDAGE:
            type==13?ItemIconsV84.ENERGY_RATION:type,18);
    }
    private void showLootTileV134(SquareItemSlotV88 cell,int type,int amount,
                                  boolean chosen){
        if(type<0||type>=39||amount<=0){
            cell.setText("");
            cell.setCompoundDrawables(null,null,null,null);
            cell.setContentDescription("Empty inventory slot");
            return;
        }
        String name=GameView.INVENTORY_NAMES_V92[type];
        cell.setText(name.substring(0,Math.min(7,name.length()))+
            "\n×"+amount+(chosen?" ✓":""));
        cell.setCompoundDrawables(null,lootIconV134(type),null,null);
        cell.setCompoundDrawablePadding(1);
        cell.setTextColor(chosen?0xfff6d37c:0xffe6d7b7);
        cell.setContentDescription(name+" ×"+amount);
    }
    /** A single, stable listener reads the current compacted source kind. */
    private void attachCompactLootTouchV134(SquareItemSlotV88 cell,int[] selected,
                                             Runnable[] refresh,LootCountV95 counts){
        final float[] first={0f,0f};
        final int[] pressed={-1};
        final boolean[] dragging={false};
        final float threshold=8f*getResources().getDisplayMetrics().density;
        cell.setOnClickListener(v->{
            Object tag=v.getTag();
            if(!(tag instanceof Integer))return;
            int kind=(Integer)tag;
            if(kind>=0&&counts.at(kind)>0){
                selected[0]=kind;
                if(refresh[0]!=null)refresh[0].run();
            }
        });
        cell.setOnTouchListener((v,e)->{
            int action=e.getActionMasked();
            if(action==android.view.MotionEvent.ACTION_DOWN){
                Object tag=v.getTag();
                pressed[0]=tag instanceof Integer?(Integer)tag:-1;
                if(pressed[0]<0||counts.at(pressed[0])<=0)return true;
                first[0]=e.getRawX();first[1]=e.getRawY();
                dragging[0]=false;selected[0]=pressed[0];
                if(refresh[0]!=null)refresh[0].run();
                return true;
            }
            if(action==android.view.MotionEvent.ACTION_MOVE){
                int kind=pressed[0];
                if(kind>=0&&counts.at(kind)>0&&!dragging[0]&&
                    Math.hypot(e.getRawX()-first[0],
                        e.getRawY()-first[1])>threshold){
                    android.content.ClipData data=android.content.ClipData.
                        newPlainText("sp-loot-v134",Integer.toString(kind));
                    dragging[0]=v.startDragAndDrop(data,
                        new View.DragShadowBuilder(v),null,0);
                }
                return true;
            }
            if(action==android.view.MotionEvent.ACTION_UP){
                if(!dragging[0]&&pressed[0]>=0)v.performClick();
                pressed[0]=-1;dragging[0]=false;return true;
            }
            if(action==android.view.MotionEvent.ACTION_CANCEL){
                pressed[0]=-1;dragging[0]=false;return true;
            }
            return true;
        });
    }
    interface LootTakeV134 { int take(int kind); }
    interface LootAllV134 { int take(); }
    /** V134 single grid layout for corpses, caches and indoor containers.
     * Neither destination nor source uses fixed item-type coordinates.
     */
    private void compactLootDialogV134(String title,String sourceTitle,int kinds,
                                       LootCountV95 counts,LootTakeV134 take,
                                       LootAllV134 takeAll,boolean closeWhenEmpty){
        game.menuPause(true);
        if(!game.bagOrderInitializedV92)game.initInventoryOrderV92();
        game.organizeBagV131(0);
        LinearLayout shell=column();
        shell.setBackgroundColor(0xff212825);
        section(shell,title);
        shell.addView(text("Select an item or drag it into PLAYER INVENTORY. "+
            "New items fill the next available slot.",11,false));
        LinearLayout sides=new LinearLayout(this);
        sides.setOrientation(LinearLayout.HORIZONTAL);
        shell.addView(sides,new LinearLayout.LayoutParams(-1,0,1f));
        LinearLayout source=column(),destination=column();
        source.setBackgroundColor(0xff29312e);
        destination.setBackgroundColor(0xff233b34);
        sides.addView(source,new LinearLayout.LayoutParams(0,-1,1f));
        sides.addView(destination,new LinearLayout.LayoutParams(0,-1,1f));
        section(source,sourceTitle);
        section(destination,"PLAYER INVENTORY");
        ScrollView srcScroll=new ScrollView(this),dstScroll=new ScrollView(this);
        LinearLayout srcItems=column(),dstItems=column();
        srcScroll.setFillViewport(false);dstScroll.setFillViewport(false);
        srcScroll.addView(srcItems);dstScroll.addView(dstItems);
        source.addView(srcScroll,new LinearLayout.LayoutParams(-1,0,1f));
        destination.addView(dstScroll,new LinearLayout.LayoutParams(-1,0,1f));
        final SquareItemSlotV88[] sourceCells=lootGridV134(srcItems,25);
        final SquareItemSlotV88[] playerCells=lootGridV134(dstItems,40);
        final int[] selected={-1};
        final Runnable[] refresh={null},claim={null};
        final AlertDialog[] active={null};
        refresh[0]=()->{
            int index=0;
            for(int kind=0;kind<kinds;kind++){
                int amount=counts.at(kind);
                if(amount<=0)continue;
                if(index>=sourceCells.length)break;
                SquareItemSlotV88 cell=sourceCells[index++];
                int inventoryType=kind<BanditLootV87.ITEMS?kind:
                    24+(kind-BanditLootV87.ITEMS);
                cell.setTag(kind);
                showLootTileV134(cell,inventoryType,amount,selected[0]==kind);
            }
            while(index<sourceCells.length){
                SquareItemSlotV88 cell=sourceCells[index++];
                cell.setTag(-1);showLootTileV134(cell,-1,0,false);
            }
            game.reconcileBagSplitsV130();
            for(int i=0;i<playerCells.length;i++){
                int type=game.bagOrderV92[i];
                int amount=game.bagSlotQuantityV130(i);
                showLootTileV134(playerCells[i],type,amount,false);
            }
        };
        claim[0]=()->{
            int kind=selected[0];
            if(kind<0||kind>=kinds||counts.at(kind)<=0)return;
            if(take.take(kind)>0){
                selected[0]=-1;
                game.organizeBagV131(0);
                refresh[0].run();
                if(closeWhenEmpty&&active[0]!=null){
                    boolean any=false;
                    for(int k=0;k<kinds;k++)if(counts.at(k)>0){any=true;break;}
                    if(!any)active[0].dismiss();
                }
            }
        };
        for(SquareItemSlotV88 cell:sourceCells)
            attachCompactLootTouchV134(cell,selected,refresh,counts);
        View.OnDragListener drop=lootDropV95(selected,claim,kinds);
        destination.setOnDragListener(drop);
        dstScroll.setOnDragListener(drop);
        dstItems.setOnDragListener(drop);
        for(SquareItemSlotV88 cell:playerCells)cell.setOnDragListener(drop);
        refresh[0].run();
        LinearLayout footer=new LinearLayout(this);
        footer.setOrientation(LinearLayout.HORIZONTAL);
        shell.addView(footer,new LinearLayout.LayoutParams(-1,-2));
        Button loot=v62Slot("LOOT",true),all=v62Slot("LOOT ALL",true),
            close=v62Slot("CLOSE",true);
        int footerHeight=Math.round(58f*getResources().getDisplayMetrics().density);
        for(Button button:new Button[]{loot,all,close}){
            button.setTextSize(12f);
            button.setGravity(Gravity.CENTER);
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,footerHeight,1f);
            lp.setMargins(2,4,2,3);footer.addView(button,lp);
        }
        loot.setOnClickListener(v->claim[0].run());
        all.setOnClickListener(v->{
            if(takeAll.take()>0){
                game.organizeBagV131(0);
                refresh[0].run();
                if(closeWhenEmpty&&active[0]!=null)active[0].dismiss();
            }
        });
        AlertDialog dialog=new AlertDialog.Builder(this).setView(shell).create();
        active[0]=dialog;
        close.setOnClickListener(v->dialog.dismiss());
        dialog.setOnDismissListener(d->{
            game.saveProgress();game.menuPause(false);restoreFullscreenAfterShade();
        });
        dialog.show();
        dialog.setCancelable(true);
        dialog.setCanceledOnTouchOutside(true);
        resizeSettingsWindow(dialog,94,88);
    }
    void lootBanditBagV87(BanditLootV87.Bag bag){
        if(game==null||bag==null||!game.banditLootV87.contains(bag)||
            !game.isPlaying()||game.nearbyBanditBagV87()!=bag)return;
        ExpeditionSitesV88.Site site=ExpeditionSitesV88.nearest(
            bag.x-115f,bag.y-91f,12f);
        compactLootDialogV134(
            bag.corpse?"FALLEN CHARACTER  •  SEARCH POSSESSIONS":
                site==null?"BANDIT BACKPACK  •  SEARCH & TRANSFER":
                site.name+"  •  SUPPLY CACHE",
            site==null?"BANDIT LOOT":"SCAVENGE SUPPLIES",
            BanditLootV87.ITEMS,
            kind->bag.count[kind],
            kind->game.lootBanditStackV87(bag,kind),
            ()->game.lootAllBanditV87(bag),true);
    }
    void lootClinicStorageV89(ClinicInteriorV89.Storage box){
        if(game==null||box==null||!game.insideClinicV89||
           !game.clinicInteriorV89.contains(box)||!game.isPlaying()||
            game.nearestAnyInteriorStorageV91(game.playerX,game.playerY,
                ClinicInteriorV89.USE_RADIUS)!=box)return;
        compactLootDialogV134(game.currentSiteNameV91()+" • "+box.label,
            "CONTAINER SUPPLIES",GearLootV95.TOTAL,
            kind->kind<BanditLootV87.ITEMS?box.amount[kind]:
                game.remainingGearV95(box,kind-BanditLootV87.ITEMS),
            kind->kind<BanditLootV87.ITEMS?
                game.lootClinicStackV89(box,kind):
                game.lootClinicGearV95(box,kind-BanditLootV87.ITEMS),
            ()->game.lootClinicAllV89(box),false);
    }
    /** V97 dedicated responsive NPC interface. Never combine setMessage and
     * setItems on one AlertDialog: on Android one can hide the other.
     */
    void npcInteractionV92(int role){
        if(game==null||!game.isPlaying()||game.nearbyNPCInteractionV92()<0)return;
        final int npc=Math.max(0,Math.min(4,role));
        game.menuPause(true);
        LinearLayout panel=column();
        panel.setPadding(14,10,14,10);
        panel.setBackgroundColor(0xff20302f);
        TextView header=text(NPCDialogueV97.ROLES[npc]+" • TALK / TRADE",19,true);
        header.setTextColor(0xffe5d3a7);panel.addView(header);
        TextView reputation=text("",13,false);panel.addView(reputation);
        Runnable refresh=()->reputation.setText("REPUTATION "+
            game.relationshipsV92.reputation+"  •  SCRAP "+game.scrap+
            "  •  ALLIES "+game.friends.size()+"/6");
        refresh.run();
        panel.addView(text(NPCDialogueV97.answer(npc,0),13,false));
        ScrollView scroll=new ScrollView(this);
        LinearLayout actions=column();
        scroll.addView(actions);
        panel.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        final AlertDialog[] shell={null};
        action(actions,"TALK  •  Ask questions",()->{
            new AlertDialog.Builder(this).setTitle(NPCDialogueV97.ROLES[npc]+" • QUESTIONS")
                .setItems(NPCDialogueV97.QUESTIONS,(d,question)->
                    new AlertDialog.Builder(this).setTitle(
                        NPCDialogueV97.QUESTIONS[question])
                        .setMessage(NPCDialogueV97.answer(npc,question))
                        .setPositiveButton("BACK",(reply,which)->{})
                        .show())
                .setNegativeButton("BACK",(d,which)->{})
                .show();
        });
        action(actions,"TRADE  •  Exchange real inventory",()->{
            String[] offers={"2 SCRAP → 1 MEDKIT","1 SCRAP → 2 FOOD",
                "1 SCRAP → 2 WATER"};
            new AlertDialog.Builder(this).setTitle("TRADE WITH "+
                NPCDialogueV97.ROLES[npc]).setItems(offers,(d,choice)->{
                    boolean ok=game.tradeNPCV92(choice);
                    refresh.run();
                    Toast.makeText(this,ok?"TRADE COMPLETED — "+offers[choice]:
                        "INSUFFICIENT SCRAP OR NPC OUT OF RANGE",Toast.LENGTH_SHORT).show();
                }).setNegativeButton("BACK",(d,w)->{}).show();
        });
        action(actions,"RECRUIT / FOLLOW  •  4 scrap, reputation 30+",()->{
            if(!NPCDialogueV97.recruitable(npc)){
                Toast.makeText(this,"This NPC cannot be recruited",
                    Toast.LENGTH_SHORT).show();return;
            }
            new AlertDialog.Builder(this).setTitle("RECRUIT COMPANION")
                .setMessage("Spend 4 scrap to recruit this friendly survivor? "+
                    "The companion will follow you outdoors and inside buildings. "+
                    "Requires reputation 30 or higher and an available ally slot.")
                .setPositiveButton("RECRUIT",(d,which)->{
                    boolean ok=game.tradeNPCV92(3);
                    refresh.run();
                    Toast.makeText(this,ok?"COMPANION RECRUITED — FOLLOWING":
                        "NEED 4 SCRAP, REPUTATION 30+, OR A FREE SLOT",
                        Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("CANCEL",(d,w)->{}).show();
        });
        action(actions,"GIVE ITEM  •  Transfer supplies",()->{
            String[] gifts={
                "FOOD  ×1 (you have "+game.foodCount+")",
                "WATER  ×1 (you have "+game.waterCount+")",
                "MEDKIT  ×1 (you have "+game.medkits+")",
                "SCRAP  ×2 (you have "+game.scrap+")",
                "BANDAGE  ×1 (you have "+game.bandagesV88+")"};
            new AlertDialog.Builder(this).setTitle("GIVE SUPPLIES TO "+
                NPCDialogueV97.ROLES[npc]).setItems(gifts,(d,which)->{
                    boolean ok=game.giveNPCV97(which);
                    refresh.run();
                    Toast.makeText(this,ok?"ITEM TRANSFERRED — TRUST +2":
                        "ITEM UNAVAILABLE OR NPC OUT OF RANGE",Toast.LENGTH_SHORT).show();
                }).setNegativeButton("BACK",(d,w)->{}).show();
        });
        action(actions,"LEAVE  •  Return to game",()->{
            if(shell[0]!=null)shell[0].dismiss();
        });
        AlertDialog dialog=new AlertDialog.Builder(this).setView(panel).create();
        shell[0]=dialog;
        dialog.setOnDismissListener(d->{
            game.menuPause(false);restoreFullscreenAfterShade();
        });
        dialog.show();
        dialog.setCancelable(true);
        resizeSettingsWindow(dialog,76,87);
    }
    /** Works for tap-to-drop and for a genuine bag-slot drag to the bin. */
    void dropQuantityDialogV129(int kind,Runnable refresh){
        if(game==null||kind<0||kind>=39)return;
        final int available=game.inventoryQuantityV92(kind);
        if(available<=0)return;
        final int[] selected={1};
        LinearLayout editor=column();
        editor.setPadding(24,16,24,10);
        TextView quantity=text("DROP 1 / "+available,16,true);
        quantity.setGravity(Gravity.CENTER);
        editor.addView(quantity);
        SeekBar slider=new SeekBar(this);
        slider.setMax(available-1);slider.setProgress(0);
        editor.addView(slider);
        LinearLayout steps=new LinearLayout(this);
        steps.setOrientation(LinearLayout.HORIZONTAL);
        Button minus=v62Slot("−",true),plus=v62Slot("+",true);
        steps.addView(minus,new LinearLayout.LayoutParams(0,-2,1f));
        steps.addView(plus,new LinearLayout.LayoutParams(0,-2,1f));
        editor.addView(steps);
        slider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar s,int progress,boolean fromUser){
                selected[0]=1+progress;
                quantity.setText("DROP "+selected[0]+" / "+available);
            }
            public void onStartTrackingTouch(SeekBar s){}
            public void onStopTrackingTouch(SeekBar s){}
        });
        minus.setOnClickListener(v->slider.setProgress(Math.max(0,slider.getProgress()-1)));
        plus.setOnClickListener(v->slider.setProgress(Math.min(
            slider.getMax(),slider.getProgress()+1)));
        new AlertDialog.Builder(this)
            .setTitle("DROP "+GameView.INVENTORY_NAMES_V92[kind])
            .setMessage("Place the selected quantity on the ground. "+
                "It remains for "+prefs.getInt("groundDropDaysV129",2)+
                " in-game day(s) and can be recovered.")
            .setView(editor)
            .setNegativeButton("CANCEL",null)
            .setPositiveButton("DROP",(d,w)->{
                boolean success=game.dropInventoryV129(kind,selected[0]);
                if(success&&refresh!=null)refresh.run();
                Toast.makeText(this,success?"Dropped "+selected[0]+" "+
                    GameView.INVENTORY_NAMES_V92[kind]:
                    "Could not drop this stack here",Toast.LENGTH_SHORT).show();
            }).show();
    }
    void dropByListV129(Runnable refresh){
        java.util.ArrayList<String> labels=new java.util.ArrayList<>();
        java.util.ArrayList<Integer> indexes=new java.util.ArrayList<>();
        for(int i=0;i<39;i++){
            int quantity=game.inventoryQuantityV92(i);
            if(quantity<=0)continue;
            indexes.add(i);
            labels.add(GameView.INVENTORY_NAMES_V92[i]+"  ×"+quantity);
        }
        if(labels.isEmpty()){
            Toast.makeText(this,"Inventory is empty",Toast.LENGTH_SHORT).show();return;
        }
        new AlertDialog.Builder(this).setTitle("CHOOSE ITEM TO DROP")
            .setItems(labels.toArray(new String[0]),
                (dialog,selected)->dropQuantityDialogV129(indexes.get(selected),refresh))
            .setNegativeButton("CANCEL",null).show();
    }
    void searchIndoorCorpseDialogV129(int corpseIndex){
        if(game==null||!game.insideClinicV89||corpseIndex<0||
            corpseIndex>=game.clinicActorsV90.actors.length)return;
        ClinicActorsV90.Actor actor=game.clinicActorsV90.actors[corpseIndex];
        if(actor.active)return;
        boolean looted=game.indoorCorpseSearchedV129(corpseIndex);
        new AlertDialog.Builder(this)
            .setTitle("SEARCH FALLEN CHARACTER")
            .setMessage(looted?"Already searched; nothing remains.":
                "Possessions: "+game.indoorCorpseContentsV129(corpseIndex))
            .setNegativeButton("CLOSE",null)
            .setPositiveButton("SEARCH",(d,w)->{
                if(!game.searchIndoorCorpseV129(corpseIndex))
                    Toast.makeText(this,looted?"Already searched":
                        "Move closer to search",Toast.LENGTH_SHORT).show();
            }).show();
    }
    void recoverDroppedV129(DroppedItemsV129.Stack stack){
        if(game==null||stack==null||!game.droppedItemsV129.contains(stack))return;
        new AlertDialog.Builder(this)
            .setTitle("PICK UP "+GameView.INVENTORY_NAMES_V92[stack.type])
            .setMessage("Recover "+stack.quantity+" item(s) from the ground?")
            .setNegativeButton("LEAVE",null)
            .setPositiveButton("PICK UP",(d,w)->{
                boolean taken=game.takeDroppedV129(stack);
                Toast.makeText(this,taken?"Recovered items":
                    "Cannot recover items at this location or capacity",
                    Toast.LENGTH_SHORT).show();
            }).show();
    }
    /** Quantity picker for either a real inventory split or dropping a stack. */
    void bagQuantityMenuV130(int position,boolean split,Runnable redraw){
        if(game==null||position<0||position>=40)return;
        game.reconcileBagSplitsV130();
        int quantity=game.bagSlotQuantityV130(position);
        int maximum=split?quantity-1:quantity;
        if(maximum<1)return;
        int kind=game.bagOrderV92[position];
        LinearLayout content=column();content.setPadding(20,14,20,10);
        TextView count=text("1 / "+maximum,15,true);
        count.setGravity(Gravity.CENTER);content.addView(count);
        SeekBar slider=new SeekBar(this);
        slider.setMax(maximum-1);content.addView(slider);
        LinearLayout line=new LinearLayout(this);
        line.setOrientation(LinearLayout.HORIZONTAL);
        Button minus=v62Slot("−",true),plus=v62Slot("+",true);
        line.addView(minus,new LinearLayout.LayoutParams(0,-2,1f));
        line.addView(plus,new LinearLayout.LayoutParams(0,-2,1f));
        content.addView(line);
        slider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar s,int progress,boolean fromUser){
                count.setText((progress+1)+" / "+maximum);
            }
            public void onStartTrackingTouch(SeekBar s){}
            public void onStopTrackingTouch(SeekBar s){}
        });
        minus.setOnClickListener(v->slider.setProgress(Math.max(0,slider.getProgress()-1)));
        plus.setOnClickListener(v->slider.setProgress(
            Math.min(slider.getMax(),slider.getProgress()+1)));
        new AlertDialog.Builder(this)
            .setTitle((split?"SPLIT ":"DROP ")+GameView.INVENTORY_NAMES_V92[kind])
            .setView(content)
            .setNegativeButton("CANCEL",null)
            .setPositiveButton(split?"SPLIT STACK":"DROP",(dialog,which)->{
                int n=slider.getProgress()+1;
                boolean ok=split?game.splitBagSlotV130(position,n):
                    game.dropBagSlotV130(position,n);
                if(ok){
                    if(redraw!=null)redraw.run();
                }else Toast.makeText(this,split?
                    "No empty bag slot is available":"Unable to drop this stack",
                    Toast.LENGTH_SHORT).show();
            }).show();
    }
    void bagItemMenuV130(int position,Runnable refresh,V62InventoryPreview avatar,
                         AlertDialog[] bagDialog,Runnable refreshEquipment){
        if(game==null||position<0||position>=40)return;
        game.reconcileBagSplitsV130();
        int kind=game.bagOrderV92[position],quantity=game.bagSlotQuantityV130(position);
        if(kind<0||kind>=39||quantity<=0)return;
        java.util.ArrayList<String> choices=new java.util.ArrayList<>();
        if(kind>=24)choices.add("EQUIP");
        else if(kind>=8&&kind<=11)choices.add("PLACE IN WORLD");
        else if(kind==1||kind==3||kind==4||kind==12||kind==13)
            choices.add("USE");
        if(kind<14)choices.add("ASSIGN QUICK SLOT");
        if(quantity>1)choices.add("SPLIT STACK");
        choices.add("DROP");
        choices.add("CANCEL");
        new AlertDialog.Builder(this)
            .setTitle(GameView.INVENTORY_NAMES_V92[kind]+" ×"+quantity+
                "\nUNIT WT "+InventoryCatalogV131.massLabel(kind,1)+
                "   STACK WT "+InventoryCatalogV131.massLabel(kind,quantity)+
                " LOAD")
            .setItems(choices.toArray(new String[0]),(dialog,chosen)->{
                String action=choices.get(chosen);
                if(action.equals("DROP")||action.equals("SPLIT STACK")){
                    bagQuantityMenuV130(position,action.equals("SPLIT STACK"),refresh);
                }else if(action.equals("EQUIP")){
                    int slot=InventoryCatalogV131.equipmentSlot(kind);
                    boolean equipped=game.equipInventoryItemV131(kind,slot);
                    if(equipped){
                        avatar.invalidate();refresh.run();
                        if(refreshEquipment!=null)refreshEquipment.run();
                    }
                    else Toast.makeText(this,"Unable to equip",Toast.LENGTH_SHORT).show();
                }else if(action.equals("PLACE IN WORLD")){
                    if(game.selectPlaceItemV84(kind-8)&&bagDialog[0]!=null)
                        bagDialog[0].dismiss();
                }else if(action.equals("USE")){
                    int useKind=kind==3?6:kind==4?7:kind==12?13:
                        kind==13?14:kind;
                    boolean ok=game.useBackpackV88(useKind);
                    if(!ok)Toast.makeText(this,"Cannot use this item now",
                        Toast.LENGTH_SHORT).show();
                    game.reconcileBagSplitsV130();
                    refresh.run();avatar.invalidate();
                }else if(action.equals("ASSIGN QUICK SLOT")){
                    String[] numbers={"SLOT 1","SLOT 2","SLOT 3",
                        "SLOT 4","SLOT 5","SLOT 6"};
                    new AlertDialog.Builder(this).setTitle("ASSIGN "+GameView.INVENTORY_NAMES_V92[kind])
                        .setItems(numbers,(d,index)->game.setHotbarItem(index,
                            kind>=8?kind+1:kind==3?6:kind==4?7:
                            kind==12?13:kind==13?14:kind))
                        .show();
                }
            }).show();
    }
    void inventory(){
        if(game==null||!game.isPlaying())return;
        game.menuPause(true);
        LinearLayout shell=column();
        shell.setBackgroundColor(0xff251e1a);
        TextView handle=text("✦  SURVIVAL PARADISE  •  INVENTORY & EQUIPMENT  ✦",14,true);
        handle.setGravity(Gravity.CENTER);
        handle.setTextColor(0xffe5b966);handle.setBackgroundColor(0xff60402d);
        shell.addView(handle);
        ScrollView scroll=new ScrollView(this);
        LinearLayout root=column();
        root.setBackgroundColor(0xff2e2521);scroll.addView(root);
        LinearLayout row=new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        root.addView(row);
        LinearLayout left=column(),right=column();
        left.setBackgroundColor(0xff302621);
        right.setBackgroundColor(0xff282321);
        row.addView(left,new LinearLayout.LayoutParams(0,-2,36f));
        row.addView(right,new LinearLayout.LayoutParams(0,-2,64f));
        section(left,"SURVIVOR   •   EQUIPMENT");
        final Runnable[] redrawV92={null};
        final Runnable[] refreshEquipmentV131={null};
        final AlertDialog[] bagDialogV84=new AlertDialog[1];
        final Button[] equipmentButtonsV131=new Button[8];
        final String[] equipment={"HEAD","FACE","TORSO","LEGS",
            "FEET","BACK","PRIMARY","OFF-HAND"};
        V62InventoryPreview avatar=new V62InventoryPreview(this,game);
        LinearLayout equipmentSurroundV131=new LinearLayout(this);
        equipmentSurroundV131.setOrientation(LinearLayout.HORIZONTAL);
        left.addView(equipmentSurroundV131);
        LinearLayout leftSocketsV131=column(),rightSocketsV131=column();
        int avatarHeightV131=Math.round(185*getResources().getDisplayMetrics().density);
        equipmentSurroundV131.addView(leftSocketsV131,
            new LinearLayout.LayoutParams(0,avatarHeightV131,1.1f));
        android.widget.FrameLayout avatarFrameV131=new android.widget.FrameLayout(this);
        avatarFrameV131.addView(avatar,
            new android.widget.FrameLayout.LayoutParams(-1,-1));
        equipmentSurroundV131.addView(avatarFrameV131,
            new LinearLayout.LayoutParams(0,avatarHeightV131,1.75f));
        equipmentSurroundV131.addView(rightSocketsV131,
            new LinearLayout.LayoutParams(0,avatarHeightV131,1.1f));
        for(int rowIndex=0;rowIndex<3;rowIndex++){
            int[] leftTypes={0,2,4},rightTypes={1,3,5};
            for(int side=0;side<2;side++){
                int ix=side==0?leftTypes[rowIndex]:rightTypes[rowIndex];
                Button socket=v62Slot(equipment[ix]+"\nEMPTY",true);
                socket.setTextSize(8.5f);
                LinearLayout holder=side==0?leftSocketsV131:rightSocketsV131;
                LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,0,1f);
                lp.setMargins(2,3,2,3);holder.addView(socket,lp);
                equipmentButtonsV131[ix]=socket;
            }
        }
        LinearLayout handsV131=new LinearLayout(this);
        handsV131.setOrientation(LinearLayout.HORIZONTAL);
        left.addView(handsV131);
        for(int ix=6;ix<8;ix++){
            Button socket=v62Slot(equipment[ix],true);
            socket.setTextSize(9f);
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,
                Math.round(67*getResources().getDisplayMetrics().density),1f);
            lp.setMargins(2,3,2,3);handsV131.addView(socket,lp);
            equipmentButtonsV131[ix]=socket;
        }
        refreshEquipmentV131[0]=()->{
            for(int ix=0;ix<equipmentButtonsV131.length;ix++){
                Button socket=equipmentButtonsV131[ix];
                if(socket==null)continue;
                int equippedType=-1;
                if(ix==5&&game.fieldFindsV91.equipped>=0)
                    equippedType=24+game.fieldFindsV91.equipped;
                else if(ix==0||ix==2||ix==3||ix==4){
                    int clothing=ix==0?0:ix==2?1:ix==3?2:3;
                    int variant=game.wardrobeV92.equipped[clothing];
                    if(variant>=0)equippedType=27+clothing*3+variant;
                }
                String value=equippedType>=0?
                    GameView.INVENTORY_NAMES_V92[equippedType]:
                    ix==6?LOADOUTS[game.gun]:
                    ix==7?(game.dualTorch&&game.lampOn?"FLASHLIGHT":"EMPTY"):
                    ix==1?"MASK SLOT":"EMPTY";
                if(value.length()>19)value=value.substring(0,19);
                socket.setText(equipment[ix]+"\n"+value);
                android.graphics.drawable.Drawable icon=
                    equippedType>=0?GearItemIconsV95.drawable(this,equippedType-24,29):
                    ix==6||ix==7?game.itemIconsV84.drawable(getResources(),
                        ix==7?ItemIconsV84.TORCH:ItemIconsV84.RIFLE,29):
                    GearItemIconsV95.silhouette(this,ix,29);
                socket.setCompoundDrawables(null,icon,null,null);
                socket.setCompoundDrawablePadding(1);
                socket.setContentDescription(equipment[ix]+
                    " equipment socket. "+value+". Drag compatible equipment here.");
            }
            avatar.invalidate();
        };
        for(int index=0;index<8;index++){
            final int socketIndex=index;
            Button socket=equipmentButtonsV131[index];
            socket.setOnDragListener((view,event)->{
                if(event.getAction()==android.view.DragEvent.ACTION_DRAG_STARTED)
                    return event.getClipDescription()!=null&&
                        event.getClipDescription().hasMimeType(
                            android.content.ClipDescription.MIMETYPE_TEXT_PLAIN);
                if(event.getAction()==android.view.DragEvent.ACTION_DROP){
                    try{
                        int position=Integer.parseInt(event.getClipData().
                            getItemAt(0).getText().toString());
                        if(position<0||position>=40)return false;
                        int type=game.bagOrderV92[position];
                        if(game.bagSlotQuantityV130(position)<1||
                           !InventoryCatalogV131.compatible(type,socketIndex))
                            return false;
                        boolean success=game.equipInventoryItemV131(type,socketIndex);
                        if(success){
                            refreshEquipmentV131[0].run();
                            if(redrawV92[0]!=null)redrawV92[0].run();
                        }
                        return success;
                    }catch(Exception ignored){return false;}
                }
                return true;
            });
            socket.setOnClickListener(view->{
                if(socketIndex==6){
                    new AlertDialog.Builder(this).setTitle("EQUIP PRIMARY WEAPON")
                        .setItems(LOADOUTS,(d,weapon)->{
                            prefs.edit().putInt("gun",weapon).apply();
                            game.reloadSettings();game.saveProgress();
                            refreshEquipmentV131[0].run();
                        }).show();
                    return;
                }
                if(socketIndex==7){
                    boolean enabled=!(game.lampOn&&game.dualTorch);
                    prefs.edit().putBoolean("dualTorch",enabled)
                        .putBoolean("lampOn",enabled).apply();
                    game.reloadSettings();game.saveProgress();
                    refreshEquipmentV131[0].run();return;
                }
                if(socketIndex==1){
                    Toast.makeText(this,"Face gear will appear here when obtained",
                        Toast.LENGTH_SHORT).show();return;
                }
                java.util.ArrayList<String> choices=new java.util.ArrayList<>();
                java.util.ArrayList<Integer> kinds=new java.util.ArrayList<>();
                choices.add("UNEQUIP / REMOVE");kinds.add(-1);
                for(int kind=24;kind<39;kind++){
                    if(InventoryCatalogV131.compatible(kind,socketIndex)&&
                       game.availableInventoryV131(kind)>0){
                        choices.add(GameView.INVENTORY_NAMES_V92[kind]+" ×"+
                            game.availableInventoryV131(kind));
                        kinds.add(kind);
                    }
                }
                new AlertDialog.Builder(this)
                    .setTitle(equipment[socketIndex]+" EQUIPMENT")
                    .setItems(choices.toArray(new String[0]),(dialog,which)->{
                        int kind=kinds.get(which);
                        boolean success=kind<0?
                            game.unequipInventorySlotV131(socketIndex):
                            game.equipInventoryItemV131(kind,socketIndex);
                        if(success){
                            refreshEquipmentV131[0].run();
                            if(redrawV92[0]!=null)redrawV92[0].run();
                        }else Toast.makeText(this,"Equipment unavailable",
                            Toast.LENGTH_SHORT).show();
                    }).show();
            });
        }
        refreshEquipmentV131[0].run();
        LinearLayout vital=new LinearLayout(this);
        vital.setOrientation(LinearLayout.HORIZONTAL);
        vital.addView(text("HP "+Math.round(game.health),12,true),
            new LinearLayout.LayoutParams(0,-2,1));
        vital.addView(text("STA "+Math.round(game.stamina),12,true),
            new LinearLayout.LayoutParams(0,-2,1));
        vital.addView(text("FOOD "+game.foodCount+"   WATER "+game.waterCount,12,true),
            new LinearLayout.LayoutParams(0,-2,2));
        left.addView(vital);
        // V96 cosmetic selection: 20 original isolated pack sprites and four
        // approved headgear designs. Capacity/loot/save game systems unchanged.
        LinearLayout appearanceV96=new LinearLayout(this);
        appearanceV96.setOrientation(LinearLayout.HORIZONTAL);
        Button packLookV96=v62Slot("PACK LOOK\n"+WearableArtV96.PACK_NAMES[game.backpackStyleV96],true);
        Button headLookV96=v62Slot("HEADGEAR LOOK\n"+WearableArtV96.HEAD_NAMES[game.headgearStyleV96],true);
        packLookV96.setOnClickListener(v->new AlertDialog.Builder(this)
            .setTitle("BACKPACK APPEARANCE — 20 STYLES")
            .setSingleChoiceItems(WearableArtV96.PACK_NAMES,game.backpackStyleV96,(d,i)->{
                game.backpackStyleV96=i;game.saveProgress();avatar.invalidate();
                packLookV96.setText("PACK LOOK\n"+WearableArtV96.PACK_NAMES[i]);d.dismiss();
            }).show());
        headLookV96.setOnClickListener(v->new AlertDialog.Builder(this)
            .setTitle("APPROVED HEADGEAR — 4 STYLES")
            .setSingleChoiceItems(WearableArtV96.HEAD_NAMES,game.headgearStyleV96,(d,i)->{
                game.headgearStyleV96=i;game.saveProgress();avatar.invalidate();
                headLookV96.setText("HEADGEAR LOOK\n"+WearableArtV96.HEAD_NAMES[i]);d.dismiss();
            }).show());
        Button bootLookV133=v62Slot("BOOTS LOOK\n"+
            BootArtV133.NAMES[game.bootStyleV133],true);
        bootLookV133.setOnClickListener(v->new AlertDialog.Builder(this)
            .setTitle("V133 APPROVED BOOTS — 5 ANIMATED DESIGNS")
            .setSingleChoiceItems(BootArtV133.NAMES,game.bootStyleV133,(d,i)->{
                game.bootStyleV133=BootArtV133.clampStyle(i);
                game.saveProgress();avatar.invalidate();
                bootLookV133.setText("BOOTS LOOK\n"+BootArtV133.NAMES[i]);
                d.dismiss();
            }).show());
        appearanceV96.addView(packLookV96,new LinearLayout.LayoutParams(0,-2,1));
        appearanceV96.addView(headLookV96,new LinearLayout.LayoutParams(0,-2,1));
        appearanceV96.addView(bootLookV133,new LinearLayout.LayoutParams(0,-2,1));
        left.addView(appearanceV96);
        left.addView(text("Carry capacity: "+game.fieldFindsV91.capacity()+
            " • ENC "+Math.round(game.encumbranceV91())+"% • Packs appear on the survivor.",12,false));
        section(right,"BACKPACK   •   40 COMPACT SLOTS");
        LinearLayout sortBarV131=new LinearLayout(this);
        sortBarV131.setOrientation(LinearLayout.HORIZONTAL);
        right.addView(sortBarV131);
        Button sortV131=v62Slot("SORT ▾",true);
        TextView sortingV131=text("TYPE  •  WEIGHT  •  NAME",11,false);
        sortBarV131.addView(sortV131,
            new LinearLayout.LayoutParams(0,-2,1.3f));
        sortBarV131.addView(sortingV131,
            new LinearLayout.LayoutParams(0,-2,2f));
        sortV131.setOnClickListener(v->new AlertDialog.Builder(this)
            .setTitle("SORT BACKPACK")
            .setItems(new String[]{"GROUP & COMPACT","ITEM TYPE",
                "WEIGHT (HEAVIEST FIRST)","NAME (A–Z)"},(dialog,which)->{
                game.organizeBagV131(which);
                sortingV131.setText(new String[]{"GROUPED","BY TYPE",
                    "BY WEIGHT","A–Z"}[which]);
                if(redrawV92[0]!=null)redrawV92[0].run();
                prefs.edit().putInt("bagSortV131",which).apply();
            }).show());
        right.addView(text("Tap an item for weight, actions, splitting and dropping.",11,false));
        final Button[] backpackStackButtonsV83=new Button[14];
        final SquareItemSlotV88[] tilesV92=new SquareItemSlotV88[40];
        final int[] currentDragSourceV130={-1};
        final boolean[] dragLeftWindowV130={false};
        final boolean[] dragHandledV130={false};
        final Runnable refreshCraftCountsV83=()->{
            if(redrawV92[0]!=null)redrawV92[0].run();
        };
        if(!game.bagOrderInitializedV92)game.initInventoryOrderV92();
        game.organizeBagV131(0); // V134: first row starts at the first slot.
        game.reconcileBagSplitsV130();
        right.addView(text("Hold and drag items between slots, or onto DROP HERE. "+
            "Use DROP ITEM for a selectable list and quantity slider.",11,false));
        for(int ir=0;ir<5;ir++){
            LinearLayout slots=new LinearLayout(this);
            slots.setOrientation(LinearLayout.HORIZONTAL);
            for(int ic=0;ic<8;ic++){
                final int position=ir*8+ic;
                SquareItemSlotV88 slot=v88SquareSlot("",false);
                tilesV92[position]=slot;
                slot.setGravity(Gravity.CENTER);
                slot.setTextSize(8f);
                slot.setPadding(1,1,1,1);
                // V134 weighted cells occupy the entire row, never clip horizontally.
                LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(0,-2,1f);
                int margin=Math.max(1,Math.round(getResources().
                    getDisplayMetrics().density));
                params.setMargins(margin,margin,margin,margin);
                slots.addView(slot,params);
                slot.setOnLongClickListener(v->{
                    int type=game.bagOrderV92[position];
                    if(game.bagSlotQuantityV130(position)<=0)return false;
                    currentDragSourceV130[0]=position;
                    dragHandledV130[0]=false;
                    dragLeftWindowV130[0]=false;
                    android.content.ClipData data=android.content.ClipData.newPlainText(
                        "sp-inventory-slot",Integer.toString(position));
                    return v.startDragAndDrop(data,new View.DragShadowBuilder(v),null,0);
                });
                slot.setOnDragListener((v,event)->{
                    if(event.getAction()==android.view.DragEvent.ACTION_DRAG_LOCATION){
                        int[] viewPos=new int[2],containerPos=new int[2];
                        v.getLocationOnScreen(viewPos);
                        scroll.getLocationOnScreen(containerPos);
                        float y=viewPos[1]+event.getY();
                        float upper=containerPos[1],lower=upper+scroll.getHeight();
                        int step=Math.round(28*getResources().getDisplayMetrics().density);
                        if(y<upper+72)scroll.smoothScrollBy(0,-step);
                        else if(y>lower-72)scroll.smoothScrollBy(0,step);
                        return true;
                    }
                    if(event.getAction()==android.view.DragEvent.ACTION_DRAG_ENDED){
                        if(!event.getResult()&&dragLeftWindowV130[0]&&
                           !dragHandledV130[0]&&
                           currentDragSourceV130[0]==position){
                            dragHandledV130[0]=true;
                            v.post(()->bagQuantityMenuV130(position,false,redrawV92[0]));
                        }
                        return true;
                    }
                    if(event.getAction()==android.view.DragEvent.ACTION_DRAG_STARTED)
                        return event.getClipDescription()!=null&&
                            event.getClipDescription().hasMimeType(
                                android.content.ClipDescription.MIMETYPE_TEXT_PLAIN);
                    if(event.getAction()==android.view.DragEvent.ACTION_DROP){
                        try{
                            int source=Integer.parseInt(event.getClipData()
                                .getItemAt(0).getText().toString());
                            if(game.moveBagSlotV92(source,position)){
                                dragHandledV130[0]=true;
                                redrawV92[0].run();
                                return true;
                            }
                        }catch(Exception ignored){}
                    }
                    return true;
                });
                slot.setOnClickListener(v->bagItemMenuV130(
                    position,redrawV92[0],avatar,bagDialogV84,refreshEquipmentV131[0]));
            }
            right.addView(slots);
        }
        // Dedicated inventory discard area accepts Android drag-and-drop
        // from ANY of the 40 slots; all deletions require amount confirmation.
        LinearLayout discardRowV129=new LinearLayout(this);
        discardRowV129.setOrientation(LinearLayout.HORIZONTAL);
        right.addView(discardRowV129);
        Button dropSelectV129=v62Slot("DROP ITEM",true);
        Button trashV129=v62Slot("DROP HERE",true);
        trashV129.setCompoundDrawablesWithIntrinsicBounds(
            android.R.drawable.ic_menu_delete,0,0,0);
        trashV129.setContentDescription("Drop item here; choose an amount");
        discardRowV129.addView(dropSelectV129,
            new LinearLayout.LayoutParams(0,-2,1f));
        discardRowV129.addView(trashV129,
            new LinearLayout.LayoutParams(0,-2,1f));
        dropSelectV129.setOnClickListener(v->dropByListV129(redrawV92[0]));
        trashV129.setOnClickListener(v->dropByListV129(redrawV92[0]));
        trashV129.setOnDragListener((v,event)->{
            if(event.getAction()==android.view.DragEvent.ACTION_DRAG_STARTED)
                return event.getClipDescription()!=null&&
                    event.getClipDescription().hasMimeType(
                        android.content.ClipDescription.MIMETYPE_TEXT_PLAIN);
            if(event.getAction()==android.view.DragEvent.ACTION_DROP){
                try{
                    int source=Integer.parseInt(event.getClipData().getItemAt(0)
                        .getText().toString());
                    if(source<0||source>=game.bagOrderV92.length)return false;
                    if(game.bagSlotQuantityV130(source)<=0)return false;
                    dragHandledV130[0]=true;
                    bagQuantityMenuV130(source,false,redrawV92[0]);
                    return true;
                }catch(Exception ignored){return false;}
            }
            return true;
        });
        redrawV92[0]=()->{
            game.reconcileBagSplitsV130();
            for(int position=0;position<tilesV92.length;position++){
                SquareItemSlotV88 tile=tilesV92[position];
                int kind=game.bagOrderV92[position],qty=game.bagSlotQuantityV130(position);
                if(qty<=0){
                    tile.setText("");
                    tile.setCompoundDrawables(null,null,null,null);
                    tile.setContentDescription("Empty inventory slot");
                }else{
                    String name=GameView.INVENTORY_NAMES_V92[kind];
                    tile.setText((name.length()>7?name.substring(0,6):name)+"\n×"+qty);
                    android.graphics.drawable.Drawable itemIcon=kind>=24&&kind<39?
                        GearItemIconsV95.drawable(this,kind-24,18):
                        kind>=14?FieldItemIconsV91.drawable(getResources(),kind-14,18):
                        game.itemIconsV84.drawable(getResources(),
                            kind==10?ItemIconsV84.WATER_COLLECTOR:
                            kind==11?ItemIconsV84.FIELD_SHELTER:
                            kind==12?ItemIconsV84.BANDAGE:
                            kind==13?ItemIconsV84.ENERGY_RATION:kind,18);
                    tile.setCompoundDrawables(null,itemIcon,null,null);
                    tile.setCompoundDrawablePadding(1);
                    tile.setContentDescription(name+" "+qty+" items; hold to drag");
                }
            }
        };
        // A dragged item released outside the slots (or beyond this dialog)
        // uses the same confirmed quantity picker as the trash icon.
        View.OnDragListener outsideDropV130=(target,event)->{
            int action=event.getAction();
            if(action==android.view.DragEvent.ACTION_DRAG_STARTED)return true;
            if(action==android.view.DragEvent.ACTION_DRAG_EXITED){
                dragLeftWindowV130[0]=true;return true;
            }
            if(action==android.view.DragEvent.ACTION_DRAG_ENTERED){
                dragLeftWindowV130[0]=false;return true;
            }
            if(action==android.view.DragEvent.ACTION_DROP){
                if(!dragHandledV130[0]){
                    int source=currentDragSourceV130[0];
                    if(source>=0&&game.bagSlotQuantityV130(source)>0){
                        dragHandledV130[0]=true;
                        bagQuantityMenuV130(source,false,redrawV92[0]);
                    }
                }
                return true;
            }
            return true;
        };
        shell.setOnDragListener(outsideDropV130);
        left.setOnDragListener(outsideDropV130);
        scroll.setOnDragListener(outsideDropV130);
        right.setOnDragListener(outsideDropV130);
        redrawV92[0].run();
        section(right,"CRAFT & PLACE IN WORLD");
        right.addView(text("CRAFT → BAG. Select a structure, point using AIM, then press USE to place. Press BAG to cancel.",11,false));
        LinearLayout recipesV83=new LinearLayout(this);
        recipesV83.setOrientation(LinearLayout.HORIZONTAL);
        right.addView(recipesV83);
        Button craftWall=v62Slot("BARRICADE\n4 WOOD + 2 STONE",true);
        Button craftLight=v62Slot("LIGHT POST\n2 WOOD + 2 FIBER + 1 SCRAP",true);
        int recipeHeight=Math.round(49*getResources().getDisplayMetrics().density);
        recipesV83.addView(craftWall,new LinearLayout.LayoutParams(0,recipeHeight,1));
        recipesV83.addView(craftLight,new LinearLayout.LayoutParams(0,recipeHeight,1));
        craftWall.setOnClickListener(v->{
            boolean built=game.craftIntoBagV84(CampCraftV83.BARRICADE);
            Toast.makeText(this,built?"Barricade added to bag":game.craftV83.error,Toast.LENGTH_SHORT).show();
            if(built){refreshCraftCountsV83.run();avatar.invalidate();}
        });
        craftLight.setOnClickListener(v->{
            boolean built=game.craftIntoBagV84(CampCraftV83.LIGHT_POST);
            Toast.makeText(this,built?"Light post added to bag":game.craftV83.error,Toast.LENGTH_SHORT).show();
            if(built){refreshCraftCountsV83.run();avatar.invalidate();}
        });
        LinearLayout supportV88=new LinearLayout(this);
        supportV88.setOrientation(LinearLayout.HORIZONTAL);
        right.addView(supportV88);
        Button waterCollector=v62Slot("WATER COLLECTOR\n3 WOOD · 2 STONE · 3 FIBER · 1 SCRAP",true);
        Button shelter=v62Slot("FIELD SHELTER\n5 WOOD · 4 FIBER · 1 SCRAP",true);
        supportV88.addView(waterCollector,new LinearLayout.LayoutParams(0,
            Math.round(60*getResources().getDisplayMetrics().density),1f));
        supportV88.addView(shelter,new LinearLayout.LayoutParams(0,
            Math.round(60*getResources().getDisplayMetrics().density),1f));
        waterCollector.setOnClickListener(v->{
            boolean ok=game.craftIntoBagV84(CampCraftV83.WATER_COLLECTOR);
            Toast.makeText(this,ok?"Water collector added to bag":game.craftV83.error,Toast.LENGTH_SHORT).show();
            if(ok){refreshCraftCountsV83.run();avatar.invalidate();}
        });
        shelter.setOnClickListener(v->{
            boolean ok=game.craftIntoBagV84(CampCraftV83.FIELD_SHELTER);
            Toast.makeText(this,ok?"Field shelter added to bag":game.craftV83.error,Toast.LENGTH_SHORT).show();
            if(ok){refreshCraftCountsV83.run();avatar.invalidate();}
        });
        LinearLayout utilityRecipesV88=new LinearLayout(this);
        utilityRecipesV88.setOrientation(LinearLayout.HORIZONTAL);
        right.addView(utilityRecipesV88);
        Button bandageButton=v62Slot("CRAFT BANDAGE\n2 FIBER + 1 SCRAP",true);
        Button energyButton=v62Slot("CRAFT ENERGY RATION\n1 FOOD + 1 WATER",true);
        utilityRecipesV88.addView(bandageButton,new LinearLayout.LayoutParams(0,
            Math.round(57*getResources().getDisplayMetrics().density),1));
        utilityRecipesV88.addView(energyButton,new LinearLayout.LayoutParams(0,
            Math.round(57*getResources().getDisplayMetrics().density),1));
        bandageButton.setOnClickListener(v->{
            boolean ok=game.craftConsumableV88(0);
            Toast.makeText(this,ok?"Bandage added to bag":"Need 2 fiber and 1 scrap",
                Toast.LENGTH_SHORT).show();
            if(ok){refreshCraftCountsV83.run();avatar.invalidate();}
        });
        energyButton.setOnClickListener(v->{
            boolean ok=game.craftConsumableV88(1);
            Toast.makeText(this,ok?"Energy ration added to bag":"Need food and water",
                Toast.LENGTH_SHORT).show();
            if(ok){refreshCraftCountsV83.run();avatar.invalidate();}
        });

        section(right,"QUICK ACCESS   •   6 SLOTS");
        right.addView(text("Tap a quick slot to choose an item. It appears on the gameplay HUD.",12,false));
        LinearLayout quickRow=new LinearLayout(this);
        quickRow.setOrientation(LinearLayout.HORIZONTAL);
        right.addView(quickRow);
        final Runnable[] refresh=new Runnable[1];
        refresh[0]=()->{
            quickRow.removeAllViews();
            for(int i=0;i<6;i++){
                final int slotIndex=i,item=game.hotbar[i];
                Button hot=v62Slot((i+1)+"\n"+GameView.hotbarLabel(item),true);
                hot.setCompoundDrawables(null,game.itemIconsV84.drawable(getResources(),
                    ItemIconsV84.hotbarType(item),31),null,null);
                hot.setCompoundDrawablePadding(2);
                hot.setGravity(Gravity.CENTER);
                hot.setTextSize(10f);
                hot.setPadding(1,2,1,1);
                LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,
                    Math.round(74*getResources().getDisplayMetrics().density),1);
                p.setMargins(2,2,2,2);quickRow.addView(hot,p);
                hot.setOnDragListener((v,event)->{
                    if(event.getAction()==android.view.DragEvent.ACTION_DRAG_STARTED)
                        return event.getClipDescription()!=null&&
                            event.getClipDescription().hasMimeType(
                                android.content.ClipDescription.MIMETYPE_TEXT_PLAIN);
                    if(event.getAction()==android.view.DragEvent.ACTION_DROP){
                        try{
                            int from=Integer.parseInt(event.getClipData()
                                .getItemAt(0).getText().toString());
                            int type=game.bagOrderV92[from];
                            int draggedItem=type==3?6:type==4?7:
                                type>=8&&type<=13?type+1:type;
                            if(game.inventoryQuantityV92(type)>0&&type<=13&&
                                type!=0&&type!=5&&type!=6&&type!=7){
                                game.setHotbarItem(slotIndex,draggedItem);
                                refresh[0].run();return true;
                            }
                        }catch(Exception ignored){}
                    }
                    return true;
                });
                hot.setOnClickListener(v->{
                    new AlertDialog.Builder(this).setTitle("ASSIGN QUICK SLOT "+(slotIndex+1))
                      .setItems(GameView.HOTBAR_TYPES,(d,which)->{
                          game.setHotbarItem(slotIndex,which);refresh[0].run();
                      }).show();
                });
            }
        };
        refresh[0].run();
        root.addView(text("Wearable hats, jackets, trousers, boots and backpacks are found in searchable cases. Equipment overlays retain the original approved survivor pixels.",12,false));
        shell.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout tools=new LinearLayout(this);tools.setOrientation(LinearLayout.HORIZONTAL);
        Button smaller=v62Slot("WINDOW −",true),larger=v62Slot("WINDOW +",true);
        Button closeBag=v62Slot("CLOSE BAG",true);
        int footerDp=Math.round(50*getResources().getDisplayMetrics().density);
        tools.addView(smaller,new LinearLayout.LayoutParams(0,footerDp,1));
        tools.addView(larger,new LinearLayout.LayoutParams(0,footerDp,1));
        tools.addView(closeBag,new LinearLayout.LayoutParams(0,footerDp,1));
        shell.addView(tools);
        // A compact in-panel footer avoids Android AlertDialog’s large button strip.
        AlertDialog dialog=new AlertDialog.Builder(this).setView(shell).create();
        closeBag.setOnClickListener(v->dialog.dismiss());
        dialog.setOnDismissListener(d->{
            game.saveProgress();game.menuPause(false);restoreFullscreenAfterShade();
        });
        dialog.show();
        dialog.setCancelable(true);
        dialog.setCanceledOnTouchOutside(true);
        bagDialogV84[0]=dialog;
        final int[] width={prefs.getInt("bagWindowWidth",94)},
                    height={prefs.getInt("bagWindowHeight",92)};
        makeWindowMovable(dialog,handle,width[0],height[0],"bagWindow");
        smaller.setOnClickListener(v->{
            width[0]=Math.max(60,width[0]-5);height[0]=Math.max(58,height[0]-5);
            prefs.edit().putInt("bagWindowWidth",width[0]).putInt("bagWindowHeight",height[0]).apply();
            makeWindowMovable(dialog,handle,width[0],height[0],"bagWindow");
        });
        larger.setOnClickListener(v->{
            width[0]=Math.min(98,width[0]+5);height[0]=Math.min(98,height[0]+5);
            prefs.edit().putInt("bagWindowWidth",width[0]).putInt("bagWindowHeight",height[0]).apply();
            makeWindowMovable(dialog,handle,width[0],height[0],"bagWindow");
        });
    }
    /** Native in-game companion command panel, accessible from the HUD. */
    void companionCommandsV118(){
        if(game==null)return;
        game.menuPause(true);
        LinearLayout root=column();
        section(root,"COMPANION COMMANDS");
        root.addView(text("Orders apply immediately to recruited companions, including inside buildings.",12,false));
        final Button[] motion=new Button[1],fire=new Button[1],formation=new Button[1];
        motion[0]=action(root,game.companionStayV118?"FOLLOW ME":"STAY",()->{
            prefs.edit().putBoolean("companionStayV118",!game.companionStayV118).apply();
            game.reloadSettings();
            motion[0].setText(game.companionStayV118?"FOLLOW ME":"STAY");
        });
        fire[0]=action(root,game.companionHoldFireV118?"FIRE AT WILL":"HOLD FIRE",()->{
            prefs.edit().putBoolean("companionHoldFireV118",!game.companionHoldFireV118).apply();
            game.reloadSettings();
            fire[0].setText(game.companionHoldFireV118?"FIRE AT WILL":"HOLD FIRE");
        });
        formation[0]=action(root,"FORM: "+FollowFormationV61.NAMES[game.followMode],()->{
            int next=(game.followMode+1)%FollowFormationV61.NAMES.length;
            prefs.edit().putInt("followMode",next).apply();game.reloadSettings();
            formation[0].setText("FORM: "+FollowFormationV61.NAMES[game.followMode]);
        });
        section(root,"FOLLOW DISTANCE");
        slider(root,"Companion follow distance","followSpacing",
            CompanionOrdersV118.MIN_SPACING,CompanionOrdersV118.MAX_SPACING,
            CompanionOrdersV118.DEFAULT_SPACING," px");
        root.addView(text("Follow distance controls formation standoff from the player. STAY holds current positions; HOLD FIRE prevents companion gunfire. All orders persist.",11,false));
        final AlertDialog d=new AlertDialog.Builder(this).setView(root)
            .setPositiveButton("RETURN TO GAME",(dialog,which)->{}).create();
        d.setOnDismissListener(dialog->{
            game.menuPause(false);restoreFullscreenAfterShade();
        });
        d.show();
        d.setCanceledOnTouchOutside(true);
    }

    void settings(){
        game.menuPause(true);
        final AlertDialog[] activeDialog=new AlertDialog[1];
        LinearLayout shell=column();
        shell.setPadding(8,4,8,4);
        TextView dragTitle=text("⋮⋮ SETTINGS • DRAG HEADER TO MOVE WINDOW ⋮⋮",14,true);
        dragTitle.setGravity(Gravity.CENTER);
        dragTitle.setBackgroundColor(0xff355a62);
        shell.addView(dragTitle);
        final int windowW=prefs.getInt("testWindowWidth",98);
        final int windowH=prefs.getInt("testWindowHeight",96);
        LinearLayout sizeRow=new LinearLayout(this);
        sizeRow.setOrientation(LinearLayout.HORIZONTAL);
        final TextView wLabel=text("WIDTH "+windowW+"%",11,false);
        final TextView hLabel=text("HEIGHT "+windowH+"%",11,false);
        final SeekBar wSize=new SeekBar(this),hSize=new SeekBar(this);
        wSize.setMax(35);wSize.setProgress(windowW-65);
        hSize.setMax(35);hSize.setProgress(windowH-65);
        LinearLayout wGroup=column(),hGroup=column();
        wGroup.addView(wLabel);wGroup.addView(wSize);
        hGroup.addView(hLabel);hGroup.addView(hSize);
        sizeRow.addView(wGroup,new LinearLayout.LayoutParams(0,-2,1f));
        sizeRow.addView(hGroup,new LinearLayout.LayoutParams(0,-2,1f));
        // V77: window size controls move into LAYOUT rather than consume header space.
        wSize.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar b,int v,boolean user){
                int pct=65+v;wLabel.setText("WIDTH "+pct+"%");
                if(user){prefs.edit().putInt("testWindowWidth",pct).apply();
                    resizeSettingsWindow(activeDialog[0],pct,65+hSize.getProgress());}
            }
            public void onStartTrackingTouch(SeekBar b){}
            public void onStopTrackingTouch(SeekBar b){}
        });
        hSize.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar b,int v,boolean user){
                int pct=65+v;hLabel.setText("HEIGHT "+pct+"%");
                if(user){prefs.edit().putInt("testWindowHeight",pct).apply();
                    resizeSettingsWindow(activeDialog[0],65+wSize.getProgress(),pct);}
            }
            public void onStartTrackingTouch(SeekBar b){}
            public void onStopTrackingTouch(SeekBar b){}
        });
        // Left: independent, narrow section navigation. Right: the full-height
        // scrollable settings list; no stacked horizontal category button rows.
        LinearLayout contentRow=new LinearLayout(this);
        contentRow.setOrientation(LinearLayout.HORIZONTAL);
        ScrollView navScroll=new ScrollView(this);
        navScroll.setVerticalScrollBarEnabled(false);
        navScroll.setFillViewport(false);
        LinearLayout navigation=column();
        navigation.setPadding(3,3,3,3);
        navScroll.addView(navigation);
        int screenWidth=getResources().getDisplayMetrics().widthPixels;
        float density=getResources().getDisplayMetrics().density;
        int sidebarWidth=Math.min(Math.round(145f*density),Math.max(Math.round(98f*density),screenWidth/5));
        contentRow.addView(navScroll,new LinearLayout.LayoutParams(sidebarWidth,-1));
        ScrollView scroll=new ScrollView(this);
        scroll.setVerticalScrollBarEnabled(true);
        scroll.setScrollbarFadingEnabled(false);
        scroll.setFillViewport(false);
        LinearLayout root=column();
        // Slim optional swipe rails retain the original reliable scroll gestures,
        // with the actual scroll indicator on the RIGHT side of the content.
        LinearLayout frame=new LinearLayout(this);frame.setOrientation(LinearLayout.HORIZONTAL);
        TextView leftRail=text("↕",13,true),rightRail=text("↕",13,true);
        leftRail.setGravity(Gravity.CENTER);rightRail.setGravity(Gravity.CENTER);
        int railPx=Math.max(10,Math.round(density*13));
        frame.addView(leftRail,new LinearLayout.LayoutParams(railPx,-1));
        frame.addView(root,new LinearLayout.LayoutParams(0,-2,1f));
        frame.addView(rightRail,new LinearLayout.LayoutParams(railPx,-1));
        scroll.addView(frame);
        contentRow.addView(scroll,new LinearLayout.LayoutParams(0,-1,1f));
        shell.addView(contentRow,new LinearLayout.LayoutParams(-1,0,1f));
        final android.view.View.OnTouchListener railScroll=(v,e)->{
            switch(e.getActionMasked()){
                case android.view.MotionEvent.ACTION_DOWN:
                    v.setTag(Float.valueOf(e.getRawY()));return true;
                case android.view.MotionEvent.ACTION_MOVE:
                    float old=((Float)v.getTag()).floatValue();
                    float now=e.getRawY();
                    scroll.scrollBy(0,Math.round(old-now));v.setTag(Float.valueOf(now));return true;
                case android.view.MotionEvent.ACTION_UP:
                case android.view.MotionEvent.ACTION_CANCEL:return true;
            }
            return true;
        };
        leftRail.setOnTouchListener(railScroll);rightRail.setOnTouchListener(railScroll);
        section(root,"SURVIVAL PARADISE  •  V57 HYBRID DEVELOPMENT TEST");
        root.addView(text("Controls apply to the playable game, and save automatically.",13,false));
        final int playerSection=root.getChildCount();
        section(root,"PLAYER AND COMBAT");
        section(root,"V109 • APPROVED 200 CHARACTERS • WEAPONS ON, OLD GEAR HIDDEN");
        slider(root,"Player character (001–200)","playerSkinV109",1,200,124,"");
        section(root,"LIVE APPROVED CHARACTER PREVIEW");
        final CharacterPreviewV118 characterPreviewV118=new CharacterPreviewV118(this);
        activeCharacterPreviewV118=characterPreviewV118;
        root.addView(characterPreviewV118,new LinearLayout.LayoutParams(-1,dp118(185)));
        final Button posePreviewV118=stepButton118("TOGGLE IDLE / WALK");
        root.addView(posePreviewV118,new LinearLayout.LayoutParams(dp118(198),dp118(31)));
        final boolean[] previewWalkingV118={false};
        posePreviewV118.setOnClickListener(v->{
            previewWalkingV118[0]=!previewWalkingV118[0];
            characterPreviewV118.setWalkingPreview(previewWalkingV118[0]);
        });
        root.addView(text("Use this selector to test every approved fitted survivor in live play. Headgear, backpacks and legacy torso overlays are visually hidden; inventory items remain usable. Weapons and hands still render.",11,false));
        slider(root,"Character display size","scale",65,135,98,"%");
        section(root,"CHARACTER ADJUSTMENTS • TARGET");
        root.addView(text("Choose whether character adjustment sliders affect only your player or only world NPCs. Both settings profiles are saved independently.",12,false));
        Spinner characterTargetV113=new Spinner(this);
        characterTargetV113.setAdapter(new ArrayAdapter<String>(this,
            android.R.layout.simple_spinner_dropdown_item,
            new String[]{"Player character only","World NPCs only (including companions)"}));
        characterTargetV113.setSelection(Math.max(0,Math.min(1,
            prefs.getInt(CharacterScopeV113.SCOPE_KEY,CharacterScopeV113.PLAYER))));
        root.addView(characterTargetV113);
        final LinearLayout characterControlsV113=column();
        root.addView(characterControlsV113);
        final Runnable[] rebuildCharacterSlidersV113Holder=new Runnable[1];
        rebuildCharacterSlidersV113Holder[0]=()->{
            characterControlsV113.removeAllViews();
            int scope=characterTargetV113.getSelectedItemPosition();
            String label=scope==CharacterScopeV113.NPCS?"WORLD NPCs":"PLAYER";
            section(characterControlsV113,"CHARACTER FITTING • "+label);
            section(characterControlsV113,"HEAD SIZE AND FIT");
            slider(characterControlsV113,"Character head size",
                CharacterScopeV113.key("headSizeV82",scope),75,160,93,"%");
            section(characterControlsV113,"BODY SHAPE • RIGID FEET");
            slider(characterControlsV113,"Upper torso width (legs unchanged)",
                CharacterScopeV113.key("bodyWidthV114",scope),55,100,71,"%");
            slider(characterControlsV113,"Pelvis / hips width (legs unchanged)",
                CharacterScopeV113.key("pelvisWidthV115",scope),55,100,72,"%");
            section(characterControlsV113,"WEAPON + BOTH HANDS • ROTATION AXIS");
            slider(characterControlsV113,"Weapon/hand pivot horizontal",
                CharacterScopeV113.key("weaponPivotXV117",scope),
                WeaponPivotV117.MIN,WeaponPivotV117.MAX,9," px");
            slider(characterControlsV113,"Weapon/hand pivot vertical",
                CharacterScopeV113.key("weaponPivotYV117",scope),
                WeaponPivotV117.MIN,WeaponPivotV117.MAX,-5," px");
            slider(characterControlsV113,"Head follows aim (0 = off)",
                CharacterScopeV113.key("headAimTiltV111",scope),0,15,15,"°");
            slider(characterControlsV113,"Head horizontal fit",
                CharacterScopeV113.key("fitHeadXV108",scope),-24,24,0," px");
            slider(characterControlsV113,"Head vertical fit",
                CharacterScopeV113.key("fitHeadYV108",scope),-24,24,0," px");
            section(characterControlsV113,"IDLE / WALK ANIMATION");
            slider(characterControlsV113,"Idle breathing amplitude",
                CharacterScopeV113.key("fitIdleBreathV108",scope),0,12,4," px");
            slider(characterControlsV113,"Idle breathing animation speed",
                CharacterScopeV113.key("idleBreathingSpeedV110",scope),25,250,100,"%");
            slider(characterControlsV113,"Walking base frame rate (0 = fitted V5)",
                CharacterScopeV113.key("fitWalkFpsV108",scope),0,12,4," fps");
            slider(characterControlsV113,"Walking animation speed",
                CharacterScopeV113.key("walkingAnimationSpeedV79",scope),50,200,100,"%");
            characterControlsV113.addView(text("The weapon/hand pivot sliders relocate the entire original weapon, trigger hand and support hand together, retaining recoil, aim angle and bullet/flashlight origins. Zero means original V116 placement. Player / World NPC selection above saves independent pivot locations. Torso and pelvis sliders still work as before.",11,false));
            action(characterControlsV113,"RESET "+label+" CHARACTER ADJUSTMENTS",()->{
                android.content.SharedPreferences.Editor edits=prefs.edit();
                String[] keys={"headSizeV82","bodyWidthV114","pelvisWidthV115","weaponPivotXV117","weaponPivotYV117","headAimTiltV111","fitHeadXV108",
                    "fitHeadYV108","fitIdleBreathV108","idleBreathingSpeedV110",
                    "fitWalkFpsV108","walkingAnimationSpeedV79"};
                int[] defaults=ScreenshotDefaultsV121.CHARACTER_VALUES;
                for(int n=0;n<keys.length;n++)
                    edits.putInt(CharacterScopeV113.key(keys[n],scope),defaults[n]);
                edits.apply();
                game.reloadSettings();
                rebuildCharacterSlidersV113Holder[0].run();
            });
        };
        characterTargetV113.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(android.widget.AdapterView<?> parent){}
            public void onItemSelected(android.widget.AdapterView<?> parent,View view,int position,long id){
                prefs.edit().putInt(CharacterScopeV113.SCOPE_KEY,
                    Math.max(0,Math.min(1,position))).apply();
                rebuildCharacterSlidersV113Holder[0].run();
                characterPreviewV118.invalidate();
            }
        });
        rebuildCharacterSlidersV113Holder[0].run();
        action(root,"APPLY SCREENSHOT FIT TO PLAYER + ALL NPCs",()->{
            ScreenshotSettingsV121.applyCharacters(prefs,true);
            game.reloadSettings();
            rebuildCharacterSlidersV113Holder[0].run();
            characterPreviewV118.invalidate();
            Toast.makeText(this,"V121 fitting applied to both profiles",
                Toast.LENGTH_SHORT).show();
        });
        action(root,"EXPORT PLAYER CHARACTER FITTING JSON",()->exportCharacterFittingV108());
        final int combatSection=root.getChildCount();
        section(root,"COMBAT • COMPANIONS • EQUIPMENT");
        slider(root,"Hand size (independent)","hand",60,145,100,"%");
        slider(root,"Support hand horizontal reach","support",-12,24,0," px");
        slider(root,"Support hand vertical offset","supportY",-24,24,0," px");
        slider(root,"Simulation speed","speed",50,200,100,"%");
        slider(root,"Player walking speed","walkSpeedV77",75,200,130,"%");

        slider(root,"Survivors (including player)","survivors",1,9,1,"");
        root.addView(text("COMPANION FOLLOW FORMATION",13,true));
        Spinner formationPicker=new Spinner(this);
        formationPicker.setAdapter(new ArrayAdapter<String>(this,
            android.R.layout.simple_spinner_dropdown_item,FollowFormationV61.NAMES));
        formationPicker.setSelection(Math.max(0,Math.min(4,prefs.getInt("followMode",0))));
        root.addView(formationPicker);
        formationPicker.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(android.widget.AdapterView<?> parent){}
            public void onItemSelected(android.widget.AdapterView<?> parent,View v,int pos,long id){
                prefs.edit().putInt("followMode",pos).apply();
                game.reloadSettings();
            }
        });
        slider(root,"Companion spacing","followSpacing",70,450,125," px");
        action(root,"OPEN COMPANION COMMANDS",()->companionCommandsV118());
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
        final int gameplaySection=root.getChildCount();
        section(root,"GAMEPLAY AND APPEARANCE");
        check(root,"Flashlight in off-hand with pistol / revolver / UZI","dualTorch",true);
        check(root,"Show hands","hands",true);
        check(root,"Show weapons","weapons",true);
        check(root,"Grip anchors","anchors",false);
        check(root,"AI hitboxes","hitboxes",false);
        check(root,"Enemy AI","enemyAI",true);
        check(root,"Aiming rotation","aimRotation",true);
        check(root,"Firing recoil","recoil",true);
        check(root,"Small muzzle flash (gunfire only)","gunMuzzleV119",true);
        check(root,"Short real-bullet tracers","gunTrailV119",true);
        check(root,"Item drops + inventory","loot",true);
        slider(root,"Discarded items remain on ground",
            "groundDropDaysV129",1,2,2," game days");
        check(root,"Automatic day / night cycle","autoDayNight",true);
        slider(root,"Real minutes per game day","dayLength",12,120,36," min");
        check(root,"Manual night (when automatic is OFF)","night",true);
        slider(root,"Night darkness","darkness",45,96,83,"%");
        slider(root,"Flashlight beam distance","beamReach",260,690,490," px");
        check(root,"Hand flashlight switched on","lampOn",true);
        check(root,"Warm campfires and flames","campfiresLit",true);
        check(root,"Neon building signs","neonLights",true);
        check(root,"Full-screen immersive gameplay","fullscreen",true);
        final int worldSection=root.getChildCount();
        section(root,"WORLD TEST LAB  •  V58");
        root.addView(text("All original settings and touch controls remain available. " +
            "The options below modify the live V54 chunk-streaming test.",13,false));
        check(root,"Show FPS, player coordinates, NPC and chunk diagnostics","testPerf",false);
        check(root,"Compact diagnostics without a large background","compactDebugV76",true);
        slider(root,"Top button background opacity","topButtonOpacityV76",0,65,22,"%");
        check(root,"Show loaded chunk grid and coordinates","testChunkGrid",false);
        final int aimSection=root.getChildCount();
        section(root,"CAMERA AND TOUCH CONTROLS");
        root.addView(text("Right stick aims only. Left and right FIRE / MELEE act independently.",14,true));
        check(root,"Show classic six status bars","showStatusBars",true);
        check(root,"Show world aiming crosshair","showCrosshair",true);
        slider(root,"Approved crimson crosshair size","reticleSize",40,220,100,"%");
        root.addView(text("CLASSIC V61 AIM RESTORED: drag the aim thumb from its center toward the rim. Both the thumb and crosshair slide directly with your finger, without auto-extension, acceleration, or aim zones.",11,false));
        slider(root,"Released crosshair distance (weapon-relative)","crosshairRestPercent",50,200,100,"%");
        check(root,"Circular camera look-ahead (ON by default)","classicAimCameraV71",true);
        weaponPanSlider(root);
        slider(root,"Camera look-ahead stick threshold","lookAheadThreshold",30,95,72,"%");
        slider(root,"Camera panning response speed","lookAheadSmooth",2,18,8," /s");
        slider(root,"Maximum camera pan speed","cameraPanSpeedV68",120,1200,350," px/s");
        slider(root,"Camera zoom — lower = farther view","cameraZoom",45,180,100,"%");
        slider(root,"Movement joystick size","movePadSize",70,180,100,"%");
        slider(root,"Aiming joystick size","aimPadSize",70,180,100,"%");
        slider(root,"Movement joystick sensitivity","moveSensitivity",50,160,100,"%");
        slider(root,"Aiming joystick sensitivity","aimSensitivity",50,160,100,"%");
        slider(root,"Joystick transparency / opacity","controlOpacity",25,100,100,"%");
        action(root,"OPEN ON-SCREEN HUD EDITOR",()->{
            prefs.edit().putBoolean("editControls",true).apply();
            game.reloadSettings();
            if(activeDialog[0]!=null)activeDialog[0].dismiss();
        });
        final int layoutSection=root.getChildCount();
        section(root,"SETTINGS LAYOUT  •  LIVE (reopen to apply sizes)");
        root.addView(sizeRow);
        slider(root,"Settings text size","menuTextSize",75,155,100,"%");
        slider(root,"Settings slider thickness","menuSliderSize",65,160,100,"%");
        slider(root,"Settings row spacing","menuRowSpacing",50,180,100,"%");
        final int perfSection=root.getChildCount();
        section(root,"CHUNK ENGINE  •  LIVE SETTINGS");
        slider(root,"Distant NPC sleep radius","npcSleepRadius",600,2400,1200," px");
        slider(root,"Lighting performance (100 = original quality)",
               "lightResolution",100,300,220,"%");
        check(root,"Cache night lightmap when camera is still","staticLightCache",true);
        check(root,"Mobile performance: simplified point-light shadows","fastPointLights",true);
        root.addView(text("FPS test: compare static-light cache ON/OFF at spawn camp. "+
              "CPU UPDATE / DRAW / LIGHT timing appears on the FPS HUD.",12,false));
        root.addView(text("Higher lighting performance reduces lightmap resolution " +
            "and shadow-processing cost. Original quality is 100%.",12,false));
        slider(root,"Maximum resident terrain chunks","testCacheMax",12,64,36,"");
        slider(root,"Chunk preloading radius","testPreloadRadius",1,3,2," chunks");
        action(root,"View current FPS and chunk statistics",()->{
            Toast.makeText(this,game.testStats(),Toast.LENGTH_LONG).show();
        });
        section(root,"V128 JOINED PROCEDURAL WORLD • INDUSTRIAL REGION");
        root.addView(text("The original camp and main highway now connect without a portal "+
            "to an industrial region 12 sectors wide and 10 sectors high. "+
            "Factory locations, interiors, loot and NPCs use the selected industrial seed. "+
            "The older general terrain keeps its original deterministic seed.",13,false));
        action(root,"SET INDUSTRIAL REGION SEED (NEW GAME)",()->{
            final android.widget.EditText field=new android.widget.EditText(this);
            field.setInputType(android.text.InputType.TYPE_CLASS_NUMBER|
                android.text.InputType.TYPE_NUMBER_FLAG_SIGNED);
            field.setSingleLine(true);
            field.setText(String.valueOf(game.industrialSeedV123));
            field.selectAll();
            new android.app.AlertDialog.Builder(this)
                .setTitle("Procedural industrial world seed")
                .setView(field)
                .setNegativeButton("CANCEL",null)
                .setPositiveButton("GENERATE",(dialog,which)->{
                    try{
                        int next=Integer.parseInt(field.getText().toString().trim());
                        // Changing the seed is a NEW GAME, not a live map
                        // mutation, and must not silently delete progress.
                        new AlertDialog.Builder(this)
                            .setTitle("Start a new seeded world?")
                            .setMessage("This starts a new game and resets your current progress. "+
                                "Export your existing save first if you need to keep it.")
                            .setNegativeButton("CANCEL",null)
                            .setPositiveButton("START NEW WORLD",(confirmation,accepted)->{
                                game.saveProgress();
                                prefs.edit().putInt(IndustrialWorldV123.SEED_PREF,next).apply();
                                game.newGame();
                                if(activeDialog[0]!=null)activeDialog[0].dismiss();
                                game.menuPause(false);
                                Toast.makeText(this,"Joined world / industrial seed: "+next,
                                    Toast.LENGTH_LONG).show();
                            }).show();
                    }catch(NumberFormatException ex){
                        Toast.makeText(this,"Enter a signed whole-number seed",
                            Toast.LENGTH_LONG).show();
                    }
                }).show();
        });
        action(root,"TRAVEL TO INDUSTRIAL HIGHWAY ENTRANCE",()->{
            if(game.insideClinicV89)game.exitClinicV89();
            float x=IndustrialBiomeBridgeV128.WEST-450f;
            float y=IndustrialBiomeBridgeV128.ROAD_CENTER_Y;
            testTravel(x-game.playerX,y-game.playerY,
                "Highway approach to industrial biome");
        });
        action(root,"TRAVEL TO INDUSTRIAL FACTORY GATE",()->{
            if(game.insideClinicV89)game.exitClinicV89();
            IndustrialWorldV123.District factory=IndustrialWorldV123.district(
                0,0,game.industrialSeedV123);
            float x=IndustrialBiomeBridgeV128.worldX(factory.doorX);
            float y=IndustrialBiomeBridgeV128.worldY(factory.doorY+112f);
            testTravel(x-game.playerX,y-game.playerY,
                "Industrial factory, joined world coordinates");
        });
        section(root,"TRAVEL / CONTINUITY TESTS");
        root.addView(text("Teleporting changes only player coordinates. The original camp, " +
            "seed, save file, characters, and inventory remain intact.",13,false));
        action(root,"Travel 8 chunks east",()->testTravel(8f*WorldChunkModel.CHUNK_SIZE,0,
            "Moved 8 chunks east"));
        action(root,"Travel 8 chunks west",()->testTravel(-8f*WorldChunkModel.CHUNK_SIZE,0,
            "Moved 8 chunks west"));
        action(root,"Travel 8 chunks north",()->testTravel(0,-8f*WorldChunkModel.CHUNK_SIZE,
            "Moved 8 chunks north"));
        action(root,"Travel 8 chunks south",()->testTravel(0,8f*WorldChunkModel.CHUNK_SIZE,
            "Moved 8 chunks south"));
        action(root,"Return to original survivor camp",()->testTravel(
            GameView.CAMP_X-game.playerX,GameView.CAMP_Y-game.playerY,
            "Returned to survivor camp"));
        final int actionSection=root.getChildCount();
        section(root,"GAME ACTIONS");
        action(root,"Save game now",()->{game.saveProgress();Toast.makeText(this,"Game saved",Toast.LENGTH_SHORT).show();});
        section(root,"SAVE TRANSFER AND BACKUP");
        root.addView(text("Uninstalling deletes Android private data. Export a save file before uninstalling; use IMPORT after reinstalling. Installing over a prior APK requires the same signing certificate.",12,false));
        action(root,"EXPORT GAME SAVE TO FILE",()->exportGameSaveV85());
        action(root,"IMPORT GAME SAVE FROM FILE",()->importGameSaveV85());
        action(root,"Take screenshot",()->captureGame());
        action(root,"Restore default settings",()->{
            prefs.edit().putInt("scale",ScreenshotDefaultsV121.CHARACTER_SCALE).putInt("hand",100).putInt("support",0).putInt("supportY",0)
              .putInt("speed",100).putInt("walkSpeedV77",130).putInt("walkingAnimationSpeedV79",100)
               .putInt("idleBreathingSpeedV110",100).putInt("headAimTiltV111",10).putInt("survivors",1).putInt("gun",0)
              .putBoolean("hands",true).putBoolean("weapons",true).putBoolean("anchors",false)
              .putBoolean("hitboxes",false).putBoolean("enemyAI",true).putBoolean("aimRotation",true)
               .putBoolean("recoil",true).putBoolean("gunMuzzleV119",true)
               .putBoolean("gunTrailV119",true)
               .putBoolean("loot",true).putBoolean("night",true)
              .putBoolean("autoDayNight",true).putInt("dayLength",36)
              .putInt("darkness",83).putInt("beamReach",490)
              .putBoolean("lampOn",true).putBoolean("campfiresLit",true)
              .putBoolean("neonLights",true)
              .putBoolean("fullscreen",true)
              .putBoolean("testPerf",false).putBoolean("compactDebugV76",true).putBoolean("testChunkGrid",false)
              .putInt("cameraZoom",100).putInt("movePadSize",180)
              .putInt("aimPadSize",180).putInt("moveSensitivity",100)
              .putInt("aimSensitivity",100).putInt("controlOpacity",100)
              .putInt("hudOpacityV73",100).putInt("topButtonOpacityV76",22)
              .putInt("testCacheMax",36).putInt("testPreloadRadius",2)
              .putInt("npcSleepRadius",1200).putInt("lightResolution",150)
              .putInt("fireButtonSize",100).putInt("fireButtonX",0)
              .putInt("fireButtonY",0)
              .putInt("testWindowWidth",96).putInt("testWindowHeight",94)
              .putInt("menuTextSize",100).putInt("menuSliderSize",100)
              .putInt("menuRowSpacing",100).putBoolean("dualTorch",true)
              .putBoolean("showStatusBars",true).putBoolean("showCrosshair",true)
              .putBoolean("lookAheadEnabled",true).putBoolean("classicAimCameraV71",true)
              .putInt("lookAheadThreshold",72)
              .putInt("lookAheadStrength",420).putInt("lookAheadSmooth",8)
              .putInt("cameraPanPercentV72",72)
              .putInt("followMode",0).putInt("followSpacing",125)
              .putBoolean("companionStayV118",false).putBoolean("companionHoldFireV118",false)
              .putInt("cursorSpeed",400)
              .putInt("crosshairRestPercent",100).putInt("cursorSpeedV68",650)
              .putInt("aimDeadzoneV68",17).putInt("aimCurveV68",175)
              .putInt("aimSteeringV68",100).putInt("cameraPanSpeedV68",350)
              .putInt("reticleSize",100).putInt("headSizeV82",100)
              .putInt("bodyWidthV114",100).putInt("bodyWidthV114NpcV113",100)
              .putInt("pelvisWidthV115",100).putInt("pelvisWidthV115NpcV113",100)
              .putInt("weaponPivotXV117",0).putInt("weaponPivotYV117",0)
              .putInt("weaponPivotXV117NpcV113",0).putInt("weaponPivotYV117NpcV113",0)
              .putInt(CharacterScopeV113.SCOPE_KEY,CharacterScopeV113.PLAYER)
              .putInt(CharacterFitV108.X_KEY,CharacterFitV108.HEAD_X_DEFAULT)
              .putInt(CharacterFitV108.Y_KEY,CharacterFitV108.HEAD_Y_DEFAULT)
              .putInt(CharacterFitV108.BREATH_KEY,CharacterFitV108.BREATH_DEFAULT)
              .putInt(CharacterFitV108.WALK_FPS_KEY,CharacterFitV108.WALK_FPS_DEFAULT)
              .putBoolean("staticLightCache",true)
              .putBoolean("fastPointLights",true).putInt("lightResolution",220)
              .putBoolean("editControls",false).apply();
            ScreenshotSettingsV121.applyCharacters(prefs,true);
            ScreenshotSettingsV121.applyHud(prefs,game.viewW,true);
            wSize.setProgress(96-65);hSize.setProgress(94-65);
            resizeSettingsWindow(activeDialog[0],96,94);
            game.reloadSettings();applyImmersive();
            Toast.makeText(this,"Defaults restored. Reopen settings to see the values.",Toast.LENGTH_LONG).show();
        });
        // Persistent pinned fast-scroll track: drag from 0 to 100% instead of
        // swiping through dozens of game settings.
        LinearLayout track=new LinearLayout(this);
        track.setOrientation(LinearLayout.HORIZONTAL);
        final TextView nav=text("SCROLL 0%",12,true);
        track.addView(nav);
        final SeekBar fastScroll=new SeekBar(this);
        fastScroll.setMax(100);
        track.addView(fastScroll,new LinearLayout.LayoutParams(0,-2,1f));
        navigation.addView(track);
        fastScroll.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar b,int progress,boolean user){
                if(!user)return;
                scroll.post(()->{
                    int max=Math.max(0,root.getHeight()-scroll.getHeight());
                    scroll.scrollTo(0,Math.round(max*progress/100f));
                });
            }
            public void onStartTrackingTouch(SeekBar b){}
            public void onStopTrackingTouch(SeekBar b){}
        });
        scroll.setOnScrollChangeListener((v,x,y,oldX,oldY)->{
            int max=Math.max(1,root.getHeight()-scroll.getHeight());
            int pct=Math.max(0,Math.min(100,Math.round(y*100f/max)));
            fastScroll.setProgress(pct);
            nav.setText("SCROLL "+pct+"%");
        });
        // V118 category pages: only one section is mounted visibly.
        // Scrolling cannot enter another category or accidentally move its sliders.
        final java.util.ArrayList<View> allSettingsV118=new java.util.ArrayList<>();
        for(int k=0;k<root.getChildCount();k++)
            allSettingsV118.add(root.getChildAt(k));
        int[] sectionBoundariesV118={0,combatSection,gameplaySection,worldSection,
            aimSection,layoutSection,perfSection,actionSection,allSettingsV118.size()};
        final String[] categoryNamesV118={
            "CHARACTER","COMBAT / SQUAD","GAMEPLAY","WORLD",
            "AIM / CAMERA","LAYOUT","PERFORMANCE","ACTIONS"};
        root.removeAllViews();
        final LinearLayout[] categoryPagesV118=new LinearLayout[categoryNamesV118.length];
        for(int k=0;k<categoryPagesV118.length;k++){
            LinearLayout page=column();page.setPadding(3,2,3,5);
            for(int n=sectionBoundariesV118[k];n<sectionBoundariesV118[k+1];n++)
                page.addView(allSettingsV118.get(n));
            page.setVisibility(k==0?View.VISIBLE:View.GONE);
            categoryPagesV118[k]=page;root.addView(page);
        }
        final int[] activePageV118={0};
        for(int k=0;k<categoryNamesV118.length;k++){
            final int selected=k;
            sideNavButton(navigation,categoryNamesV118[k],()->{
                if(activePageV118[0]==selected)return;
                categoryPagesV118[activePageV118[0]].setVisibility(View.GONE);
                categoryPagesV118[selected].setVisibility(View.VISIBLE);
                activePageV118[0]=selected;
                scroll.scrollTo(0,0);fastScroll.setProgress(0);
                scroll.requestLayout();
            });
        }
        sideNavButton(navigation,"HUD EDIT",()->{
            if(activeDialog[0]!=null)activeDialog[0].dismiss();
            hudEditor();
        });
        // Compact in-window button replaces Android AlertDialog's oversized
        // grey positive-button strip and leaves more useful scroll height.
        Button returnGame=new Button(this);
        returnGame.setText("RETURN TO GAME");
        returnGame.setTextSize(12);
        returnGame.setAllCaps(false);
        returnGame.setMinHeight(0);returnGame.setMinimumHeight(0);
        returnGame.setPadding(0,0,0,0);
        returnGame.setTextColor(0xff85d6d0);
        returnGame.setBackgroundColor(0xff23393e);
        int footerPx=Math.max(30,Math.min(
            Math.round(30f*getResources().getDisplayMetrics().density),
            getResources().getDisplayMetrics().heightPixels/12));
        shell.addView(returnGame,new LinearLayout.LayoutParams(-1,footerPx));
        AlertDialog dialog=new AlertDialog.Builder(this).setView(shell)
          .setOnCancelListener(d->game.menuPause(false)).create();
        returnGame.setOnClickListener(v->dialog.dismiss());
        activeDialog[0]=dialog;
        dialog.setOnDismissListener(d->{
            activeCharacterPreviewV118=null;
            game.menuPause(false);restoreFullscreenAfterShade();
        });
        dialog.show();
        dialog.setCancelable(true);
        dialog.setCanceledOnTouchOutside(true);
        makeWindowMovable(dialog,dragTitle,windowW,windowH,"settingsWindow");
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
    @Override protected void onPause(){if(game!=null){game.releaseControls();game.saveProgress();}super.onPause();}
}