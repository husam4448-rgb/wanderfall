package com.survivalparadise.nativegame;
public final class V76TopHudTest {
    static void require(boolean b,String message){if(!b)throw new AssertionError(message);}
    public static void main(String[]args){
        for(float width:new float[]{480,600,720,960,1200,1480,1920}){
            float previous=0;
            for(int i=0;i<TopHudV76.COUNT;i++){
                float x=TopHudV76.x(i,width),r=x+TopHudV76.buttonWidth(i,width);
                require(x>=0&&r<width&&x>previous,"overlap/offscreen "+width+" "+i);
                require(TopHudV76.hit((x+r)/2f,19f,width)==i,"touch mismatch "+i);
                require(TopHudV76.hit((x+r)/2f,4f,width)==-1,"invisible top strip");
                previous=r;
            }
            require(TopHudV76.hit(12f,55f,width)==-1,"blank top space intercepted");
        }
        require(TopHudV76.COUNT==8,"missing legacy action");
        System.out.println("V76 PASS: 8 aligned compact top actions tested at seven screen widths");
    }
}
