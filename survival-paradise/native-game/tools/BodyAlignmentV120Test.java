package com.survivalparadise.nativegame;

/** Tests actual V109 source outline geometry and front/rear foot anchoring. */
public final class BodyAlignmentV120Test {
    static void check(boolean value,String message){
        if(!value)throw new AssertionError(message);
    }
    static void near(float a,float b,String message){
        check(Math.abs(a-b)<.0001f,message+" expected "+b+" got "+a);
    }
    public static void main(String[] args) {
        near(BodyAlignmentV120.bodyFrontExclusive(100),180f,"original front edge");
        near(BodyAlignmentV120.bodyRear(100),20f,"original rear edge");
        near(BodyAlignmentV120.bodyFrontExclusive(55),144f,"minimum front edge");
        near(BodyAlignmentV120.outlineLeft(55),56f,"top outline starts at black side");
        near(BodyAlignmentV120.outlineRight(55),144f,"top outline ends at black side");
        check(BodyAlignmentV120.TORSO_OUTLINE_HEIGHT==8,"thin black upper cap");
        for(int t=55;t<=100;t++) for(int p=55;p<=100;p++) {
            int right=BodyAlignmentV120.frontBootShift(t,p);
            int left=BodyAlignmentV120.rearBootShift(p);
            float edge=BodyAlignmentV120.leadingEdge(t,p);
            near(edge,Math.max(BodyAlignmentV120.bodyFrontExclusive(t),
                BodyAlignmentV120.bodyFrontExclusive(p)),"visible final body edge");
            // max one pixel rounding: leading original x180 boot.
            check(Math.abs((180+right)-edge)<=.501f,
                "front foot MUST align with body outline, not behind it");
            check(right<=0&&right>=-36,"front boot can only retreat to final outline");
            check(left>=0&&left<=27,"rear boot must stay at back of body");
            check(40+left>=Math.round(100f+(40f-100f)*p/100f),
                "rear boot still joins original black hip bridge");
            check(40+left<140+right,
                "front and rear boots must remain in correct order");
            // All four walking frame boot blocks are translated unchanged:
            // idle/front-right x140..179, walking front x140..199,
            // backwards-side left x0..39, intermediate centered x60..119.
            for(int frame=0;frame<5;frame++){
                int frontMax=(frame==1?199:179)+right;
                int frontMin=140+right;
                check(frontMax-frontMin==(frame==1?59:39),
                    "rigid front boot width in frame "+frame);
                check(frontMax<=199&&frontMin>=0,"front boot source bounds");
                check(left>=0&&left+39<frontMin,
                    "back boot never crowds under the front");
            }
            if(t==100&&p==100)
                check(right==0&&left==0,"100/100 keeps original boot coordinates");
        }
        check(BodyAlignmentV120.frontBootShift(100,55)==0,
            "wide torso: front boot does not retreat beneath its leading edge");
        check(BodyAlignmentV120.frontBootShift(55,55)==-36,
            "matching narrow torso/pelvis: front boot aligns at x144");
        check(BodyAlignmentV120.rearBootShift(55)==27,
            "rear foot connects to bridge while remaining behind");
        System.out.println("V120 front-foot leading-edge alignment / rear-foot contact / torso top outline: PASS");
    }
}
