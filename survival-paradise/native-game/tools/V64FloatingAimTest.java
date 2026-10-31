package com.survivalparadise.nativegame;

public final class V64FloatingAimTest {
    static void require(boolean v,String msg){if(!v)throw new AssertionError(msg);}
    static void near(float got,float want,float eps,String msg){
        require(Math.abs(got-want)<=eps,msg+" got="+got+" expected="+want);
    }
    public static void main(String[] args){
        near(FloatingAimV64.response(0f,.08f,1.35f),0f,1e-6f,"center stops");
        near(FloatingAimV64.response(.079f,.08f,1.35f),0f,1e-6f,"deadzone stops");
        float fine=FloatingAimV64.response(.2f,.08f,1.35f);
        float half=FloatingAimV64.response(.6f,.08f,1.35f);
        require(fine>0f&&fine<.15f,"small touch must aim precisely");
        require(half>fine&&half<1f,"analog acceleration must be progressive");
        near(FloatingAimV64.response(1f,.08f,1.35f),1f,1e-6f,"max deflection");
        near(FloatingAimV64.response(3f,.08f,1.35f),1f,1e-6f,"over-stretch clamped");
        float fullSpeed=FloatingAimV64.scaledSpeed(6500f,1300f);
        require(1300f/fullSpeed<.3f,"full-speed viewport traversal must be under 0.3 sec");
        require(FloatingAimV64.scaledSpeed(2900f,1300f)>1200f,
                "default sensitivity must exceed old V63 maximum");
        require(FloatingAimV64.scaledSpeed(6500f,2600f)>fullSpeed,
                "wide screens receive proportional speed");
        near(FloatingAimV64.edgeStrength(650,1300,140,1f),0f,1e-5f,"center no camera pan");
        near(FloatingAimV64.edgeStrength(1220,1300,140,1f),60f/140f,1e-4f,
             "smooth pan near edge");
        near(FloatingAimV64.edgeStrength(1290,1300,140,-1f),0f,1e-5f,
             "panning must match active direction");
        near(FloatingAimV64.edgeStrength(1290,1300,140,0f),0f,1e-5f,
             "release stops camera pan");
        near(FloatingAimV64.edgeStrength(0,1300,140,-1f),1f,1e-5f,"left camera edge");
        System.out.println("V64 PASS: fast relative cursor, analog precision, deadzone, edge pan, release");
    }
}
