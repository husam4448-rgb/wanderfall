package com.survivalparadise.nativegame;
public final class V71ClassicAimTest {
    static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
    static void near(float got,float expected,String message){
        check(Math.abs(got-expected)<.001f,message+" got="+got+" expected="+expected);
    }
    public static void main(String[] args){
        float rest=190f,bulletMax=2665f;
        near(ClassicAimV71.distance(rest,bulletMax,0),rest,"release default");
        near(ClassicAimV71.distance(rest,bulletMax,.05f),rest,"deadzone");
        near(ClassicAimV71.distance(rest,bulletMax,.30f),251.5f,"light deflection proportional");
        near(ClassicAimV71.distance(rest,bulletMax,.5f),292.5f,"middle of analog pad");
        near(ClassicAimV71.distance(rest,bulletMax,1f),395f,"full deflection old 205px span");
        near(ClassicAimV71.distance(rest,bulletMax,5f),395f,"overshoot never speeds up");
        near(ClassicAimV71.distance(505,5135,.5f),607.5f,"sniper controllable span");
        near(ClassicAimV71.distance(66,88,1f),88f,"melee stops at hit reach");
        near(ClassicAimV71.heading(-1f,1f,1f),-1f,"reverse direction instant");
        near(ClassicAimV71.heading(1f,1f,-1f),1f,"reverse back instant");
        near(ClassicAimV71.heading(0f,0f,-1f),-1f,"release keeps last direction");
        near(ClassicAimV71.thumb(.5f,.5f),.5f,"thumb tracks finger");
        near(ClassicAimV71.thumb(3f,3f),1f,"thumb bounded to pad circle");
        near(ClassicAimV71.panFactor(.5f,.72f),0f,"normal aim without camera pan");
        near(ClassicAimV71.panFactor(.72f,.72f),0f,"camera threshold");
        near(ClassicAimV71.panFactor(1f,.72f),1f,"pan at full reach");
        System.out.println("V71 PASS: classic joystick travel controls crosshair, sliding knob, no acceleration, reverse instant");
    }
}
