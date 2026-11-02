package com.survivalparadise.nativegame;

/** Verify approved wearable boundaries without Android instrumentation. */
public final class V98EquipmentRegression {
    static void check(boolean pass,String what){if(!pass)throw new AssertionError(what);}
    public static void main(String[] args){
        final float[] sizes={.75f,1f,1.60f};
        for(int kind=0;kind<4;kind++){
            float lastWidth=0,lastHeight=0;
            for(float size:sizes){
                float[] r=WearableFitV98.head(kind,1f,size,0f);
                float w=r[2]-r[0],h=r[3]-r[1];
                check(w>lastWidth&&h>lastHeight,"headgear must respond to head slider");
                check(r[0]>=(-48f*size-4f)&&r[2]<=(43f*size+4f),
                      "gear overflows accepted head silhouette");
                float[] bob=WearableFitV98.head(kind,1f,size,-4f);
                check(Math.abs(bob[1]-r[1]+4f)<.001f,"idle breathing anchor");
                check(Math.abs(bob[3]-r[3]+4f)<.001f,"lower head anchor");
                lastWidth=w;lastHeight=h;
            }
        }
        check(WearableFitV98.torsoPixel(65,103,0xff526f5a),"shirt color editable");
        check(WearableFitV98.torsoPixel(65,103,0xffa75420),"orange shirt editable");
        check(!WearableFitV98.torsoPixel(65,103,0xff182426),"black outline immutable");
        check(!WearableFitV98.torsoPixel(65,85,0xffc68e63),"skin immutable");
        check(!WearableFitV98.torsoPixel(65,118,0xff526f5a),"pants not recolored");
        check(!WearableFitV98.torsoPixel(12,105,0xff526f5a),"silhouette not expanded");
        check(WearableFitV98.palettePixel(0xffae3944),"approved red palette usable");
        for(int i=0;i<3;i++){
            int row=WearableFitV98.sourceRole(i);
            check(row>=0&&row<12,"palette row");
        }
        System.out.println("V98 PASS: four fitted headgear items at 75/100/160%, breathing,"+
            " torso interior-only approved recolors and untouched outlines, face and pants");
    }
}
