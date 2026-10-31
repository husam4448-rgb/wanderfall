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
        applyImmersive();
        game=new GameView(this);
        setContentView(game);
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
    private void slider(LinearLayout root,String label,String key,int min,int max,int def,String suffix){
        LinearLayout box=column();
        int density=prefs.getInt("menuRowSpacing",100);
        box.setPadding(6,Math.max(1,density/35),6,Math.max(1,density/35));
        TextView value=text("",14,false);
        box.addView(value);
        LinearLayout track=new LinearLayout(this);
        track.setOrientation(LinearLayout.HORIZONTAL);
        TextView left=text("↕",16,true),right=text("↕",16,true);
        left.setGravity(Gravity.CENTER);right.setGravity(Gravity.CENTER);
        int gutter=Math.max(24,Math.round(getResources().getDisplayMetrics().density*28));
        track.addView(left,new LinearLayout.LayoutParams(gutter,-1));
        SeekBar bar=new SeekBar(this);bar.setMax(max-min);
        bar.setMinimumHeight(22);bar.setPadding(0,0,0,0);
        bar.setScaleY(prefs.getInt("menuSliderSize",100)/100f);
        bar.setProgress(Math.max(0,Math.min(max-min,prefs.getInt(key,def)-min)));
        track.addView(bar,new LinearLayout.LayoutParams(0,-2,1));
        track.addView(right,new LinearLayout.LayoutParams(gutter,-1));
        value.setText(label+"   "+(min+bar.getProgress())+suffix);
        box.addView(track);
        bar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar s,int progress,boolean fromUser){
                int number=min+progress;value.setText(label+"   "+number+suffix);
                if(fromUser){prefs.edit().putInt(key,number).apply();game.reloadSettings();}
            }
            public void onStartTrackingTouch(SeekBar s){}
            public void onStopTrackingTouch(SeekBar s){}
        });
        // Touching only the central track edits; wide margins remain free to scroll.
        root.addView(box);
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
    // Separate from game settings: the actual HUD has its own layout editor.
    void hudEditor(){
        game.menuPause(true);
        LinearLayout shell=column();
        section(shell,"HUD BUTTON EDITOR  •  V59");
        shell.addView(text("Select a button and adjust its placement, size and opacity. "
            +"Use ON-SCREEN DRAG to fine-tune each button directly in the game.",12,false));
        ScrollView scroll=new ScrollView(this);
        scroll.setFillViewport(false);
        LinearLayout root=column();
        scroll.addView(root);
        section(root,"BUTTON SELECTION");
        Spinner picker=new Spinner(this);
        picker.setAdapter(new ArrayAdapter<String>(this,
            android.R.layout.simple_spinner_dropdown_item,LegacyControlsV58.NAMES));
        root.addView(picker);
        LinearLayout options=column();
        root.addView(options);
        picker.setSelection(Math.max(0,Math.min(LegacyControlsV58.COUNT-1,
            prefs.getInt("selectedButton",0))));
        picker.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(android.widget.AdapterView<?> parent){}
            public void onItemSelected(android.widget.AdapterView<?> parent,View item,int index,long id){
                prefs.edit().putInt("selectedButton",index).apply();
                options.removeAllViews();
                check(options,"Enable "+LegacyControlsV58.NAMES[index],
                    "uiEnabled"+index,true);
                slider(options,"SIZE","uiSize"+index,60,160,100,"%");
                slider(options,"OPACITY","uiAlpha"+index,30,100,100,"%");
                slider(options,"HORIZONTAL POSITION","uiX"+index,-340,340,0,"");
                slider(options,"VERTICAL POSITION","uiY"+index,-270,270,0,"");
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
        action(root,"RESTORE ALL BUTTON DEFAULTS",()->{
            SharedPreferences.Editor edit=prefs.edit();
            for(int i=0;i<LegacyControlsV58.COUNT;i++)
                edit.remove("uiX"+i).remove("uiY"+i).remove("uiSize"+i)
                    .remove("uiAlpha"+i).remove("uiEnabled"+i);
            edit.putBoolean("editControls",false).apply();
            game.reloadSettings();
            if(active[0]!=null)active[0].dismiss();
            Toast.makeText(this,"HUD controls restored to approved default layout",
                    Toast.LENGTH_SHORT).show();
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
        resizeSettingsWindow(dialog,92,90);
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
        row.addView(left,new LinearLayout.LayoutParams(0,-2,44f));
        row.addView(right,new LinearLayout.LayoutParams(0,-2,56f));
        section(left,"SURVIVOR   •   EQUIPMENT");
        V62InventoryPreview avatar=new V62InventoryPreview(this,game);
        left.addView(avatar,new LinearLayout.LayoutParams(-1,
            Math.round(142*getResources().getDisplayMetrics().density)));
        LinearLayout vital=new LinearLayout(this);
        vital.setOrientation(LinearLayout.HORIZONTAL);
        vital.addView(text("HP "+Math.round(game.health),12,true),
            new LinearLayout.LayoutParams(0,-2,1));
        vital.addView(text("STA "+Math.round(game.stamina),12,true),
            new LinearLayout.LayoutParams(0,-2,1));
        vital.addView(text("FOOD "+game.foodCount+"   WATER "+game.waterCount,12,true),
            new LinearLayout.LayoutParams(0,-2,2));
        left.addView(vital);
        final String[] equipment={
            "HEAD","FACE","TORSO","LEGS","FEET","BACK","PRIMARY","OFF-HAND"};
        for(int er=0;er<4;er++){
            LinearLayout gearRow=new LinearLayout(this);
            gearRow.setOrientation(LinearLayout.HORIZONTAL);
            for(int ec=0;ec<2;ec++){
                int ix=er*2+ec;
                String label=equipment[ix];
                String value=ix==2?"SHIRT":ix==3?"PANTS":ix==4?"BOOTS":
                    ix==6?LOADOUTS[game.gun]:
                    ix==7?(game.dualTorch&&game.lampOn?"FLASHLIGHT":"EMPTY"):"EMPTY";
                Button equipped=v62Slot(label+"\n"+value,true);
                LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,
                    Math.round(32*getResources().getDisplayMetrics().density),1);
                p.setMargins(3,3,3,3);gearRow.addView(equipped,p);
                equipped.setOnClickListener(v->{
                    if(ix==6){
                        new AlertDialog.Builder(this).setTitle("EQUIP PRIMARY WEAPON")
                            .setItems(LOADOUTS,(d,weapon)->{
                                prefs.edit().putInt("gun",weapon).apply();
                                game.reloadSettings();game.saveProgress();
                                equipped.setText("PRIMARY\n"+LOADOUTS[weapon]);
                                avatar.invalidate();
                            }).show();
                    }else if(ix==7){
                        boolean enabled=!(game.lampOn&&game.dualTorch);
                        prefs.edit().putBoolean("dualTorch",enabled)
                            .putBoolean("lampOn",enabled).apply();
                        game.reloadSettings();avatar.invalidate();
                        equipped.setText("OFF-HAND\n"+(enabled?"FLASHLIGHT":"EMPTY"));
                    }else Toast.makeText(this,
                        "Approved "+label+" overlay assets not installed yet",
                        Toast.LENGTH_SHORT).show();
                });
            }
            left.addView(gearRow);
        }
        left.addView(text("Appearance uses locked character pixels. Future armor and transmog require approved overlays.",11,false));
        section(right,"BACKPACK   •   24 SLOTS");
        right.addView(text("Select an item to USE it or assign it to the quick-access bar.",12,false));
        final int[] itemKinds={0,1,2,6,7};
        for(int ir=0;ir<4;ir++){
            LinearLayout slots=new LinearLayout(this);slots.setOrientation(LinearLayout.HORIZONTAL);
            for(int ic=0;ic<6;ic++){
                int idx=ir*6+ic;
                int kind=idx==0?0:idx==1?1:idx==2?2:idx==3?6:idx==4?7:0;
                String name=idx==0?"SCRAP":idx==1?"MEDKIT":idx==2?"AMMO":
                    idx==3?"FOOD":idx==4?"WATER":"";
                int qty=idx==0?game.scrap:idx==1?game.medkits:
                    idx==2?game.ammoPacks:idx==3?game.foodCount:
                    idx==4?game.waterCount:0;
                Button slot=v62Slot(name.isEmpty()?"":name+"\n×"+qty,qty>0);
                LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(0,
                    Math.round(39*getResources().getDisplayMetrics().density),1);
                params.setMargins(3,3,3,3);slots.addView(slot,params);
                slot.setOnClickListener(v->{
                    if(idx>=5)return;
                    String[] choices={"USE","ASSIGN HOTBAR 1","ASSIGN HOTBAR 2",
                        "ASSIGN HOTBAR 3","ASSIGN HOTBAR 4","ASSIGN HOTBAR 5","ASSIGN HOTBAR 6"};
                    new AlertDialog.Builder(this).setTitle(name+" • "+qty)
                      .setItems(choices,(d,choice)->{
                        if(choice==0){
                            if(kind==0)Toast.makeText(this,
                                "Scrap is a crafting resource",Toast.LENGTH_SHORT).show();
                            else{
                                int h=game.hotbar[0];
                                game.hotbar[0]=kind;game.useHotbar(0);
                                game.hotbar[0]=h;
                                slot.setText(name+"\n×"+(kind==1?game.medkits:
                                    kind==2?game.ammoPacks:kind==6?game.foodCount:game.waterCount));
                            }
                        }else game.setHotbarItem(choice-1,kind);
                        avatar.invalidate();
                      }).show();
                });
            }
            right.addView(slots);
        }
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
                LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,
                    Math.round(37*getResources().getDisplayMetrics().density),1);
                p.setMargins(2,2,2,2);quickRow.addView(hot,p);
                hot.setOnClickListener(v->{
                    new AlertDialog.Builder(this).setTitle("ASSIGN QUICK SLOT "+(slotIndex+1))
                      .setItems(GameView.HOTBAR_TYPES,(d,which)->{
                          game.setHotbarItem(slotIndex,which);refresh[0].run();
                      }).show();
                });
            }
        };
        refresh[0].run();
        root.addView(text("Transmog / cosmetic skins: future equipment layer. Current preview changes with weapons and flashlight.",12,false));
        shell.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout tools=new LinearLayout(this);tools.setOrientation(LinearLayout.HORIZONTAL);
        Button smaller=v62Slot("WINDOW −",true),larger=v62Slot("WINDOW +",true);
        Button closeBag=v62Slot("CLOSE BAG",true);
        tools.addView(smaller,new LinearLayout.LayoutParams(0,-2,1));
        tools.addView(larger,new LinearLayout.LayoutParams(0,-2,1));
        tools.addView(closeBag,new LinearLayout.LayoutParams(0,-2,1));
        shell.addView(tools);
        // A compact in-panel footer avoids Android AlertDialog’s large button strip.
        AlertDialog dialog=new AlertDialog.Builder(this).setView(shell).create();
        closeBag.setOnClickListener(v->dialog.dismiss());
        dialog.setOnDismissListener(d->{
            game.saveProgress();game.menuPause(false);restoreFullscreenAfterShade();
        });
        dialog.show();
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
        shell.addView(sizeRow);
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
        ScrollView scroll=new ScrollView(this);
        scroll.setVerticalScrollBarEnabled(true);
        scroll.setScrollbarFadingEnabled(false);
        scroll.setFillViewport(false);
        LinearLayout root=column();
        // Permanent outer touch gutters, separate from EVERY slider's touch target.
        LinearLayout frame=new LinearLayout(this);frame.setOrientation(LinearLayout.HORIZONTAL);
        TextView leftRail=text("↕",22,true),rightRail=text("↕",22,true);
        leftRail.setGravity(Gravity.CENTER);rightRail.setGravity(Gravity.CENTER);
        int railPx=Math.round(getResources().getDisplayMetrics().density*38);
        frame.addView(leftRail,new LinearLayout.LayoutParams(railPx,-1));
        frame.addView(root,new LinearLayout.LayoutParams(0,-2,1f));
        frame.addView(rightRail,new LinearLayout.LayoutParams(railPx,-1));
        scroll.addView(frame);
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
        final LinearLayout jumpBar=new LinearLayout(this);
        jumpBar.setOrientation(LinearLayout.HORIZONTAL);
        shell.addView(jumpBar);
        final LinearLayout jumpBar2=new LinearLayout(this);
        jumpBar2.setOrientation(LinearLayout.HORIZONTAL);
        shell.addView(jumpBar2);
        shell.addView(scroll,new LinearLayout.LayoutParams(-1,0,1f));
        section(root,"SURVIVAL PARADISE  •  V57 HYBRID DEVELOPMENT TEST");
        root.addView(text("Controls apply to the playable game, and save automatically.",13,false));
        final int playerSection=root.getChildCount();
        section(root,"PLAYER AND COMBAT");
        slider(root,"Character display size","scale",65,135,100,"%");
        slider(root,"Hand size (independent)","hand",60,145,100,"%");
        slider(root,"Support hand horizontal reach","support",-12,24,0," px");
        slider(root,"Support hand vertical offset","supportY",-24,24,0," px");
        slider(root,"Simulation speed","speed",50,200,100,"%");
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
        slider(root,"Companion spacing","followSpacing",70,260,125," px");
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
        check(root,"Firing recoil + muzzle flashes","recoil",true);
        check(root,"Item drops + inventory","loot",true);
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
        check(root,"Show FPS, player coordinates, NPC and chunk diagnostics","testPerf",true);
        check(root,"Show loaded chunk grid and coordinates","testChunkGrid",false);
        final int aimSection=root.getChildCount();
        section(root,"CAMERA AND TOUCH CONTROLS");
        root.addView(text("Right stick aims only. Left and right FIRE / MELEE act independently.",14,true));
        check(root,"Show classic six status bars","showStatusBars",true);
        check(root,"Show world aiming crosshair","showCrosshair",true);
        slider(root,"Approved crimson crosshair size","reticleSize",40,220,100,"%");
        root.addView(text("Crosshair moves freely with the aim stick, stops on release, and stays inside the visible world. Camera panning does not reverse it.",11,false));
        check(root,"Aim-stick camera look-ahead","lookAheadEnabled",true);
        slider(root,"Look-ahead stick threshold","lookAheadThreshold",20,95,55,"%");
        slider(root,"Look-ahead distance","lookAheadStrength",0,1000,420," px");
        slider(root,"Camera panning response speed","lookAheadSmooth",2,18,8," /s");
        slider(root,"Aim crosshair maximum distance","cursorRange",250,1200,750," px");
        slider(root,"Floating crosshair movement speed","cursorSpeed",150,1200,500," px/s");
        slider(root,"Camera zoom","cameraZoom",70,180,100,"%");
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
        action(root,"Take screenshot",()->captureGame());
        action(root,"Restore default settings",()->{
            prefs.edit().putInt("scale",100).putInt("hand",100).putInt("support",0).putInt("supportY",0)
              .putInt("speed",100).putInt("survivors",1).putInt("gun",0)
              .putBoolean("hands",true).putBoolean("weapons",true).putBoolean("anchors",false)
              .putBoolean("hitboxes",false).putBoolean("enemyAI",true).putBoolean("aimRotation",true)
               .putBoolean("recoil",true).putBoolean("loot",true).putBoolean("night",true)
              .putBoolean("autoDayNight",true).putInt("dayLength",36)
              .putInt("darkness",83).putInt("beamReach",490)
              .putBoolean("lampOn",true).putBoolean("campfiresLit",true)
              .putBoolean("neonLights",true)
              .putBoolean("fullscreen",true)
              .putBoolean("testPerf",true).putBoolean("testChunkGrid",false)
              .putInt("cameraZoom",100).putInt("movePadSize",100)
              .putInt("aimPadSize",100).putInt("moveSensitivity",100)
              .putInt("aimSensitivity",100).putInt("controlOpacity",100)
              .putInt("testCacheMax",36).putInt("testPreloadRadius",2)
              .putInt("npcSleepRadius",1200).putInt("lightResolution",150)
              .putInt("fireButtonSize",100).putInt("fireButtonX",0)
              .putInt("fireButtonY",0)
              .putInt("testWindowWidth",96).putInt("testWindowHeight",94)
              .putInt("menuTextSize",100).putInt("menuSliderSize",100)
              .putInt("menuRowSpacing",100).putBoolean("dualTorch",true)
              .putBoolean("showStatusBars",true).putBoolean("showCrosshair",true)
              .putBoolean("lookAheadEnabled",true).putInt("lookAheadThreshold",55)
              .putInt("lookAheadStrength",420).putInt("lookAheadSmooth",8)
              .putInt("followMode",0).putInt("followSpacing",125).putInt("cursorSpeed",400)
              .putInt("cursorRange",750).putInt("reticleSize",100).putBoolean("staticLightCache",true)
              .putBoolean("fastPointLights",true).putInt("lightResolution",220)
              .putBoolean("editControls",false).apply();
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
        shell.addView(track);
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
        jumpButton(jumpBar,"CHARACTER",()->
            scroll.post(()->scroll.smoothScrollTo(0,root.getChildAt(playerSection).getTop())));
        jumpButton(jumpBar,"GAMEPLAY",()->
            scroll.post(()->scroll.smoothScrollTo(0,root.getChildAt(gameplaySection).getTop())));
        jumpButton(jumpBar,"WORLD",()->
            scroll.post(()->scroll.smoothScrollTo(0,root.getChildAt(worldSection).getTop())));
        jumpButton(jumpBar,"AIM / CAMERA",()->
            scroll.post(()->scroll.smoothScrollTo(0,root.getChildAt(aimSection).getTop())));
        jumpButton(jumpBar2,"LAYOUT",()->
            scroll.post(()->scroll.smoothScrollTo(0,root.getChildAt(layoutSection).getTop())));
        jumpButton(jumpBar2,"PERFORMANCE",()->
            scroll.post(()->scroll.smoothScrollTo(0,root.getChildAt(perfSection).getTop())));
        jumpButton(jumpBar2,"ACTIONS",()->
            scroll.post(()->scroll.smoothScrollTo(0,root.getChildAt(actionSection).getTop())));
        jumpButton(jumpBar2,"HUD EDIT",()->{
            if(activeDialog[0]!=null)activeDialog[0].dismiss();
            hudEditor();
        });
        AlertDialog dialog=new AlertDialog.Builder(this).setView(shell)
          .setPositiveButton("RETURN TO GAME",(d,w)->game.menuPause(false))
          .setOnCancelListener(d->game.menuPause(false)).create();
        activeDialog[0]=dialog;
        dialog.setOnDismissListener(d->{game.menuPause(false);restoreFullscreenAfterShade();});
        dialog.show();
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