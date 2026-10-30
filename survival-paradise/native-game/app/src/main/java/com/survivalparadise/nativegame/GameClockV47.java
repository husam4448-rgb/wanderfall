package com.survivalparadise.nativegame;

/** Persisted, uninterrupted in-game solar clock. Pause freezes the clock. */
public final class GameClockV47 {
    private float minuteOfDay;
    private int day=1;
    private float realDayMinutes=36f;

    public GameClockV47(float startMinute){setClock(startMinute,1);}
    public void configure(float realMinutes){realDayMinutes=Math.max(12f,Math.min(120f,realMinutes));}
    public void setClock(float minutes,int number){
        minuteOfDay=wrap(minutes); day=Math.max(1,number);
    }
    public void jumpToHour(float hour){minuteOfDay=wrap(hour*60f);}
    private static float wrap(float value){float v=value%1440f;return v<0?v+1440f:v;}
    public void advance(float realSeconds){
        if(realSeconds<=0)return;
        float minutes=Math.min(realSeconds,.25f)*24f/realDayMinutes;
        float value=minuteOfDay+minutes;
        if(value>=1440){day+=(int)(value/1440f);}
        minuteOfDay=wrap(value);
    }
    public int day(){return day;}
    public float minute(){return minuteOfDay;}
    public float hour(){return minuteOfDay/60f;}
    public String display(){int n=((int)minuteOfDay)%1440;return String.format(java.util.Locale.US,"D%d %02d:%02d",day,n/60,n%60);}
    private static float smooth(float t){t=Math.max(0f,Math.min(1f,t));return t*t*(3-2*t);}
    /** 0 = full daylight, 1 = full night. Dawn 04:30-07:00; dusk 17:30-20:00. */
    public float nightFraction(){
        float h=hour();
        if(h<4.5f||h>=20f)return 1f;
        if(h<7f)return 1f-smooth((h-4.5f)/2.5f);
        if(h<17.5f)return 0f;
        return smooth((h-17.5f)/2.5f);
    }
    public int darkness(int nightAlpha){return Math.round(Math.max(0,Math.min(248,nightAlpha))*nightFraction());}
}