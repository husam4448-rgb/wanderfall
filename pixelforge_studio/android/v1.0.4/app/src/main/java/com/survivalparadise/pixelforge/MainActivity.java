package com.survivalparadise.pixelforge;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Base64;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.io.OutputStream;

public final class MainActivity extends Activity {
    private static final int OPEN = 1001, SAVE = 1002;
    private final String startPage = "file:///android_asset/index.html";
    private WebView web;
    private ValueCallback<Uri[]> chooser;
    private byte[] toSave;

    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);
        hideSystemNavigation();
        web = new WebView(this);
        web.setBackgroundColor(0xff0e1519);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setAllowFileAccessFromFileURLs(false);
        s.setAllowUniversalAccessFromFileURLs(false);
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return !request.getUrl().toString().startsWith("file:///android_asset/");
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onShowFileChooser(WebView w, ValueCallback<Uri[]> cb, FileChooserParams p) {
                if (chooser != null) chooser.onReceiveValue(null);
                chooser = cb;
                try {
                    Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                    i.addCategory(Intent.CATEGORY_OPENABLE);
                    i.setType("*/*");
                    startActivityForResult(i, OPEN);
                    return true;
                } catch (Exception e) {
                    chooser = null;
                    cb.onReceiveValue(null);
                    return false;
                }
            }
        });
        web.addJavascriptInterface(new FileBridge(), "PixelForgeAndroid");
        setContentView(web);
        web.loadUrl(startPage);
    }
    private void hideSystemNavigation() {
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_FULLSCREEN |
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
            View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN);
    }
    public final class FileBridge {
        @JavascriptInterface
        public void saveBase64(String name, String mime, String b64) {
            try {
                byte[] content = Base64.decode(b64, Base64.DEFAULT);
                runOnUiThread(() -> {
                    toSave = content;
                    Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                    i.addCategory(Intent.CATEGORY_OPENABLE);
                    i.setType(mime == null || mime.isEmpty() ? "application/octet-stream" : mime);
                    i.putExtra(Intent.EXTRA_TITLE, name);
                    try { startActivityForResult(i, SAVE); } catch (Exception e) { toSave = null; }
                });
            } catch (Exception ignored) { }
        }
    }
    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data);
        if (request == OPEN) {
            if (chooser != null) {
                Uri[] urls = (result == RESULT_OK && data != null && data.getData() != null)
                    ? new Uri[]{data.getData()} : null;
                chooser.onReceiveValue(urls);
                chooser = null;
            }
        } else if (request == SAVE) {
            if (result == RESULT_OK && data != null && data.getData() != null && toSave != null) {
                try (OutputStream o = getContentResolver().openOutputStream(data.getData())) {
                    if (o != null) o.write(toSave);
                } catch (Exception ignored) { }
            }
            toSave = null;
        }
        hideSystemNavigation();
    }
    @Override public void onConfigurationChanged(android.content.res.Configuration cfg) {
        super.onConfigurationChanged(cfg);
        hideSystemNavigation();
    }
    @Override public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) hideSystemNavigation();
    }
    @Override public void onBackPressed() {
        web.evaluateJavascript("document.getElementById('modal').hidden=true;", null);
    }
    @Override protected void onDestroy() {
        if (web != null) { web.destroy(); web=null; }
        super.onDestroy();
    }
}
