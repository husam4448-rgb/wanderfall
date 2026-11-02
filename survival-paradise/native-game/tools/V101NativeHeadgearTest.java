package com.survivalparadise.nativegame;

/** Source-only V101 headgear fit regression. No Android build or APK. */
public final class V101NativeHeadgearTest {
    private static void ok(boolean condition,String label){
        if(!condition)throw new AssertionError(label);
    }
    public static void main(String[] ignored){
        for(int kind=0;kind<4;kind++){
            int width=HeadgearFitV101.COLUMNS[kind]*HeadgearFitV101.PIXEL_STEP;
            int height=HeadgearFitV101.ROWS[kind]*HeadgearFitV101.PIXEL_STEP;
            ok(HeadgearFitV101.X[kind]+width<=HeadgearFitV101.FRAME_WIDTH,"width fit");
            ok(HeadgearFitV101.Y[kind]+height<=HeadgearFitV101.FRAME_HEIGHT,"height fit");
            float last=0f;
            for(float headSize:new float[]{.75f,1f,1.60f}){
                float[] rect=HeadgearFitV101.bounds(1f,headSize,0f);
                float actual=rect[2]-rect[0];
                ok(actual>last,"monotonic head sizing");
                last=actual;
                float[] breathing=HeadgearFitV101.bounds(1f,headSize,-4f);
                ok(Math.abs(breathing[1]-rect[1]+4)<.001,"idle top");
                ok(Math.abs(breathing[3]-rect[3]+4)<.001,"idle bottom");
                float[] zoom=HeadgearFitV101.bounds(2f,headSize,0f);
                ok(Math.abs((zoom[2]-zoom[0])-2*actual)<.001,"world scaling");
            }
        }
        System.out.println("V101 VERIFIED: four native-grid headgear fits 75/100/160, idle, scale");
    }
}
