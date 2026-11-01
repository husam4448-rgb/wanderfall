package com.survivalparadise.nativegame;
/** Stable relation/reputation and situational speech without network dialogue. */
public final class NPCRelationshipsV92 {
    public static final int HOSTILE=-1,NEUTRAL=0,FRIENDLY=1;
    public int reputation=25;
    public int tradeCount;
    public static int stance(int type,boolean bandit,boolean follower){
        if(bandit||type==ClinicActorsV90.ZOMBIE||type==ClinicActorsV90.FERAL||
            type==ClinicActorsV90.RAIDER)return HOSTILE;
        if(follower||type==ClinicActorsV90.MEDIC||type==ClinicActorsV90.SURVIVOR)return FRIENDLY;
        return NEUTRAL;
    }
    public String speech(int role,int phase,boolean threat){
        if(role==HOSTILE)return threat?"You're trespassing!":"Keep your distance.";
        if(role==FRIENDLY)return threat?"I'll cover you!":
            (phase%3==0?"Area looks clear.":phase%3==1?"Stay close.":"Need supplies?");
        if(threat)return "Hostiles nearby!";
        return phase%3==0?"Want to trade?":phase%3==1?"Good to see another survivor.":"Roads are dangerous.";
    }
    public boolean canRecruit(){return reputation>=30;}
    public void trade(){tradeCount++;reputation=Math.min(100,reputation+4);}
    public void helped(){reputation=Math.min(100,reputation+2);}
    public String encode(){return reputation+","+tradeCount;}
    public void decode(String src){
        reputation=25;tradeCount=0;
        if(src==null)return;
        try{
            String[] parts=src.split(",",-1);
            if(parts.length!=2)return;
            reputation=Math.max(0,Math.min(100,Integer.parseInt(parts[0])));
            tradeCount=Math.max(0,Math.min(99999,Integer.parseInt(parts[1])));
        }catch(NumberFormatException ignored){}
    }
}