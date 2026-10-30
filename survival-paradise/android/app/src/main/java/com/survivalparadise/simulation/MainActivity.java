package com.survivalparadise.simulation;

import android.app.Activity;
import android.os.Bundle;
import android.os.Build;
import android.os.Environment;
import android.content.ContentValues;
import android.content.Intent;
import android.net.Uri;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

public class MainActivity extends Activity {
    private WebView game;
    private boolean immersive = false;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        game = new WebView(this);
        WebSettings settings = game.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(false);
        settings.setMediaPlaybackRequiresUserGesture(false);
        game.setWebChromeClient(new WebChromeClient());
        game.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                return !("file".equals(uri.getScheme()) && "/android_asset/index.html".equals(uri.getPath()));
            }
        });
        game.addJavascriptInterface(new AndroidGameControls(), "SPAndroid");
        game.setBackgroundColor(0xff101820);
        setContentView(game);
        game.loadUrl("file:///android_asset/index.html");
    }

    private void setImmersive(boolean enabled) {
        immersive = enabled;
        if (enabled) {
            getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                View.SYSTEM_UI_FLAG_FULLSCREEN |
                View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE |
                View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
        } else {
            getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_VISIBLE);
        }
    }

    public final class AndroidGameControls {
        @JavascriptInterface public void toggleFullscreen() {
            runOnUiThread(() -> setImmersive(!immersive));
        }

        @JavascriptInterface public void saveScreenshot(String pngData) {
            if (pngData == null || !pngData.startsWith("data:image/png;base64:")) return;
            // Treat JS input as untrusted; limit payload to a few MB.
            if (pngData.length() > 9000000) return;
            String bytesString = pngData.substring("data:image/png;base64:".length());
            try {
                byte[] bytes = Base64.decode(bytesString, Base64.DEFAULT);
                if (bytes.length < 20 || bytes.length > 7000000) return;
                final byte[] image = bytes;
                runOnUiThread(() -> savePng(image));
            } catch (IllegalArgumentException ignored) {
                runOnUiThread(() -> Toast.makeText(MainActivity.this, "Screenshot data invalid", Toast.LENGTH_SHORT).show());
            }
        }
    }

    private void savePng(byte[] image) {
        try {
            String name = "Survival_Paradise_" + System.currentTimeMillis() + ".png";
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                ContentValues metadata = new ContentValues();
                metadata.put(MediaStore.Images.Media.DISPLAY_NAME, name);
                metadata.put(MediaStore.Images.Media.MIME_TYPE, "image/png");
                metadata.put(MediaStore.Images.Media.RELATIVE_PATH,
                        Environment.DIRECTORY_PICTURES + "/SurvivalParadise");
                metadata.put(MediaStore.Images.Media.IS_PENDING, 1);
                Uri uri = getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, metadata);
                if (uri == null) throw new Exception("Gallery write failed");
                try (OutputStream stream = getContentResolver().openOutputStream(uri)) {
                    if (stream == null) throw new Exception("Screenshot stream unavailable");
                    stream.write(image);
                } catch (Exception e) {
                    getContentResolver().delete(uri, null, null);
                    throw e;
                }
                ContentValues ready = new ContentValues();
                ready.put(MediaStore.Images.Media.IS_PENDING, 0);
                getContentResolver().update(uri, ready, null, null);
                Toast.makeText(this, "Screenshot saved to Pictures/SurvivalParadise", Toast.LENGTH_LONG).show();
            } else {
                File base = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
                if (base == null) base = getFilesDir();
                File folder = new File(base, "SurvivalParadise");
                if (!folder.exists() && !folder.mkdirs()) throw new Exception("Storage unavailable");
                try (OutputStream stream = new FileOutputStream(new File(folder, name))) {
                    stream.write(image);
                }
                Toast.makeText(this, "Screenshot saved to app Pictures folder", Toast.LENGTH_LONG).show();
            }
        } catch (Exception e) {
            Toast.makeText(this, "Unable to save screenshot", Toast.LENGTH_LONG).show();
        }
    }

    @Override public void onBackPressed() {
        if (game != null) {
            game.evaluateJavascript(
                "(window.SP_TEST_API&&window.SP_TEST_API.settings&&" +
                "window.SP_TEST_API.settings.isOpen())?" +
                "(window.SP_TEST_API.settings.close(),true):false",
                result -> { if (!"true".equals(result)) MainActivity.super.onBackPressed(); });
        } else super.onBackPressed();
    }

    @Override public void onDestroy() {
        if (game != null) {
            game.removeJavascriptInterface("SPAndroid");
            game.loadUrl("about:blank");
            game.destroy();
            game = null;
        }
        super.onDestroy();
    }
}
