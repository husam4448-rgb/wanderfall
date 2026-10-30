package com.survivalparadise.simulation;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    private WebView game;
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        game = new WebView(this);
        WebSettings settings = game.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        game.setWebChromeClient(new WebChromeClient());
        game.setWebViewClient(new WebViewClient());
        game.setBackgroundColor(0xff101820);
        setContentView(game);
        game.loadUrl("file:///android_asset/index.html");
    }
    @Override public void onDestroy() {
        if (game != null) {
            game.loadUrl("about:blank");
            game.destroy();
            game = null;
        }
        super.onDestroy();
    }
}
